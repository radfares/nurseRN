"""
Response Synthesizer - Combines agent outputs into coherent responses.

Uses LLM to synthesize results from multiple agent tasks into
natural language responses for the user.

Created: 2025-12-11
"""

import json
import logging
import os
from typing import Any, Dict, List, TYPE_CHECKING, Optional

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

    def synthesize(
        self,
        user_message: str,
        plan: List[Any],
        results: Dict[str, Any],
        context: "ConversationContext"
    ) -> str:
        """
        Synthesize agent results into a coherent response.

        Args:
            user_message: Original user request
            plan: List of AgentTask objects that were executed
            results: Dict mapping task_id to execution results
            context: Current conversation context

        Returns:
            Natural language response for the user
        """
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

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Synthesis failed: {e}", exc_info=True)
            return self._fallback_synthesis(results)

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
- Over-promise or make clinical recommendations"""

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

        return f"""User request: "{user_message}"

Project: {context.project_name}
Phase: {context.current_phase}

Execution Plan:
{chr(10).join(plan_summary)}

Results:
{chr(10).join(results_summary)}

Synthesize these results into a helpful response for the user."""

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
