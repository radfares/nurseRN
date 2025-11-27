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

        This agent has no external tools - it provides timeline guidance
        based on hardcoded project milestones (Nov 2025 - June 2026).
        """
        # No tools needed for timeline agent
        return []

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
                PROJECT TIMELINE (Nov 2025 - June 2026):

                NOVEMBER 19, 2025 (2 hours):
                - Introduction to improvement project
                - PICOT education
                - Topic brainstorming
                - Initial discussion with CNS facilitator
                - Action: Connect with Nurse Manager, get topic confirmation form signed

                DECEMBER 17, 2025 (2 hours):
                - DUE: NM confirmation form to Kelly Miller (kmille45@hfhs.org)
                - PICOT statement review and approval by CNS lead
                - Identify major issue type (policy adherence, patient safety, education, etc.)
                - Action: Email Laura Arrick (Larrick1@hfhs.org) for literature search help
                - Find reasons why improvement is important (Joint Commission, Core Measures, etc.)

                JANUARY 21, 2026 (1 hour):
                - Literature search and article selection
                - Choose THREE (3) research articles
                - Analyze articles for applicable insights
                - Identify best practice recommendations
                - Action: Prepare article summaries and highlights

                FEBRUARY 18, 2026 (1 hour):
                - Continue literature analysis if needed
                - Begin intervention planning

                MARCH 18, 2026 (1 hour):
                - Outline realistic improvement steps
                - Plan pre/post intervention data collection
                - Invite key stakeholders for input
                - Define success measurements
                - Action: Touch base with Nurse Manager
                - Identify needed tools and involved people
                - Determine if other departments needed
                - CNS introduces presentation evaluation tool

                APRIL 22, 2026 (2 hours):
                - DEADLINE: Complete poster board
                - Required content:
                  * Approved PICOT statement
                  * Problem/issue background
                  * Associated standards
                  * Literature search summary (3 articles)
                  * Intervention recommendations (sequential steps)
                  * Data collection plan (pre/post)
                  * Conclusions and nursing recommendations
                - DUE: Email PowerPoint to Kelly Miller (kmille45@hfhs.org)

                MAY 20, 2026 (1 hour):
                - Practice Day
                - Practice presentations
                - Dress code: Business casual/scrubs (NO jeans, sweatpants, hoodies)

                JUNE 17, 2026:
                - Final presentations
                - Graduation ceremony
                - All group members present

                GUIDANCE PRINCIPLES:
                1. Help residents understand current month's requirements
                2. Suggest next steps based on timeline
                3. Remind about deadlines and deliverables
                4. Provide examples when helpful
                5. Keep track of completed vs. pending tasks
                6. Suggest when to reach out to specific people (CNS, NM, librarian)

                RESPONSE FORMAT:
                - Clearly state current phase
                - List immediate next steps
                - Identify upcoming deadlines
                - Suggest who to contact if needed
                - Provide actionable guidance
                """),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
            db=SqliteDb(db_file=get_db_path("project_timeline")),
        )

    def show_usage_examples(self) -> None:
        """Display usage examples for the Project Timeline Assistant."""
        print("\n📅 Project Timeline Assistant Ready!")
        print("\nHelps you stay on track with monthly milestones")
        print("Timeline: November 2025 - June 2026")
        print("\nExample usage:")
        print("-" * 60)

        print("\n1. Check current requirements:")
        print('   response = project_timeline_agent.run("""')
        print('   What do I need to complete this month?""")')

        print("\n2. Plan ahead:")
        print('   response = project_timeline_agent.run("""')
        print('   What are the key deliverables for January?""")')

        print("\n3. Get unstuck:")
        print('   response = project_timeline_agent.run("""')
        print('   I finished my PICOT statement, what should I do next?""")')

        print("\n4. With Streaming:")
        print('   project_timeline_agent.print_response("""')
        print('   What deadlines are coming up this month?""", stream=True)')

        print("\n" + "-" * 60)
        print("\n💡 TIP: This timeline is specific to Nov 2025 - June 2026!")
        print("Use stream=True for real-time response generation.")


# Create global instance for backward compatibility
# Wrapped in try/except for graceful degradation if initialization fails
try:
    _project_timeline_agent_instance = ProjectTimelineAgent()
    project_timeline_agent = _project_timeline_agent_instance.agent
except Exception as _init_error:
    import logging
    logging.error(f"Failed to initialize ProjectTimelineAgent: {_init_error}")
    _project_timeline_agent_instance = None
    project_timeline_agent = None
    # Re-raise only if running as main module
    if __name__ == "__main__":
        raise


if __name__ == "__main__":
    if _project_timeline_agent_instance is not None:
        _project_timeline_agent_instance.run_with_error_handling()
    else:
        print("❌ Agent failed to initialize. Check logs for details.")
