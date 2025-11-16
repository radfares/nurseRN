"""
Nursing Research Agent - Specialized for Healthcare Improvement Projects
Focused on PICOT development, literature review, evidence-based practice

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
CRITICAL SECURITY FIX: Moved API keys to environment variables
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
"""

import os
from datetime import datetime
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from agno.tools.serpapi import SerpApiTools

# PHASE 1: Import centralized configuration
from agent_config import get_db_path

# PHASE 2: Use base_agent utilities
from base_agent import setup_agent_logging, run_agent_with_error_handling

# Setup logging using shared utility
logger = setup_agent_logging("Nursing Research Agent")

# PHASE 1 SECURITY FIX: Get API keys from environment variables
# Set these in your environment before running:
#   export EXA_API_KEY="your-exa-key"
#   export SERP_API_KEY="your-serp-api-key"
# OR add to .env file (and add .env to .gitignore)
EXA_API_KEY = os.getenv("EXA_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Validate API keys are set
if not EXA_API_KEY:
    logger.warning("EXA_API_KEY environment variable not set. Exa search will fail.")
if not SERP_API_KEY:
    logger.warning("SERP_API_KEY environment variable not set. SerpAPI search will fail.")

# ************* Nursing Research Agent *************
nursing_research_agent = Agent(
    name="Nursing Research Agent",
    role="Healthcare improvement project research specialist",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        # PHASE 1 SECURITY FIX: Exa for recent healthcare articles and research
        # API key now loaded from environment variable (line 25)
        ExaTools(
            api_key=EXA_API_KEY,  # From environment variable
            start_published_date="2020-01-01",  # Last 5 years of research
            type="neural",  # Better for academic/clinical content
        ),
        # PHASE 1 SECURITY FIX: SerpAPI for general healthcare standards and guidelines
        # API key now loaded from environment variable (line 26)
        SerpApiTools(
            api_key=SERP_API_KEY  # From environment variable
        ),
    ],
    description=dedent("""\
        You are a specialized Nursing Research Assistant focused on healthcare improvement projects.
        You help with PICOT development, literature searches, evidence-based practice research,
        and healthcare standards (Joint Commission, National Patient Safety Goals, etc.).
        You understand nursing-sensitive indicators, quality improvement, and clinical research.
        """),
    instructions=dedent("""\
        EXPERTISE AREAS:
        1. PICOT Question Development
           - Help formulate Population, Intervention, Comparison, Outcome, Time questions
           - Ensure questions are specific, measurable, and clinically relevant
        
        2. Literature Search & Analysis
           - Search for peer-reviewed nursing and healthcare research
           - Focus on evidence-based practice and quality improvement
           - Identify research articles published in last 5 years
           - Summarize key findings, methodology, and recommendations
        
        3. Healthcare Standards & Guidelines
           - Joint Commission accreditation criteria
           - National Patient Safety Goals
           - Core Measures and nursing-sensitive indicators
           - Infection control standards
           - Best practice guidelines
        
        4. Quality Improvement Framework
           - Problem identification and root cause analysis
           - Intervention planning and implementation steps
           - Data collection methods (pre/post intervention)
           - Success metrics and evaluation criteria
        
        5. Stakeholder Identification
           - Identify relevant clinical experts (infection control, wound care, etc.)
           - Suggest interdisciplinary team members
           - Recommend departmental collaborations
        
        SEARCH STRATEGY:
        - For recent research: Use Exa (academic articles, clinical studies)
        - For standards/guidelines: Use SerpAPI (official organizations)
        - Always prioritize peer-reviewed, evidence-based sources
        - Cite sources with links and publication dates
        
        RESPONSE FORMAT:
        - Use clear headings and bullet points
        - Summarize key takeaways
        - Provide actionable recommendations
        - Include relevant citations
        - Highlight best practices and guidelines
        """),
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    markdown=True,
    # PHASE 1: Database path using centralized config
    # OLD (commented for reference): db=SqliteDb(db_file="tmp/nursing_research_agent.db")
    db=SqliteDb(db_file=get_db_path("nursing_research")),
)

logger.info(f"Nursing Research Agent initialized: {get_db_path('nursing_research')}")

# ************* Usage Examples *************
def show_usage_examples():
    """Display usage examples for the Nursing Research Agent."""
    # PHASE 1 SECURITY: Validate API keys are set
    if not EXA_API_KEY or not SERP_API_KEY:
        print("\n⚠️  WARNING: API keys not configured!")
        print("\nRequired environment variables:")
        if not EXA_API_KEY:
            print("  ❌ EXA_API_KEY - Not set")
        else:
            print("  ✓ EXA_API_KEY - Set")
        if not SERP_API_KEY:
            print("  ❌ SERP_API_KEY - Not set")
        else:
            print("  ✓ SERP_API_KEY - Set")
        print("\nTo set API keys:")
        print('  export EXA_API_KEY="your-exa-key"')
        print('  export SERP_API_KEY="your-serp-api-key"')
        print("\nThe agent will run but searches will fail without valid API keys.\n")
        logger.error("API keys not configured. Agent functionality will be limited.")

    print("🏥 Nursing Research Agent Ready!")
    print("\nSpecialized for healthcare improvement projects:")
    print("  ✓ PICOT question development")
    print("  ✓ Literature searches (nursing research)")
    print("  ✓ Evidence-based practice guidelines")
    print("  ✓ Healthcare standards (Joint Commission, Patient Safety)")
    print("  ✓ Quality improvement frameworks")
    print("\nExample usage:")
    print("-" * 60)

    print("\n1. PICOT Development:")
    print('   response = nursing_research_agent.run("""')
    print('   Help me develop a PICOT question for reducing patient falls')
    print('   in a medical-surgical unit""")')

    print("\n2. Literature Search:")
    print('   response = nursing_research_agent.run("""')
    print('   Find 3 recent research articles about catheter-associated')
    print('   urinary tract infection prevention""")')

    print("\n3. Standards Research:")
    print('   response = nursing_research_agent.run("""')
    print('   What are the Joint Commission requirements for medication')
    print('   reconciliation?""")')

    print("\n4. With Streaming (real-time responses):")
    print('   nursing_research_agent.print_response("""')
    print('   Find 3 recent studies on fall prevention""", stream=True)')

    print("\n" + "-" * 60)
    print("\n💡 TIP: Use stream=True for real-time response generation")


if __name__ == "__main__":
    # PHASE 2: Use shared error handling utility
    run_agent_with_error_handling(
        "Nursing Research Agent",
        logger,
        show_usage_examples
    )

