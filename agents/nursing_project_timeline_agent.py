"""
Nursing Project Timeline Assistant
Helps track project milestones and provides month-specific guidance

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
PHASE 2 COMPLETE (2025-11-26): Refactored to use BaseAgent inheritance
"""

from textwrap import dedent
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
import re

# Module exports
__all__ = ['ProjectTimelineAgent', 'project_timeline_agent']

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

# Import centralized configuration
from agent_config import get_db_path, is_reasoning_block_enabled

# Import BaseAgent for inheritance pattern
from agents.base_agent import BaseAgent


class ProjectTimelineAgent(BaseAgent):
    """
    Project Timeline Assistant - Milestone tracking and guidance.

    No external tools - pure timeline guidance and project management.
    Provides month-by-month guidance for nursing residency improvement project.
    """

    def __init__(self):
        # No tools for this agent (pure guidance/timeline tracking)
        tools = self._create_tools()
        super().__init__(
            agent_name="Project Timeline Assistant",
            agent_key="project_timeline",
            tools=tools
        )

    def _create_tools(self) -> list:
        """
        Create tools for the timeline agent.

        This agent uses MilestoneTools to query the project database
        for milestone information (instead of hardcoded dates).
        """
        import sys
        import os
        # Add parent directory to path to import from src
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        from src.services.api_tools import create_milestone_tools_safe, build_tools_list

        # DISABLED: ReasoningTools causes runaway loops (agno library bug)
        # Using reasoning=True parameter instead - provides same capability with proper limits
        # reasoning_tools = ReasoningTools(add_instructions=False)

        # Create milestone database tool
        milestone_tool = create_milestone_tools_safe(required=False)

        # Milestone tools only - reasoning handled by reasoning=True parameter
        tools = build_tools_list(milestone_tool)

        # Log tool availability
        print("ℹ️ Reasoning: via reasoning=True parameter (not ReasoningTools)")
        if milestone_tool:
            print("✅ MilestoneTools available - will query database for timeline")
        else:
            print("⚠️ MilestoneTools unavailable - timeline guidance limited")

        return tools

    def _create_agent(self) -> Agent:
        """Create and configure the Project Timeline Agent."""
        return Agent(
            name="Project Timeline Assistant",
            role="Guide nursing residents through improvement project milestones",
            model=OpenAIChat(id="gpt-4o-mini", temperature=0),  # Cheaper for timeline/guidance
            reasoning=True,  # Enable chain-of-thought for complex project planning
            reasoning_model=OpenAIChat(id="gpt-4o-mini", max_tokens=1500),  # Separate reasoning model
            tools=self.tools,
            description=dedent("""\
                You are a Project Timeline Assistant for the Nursing Residency improvement project
                running from November 2025 to June 2026. You help residents stay on track with
                monthly deliverables and provide guidance for each phase of the project.
                """),
            instructions=dedent("""\
                PROJECT TIMELINE ASSISTANT - Database-Driven Guidance

                ABSOLUTE LAW #1: DATABASE GROUNDING
                - You MUST query the database for milestone dates and status
                - NEVER invent or assume dates, deadlines, or deliverables
                - If the database is empty or missing data, state that clearly
                - Do not "fill in" missing dates with guesses

                ABSOLUTE LAW #2: ACCURACY OVER HELPFULNESS
                - It is better to say "I don't know" than to give a wrong date
                - If tool execution fails, do not guess the timeline
                - Always cite the specific milestone name from the database

                You have access to the milestones table via MilestoneTools. Use these tools to provide
                accurate, up-to-date timeline guidance based on the ACTUAL project database.

                AVAILABLE TOOLS:
                1. get_all_milestones() - Retrieve all milestones with status and dates
                2. get_next_milestone() - Find the next incomplete milestone
                3. get_milestones_by_date_range(start, end) - Get milestones in timeframe
                4. update_milestone_status(id, status) - Mark milestones as pending/in_progress/completed
                5. add_milestone(name, date, description, deliverables) - Add custom milestones

                HOW TO USE TOOLS:
                - When asked about timeline/deadlines → Use get_all_milestones() or get_next_milestone()
                - When asked "what's next?" → Use get_next_milestone()
                - When asked about specific date range → Use get_milestones_by_date_range()
                - When user completes a task → Use update_milestone_status() to mark it
                - When user needs custom milestone → Use add_milestone()

                MILESTONE STATUS MEANINGS:
                - pending: Not started yet
                - in_progress: Currently working on this
                - completed: Finished (has completion_date)
                - overdue: Past due_date and not completed

                GUIDANCE PRINCIPLES:
                1. Query database FIRST before answering timeline questions
                2. Help residents understand current phase based on DB status
                3. Suggest next steps based on incomplete milestones
                4. Remind about deadlines from database, not assumptions
                5. Provide examples when helpful
                6. Track completion by updating milestone status
                7. Calculate days until due dates
                8. Flag overdue milestones

                RESPONSE FORMAT:
                - Query the database to get current milestone data
                - Clearly state current phase based on milestone status
                - List immediate next steps from deliverables
                - Identify upcoming deadlines with days remaining
                - Suggest who to contact if milestone notes include contacts
                - Provide actionable guidance based on actual data

                EXAMPLE INTERACTIONS:

                User: "What's my next deadline?"
                You: [Call get_next_milestone()]
                Response: "Your next milestone is PICOT Development, due December 17, 2025 (21 days from now).
                Status: in_progress. Deliverables: Approved PICOT statement, NM confirmation form."

                User: "I finished my PICOT statement"
                You: [Call update_milestone_status(1, 'completed')]
                Response: "Great! I've marked 'PICOT Development' as completed. Your next milestone is
                Literature Search, due January 21, 2026."

                User: "What do I need to complete this month?"
                You: [Call get_milestones_by_date_range('2025-12-01', '2025-12-31')]
                Response: [List milestones due this month with status and deliverables]

                IMPORTANT:
                - Trust the database as the source of truth
                - If a milestone has custom notes, include them in your response
                - If all milestones are completed, congratulate the user
                - If no milestones exist, suggest creating them
                """) + (
                "\n"
                + dedent("""\
                REASONING APPROACH (PROJECT PLANNING):
                - Break down complex requests into timeframe, dependency chain, and deliverables before answering
                - State assumptions about dates, responsible roles, and scope; ask for missing details instead of guessing
                - Query the milestone database first; align every recommendation to a specific record
                - Identify dependencies and critical path; call out blockers and resource constraints explicitly
                - Offer alternatives (sequence changes, scope trims, backups) and note trade-offs in risk, effort, or quality
                - Surface uncertainties (missing dates, ambiguous status) and propose concrete next tool calls to resolve them
                - Keep database grounding rules primary; reasoning supports but never overrides refusal to invent dates
                - Communicate concise next steps with owners, due dates, and days remaining
                """)
                if is_reasoning_block_enabled()
                else ""
            ),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
            tool_call_limit=10,  # CRITICAL: Prevent runaway loops (was unlimited)
            reasoning_max_steps=5,  # Reduce from default 10 to prevent excessive API calls
            db=SqliteDb(db_file=get_db_path("project_timeline")),
            pre_hooks=[self._audit_pre_hook],
            post_hooks=[self._audit_post_hook],
        )

    def run_with_grounding_check(self, query: str, **kwargs) -> Any:
        """Execute the agent with database grounding enforcement."""
        import traceback

        agent_kwargs = dict(kwargs)
        project_name = agent_kwargs.pop("project_name", None)
        if self.audit_logger:
            self.audit_logger.log_query_received(query, project_name)

        stream_requested = bool(agent_kwargs.get("stream"))

        try:
            milestone_snapshot = self._get_milestone_snapshot(project_name=project_name)
            self._last_milestone_snapshot = milestone_snapshot

            if milestone_snapshot is None:
                raise ValueError("Unable to query milestones table (no milestone snapshot available).")

            if len(milestone_snapshot) == 0:
                raise ValueError(
                    "Milestones table is empty for the active project. "
                    "I cannot provide timeline dates without database records."
                )

            grounded_query = self._build_grounded_query(query, milestone_snapshot)
            response = self.agent.run(grounded_query, **agent_kwargs)

            if stream_requested:
                return response

            self._validate_run_output(response)

            if self.audit_logger:
                self.audit_logger.log_response_generated(
                    response=str(response.content),
                    response_type="success",
                    validation_passed=True
                )

            return response

        except ValueError as validation_error:
            if self.audit_logger:
                self.audit_logger.log_error(
                    error_type="DatabaseGroundingViolation",
                    error_message=str(validation_error),
                    stack_trace=traceback.format_exc()
                )

            return {
                "content": (
                    "DATABASE GROUNDING SYSTEM ACTIVATED\n\n"
                    f"{str(validation_error)}\n\n"
                    "I must query the database before providing timeline information.\n"
                    "Please rephrase your question so I can look up the actual milestones."
                ),
                "validation_passed": False
            }

        except Exception as e:
            if self.audit_logger:
                self.audit_logger.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise

    def _validate_run_output(self, run_output: Any) -> bool:
        """
        Ensure milestone dates match database.
        BLOCKS if dates mentioned without database query.
        """
        import re

        content = str(run_output.content) if hasattr(run_output, 'content') else str(run_output)
        snapshot = getattr(self, "_last_milestone_snapshot", None)
        allowed_dates, allowed_month_years = self._allowed_dates_from_snapshot(snapshot)
        if not allowed_dates:
            allowed_dates, allowed_month_years = self._allowed_dates_from_run_output(run_output)

        date_pattern = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s*\d{4})?|202\d-\d{2}-\d{2}"
        dates_found = re.findall(date_pattern, content, re.IGNORECASE)

        month_year_pattern = r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+202\d"
        month_years_found = re.findall(month_year_pattern, content, re.IGNORECASE)

        milestone_keywords = ("milestone", "deliverable", "deadline", "due date", "due by", "next deadline", "next milestone")
        has_milestone_content = any(kw in content.lower() for kw in milestone_keywords)

        if (dates_found or month_years_found or has_milestone_content) and not allowed_dates:
            if self.audit_logger:
                self.audit_logger.log_validation_check(
                    "database_grounding",
                    False,
                    {
                        "dates_found": dates_found,
                        "has_milestone_content": has_milestone_content,
                        "reason": "Timeline data mentioned without milestones table verification"
                    }
                )

            raise ValueError(
                f"DATABASE GROUNDING VIOLATION\n"
                f"Timeline information provided without querying/verifying against the milestones table.\n"
                f"Dates found: {dates_found}\n"
                f"REQUIRED: Query milestones table before providing timeline information."
            )

        unverified_dates = self._find_unverified_dates(dates_found, allowed_dates)
        unverified_month_years = {
            my for my in (self._normalize_month_year(m) for m in month_years_found) if my and my not in allowed_month_years
        }

        if unverified_dates or unverified_month_years:
            if self.audit_logger:
                self.audit_logger.log_validation_check(
                    "database_grounding",
                    False,
                    {
                        "unverified_dates": sorted(unverified_dates),
                        "unverified_month_years": sorted(unverified_month_years),
                        "reason": "Timeline dates/months not verified against milestones table",
                    },
                )
            raise ValueError(
                "DATABASE GROUNDING VIOLATION\n"
                "Timeline information included dates/months that are not present in the milestones table.\n"
                f"Unverified dates: {sorted(unverified_dates)}\n"
                f"Unverified months: {sorted(unverified_month_years)}\n"
                "REQUIRED: Only mention milestone dates returned by the database."
            )

        if self.audit_logger:
            self.audit_logger.log_validation_check("database_grounding", True, {})

        return True

    def _get_milestone_snapshot(self, project_name: Optional[str]) -> Optional[List[Dict[str, Any]]]:
        """
        Query the milestones table (source of truth) and return a list of milestone dicts.

        This is the grounding requirement: timeline answers must be based on the DB.
        """
        try:
            from src.tools.milestone_tools import MilestoneTools

            tool = MilestoneTools(project_name=project_name)
            raw = tool.get_all_milestones()
            parsed = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(parsed, dict) and parsed.get("error"):
                return None
            if isinstance(parsed, list):
                return parsed
            return None
        except Exception:
            return None

    @staticmethod
    def _build_grounded_query(user_query: str, milestones: List[Dict[str, Any]]) -> str:
        snapshot = json.dumps(milestones, indent=2, default=str)
        return (
            f"{user_query}\n\n"
            "DATABASE GROUNDING (milestones table snapshot):\n"
            f"{snapshot}\n\n"
            "Rules:\n"
            "- Use ONLY milestone names/dates/status from the snapshot above.\n"
            "- If the snapshot does not contain the requested timeframe, say so and suggest using a date range query.\n"
            "- Do not invent dates/months. If unsure, ask a follow-up question.\n"
        )

    @staticmethod
    def _allowed_dates_from_snapshot(
        milestones: Optional[List[Dict[str, Any]]],
    ) -> Tuple[Set[str], Set[str]]:
        if not milestones:
            return set(), set()

        allowed_dates: Set[str] = set()
        allowed_month_years: Set[str] = set()

        for m in milestones:
            for key in ("due_date", "completion_date"):
                val = m.get(key)
                if isinstance(val, str) and val:
                    allowed_dates.add(val)
                    try:
                        dt = datetime.strptime(val, "%Y-%m-%d")
                        allowed_month_years.add(dt.strftime("%B %Y"))
                    except Exception:
                        continue

        return allowed_dates, allowed_month_years

    @staticmethod
    def _normalize_month_year(value: str) -> Optional[str]:
        val = (value or "").strip()
        if not val:
            return None
        # Normalize capitalization: "january 2026" -> "January 2026"
        parts = val.split()
        if len(parts) != 2:
            return None
        month, year = parts
        return f"{month.capitalize()} {year}"

    def _find_unverified_dates(self, raw_dates: List[str], allowed_dates: Set[str]) -> Set[str]:
        unverified: Set[str] = set()
        for raw in raw_dates:
            normalized = self._normalize_date_to_iso(raw)
            if normalized is None:
                unverified.add(raw)
                continue
            if normalized not in allowed_dates:
                unverified.add(normalized)
        return unverified

    @staticmethod
    def _normalize_date_to_iso(value: str) -> Optional[str]:
        val = (value or "").strip()
        if not val:
            return None

        # ISO already
        if re.match(r"^202\d-\d{2}-\d{2}$", val):
            return val

        # Month Day, Year (year required for grounding)
        try:
            cleaned = val.replace(",", "")
            dt = datetime.strptime(cleaned, "%B %d %Y")
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return None

    @staticmethod
    def _allowed_dates_from_run_output(run_output: Any) -> Tuple[Set[str], Set[str]]:
        """
        Best-effort extraction of allowed milestone dates from tool outputs embedded in RunOutput.

        This keeps grounding enforcement working even when callers bypass run_with_grounding_check
        (e.g., calling the underlying agno Agent directly).
        """
        text = ""
        if hasattr(run_output, "messages") and run_output.messages:
            try:
                text = "\n".join(str(m) for m in run_output.messages)
            except Exception:
                text = str(run_output)
        else:
            text = str(run_output.content) if hasattr(run_output, "content") else str(run_output)

        due_dates = set(re.findall(r"\"due_date\"\\s*:\\s*\"(\\d{4}-\\d{2}-\\d{2})\"", text))
        completion_dates = set(re.findall(r"\"completion_date\"\\s*:\\s*\"(\\d{4}-\\d{2}-\\d{2})\"", text))
        allowed_dates = due_dates | completion_dates

        allowed_month_years: Set[str] = set()
        for d in allowed_dates:
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
                allowed_month_years.add(dt.strftime("%B %Y"))
            except Exception:
                continue

        return allowed_dates, allowed_month_years

    def show_usage_examples(self) -> None:
        """Display usage examples for the Project Timeline Assistant."""
        print("\n📅 Project Timeline Assistant Ready!")
        print("\nHelps you stay on track with project milestones")
        print("Queries your project database for accurate, up-to-date timeline information")
        print("\nExample usage:")
        print("-" * 60)

        print("\n1. Check upcoming milestones:")
        print('   response = project_timeline_agent.run("""')
        print('   What are my upcoming milestones?""")')

        print("\n2. Get next deadline:")
        print('   response = project_timeline_agent.run("""')
        print('   What\'s my next deadline?""")')

        print("\n3. Mark milestone complete:")
        print('   response = project_timeline_agent.run("""')
        print('   I finished my PICOT statement, mark it as completed""")')

        print("\n4. Check date range:")
        print('   response = project_timeline_agent.run("""')
        print('   What milestones are due this month?""")')

        print("\n5. With Streaming:")
        print('   project_timeline_agent.print_response("""')
        print('   Show me the status of all my milestones""", stream=True)')

        print("\n" + "-" * 60)
        print("\n💡 TIP: Timeline data comes from your project database!")
        print("Use stream=True for real-time response generation.")


