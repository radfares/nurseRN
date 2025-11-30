"""
Nursing Research Agent - Specialized for Healthcare Improvement Projects
Focused on PICOT development, literature review, evidence-based practice

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
CRITICAL SECURITY FIX: Moved API keys to environment variables
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
WEEK 1 REFACTORING (2025-11-22): Added circuit breaker protection and resilience
PHASE 2 COMPLETE (2025-11-23): Refactored to use BaseAgent inheritance
MULTI-TOOL UPDATE (2025-11-26): Added PubMed (PRIMARY), SerpAPI tools
    - ArXiv and Exa DISABLED (instructions alone cannot prevent tool usage)
    - Tool priority: PubMed > SerpAPI (ArXiv/Exa removed from tools list)
    - Only healthcare-appropriate tools are available to the agent
FREE API UPDATE (2025-11-26): Added 5 free healthcare research APIs
    - ClinicalTrials.gov, medRxiv, Semantic Scholar, CORE, DOAJ
    - All tools follow existing safe wrapper pattern with circuit breaker protection
"""

import os
import sys
from textwrap import dedent

# Module exports
__all__ = ['NursingResearchAgent', 'nursing_research_agent']

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

# Import centralized configuration
from agent_config import get_db_path

# Import BaseAgent for inheritance pattern
from .base_agent import BaseAgent

# Import resilience infrastructure
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.services.api_tools import (
    create_exa_tools_safe,
    create_serp_tools_safe,
    create_pubmed_tools_safe,
    create_arxiv_tools_safe,
    create_clinicaltrials_tools_safe,
    create_medrxiv_tools_safe,
    create_semantic_scholar_tools_safe,
    create_core_tools_safe,
    create_doaj_tools_safe,
    create_safety_tools_safe,
    build_tools_list,
    get_api_status
)


