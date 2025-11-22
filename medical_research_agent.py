"""
Medical Research Agent - PubMed Database Access
Specialized for searching biomedical and nursing literature
Perfect for finding peer-reviewed clinical studies

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
PHASE 3 UPDATE (2025-11-20): Enhanced PubMed configuration for full metadata
WEEK 1 REFACTORING (2025-11-22): Added circuit breaker protection and resilience
  - Safe tool creation with graceful degradation
  - Enhanced error handling and logging
"""

import os
import sys
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

# PHASE 1: Import centralized configuration
from agent_config import get_db_path

# PHASE 2: Use base_agent utilities
from base_agent import setup_agent_logging, run_agent_with_error_handling

# WEEK 1 REFACTORING: Import resilience infrastructure
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.services.api_tools import (
    create_pubmed_tools_safe,
    build_tools_list,
    get_api_status
)

# Setup logging using shared utility
logger = setup_agent_logging("Medical Research Agent")

# WEEK 1 REFACTORING: Create tools with resilience
# PubMed doesn't require API keys (just email), so it's generally available
pubmed_tool = create_pubmed_tools_safe(required=False)

# Build tools list, filtering out None values
available_tools = build_tools_list(pubmed_tool)

# Log tool availability
if pubmed_tool:
    logger.info("✅ PubMed search available")
else:
    logger.warning("⚠️  PubMed search unavailable (tool creation failed)")

if not available_tools:
    logger.error("❌ No search tools available! Agent will have limited functionality.")

# ************* Medical Research Agent (PubMed) *************
medical_research_agent = Agent(
    name="Medical Research Agent",
    role="Search PubMed for biomedical and nursing research",
    model=OpenAIChat(id="gpt-4o"),
    tools=available_tools,  # Use safely-created tools
    description=dedent("""\
        You are a Medical Literature Search Specialist with access to PubMed,
        the premier database for biomedical and healthcare research. You help
        find peer-reviewed studies, clinical trials, systematic reviews, and
        nursing research articles.
        """),
    instructions=dedent("""\
        EXPERTISE: PubMed Medical Literature Search
        
        SEARCH STRATEGY:
        1. Use specific medical terminology and MeSH terms when possible
        2. Focus on peer-reviewed, evidence-based research
        3. Prioritize recent publications (last 5-10 years) unless specified
        4. Look for systematic reviews and meta-analyses when available
        5. Include clinical trials and observational studies
        
        SEARCH TYPES:
        - Clinical studies and trials
        - Systematic reviews and meta-analyses
        - Nursing research and quality improvement
        - Evidence-based practice guidelines
        - Case studies and cohort studies
        
        RESPONSE FORMAT:
        For each article found, provide:
        - Title and authors (first author provided)
        - Publication year and journal
        - PubMed ID (PMID) and PubMed URL
        - DOI link (for citations)
        - Full-text access link (when available via PMC or DOI)
        - Keywords and MeSH terms (Medical Subject Headings)
        - Publication type (research article, review, clinical trial, etc.)
        - Full structured abstract with sections:
          * OBJECTIVE/BACKGROUND
          * METHODS
          * RESULTS
          * CONCLUSIONS
        - Key findings relevant to the query
        - Study design and methodology
        - Clinical implications
        
        NOTE: With results_expanded=True, you have access to comprehensive metadata:
        - Direct links for immediate access and citation
        - MeSH terms for deeper literature searches
        - Keywords for finding related research
        - Complete structured abstracts (not truncated)
        - Publication types for filtering study designs
        
        QUALITY INDICATORS:
        - Peer-reviewed journals
        - High-impact publications
        - Large sample sizes
        - Recent research (prefer last 5 years)
        - Relevant to clinical practice
        
        EXAMPLES OF GOOD SEARCHES:
        - "Fall prevention interventions elderly hospitalized patients"
        - "Catheter-associated urinary tract infection prevention"
        - "Pressure ulcer prevention protocols nursing homes"
        - "Medication reconciliation effectiveness"
        - "Patient safety culture healthcare"
        """),
    add_history_to_context=True,
    add_datetime_to_context=True,
    markdown=True,
    # PHASE 1: Database path using centralized config
    # OLD (commented for reference): db=SqliteDb(db_file="tmp/medical_research_agent.db")
    db=SqliteDb(db_file=get_db_path("medical_research")),
)

logger.info(f"Medical Research Agent initialized: {get_db_path('medical_research')}")

# ************* Usage Examples *************
def show_usage_examples():
    """Display usage examples for the Medical Research Agent."""
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

    # Check PubMed (optional email)
    if api_status["pubmed"]["email_set"]:
        print("  ✅ PubMed - Email configured (recommended)")
    else:
        print("  ⚠️  PubMed - Using default email (set PUBMED_EMAIL for better tracking)")

    print("-" * 60)

    # Warning if no search tools available
    if not available_tools:
        print("\n⚠️  WARNING: PubMed tool not available!")
        print("   This is unusual - check logs for errors.")
        print()

    print("\n🏥 Medical Research Agent (PubMed) Ready!")
    print("\nSpecialized for biomedical and nursing literature")
    print("✨ Enhanced with full metadata (DOI, URLs, MeSH terms, full abstracts)")
    print("\nExample queries:")
    print("-" * 60)

    print("\n1. Find clinical studies:")
    print('   response = medical_research_agent.run("""')
    print('   Find recent studies on fall prevention in elderly')
    print('   hospitalized patients""")')

    print("\n2. Search for specific conditions:")
    print('   response = medical_research_agent.run("""')
    print('   Find evidence-based interventions for catheter-associated')
    print('   urinary tract infections""")')

    print("\n3. Literature review:")
    print('   response = medical_research_agent.run("""')
    print('   Find 3 recent peer-reviewed articles about pressure')
    print('   ulcer prevention in critical care""")')

    print("\n4. With Streaming:")
    print('   medical_research_agent.print_response("""')
    print('   Search for CAUTI prevention studies""", stream=True)')

    print("\n" + "-" * 60)
    print("\n💡 TIP: PubMed has millions of biomedical articles!")
    print("Be specific about your topic for best results.")
    print("Use stream=True for real-time response generation.")
    print("\n📚 Full metadata includes: DOI, URLs, MeSH terms, keywords, structured abstracts")


if __name__ == "__main__":
    # PHASE 2: Use shared error handling utility
    run_agent_with_error_handling(
        "Medical Research Agent",
        logger,
        show_usage_examples
    )