# Create global instance for backward compatibility
# Wrapped in try/except for graceful degradation if initialization fails
try:
    _project_timeline_agent_instance = ProjectTimelineAgent()
    project_timeline_agent = _project_timeline_agent_instance.agent
    logger = _project_timeline_agent_instance.logger  # Expose logger for backward compatibility
except Exception as _init_error:
    import logging
    logging.error(f"Failed to initialize ProjectTimelineAgent: {_init_error}")
    _project_timeline_agent_instance = None
    project_timeline_agent = None
    logger = logging.getLogger(__name__)
    # Re-raise only if running as main module
    if __name__ == "__main__":
        raise


def show_usage_examples():
    """Display usage examples for the Project Timeline Assistant (module-level wrapper)."""
    if _project_timeline_agent_instance is not None:
        _project_timeline_agent_instance.show_usage_examples()
    else:
        print("❌ Project Timeline Agent not initialized")


def get_project_timeline_agent():
    """Factory function to get the ProjectTimelineAgent instance.

    Returns:
        ProjectTimelineAgent wrapper instance, or None if initialization failed.
    """
    return _project_timeline_agent_instance


if __name__ == "__main__":
    if _project_timeline_agent_instance is not None:
        _project_timeline_agent_instance.run_with_error_handling()
    else:
        print("❌ Agent failed to initialize. Check logs for details.")
