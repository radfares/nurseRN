"""
Response Synthesizer - Combines agent outputs into coherent responses.

Uses LLM to synthesize results from multiple agent tasks into
natural language responses for the user.

Created: 2025-12-11
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, TYPE_CHECKING, Optional, Set, Tuple

from openai import OpenAI

if TYPE_CHECKING:
    from src.orchestration.conversation_context import ConversationContext

logger = logging.getLogger(__name__)


class ResponseSynthesizer:
    """
    Synthesizes agent outputs into user-facing responses.

    Takes execution plan results and creates coherent, helpful responses
    that summarize findings, highlight key information, and guide next steps.
    """

    # Class-level tracking of completed synthesis requests (Phase 3)
    _synthesis_completed: set = set()

    def __init__(self, model: str = "gpt-4o", client: Optional[OpenAI] = None):
        """
        Initialize synthesizer.

        Args:
            model: OpenAI model to use for synthesis
        """
        if client is not None:
            self.client = client
        else:
            api_key = os.getenv("OPENAI_API_KEY")
            self.client = OpenAI() if api_key else None
        self.model = model

    @classmethod
    def reset_synthesis_tracking(cls):
        """Reset synthesis tracking (for testing)."""
        cls._synthesis_completed.clear()

    def synthesize(
        self,
        user_message: str,
        plan: List[Any],
        results: Dict[str, Any],
        context: "ConversationContext",
        request_id: Optional[str] = None
    ) -> str:
        """
        Synthesize agent results into a coherent response.

        Args:
            user_message: Original user request
            plan: List of AgentTask objects that were executed
            results: Dict mapping task_id to execution results
            context: Current conversation context
            request_id: Optional request ID for duplicate detection (Phase 3)

        Returns:
            Natural language response for the user
        """
        # Phase 3 Guard: Prevent duplicate synthesis for the same request
        if request_id and request_id in self._synthesis_completed:
            logger.warning(
                f"PHASE3 GUARD: Duplicate synthesis attempt detected for request_id={request_id}. "
                "Returning cached acknowledgment."
            )
            return "Response already generated for this request."
        # Phase 3 Guard: Check if results is empty or contains no valid data
        if not results or len(results) == 0:
            logger.warning("PHASE3 GUARD: Synthesis aborted - results dict is empty")
            return self._synthesize_no_results()

        # Phase 3 Guard: Check if at least one result is successful with valid output
        has_valid_result = False
        for task_id, result in results.items():
            if result.get("success", False):
                output = result.get("output")
                # Verify output is not None and not empty
                if output is not None and output != {}:
                    has_valid_result = True
                    break

        if not has_valid_result:
            logger.warning(
                "PHASE3 GUARD: Synthesis aborted - no successful results with valid output. "
                f"Results: {list(results.keys())}"
            )
            return self._synthesize_no_valid_output(results)

        # Check for failures
        failures = [
            task_id for task_id, result in results.items()
            if not result.get("success", False)
        ]

        if len(failures) == len(results) and len(results) > 0:
            return self._synthesize_failure(failures, results)

        # Build synthesis prompt
        system_prompt = self._build_system_prompt()
        user_prompt = self._build_user_prompt(user_message, plan, results, context)

        try:
            if self.client is None:
                raise RuntimeError("OpenAI client unavailable; using fallback synthesis")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )

            synthesized_response = response.choices[0].message.content
            synthesized_response = self._enforce_timeline_grounding(
                user_message=user_message,
                synthesized_response=synthesized_response,
                results=results,
            )

            # Phase 3: Mark synthesis as completed
            if request_id:
                self._synthesis_completed.add(request_id)
                logger.info(f"PHASE3: Synthesis completed for request_id={request_id}")

            return synthesized_response

        except Exception as e:
            logger.error(f"Synthesis failed: {e}", exc_info=True)
            fallback_response = self._fallback_synthesis(results)
            fallback_response = self._enforce_timeline_grounding(
                user_message=user_message,
                synthesized_response=fallback_response,
                results=results,
            )

            # Phase 3: Mark synthesis as completed even for fallback
            if request_id:
                self._synthesis_completed.add(request_id)
                logger.info(f"PHASE3: Fallback synthesis completed for request_id={request_id}")

            return fallback_response

    def _build_system_prompt(self) -> str:
        """Build system prompt for synthesis."""
        return """You are a helpful nursing research assistant synthesizing results.

Your role is to:
1. Combine outputs from multiple research agents into a coherent response
2. Highlight the most important findings
3. Present information in a clear, actionable format
4. Use nursing/healthcare terminology appropriately
5. Be concise but thorough

Format guidelines:
- Use bullet points for lists
- Bold key terms and findings
- Include relevant citations when available (PMID, DOI)
- End with suggested next steps when appropriate

Do NOT:
- Make up information not in the results
- Add citations that weren't found by the agents
- Over-promise or make clinical recommendations

