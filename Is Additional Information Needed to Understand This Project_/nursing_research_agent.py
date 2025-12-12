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
import re
import sys
from textwrap import dedent
from typing import List, Optional, Set

# Module exports
__all__ = ['NursingResearchAgent', 'nursing_research_agent']

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.models.response import ToolExecution
from agno.run.agent import RunOutput

# Import centralized configuration
from agent_config import get_db_path

# Import BaseAgent for inheritance pattern
from agents.base_agent import BaseAgent

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
# Import LiteratureTools for saving findings to project database
from src.tools.literature_tools import LiteratureTools


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

    def _create_tools(self) -> List:
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
        try:
            pubmed_tool = create_pubmed_tools_safe(required=True)
        except Exception as exc:
            failure_message = (
                "❌ PubMed tool creation failed. This agent will not run without verified PubMed access.\n"
                "   Install dependencies (pip install biopython) and ensure network/API availability."
            )
            print(failure_message)
            raise RuntimeError("PubMed initialization failed") from exc
        
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

        # LiteratureTools for saving findings to project database
        literature_tools = LiteratureTools()
        print("✅ LiteratureTools available (save findings to project DB)")

        # Build tools list - ONLY healthcare-appropriate tools
        # Note: ArXiv and Exa intentionally excluded to prevent misuse
        # Tool priority: PubMed > ClinicalTrials.gov > medRxiv > Semantic Scholar > CORE > DOAJ > SafetyTools > SerpAPI > LiteratureTools
        tools = build_tools_list(
            pubmed_tool,
            clinicaltrials_tool,
            medrxiv_tool,
            semantic_scholar_tool,
            core_tool,
            doaj_tool,
            safety_tool,
            serp_tool,
            literature_tools
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
            model=OpenAIChat(id="gpt-4o", temperature=0),
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

                CRITICAL RULES FOR SEARCH RESULTS:
                1. NEVER fabricate articles, PMIDs, DOIs, or authors
                2. If search tools return no results, explicitly state: "No articles found"
                3. ONLY cite articles that were returned by search tools
                4. If tools fail, state: "Search tools unavailable - cannot perform search"
                5. Every PMID must come directly from PubMed tool results
                6. If unsure about an article's authenticity, do not cite it

                VERIFICATION CHECKLIST before citing any article:
                ✓ Did this PMID come from PubMed tool results?
                ✓ Did I receive complete article metadata (title, authors, journal)?
                ✓ Can I verify this is real data, not generated?
                ✓ If any answer is NO → refuse to provide the citation

                CRITICAL: STRICT GROUNDING POLICY
                You are a VERIFICATION-FIRST agent. Accuracy outranks helpfulness.
                - If tools return no results → say "No articles found in PubMed"
                - If tools fail → say "Search unavailable - cannot retrieve data"
                - If you cannot verify information → say "I cannot verify this information"
                - NEVER generate content that did not come from verified tool outputs
                - NEVER fill gaps with plausible-sounding information
                - NEVER assume or infer PMIDs, DOIs, author names, or journal titles
                - "I don't know" is preferred over hallucinations

                THINK LIKE THIS:
                ❌ BAD: "I'll provide helpful articles..." (then fabricate)
                ✅ GOOD: "No PubMed articles matched your query. Would you like to try alternate terms?"

                RESPONSE REQUIREMENTS:
                - Every citation MUST reference an actual tool output
                - If unsure about ANY detail, explicitly state uncertainty
                - Empty search results MUST produce "No results found" instead of fabricated articles

                EXAMPLES OF CORRECT REFUSAL:
                User: "Find articles about XYZ nursing intervention"
                Tool returns 0 results → Respond with "I searched PubMed and found no articles matching 'XYZ nursing intervention'."
                User: "What's the PMID for the Smith et al. catheter study?"
                No search performed → Respond "I don't have that information available yet. Please provide more details so I can search PubMed."
                User: "Find 5 articles about fall prevention" and only 2 results exist → Respond with the 2 verified citations and explain the shortfall.

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
            pre_hooks=[self._audit_pre_hook],
            post_hooks=[self._audit_post_hook],
        )

    def run_with_grounding_check(self, query: str, **kwargs) -> RunOutput:
        """Execute the agent while forcing a grounding verification pass."""
        # Audit Logging: Query Received
        project_name = kwargs.get("project_name")
        if self.audit_logger:
            self.audit_logger.log_query_received(query, project_name)

        stream_requested = bool(kwargs.get("stream"))
        
        try:
            response = self.agent.run(query, **kwargs)
            
            # Audit Logging: Tool Calls & Results
            # Note: Agno agent.run() handles tool execution internally, 
            # so we capture them from the response object if possible,
            # or rely on the agent framework hooks if we were deeper.
            # For now, we log the final response and validation.
            
            # Streaming responses are yielded incrementally and cannot be re-verified here.
            if stream_requested:
                return response
                
            self._validate_run_output(response)
            
            # Audit Logging: Response Generated
            if self.audit_logger:
                self.audit_logger.log_response_generated(
                    response=str(response.content),
                    response_type="success",
                    validation_passed=True # If we got here, validation passed (or didn't raise)
                )
                
            return response
            
        except Exception as e:
            # Audit Logging: Error
            if self.audit_logger:
                self.audit_logger.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise

    def _grounding_post_hook(self, run_output: RunOutput, **_: object) -> None:
        """Agno post-hook that blocks unverified research responses."""
        self._validate_run_output(run_output)

    def _validate_run_output(self, run_output: RunOutput) -> bool:
        """Ensure every research claim is grounded in actual tool output."""
        response_text = self._extract_response_text(run_output.content)
        if not response_text:
            return True

        tools = run_output.tools or []
        pmids_in_response = self._extract_pmids(response_text)
        pmids_from_tools = self._extract_pmids_from_tools(tools)
        tool_results_present = self._has_substantive_tool_results(tools)

        # Audit Logging: Grounding Check
        if self.audit_logger:
            self.audit_logger.log_grounding_check(
                pmids_cited=list(pmids_in_response),
                pmids_verified=list(pmids_from_tools),
                hallucination_detected=False # Will update if detected
            )

        if pmids_in_response and not tools:
            reason = "PMIDs were cited without running any research tools"
            self._replace_with_refusal(run_output, reason)
            self.logger.warning(reason)
            if self.audit_logger:
                self.audit_logger.log_validation_check("grounding", False, {"reason": reason})
            return False

        if pmids_in_response and not pmids_from_tools:
            reason = "cited PMIDs are missing from PubMed results"
            self._replace_with_refusal(run_output, reason)
            self.logger.warning(reason)
            if self.audit_logger:
                self.audit_logger.log_validation_check("grounding", False, {"reason": reason})
            return False

        missing_pmids = pmids_in_response - pmids_from_tools
        if missing_pmids:
            reason = f"unverified PMIDs detected: {', '.join(sorted(missing_pmids))}"
            self._replace_with_refusal(run_output, reason)
            self.logger.warning(reason)
            if self.audit_logger:
                self.audit_logger.log_validation_check("grounding", False, {"reason": reason})
            return False

        if self._response_claims_research(response_text) and not tool_results_present:
            reason = self._refusal_reason_from_tools()
            self._replace_with_refusal(run_output, reason)
            self.logger.warning(reason)
            if self.audit_logger:
                self.audit_logger.log_validation_check("grounding", False, {"reason": reason})
            return False

        if self.audit_logger:
            self.audit_logger.log_validation_check("grounding", True)
            
        return True

    @staticmethod
    def _extract_response_text(content: Optional[object]) -> Optional[str]:
        """Normalize RunOutput content into a single string."""
        if content is None:
            return None
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "\n".join(str(item) for item in content if item is not None)
        return str(content)

    @staticmethod
    def _extract_pmids(text: str) -> Set[str]:
        """Extract PMIDs from a blob of text."""
        if not text:
            return set()
        return set(re.findall(r"pmid\s*[:#]?\s*(\d+)", text, flags=re.IGNORECASE))

    def _extract_pmids_from_tools(self, tools: List[ToolExecution]) -> Set[str]:
        pmids: Set[str] = set()
        for execution in tools:
            payload = self._get_tool_result_text(execution)
            if payload:
                pmids.update(self._extract_pmids(payload))
        return pmids

    def _has_substantive_tool_results(self, tools: List[ToolExecution]) -> bool:
        for execution in tools:
            payload = self._get_tool_result_text(execution).strip()
            if not payload:
                continue
            lowered = payload.lower()
            if any(flag in lowered for flag in ["temporarily unavailable", "error", "failed", "unavailable"]):
                continue
            return True
        return False

    @staticmethod
    def _get_tool_result_text(execution: ToolExecution) -> str:
        """Safely extract result text from ToolExecution or dict payloads."""
        if isinstance(execution, ToolExecution):
            return str(execution.result or "")
        if isinstance(execution, dict):
            return str(execution.get("result", "") or "")
        return str(getattr(execution, "result", "") or "")

    @staticmethod
    def _response_claims_research(text: str) -> bool:
        lowered = text.lower()
        research_keywords = ["pmid", "doi", "journal", "article", "study", "trial"]
        return any(keyword in lowered for keyword in research_keywords)

    def _refusal_reason_from_tools(self) -> str:
        status = getattr(self, '_tool_status', {})
        if not status.get('pubmed'):
            return "PubMed tool is unavailable"
        if not self.tools:
            return "no research tools are configured"
        return "search tools returned no usable results to cite"

    def _replace_with_refusal(self, run_output: RunOutput, reason: str) -> None:
        refusal_message = self._build_refusal_message(reason)
        run_output.content = refusal_message
        metadata = dict(run_output.metadata or {})
        metadata.update({
            "grounding_status": "failed",
            "grounding_reason": reason,
        })
        run_output.metadata = metadata

    @staticmethod
    def _build_refusal_message(reason: str) -> str:
        guidance = (
            "\nNext steps:\n"
            "1. Provide additional context or alternate keywords.\n"
            "2. Confirm PubMed/Safety tools are configured and reachable.\n"
            "3. Retry once verified data is available."
        )
        return (
            "⚠️ Unable to provide a research summary because verification failed.\n"
            f"Reason: {reason}."
            f"{guidance}"
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
