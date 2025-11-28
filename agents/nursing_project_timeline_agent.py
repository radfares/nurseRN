"""
Nursing Project Timeline Assistant
Helps track project milestones and provides month-specific guidance

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
PHASE 2 COMPLETE (2025-11-26): Refactored to use BaseAgent inheritance
"""

from textwrap import dedent

# Module exports
__all__ = ['ProjectTimelineAgent', 'project_timeline_agent']

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

# Import centralized configuration
from agent_config import get_db_path

# Import BaseAgent for inheritance pattern
from .base_agent import BaseAgent


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

        # Create milestone database tool
        milestone_tool = create_milestone_tools_safe(required=False)

        tools = build_tools_list(milestone_tool)

        # Log tool availability
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
            model=OpenAIChat(id="gpt-4o-mini"),  # Cheaper for timeline/guidance
            tools=self.tools,
            description=dedent("""\
                You are a Project Timeline Assistant for the Nursing Residency improvement project
                running from November 2025 to June 2026. You help residents stay on track with
                monthly deliverables and provide guidance for each phase of the project.
                """),
            instructions=dedent("""\
                PROJECT TIMELINE ASSISTANT - Database-Driven Guidance

                You have access to the milestones table via MilestoneTools. Use these tools to provide
                accurate, up-to-date timeline guidance based on the ACTUAL project database.

                CRITICAL: ALWAYS query the database - NEVER assume or invent dates.

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
                """),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
            db=SqliteDb(db_file=get_db_path("project_timeline")),
        )

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


if __name__ == "__main__":
    if _project_timeline_agent_instance is not None:
        _project_timeline_agent_instance.run_with_error_handling()
    else:
        print("❌ Agent failed to initialize. Check logs for details.")