Timeline grounding rule:
- If you mention milestones/deadlines/timeline dates, they MUST come from database-backed milestone results.
- If milestone data was not returned by agents, say you cannot provide timeline dates without querying the milestones table."""

    def _enforce_timeline_grounding(
        self,
        *,
        user_message: str,
        synthesized_response: str,
        results: Dict[str, Any],
    ) -> str:
        """
        Guardrail: prevent timeline/milestone claims without DB verification.

        Rationale: The synthesizer is allowed to be fluent, but must not introduce
        timeline dates/months that were not verified via the milestones table.
        """
        response_text = synthesized_response or ""
        if not isinstance(response_text, str):
            response_text = str(response_text)

        has_timeline_claims, found_dates, found_month_years = self._detect_timeline_claims(response_text)
        if not has_timeline_claims:
            return response_text

        allowed_dates, allowed_month_years, has_milestones_data = self._extract_allowed_milestone_dates(results)

        if not has_milestones_data:
            logger.warning(
                "DATABASE GROUNDING GUARD: synthesized response contained timeline claims "
                "but no milestones table results were found in task outputs."
            )
            return (
                "DATABASE GROUNDING SYSTEM ACTIVATED\n\n"
                "I can’t provide project timeline/milestone dates without verifying them in the database.\n"
                "Please run a timeline query so I can read the `milestones` table (e.g., “Show my milestones” "
                "or “What’s my next deadline?”)."
            )

        unverified_dates = {
            d for d in (self._normalize_date_to_iso(x) for x in found_dates) if d and d not in allowed_dates
        }
        unverified_month_years = {
            m for m in (self._normalize_month_year(x) for x in found_month_years) if m and m not in allowed_month_years
        }

        if unverified_dates or unverified_month_years:
            logger.warning(
                "DATABASE GROUNDING GUARD: synthesized response contained unverified timeline dates/months "
                f"unverified_dates={sorted(unverified_dates)} unverified_month_years={sorted(unverified_month_years)}"
            )
            return (
                "DATABASE GROUNDING SYSTEM ACTIVATED\n\n"
                "Timeline information in the draft response included dates/months that were not verified against "
                "the `milestones` table.\n"
                "Please re-run your timeline question so I can quote the exact milestone records."
            )

        return response_text

    @staticmethod
    def _detect_timeline_claims(text: str) -> Tuple[bool, List[str], List[str]]:
        lowered = (text or "").lower()
        timeline_keywords = (
            "milestone",
            "milestones",
            "deadline",
            "deadlines",
            "due date",
            "due",
            "timeline",
            "schedule",
            "next deadline",
            "next milestone",
        )
        has_keywords = any(k in lowered for k in timeline_keywords)

        date_pattern = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\\s+\\d{1,2}(?:,?\\s*\\d{4})?|202\\d-\\d{2}-\\d{2}"
        month_year_pattern = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\\s+202\\d"

        dates_found = re.findall(date_pattern, text or "", re.IGNORECASE)
        month_years_found = re.findall(month_year_pattern, text or "", re.IGNORECASE)

        # Only enforce when there's a meaningful timeline claim (specific "what/when is due" info).
        has_specific_timeline_language = bool(
            re.search(r"\\b(next milestone|next deadline|due by|due date|due this|due next)\\b", lowered)
        )
        has_timeline_claims = bool(
            (dates_found or month_years_found) and has_keywords
        ) or (has_keywords and has_specific_timeline_language)
        return has_timeline_claims, dates_found, month_years_found

    @staticmethod
    def _extract_allowed_milestone_dates(results: Dict[str, Any]) -> Tuple[Set[str], Set[str], bool]:
        allowed_dates: Set[str] = set()
        allowed_month_years: Set[str] = set()
        has_milestones_data = False

        for result in (results or {}).values():
            if not isinstance(result, dict) or not result.get("success"):
                continue

            agent = str(result.get("agent", "")).lower()
            action = str(result.get("action", "")).lower()
            if agent == "project_timeline" or "milestone" in action:
                has_milestones_data = True

            output = result.get("output")
            output_text = output if isinstance(output, str) else json.dumps(output, default=str)

            # Evidence of milestones table data in the payload
            if '"due_date"' in output_text or "milestone_id" in output_text or "milestone_name" in output_text:
                has_milestones_data = True

            for d in re.findall(r"\\b(\\d{4}-\\d{2}-\\d{2})\\b", output_text):
                allowed_dates.add(d)

        for d in allowed_dates:
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
                allowed_month_years.add(dt.strftime("%B %Y"))
            except Exception:
                continue

        return allowed_dates, allowed_month_years, has_milestones_data

    @staticmethod
    def _normalize_date_to_iso(value: str) -> Optional[str]:
        val = (value or "").strip()
        if not val:
            return None

        if re.match(r"^202\\d-\\d{2}-\\d{2}$", val):
            return val

        try:
            cleaned = val.replace(",", "")
            dt = datetime.strptime(cleaned, "%B %d %Y")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return None

    @staticmethod
    def _normalize_month_year(value: str) -> Optional[str]:
        val = (value or "").strip()
        if not val:
            return None
        parts = val.split()
        if len(parts) != 2:
            return None
        month, year = parts
        return f"{month.capitalize()} {year}"

    def _build_user_prompt(
        self,
        user_message: str,
        plan: List[Any],
        results: Dict[str, Any],
        context: "ConversationContext"
    ) -> str:
        """Build user prompt with execution context and results."""
        # Format plan summary
        plan_summary = []
        for task in plan:
            plan_summary.append(f"- {task.task_id}: {task.agent_name}.{task.action}")

        # Phase 2: Extract shortfall metadata
        shortfall_notes = []

        # Format results
        results_summary = []
        for task_id, result in results.items():
            if result.get("success"):
                output = result.get("output", {})
                # Handle Pydantic models and other non-JSON-serializable objects
                try:
                    # Try Pydantic model_dump
                    if hasattr(output, 'model_dump'):
                        output = output.model_dump()
                    elif hasattr(output, 'dict'):
                        output = output.dict()

                    # Phase 2: Check for shortfall metadata
                    if isinstance(output, dict):
                        requested = output.get("requested")
                        found = output.get("found")
                        has_shortfall = output.get("has_shortfall", False)

                        if requested is not None and found is not None and has_shortfall:
                            shortfall_notes.append(
                                f"- {task_id}: Requested {requested} results, found {found} "
                                f"({output.get('shortfall_ratio', 0.0):.0%} of requested)"
                            )

                    # Truncate large outputs
                    output_str = json.dumps(output, indent=2, default=str)
                    if len(output_str) > 2000:
                        output_str = output_str[:2000] + "\n... (truncated)"
                except (TypeError, ValueError) as e:
                    # Fallback: convert to string
                    output_str = str(output)[:2000]

                results_summary.append(f"### {task_id} ({result.get('agent')}.{result.get('action')})\n{output_str}")
            else:
                results_summary.append(f"### {task_id} - FAILED\nError: {result.get('error')}")

        # Phase 2: Include shortfall context in prompt
        shortfall_context = ""
        if shortfall_notes:
            shortfall_context = f"""

