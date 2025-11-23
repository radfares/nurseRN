"""
Medical Research Agent - PubMed Database Access
Specialized for searching biomedical and nursing literature
Perfect for finding peer-reviewed clinical studies

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
PHASE 3 UPDATE (2025-11-20): Enhanced PubMed configuration for full metadata
WEEK 1 REFACTORING (2025-11-22): Added circuit breaker protection and resilience
PHASE 2 COMPLETE (2025-11-23): Refactored to use BaseAgent inheritance
"""

import os
import sys
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

# Import centralized configuration
from agent_config import get_db_path

# Import BaseAgent for inheritance pattern
from base_agent import BaseAgent

# Import resilience infrastructure
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.services.api_tools import (
    create_pubmed_tools_safe,
    build_tools_list,
    get_api_status
)


class MedicalResearchAgent(BaseAgent):
    """Medical Research Agent with PubMed database access."""

    def __init__(self):
        tools = self._create_tools()
        super().__init__(
            agent_name="Medical Research Agent",
            agent_key="medical_research",
            tools=tools
        )

    def _create_tools(self) -> list:
        """Create PubMed tools with safe fallback."""
        # PubMed doesn't require API keys (just email), so it's generally available
        pubmed_tool = create_pubmed_tools_safe(required=False)

        # Build tools list, filtering out None values
        tools = build_tools_list(pubmed_tool)

        # Log tool availability (using print since self.logger not available yet)
        if pubmed_tool:
            print("✅ PubMed search available")
        else:
            print("⚠️ PubMed search unavailable (tool creation failed)")

        if not tools:
            print("❌ No search tools available! Agent will have limited functionality.")

        return tools

    def _create_agent(self) -> Agent:
        """Create and configure the Medical Research Agent."""
        return Agent(
            name="Medical Research Agent",
            role="Search PubMed for biomedical and nursing research",
            model=OpenAIChat(id="gpt-4o"),
            tools=self.tools,
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
            db=SqliteDb(db_file=get_db_path("medical_research")),
        )

    def show_usage_examples(self):
        """Display usage examples for the Medical Research Agent."""
        # Enhanced API status reporting
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
            print("  ⚠️ PubMed - Using default email (set PUBMED_EMAIL for better tracking)")

        print("-" * 60)

        # Warning if no search tools available
        if not self.tools:
            print("\n⚠️ WARNING: PubMed tool not available!")
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


# Create global instance for backward compatibility
_medical_research_agent_instance = MedicalResearchAgent()
medical_research_agent = _medical_research_agent_instance.agent


if __name__ == "__main__":
    _medical_research_agent_instance.run_with_error_handling()
