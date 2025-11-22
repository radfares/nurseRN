"""
Nursing Research Agent - Specialized for Healthcare Improvement Projects
Focused on PICOT development, literature review, evidence-based practice

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
CRITICAL SECURITY FIX: Moved API keys to environment variables
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
WEEK 1 REFACTORING (2025-11-22): Added circuit breaker protection and resilience
  - Safe tool creation with graceful degradation
  - API status reporting and validation
  - Circuit breaker infrastructure for API calls
"""

import os
import sys
from datetime import datetime
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

# PHASE 1: Import centralized configuration
from agent_config import get_db_path

# PHASE 2: Use base_agent utilities
from base_agent import setup_agent_logging, run_agent_with_error_handling

# WEEK 1 REFACTORING: Import resilience infrastructure
# Add parent directory to path to import src modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.services.api_tools import (
    create_exa_tools_safe,
    create_serp_tools_safe,
    build_tools_list,
    get_api_status
)

# Setup logging using shared utility
logger = setup_agent_logging("Nursing Research Agent")

# WEEK 1 REFACTORING: Create tools with resilience
# Tools are created safely with fallback behavior if API keys missing
exa_tool = create_exa_tools_safe(required=False)
serp_tool = create_serp_tools_safe(required=False)

# Build tools list, filtering out None values
available_tools = build_tools_list(exa_tool, serp_tool)

# Log tool availability
if exa_tool:
    logger.info("✅ Exa search available")
else:
    logger.warning("⚠️  Exa search unavailable (EXA_API_KEY not set)")

if serp_tool:
    logger.info("✅ SerpAPI search available")
else:
    logger.warning("⚠️  SerpAPI search unavailable (SERP_API_KEY not set)")

if not available_tools:
    logger.error("❌ No search tools available! Agent will have limited functionality.")

# ************* Nursing Research Agent *************
nursing_research_agent = Agent(
    name="Nursing Research Agent",
    role="Healthcare improvement project research specialist",
    model=OpenAIChat(id="gpt-4o"),
    tools=available_tools,  # Use safely-created tools
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
    # WEEK 1 REFACTORING: Enhanced API status reporting
    api_status = get_api_status()

    print("\n📊 API Configuration Status:")
    print("-" * 60)

    # Check OpenAI (required)
    if api_status["openai"]["key_set"]:
        print("  ✅ OpenAI API - Configured (REQUIRED)")
    else:
        print("  ❌ OpenAI API - NOT configured (REQUIRED)")
        print("     Set OPENAI_API_KEY environment variable")

    # Check Exa (optional)
    if api_status["exa"]["key_set"]:
        print("  ✅ Exa API - Configured (literature search)")
    else:
        print("  ⚠️  Exa API - NOT configured (optional, limits search capability)")
        print("     Set EXA_API_KEY for recent article searches")

    # Check SERP (optional)
    if api_status["serp"]["key_set"]:
        print("  ✅ SerpAPI - Configured (web search)")
    else:
        print("  ⚠️  SerpAPI - NOT configured (optional, limits search capability)")
        print("     Set SERP_API_KEY for standards/guidelines search")

    print("-" * 60)

    # Warning if no search tools available
    if not available_tools:
        print("\n⚠️  WARNING: No search tools configured!")
        print("   Agent can still help with PICOT development and guidance,")
        print("   but cannot perform literature or web searches.")
        print("\n   To enable full functionality:")
        print('   export EXA_API_KEY="your-exa-key"')
        print('   export SERP_API_KEY="your-serp-key"')
        print()
    elif len(available_tools) < 2:
        print("\n⚠️  NOTE: Some search capabilities are limited.")
        print("   Consider setting all API keys for full functionality.\n")

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