IMPORTANT - Partial Results Context:
{chr(10).join(shortfall_notes)}

When synthesizing your response:
- Acknowledge that fewer results were found than requested
- Adjust your tone to reflect partial/limited findings
- Do NOT claim comprehensive coverage
- Suggest that more specific search terms or broader criteria might help"""

        return f"""User request: "{user_message}"

Project: {context.project_name}
Phase: {context.current_phase}

Execution Plan:
{chr(10).join(plan_summary)}

Results:
{chr(10).join(results_summary)}{shortfall_context}

Synthesize these results into a helpful response for the user."""

    def _synthesize_no_results(self) -> str:
        """Generate response when results dict is empty."""
        return """Unable to process your request - no agent tasks were executed.

This may indicate a planning issue. Please try:
1. Rephrasing your request with more context
2. Starting with a simpler query
3. Checking that your request is related to nursing research

Type 'help' for available commands."""

    def _synthesize_no_valid_output(self, results: Dict[str, Any]) -> str:
        """Generate response when no results contain valid output."""
        # Try to extract partial information about what failed
        failed_tasks = []
        for task_id, result in results.items():
            agent = result.get('agent', 'unknown')
            action = result.get('action', 'unknown')
            error = result.get('error', 'No output produced')
            failed_tasks.append(f"- {agent}.{action}: {error}")

        return f"""Unable to complete your request - all agent tasks failed or produced no output.

Failed tasks:
{chr(10).join(failed_tasks)}

Please try:
1. Simplifying your request
2. Checking that required resources are available
3. Trying again in a moment

Type 'help' for available commands."""

    def _synthesize_failure(
        self,
        failures: List[str],
        results: Dict[str, Any]
    ) -> str:
        """Generate response when all tasks failed."""
        error_messages = []
        for task_id in failures:
            result = results.get(task_id, {})
            error_messages.append(f"- {task_id}: {result.get('error', 'Unknown error')}")

        return f"""I encountered errors while processing your request:

{chr(10).join(error_messages)}

Please try:
1. Rephrasing your request
2. Breaking it into smaller steps
3. Checking that required information is available

Type 'help' for available commands."""

    def _fallback_synthesis(self, results: Dict[str, Any]) -> str:
        """Simple fallback when LLM synthesis fails."""
        successful = []
        for task_id, result in results.items():
            if result.get("success"):
                output = result.get("output", {})
                if isinstance(output, dict) and "text" in output:
                    successful.append(output["text"])
                else:
                    successful.append(str(output)[:500])

        if successful:
            return "Here's what I found:\n\n" + "\n\n---\n\n".join(successful)
        else:
            return "I couldn't complete your request. Please try again or type 'help'."


__all__ = ['ResponseSynthesizer']
