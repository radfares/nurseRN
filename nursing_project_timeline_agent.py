"""
Nursing Project Timeline Assistant
Helps track project milestones and provides month-specific guidance

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
"""

import logging
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

# PHASE 1: Import centralized configuration
from agent_config import get_db_path

# PHASE 1: Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ************* Project Timeline Agent *************
project_timeline_agent = Agent(
    name="Project Timeline Assistant",
    role="Guide nursing residents through improvement project milestones",
    model=OpenAIChat(id="gpt-4o-mini"),  # Cheaper for timeline/guidance
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
    # PHASE 1: Database path using centralized config
    # OLD (commented for reference): db=SqliteDb(db_file="tmp/project_timeline_agent.db")
    db=SqliteDb(db_file=get_db_path("project_timeline")),
)

logger.info(f"Project Timeline Agent initialized: {get_db_path('project_timeline')}")

# ************* Usage Examples *************
if __name__ == "__main__":
    # PHASE 1: Add error handling for agent execution
    try:
        logger.info("Starting Project Timeline Agent")

        print("📅 Project Timeline Assistant Ready!")
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

        print("\n" + "-" * 60)

        logger.info("Project Timeline Agent ready")

    except KeyboardInterrupt:
        logger.info("Agent interrupted by user")
        print("\n\nInterrupted by user. Goodbye!")

    except Exception as e:
        logger.error(f"Agent execution failed: {type(e).__name__}: {str(e)}", exc_info=True)
        print(f"\n❌ Error: An unexpected error occurred.")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nPlease check the logs for details or contact support.")
        raise  # Re-raise to preserve stack trace for debugging