class NursingResearchAgent(BaseAgent):
    """
    Nursing Research Agent - Healthcare-focused search capability.

    ACTIVE Tools:
    1. PubMed - PRIMARY for all healthcare/nursing/medical research (peer-reviewed)
    2. ClinicalTrials.gov - Clinical trial database (public API)
    3. medRxiv - Medical preprints (free API)
    4. Semantic Scholar - AI-powered paper recommendations (free tier)
    5. CORE - Open-access research aggregator (free API)
    6. DOAJ - Directory of Open Access Journals (free API)
    7. SafetyTools - OpenFDA device recalls and drug adverse events (public API)
    8. SerpAPI - Google search for official standards/guidelines (CDC, WHO, Joint Commission)

    DISABLED Tools (not appropriate for healthcare research):
    - ArXiv - DISABLED (tech/AI preprints, not peer-reviewed clinical studies)
    - Exa - DISABLED (general web search, not healthcare-specific)

    Note: ArXiv and Exa are intentionally disabled to prevent the agent from using
    non-healthcare sources for clinical research. To re-enable for a tech/AI agent,
    see the commented code in _create_tools().
    """

    def __init__(self):
        tools = self._create_tools()
        super().__init__(
            agent_name="Nursing Research Agent",
            agent_key="nursing_research",
            tools=tools
        )

    def _create_tools(self) -> list:
        """
        Create search tools with safe fallback.
        
        TOOL USAGE POLICY (IMPORTANT):
        - PubMed: PRIMARY tool for ALL healthcare/nursing/medical research (most reliable, peer-reviewed)
        - ClinicalTrials.gov: For finding clinical trials and study protocols
        - medRxiv: For latest medical preprints (before peer review)
        - Semantic Scholar: For AI-powered paper discovery and connections
        - CORE: For open-access full-text articles
        - DOAJ: For high-quality open-access journals
        - SerpAPI: Google search for official standards/guidelines (Joint Commission, CDC, WHO websites)
        - ArXiv: RESTRICTED - Tech/AI/ML papers only, NOT for healthcare clinical research
        - Exa: RESTRICTED - Tech/AI only, NOT for healthcare research
        
        ⚠️ CRITICAL: ArXiv and Exa are NOT reliable for healthcare research!
           - ArXiv is primarily for physics, math, CS, AI/ML preprints - NOT peer-reviewed clinical studies
           - Exa is a general web/article search - NOT a healthcare-specific database
           Do NOT use ArXiv or Exa for clinical studies, nursing research, or medical evidence.
           Only use them if explicitly asked OR for tech/AI/non-healthcare science topics.
        """
        # Safe tool creation (Week 1 refactoring pattern)
        
        # PRIMARY: PubMed for healthcare research (most reliable for clinical evidence)
        pubmed_tool = create_pubmed_tools_safe(required=False)
        
        # Healthcare research tools (free APIs)
        clinicaltrials_tool = create_clinicaltrials_tools_safe(required=False)
        medrxiv_tool = create_medrxiv_tools_safe(required=False)
        semantic_scholar_tool = create_semantic_scholar_tools_safe(required=False)
        core_tool = create_core_tools_safe(required=False)
        doaj_tool = create_doaj_tools_safe(required=False)

        # Safety monitoring tools (OpenFDA - free public API)
        safety_tool = create_safety_tools_safe(required=False)

        # SECONDARY: SerpAPI (Google) for official standards/guidelines searches
        # Good for: Joint Commission, CDC, WHO, CMS official websites
        serp_tool = create_serp_tools_safe(required=False)
        
        # =====================================================================
        # DISABLED TOOLS - Not appropriate for healthcare research
        # These tools are commented out because:
        # 1. Instructions alone cannot prevent the agent from using available tools
        # 2. ArXiv contains tech/AI preprints, NOT peer-reviewed clinical studies
        # 3. Exa is a general web search, NOT a healthcare-specific database
        #
        # TO RE-ENABLE (for a tech/AI research agent):
        # Uncomment the following lines and add to build_tools_list()
        # ---------------------------------------------------------------------
        # arxiv_tool = create_arxiv_tools_safe(required=False)  # Tech/AI papers
        # exa_tool = create_exa_tools_safe(required=False)      # General web search
        # =====================================================================
        arxiv_tool = None  # DISABLED - not for healthcare
        exa_tool = None    # DISABLED - not for healthcare

        # Build tools list - ONLY healthcare-appropriate tools
        # Note: ArXiv and Exa intentionally excluded to prevent misuse
        # Tool priority: PubMed > ClinicalTrials.gov > medRxiv > Semantic Scholar > CORE > DOAJ > SafetyTools > SerpAPI
        tools = build_tools_list(
            pubmed_tool,
            clinicaltrials_tool,
            medrxiv_tool,
            semantic_scholar_tool,
            core_tool,
            doaj_tool,
            safety_tool,
            serp_tool
        )

        # Store tool availability for later reference (used by show_usage_examples)
        self._tool_status = {
            'pubmed': pubmed_tool is not None,
            'clinicaltrials': clinicaltrials_tool is not None,
            'medrxiv': medrxiv_tool is not None,
            'semantic_scholar': semantic_scholar_tool is not None,
            'core': core_tool is not None,
            'doaj': doaj_tool is not None,
            'safety': safety_tool is not None,
            'serp': serp_tool is not None,
            'arxiv': arxiv_tool is not None,  # Will be False (disabled)
            'exa': exa_tool is not None,      # Will be False (disabled)
        }

        # Log tool availability (using print since self.logger not available yet)
        print("\n📚 Search Tools Status:")
        print("-" * 50)
        
        if pubmed_tool:
            print("✅ PubMed - Available (PRIMARY for healthcare research)")
        else:
            print("⚠️ PubMed - Unavailable (tool creation failed)")
            
        if clinicaltrials_tool:
            print("✅ ClinicalTrials.gov - Available (clinical trial database)")
        else:
            print("⚠️ ClinicalTrials.gov - Unavailable (tool creation failed)")
            
        if medrxiv_tool:
            print("✅ medRxiv - Available (medical preprints)")
        else:
            print("⚠️ medRxiv - Unavailable (tool creation failed)")
            
        if semantic_scholar_tool:
            print("✅ Semantic Scholar - Available (AI-powered paper discovery)")
        else:
            print("⚠️ Semantic Scholar - Unavailable (tool creation failed)")
            
        if core_tool:
            print("✅ CORE - Available (open-access research)")
        else:
            print("⚠️ CORE - Unavailable (tool creation failed)")
            
        if doaj_tool:
            print("✅ DOAJ - Available (open-access journals)")
        else:
            print("⚠️ DOAJ - Unavailable (tool creation failed)")

        if safety_tool:
            print("✅ SafetyTools - Available (device recalls & drug events)")
        else:
            print("⚠️ SafetyTools - Unavailable (tool creation failed)")

        if serp_tool:
            print("✅ SerpAPI - Available (Google for standards/guidelines)")
        else:
            print("⚠️ SerpAPI - Unavailable (SERP_API_KEY not set)")
        
        # ArXiv and Exa are intentionally disabled for this healthcare agent
        print("🚫 ArXiv - DISABLED (not appropriate for healthcare research)")
        print("🚫 Exa - DISABLED (not appropriate for healthcare research)")
            
        print("-" * 50)

        if not tools:
            print("❌ No search tools available! Agent will have limited functionality.")
        elif not pubmed_tool:
            print("⚠️ WARNING: PubMed unavailable - healthcare research capability limited!")

        return tools

    def _create_agent(self) -> Agent:
        """Create and configure the Nursing Research Agent."""
        return Agent(
            name="Nursing Research Agent",
            role="Healthcare improvement project research specialist",
            model=OpenAIChat(id="gpt-4o"),
            tools=self.tools,
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

                SEARCH TOOL POLICY (Priority Order):
                
                PRIMARY TOOL - PubMed (USE FIRST for healthcare):
                - Use PubMed for ALL healthcare, nursing, and medical research queries
                - Most reliable source for peer-reviewed clinical studies
                - Always include PMIDs in citations
                - This is the GOLD STANDARD for evidence-based nursing research
                
                SECONDARY TOOLS - Healthcare Research Databases:
                - ClinicalTrials.gov: Use for finding clinical trials, study protocols, and trial data
                - medRxiv: Use for latest medical preprints (before peer review) - cutting-edge research
                - Semantic Scholar: Use for AI-powered paper discovery, finding connections between papers
                - CORE: Use for open-access full-text articles from repositories worldwide
                - DOAJ: Use for high-quality open-access journal articles

                SAFETY MONITORING TOOL - SafetyTools (OpenFDA):
                - Use SafetyTools when user asks about medical devices (catheters, pumps, monitors, IV equipment)
                - Use SafetyTools when user asks about medications/drugs (check for adverse events)
                - Use SafetyTools to check for FDA recalls on any medical equipment being used in projects
                - Use SafetyTools when evaluating safety of interventions involving devices or medications
                - Provides real-time FDA device recalls (Class I = most serious)
                - Provides drug adverse event reports from FDA database
                - IMPORTANT: Always check SafetyTools when a project involves medical devices or medications

                TERTIARY TOOL - SerpAPI/Google (for standards):
                - Use SerpAPI for official standards and guidelines
                - Joint Commission, CDC, WHO, CMS official websites
                - Regulatory requirements and accreditation criteria
                - Current policies and organizational recommendations
                
                NOTE: ArXiv and Exa have been disabled as they are not appropriate for healthcare research.

                RESPONSE FORMAT:
                - Use clear headings and bullet points
                - Summarize key takeaways
                - Provide actionable recommendations
                - Include relevant citations with PMIDs when available
                - Highlight best practices and guidelines
                - Always specify which database/source was used
                """),
            add_history_to_context=True,
            add_datetime_to_context=True,
            enable_agentic_memory=True,
            markdown=True,
            db=SqliteDb(db_file=get_db_path("nursing_research")),
        )

    def show_usage_examples(self) -> None:
        """Display usage examples for the Nursing Research Agent."""
        # Enhanced API status reporting
        api_status = get_api_status()
        
        # Use stored tool status from _create_tools() for accurate reporting
        tool_status = getattr(self, '_tool_status', {})

        print("\n📊 API Configuration Status:")
        print("-" * 60)

        # Check OpenAI (required)
        if api_status["openai"]["key_set"]:
            print("  ✅ OpenAI API - Configured (REQUIRED)")
        else:
            print("  ❌ OpenAI API - NOT configured (REQUIRED)")
            print("     Set OPENAI_API_KEY environment variable")

        # Check PubMed (primary for healthcare) - check actual tool status
        if tool_status.get('pubmed', False):
            print("  ✅ PubMed - Available (PRIMARY for healthcare research)")
        else:
            print("  ⚠️ PubMed - Unavailable (package not installed?)")
            print("     Run: pip install biopython")

        # Check ClinicalTrials.gov
        if tool_status.get('clinicaltrials', False):
            print("  ✅ ClinicalTrials.gov - Available (clinical trial database)")
        else:
            print("  ⚠️ ClinicalTrials.gov - Unavailable (tool creation failed)")

        # Check medRxiv
        if tool_status.get('medrxiv', False):
            print("  ✅ medRxiv - Available (medical preprints)")
        else:
            print("  ⚠️ medRxiv - Unavailable (tool creation failed)")

        # Check Semantic Scholar
        if tool_status.get('semantic_scholar', False):
            print("  ✅ Semantic Scholar - Available (AI-powered paper discovery)")
        elif api_status.get("semantic_scholar", {}).get("key_set"):
            print("  ⚠️ Semantic Scholar - Key set but tool unavailable")
        else:
            print("  ⚠️ Semantic Scholar - Available (API key optional)")

        # Check CORE
        if tool_status.get('core', False):
            print("  ✅ CORE - Available (open-access research)")
        elif api_status.get("core", {}).get("key_set"):
            print("  ⚠️ CORE - Key set but tool unavailable")
        else:
            print("  ⚠️ CORE - Available (API key optional)")

        # Check DOAJ
        if tool_status.get('doaj', False):
            print("  ✅ DOAJ - Available (open-access journals)")
        else:
            print("  ⚠️ DOAJ - Unavailable (tool creation failed)")

        # Check SafetyTools (OpenFDA)
        if tool_status.get('safety', False):
            print("  ✅ SafetyTools - Available (FDA device recalls & drug events)")
        else:
            print("  ⚠️ SafetyTools - Unavailable (tool creation failed)")

        # Check SerpAPI (secondary - standards/guidelines) - check actual tool status
        if tool_status.get('serp', False):
            print("  ✅ SerpAPI - Available (Google for standards/guidelines)")
        elif api_status["serp"]["key_set"]:
            print("  ⚠️ SerpAPI - Key set but tool unavailable")
            print("     Run: pip install google-search-results")
        else:
            print("  ⚠️ SerpAPI - NOT configured (optional)")
            print("     Set SERP_API_KEY for standards/guidelines search")

        # ArXiv and Exa are intentionally DISABLED for healthcare research
        print("  🚫 ArXiv - DISABLED (not appropriate for healthcare)")
        print("  🚫 Exa - DISABLED (not appropriate for healthcare)")

        print("-" * 60)
        print(f"  📦 Total tools loaded: {len(self.tools)}")

        # Tool usage policy reminder
        print("\n📋 SEARCH TOOL POLICY (Healthcare Only):")
        print("  🔬 PubMed            → Healthcare, nursing, medical research (PRIMARY)")
        print("  🏥 ClinicalTrials.gov → Clinical trials and study protocols")
        print("  📄 medRxiv            → Medical preprints (latest research)")
        print("  🤖 Semantic Scholar   → AI-powered paper discovery")
        print("  📚 CORE               → Open-access full-text articles")
        print("  📖 DOAJ               → High-quality open-access journals")
        print("  ⚠️  SafetyTools        → FDA device recalls & drug adverse events")
        print("  🏛️ SerpAPI            → Official standards, guidelines, regulations (Google)")
        print("  🚫 ArXiv              → DISABLED (not for healthcare)")
        print("  🚫 Exa                → DISABLED (not for healthcare)")
        print()

        # Warning if no search tools available
        if not self.tools:
            print("\n⚠️ WARNING: No search tools configured!")
            print("   Agent can still help with PICOT development and guidance,")
            print("   but cannot perform literature or web searches.")
            print()

        print("🏥 Nursing Research Agent Ready!")
        print("\nSpecialized for healthcare improvement projects:")
        print("  ✓ PICOT question development")
        print("  ✓ Literature searches via PubMed (peer-reviewed clinical studies)")
        print("  ✓ Clinical trial searches via ClinicalTrials.gov")
        print("  ✓ Latest medical preprints via medRxiv")
        print("  ✓ AI-powered paper discovery via Semantic Scholar")
        print("  ✓ Open-access research via CORE and DOAJ")
        print("  ✓ FDA device recalls and drug safety monitoring via SafetyTools")
        print("  ✓ Evidence-based practice guidelines")
        print("  ✓ Healthcare standards via Google (Joint Commission, CDC, WHO)")
        print("  ✓ Quality improvement frameworks")
        print("\nExample usage:")
        print("-" * 60)

        print("\n1. PICOT Development:")
        print('   response = nursing_research_agent.run("""')
        print('   Help me develop a PICOT question for reducing patient falls')
        print('   in a medical-surgical unit""")')

        print("\n2. Literature Search (uses PubMed - healthcare):")
        print('   response = nursing_research_agent.run("""')
        print('   Find 3 recent research articles about catheter-associated')
        print('   urinary tract infection prevention""")')

        print("\n3. Device Safety Check (uses SafetyTools/OpenFDA):")
        print('   response = nursing_research_agent.run("""')
        print('   Check for any FDA recalls on urinary catheters""")')

        print("\n4. Standards Research (uses SerpAPI/Google):")
        print('   response = nursing_research_agent.run("""')
        print('   What are the Joint Commission requirements for medication')
        print('   reconciliation?""")')

        print("\n5. With Streaming (real-time responses):")
        print('   nursing_research_agent.print_response("""')
        print('   Find 3 recent studies on fall prevention""", stream=True)')

        print("\n" + "-" * 60)
        print("\n💡 TIP: Use stream=True for real-time response generation")
        print("💡 TIP: SafetyTools automatically checks FDA recalls when you mention devices or drugs")


# Create global instance for backward compatibility
# Wrapped in try/except for graceful degradation if initialization fails
try:
    _nursing_research_agent_instance = NursingResearchAgent()
    nursing_research_agent = _nursing_research_agent_instance.agent
except Exception as _init_error:
    import logging
    logging.error(f"Failed to initialize NursingResearchAgent: {_init_error}")
    _nursing_research_agent_instance = None
    nursing_research_agent = None
    # Re-raise only if running as main module
    if __name__ == "__main__":
        raise


if __name__ == "__main__":
    if _nursing_research_agent_instance is not None:
        _nursing_research_agent_instance.run_with_error_handling()
    else:
        print("❌ Agent failed to initialize. Check logs for details.")
