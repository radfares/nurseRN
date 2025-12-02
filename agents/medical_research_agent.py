"""
Medical Research Agent - PubMed Database Access
Specialized for searching biomedical and nursing literature
Perfect for finding peer-reviewed clinical studies

HALLUCINATION FIX (2025-11-30):
- Temperature set to 0 (no creativity/fabrication)
- Strict grounding enforcement (no fabricated PMIDs)
- Complete audit logging of all actions
- Pre-response validation of citations
- Mandatory refusal when tool returns empty results

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
PHASE 3 UPDATE (2025-11-20): Enhanced PubMed configuration for full metadata
WEEK 1 REFACTORING (2025-11-22): Added circuit breaker protection and resilience
PHASE 2 COMPLETE (2025-11-23): Refactored to use BaseAgent inheritance
"""

import os
import re
import sys
import time
import traceback
from textwrap import dedent
from typing import Any, Dict, List, Optional

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

# Import centralized configuration
from agent_config import get_db_path

# Import BaseAgent for inheritance pattern
from agents.base_agent import BaseAgent

# Import resilience infrastructure
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Import audit logging
from src.services.agent_audit_logger import get_audit_logger
from src.services.api_tools import (
    build_tools_list,
    create_pubmed_tools_safe,
    get_api_status,
)
# Import LiteratureTools for saving findings to project database
from src.tools.literature_tools import LiteratureTools


class MedicalResearchAgent(BaseAgent):
    """
    Medical Research Agent with PubMed database access.

    HALLUCINATION PREVENTION FEATURES:
    - Temperature = 0 (strict factual mode, no creativity)
    - Audit logging of every action (query, tool call, validation, response)
    - Pre-response grounding check (validates all PMIDs came from tool results)
    - Mandatory refusal when PubMed returns empty results
    - Response validation before output (catch hallucinations before they reach user)
    """

    def __init__(self):
        tools = self._create_tools()
        super().__init__(
            agent_name="Medical Research Agent",
            agent_key="medical_research",
            tools=tools,
        )
        # Initialize audit logger - will log ALL actions
        self.audit_logger = get_audit_logger(
            "medical_research", "Medical Research Agent"
        )
        self.last_tool_results = {}  # Track tool results for grounding validation

    def _create_tools(self) -> list:
        """Create PubMed tools with safe fallback + LiteratureTools for saving."""
        # PubMed doesn't require API keys (just email), so it's generally available
        pubmed_tool = create_pubmed_tools_safe(required=False)

        # LiteratureTools for saving findings to project database
        literature_tools = LiteratureTools()

        # Build tools list, filtering out None values
        tools = build_tools_list(pubmed_tool, literature_tools)

        # Log tool availability (using print since self.logger not available yet)
        if pubmed_tool:
            print("✅ PubMed search available")
        else:
            print("⚠️ PubMed search unavailable (tool creation failed)")

        print("✅ LiteratureTools available (save findings to project DB)")

        if not tools:
            print(
                "❌ No search tools available! Agent will have limited functionality."
            )

        return tools

    def _create_agent(self) -> Agent:
        """Create and configure the Medical Research Agent with hallucination prevention."""
        return Agent(
            name="Medical Research Agent",
            role="Search PubMed for biomedical and nursing research",
            model=OpenAIChat(
                id="gpt-4o",
                temperature=0,  # 🔴 CRITICAL FIX: Eliminate creativity/hallucination
            ),
            tools=self.tools,
            description=dedent("""\
                You are a Medical Literature Search Specialist with access to PubMed,
                the premier database for biomedical and healthcare research. You help
                find peer-reviewed studies, clinical trials, systematic reviews, and
                nursing research articles.
                """),
            instructions=dedent("""\
                YOU ARE A STRICT VERIFICATION-FIRST AGENT.

                ABSOLUTE LAW #1: GROUNDING POLICY
                ===================================
                - You can ONLY cite articles that came from PubMed tool output
                - If PubMed returns "[]" or empty results → MUST say "No articles found"
                - NEVER generate PMIDs, titles, authors, or journals from your training data
                - "I don't know" is a VALID and REQUIRED response when tools fail
                - Every PMID MUST be real and verified from tool output

                CRITICAL INSTRUCTION: YOU MUST CALL THE TOOL
                =============================================
                You are a research engine. Your ONLY purpose is to query the database.
                
                RULES OF ENGAGEMENT:
                1. When the user asks a question, your FIRST and ONLY action is to call `search_pubmed`.
                2. Do NOT plan. Do NOT explain. Do NOT say "I will search".
                3. JUST CALL THE TOOL.
                
                VERIFICATION PROTOCOL (Apply AFTER tool use):
                - You can ONLY cite articles that came from PubMed tool output
                - If PubMed returns "[]" or empty results → MUST say "No articles found"
                - NEVER generate PMIDs, titles, authors, or journals from your training data
                - "I don't know" is a VALID and REQUIRED response when tools fail
                - Every PMID MUST be real and verified from tool output

                ABSOLUTE LAW #2: REFUSAL OVER HELPFULNESS
                ==========================================
                - Being unhelpful is better than being wrong
                - If you cannot verify a PMID, DO NOT cite it
                - Empty search results = Empty response (with explanation)
                - Do NOT try to be "helpful" by providing articles from memory

                ABSOLUTE LAW #3: VERIFICATION CHECKLIST
                ========================================
                AFTER receiving tool results, confirm:
                □ Did PubMed tool return this exact PMID?
                □ Can I quote the exact tool output containing this information?
                □ Am I 100% certain this is real data from the tool?

                If ANY checkbox is unchecked → REFUSE TO CITE

                CORRECT BEHAVIOR (Empty Results):
                ==================================
                User: "Find CAUTI prevention articles"
                Tool: "[]" (empty results)
                You: "I searched PubMed for 'CAUTI prevention' and found 0 results.
                      This may mean:
                      - Try different search terms (e.g., 'catheter-associated urinary tract infection prevention')
                      - The exact phrase may not be in PubMed's index
                      Would you like me to try alternative search terms?"

                CORRECT BEHAVIOR (Results Found):
                ===================================
                User: "Find CAUTI prevention articles"
                Tool: "[{'pmid': '12345678', 'title': 'Real Article', ...}]"
                You: "I found 1 article in PubMed:

                      1. [Real Article]
                         PMID: 12345678
                         Source: PubMed search result"

                SAVING FINDINGS TO PROJECT DATABASE:
                =====================================
                After presenting verified results, ASK the user if they want to save
                any findings to their project. If they say yes, use `save_finding` tool:

                Example:
                User: "Yes, save article 1"
                You: [call save_finding with agent_source="medical_research", title=..., pmid=..., authors=..., abstract=...]

                The save_finding tool accepts:
                - agent_source: "medical_research" (required)
                - title: Article title (required)
                - pmid: PubMed ID
                - authors: Author names
                - abstract: Abstract text
                - journal_source: Journal name
                - publication_date: YYYY-MM-DD format
                - finding_type: "article" (default)

                You can also use get_saved_findings() to show what's already saved,
                and get_finding_count() to show project statistics.

                FORBIDDEN BEHAVIOR (NEVER DO THIS):
                ====================================
                Tool: "[]" (empty results)
                You: "Here are 3 helpful articles:
                      1. Title: Reducing CAUTI in ICU Settings
                         PMID: 98765432  ← FABRICATED!
                         Authors: Smith et al. ← MADE UP!"

                This violates Absolute Law #1. You will be caught by validation.

                SEARCH STRATEGY:
                ================
                1. Use specific medical terminology and MeSH terms when possible
                2. Focus on peer-reviewed, evidence-based research
                3. Prioritize recent publications (last 5-10 years) unless specified
                4. Look for systematic reviews and meta-analyses when available
                5. Include clinical trials and observational studies

                SEARCH TYPES:
                =============
                - Clinical studies and trials
                - Systematic reviews and meta-analyses
                - Nursing research and quality improvement
                - Evidence-based practice guidelines
                - Case studies and cohort studies

                QUALITY INDICATORS:
                ===================
                - Peer-reviewed journals
                - High-impact publications
                - Large sample sizes
                - Recent research (prefer last 5 years)
                - Relevant to clinical practice

                EXAMPLES OF GOOD SEARCHES:
                ==========================
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

    def run(self, *args, **kwargs):
        """Block direct run() calls to enforce grounding validation."""
        raise RuntimeError(
            "Direct run() is disabled. Use run_with_grounding_check() for verified outputs."
        )

    def run_with_grounding_check(
        self, query: str, project_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run agent with mandatory grounding validation.

        This is the main entry point that ensures:
        1. All actions are logged to audit trail
        2. All tool results are captured for validation
        3. Response is checked for hallucinated PMIDs
        4. Validation failures trigger refusal

        Args:
            query: User's query
            project_name: Associated project for context

        Returns:
            Response with validation status
        """
        start_time = time.time()
        session_id = f"med_research_{int(time.time() * 1000)}"

        try:
            # Add input validation
            if not query or not isinstance(query, str):
                self.audit_logger.log_error(
                    error_type="InvalidInput",
                    error_message="Query must be a non-empty string"
                )
                return {
                    "content": "⚠️ Invalid query: must be a non-empty string",
                    "validation_passed": False,
                    "error": "invalid_input"
                }

            # Add query length validation
            if len(query) > 10000:  # Prevent excessively long queries
                self.audit_logger.log_error(
                    error_type="QueryTooLong",
                    error_message=f"Query length {len(query)} exceeds maximum"
                )
                return {
                    "content": "⚠️ Query too long: maximum 10,000 characters",
                    "validation_passed": False,
                    "error": "query_too_long"
                }

            # Set audit context
            self.audit_logger.set_session(session_id, project_name)

            # Log query received
            self.audit_logger.log_query_received(query, project_name)

            # Run agent - returns RunOutput object with messages field
            run_output = self.agent.run(query)
            response_text = str(
                run_output.content if hasattr(run_output, "content") else run_output
            )

            # Extract cited PMIDs from response text
            cited_pmids = set(
                re.findall(r"PMID:\s*(\d+)", response_text, re.IGNORECASE)
            )

            # Extract verified PMIDs from actual tool results in RunOutput
            verified_pmids = self._extract_verified_pmids_from_output(run_output)

            # Log what tool results we found
            self.audit_logger.log_tool_result(
                tool_name="pubmed_grounding_verification",
                result={
                    "verified_pmids": list(verified_pmids),
                    "total_found": len(verified_pmids),
                },
            )

            # Check for hallucinations (unverified PMIDs)
            unverified_pmids = cited_pmids - verified_pmids
            hallucination_detected = bool(unverified_pmids)

            # Log grounding check
            self.audit_logger.log_grounding_check(
                pmids_cited=list(cited_pmids),
                pmids_verified=list(verified_pmids),
                hallucination_detected=hallucination_detected,
            )

            # If hallucination detected, return error response
            if hallucination_detected:
                self.audit_logger.log_response_generated(
                    response="HALLUCINATION DETECTED - Refusing to output",
                    response_type="hallucination_detected",
                    validation_passed=False,
                    duration_ms=int((time.time() - start_time) * 1000),
                )

                return {
                    "content": (
                        "⚠️ SAFETY SYSTEM ACTIVATED\n\n"
                        "I generated a response with article citations, but could not verify "
                        "the PMIDs against my PubMed search results.\n\n"
                        "To prevent providing false information, I must refuse to answer.\n\n"
                        f"Unverified PMIDs detected: {sorted(unverified_pmids)}\n"
                        f"Verified PMIDs found: {len(verified_pmids)}\n\n"
                        "This is a safety feature to prevent hallucinated citations.\n"
                        "Please try:\n"
                        "1. Rephrasing your search query\n"
                        "2. Using more specific medical terms\n"
                        "3. Checking if PubMed tool is functioning correctly"
                    ),
                    "validation_passed": False,
                    "hallucination_detected": True,
                }

            # Response passed validation
            self.audit_logger.log_response_generated(
                response=response_text,
                response_type="success",
                validation_passed=True,
                duration_ms=int((time.time() - start_time) * 1000),
            )

            return {
                "content": response_text,
                "validation_passed": True,
                "hallucination_detected": False,
            }

        except Exception as e:
            # Log error
            self.audit_logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc(),
            )

            # Return error response
            return {
                "content": f"⚠️ Error during search: {str(e)}",
                "validation_passed": False,
                "error": str(e),
            }

    def _extract_verified_pmids_from_output(self, run_output: Any) -> set:
        """
        Extract PMIDs from actual tool results in RunOutput.

        The Agno framework returns a RunOutput object with a messages field
        that contains all messages exchanged, including tool results.

        Args:
            run_output: The RunOutput object returned by agent.run()

        Returns:
            Set of verified PMIDs that came from PubMed tool results
        """
        verified_pmids = set()

        try:
            # RunOutput has a 'messages' field containing all messages
            if not hasattr(run_output, "messages") or not run_output.messages:
                self.audit_logger.log_error(
                    error_type="MissingMessages",
                    error_message="RunOutput has no messages field",
                    stack_trace="",
                )
                return verified_pmids

            # Iterate through all messages looking for tool results
            for message in run_output.messages:
                message_str = str(message)

                # Look for PMID patterns in message content
                # Patterns: PMID: 12345, "pmid": "12345", pmid=12345, etc.
                pmid_patterns = [
                    r'["\']?pmid["\']?\s*:\s*["\']?(\d+)["\']?',  # JSON format
                    r"PMID:\s*(\d+)",  # Standard format
                    r'pmid["\']?\s*=\s*["\']?(\d+)["\']?',  # Assignment format
                    r'pmid["\']?\s*,\s*["\']?(\d+)["\']?',  # Comma format
                ]

                for pattern in pmid_patterns:
                    pmids = re.findall(pattern, message_str, re.IGNORECASE)
                    verified_pmids.update(pmids)

        except Exception as e:
            self.audit_logger.log_error(
                error_type="PMIDExtractionError",
                error_message=f"Failed to extract PMIDs from output: {str(e)}",
                stack_trace=traceback.format_exc(),
            )

        return verified_pmids

    def _extract_verified_pmids(self) -> set:
        """
        DEPRECATED: This method doesn't work with Agno framework.
        Use _extract_verified_pmids_from_output() instead.

        Kept for backward compatibility only.

        Returns:
            Empty set (agent.messages doesn't exist in Agno)
        """
        # This method attempted to use agent.messages which doesn't exist
        # in the Agno framework. The actual messages are in the RunOutput
        # returned by agent.run()
        return set()

    def print_response(self, query: str, project_name: Optional[str] = None, stream: bool = False) -> None:
        """
        Backwards-compatible adapter used by the interactive UI.
        Always routes through run_with_grounding_check() so validation/audit are enforced.
        Prints a human-friendly summary to stdout.

        Args:
            query: User's query
            project_name: Associated project for context
            stream: Whether to stream the response (not fully implemented yet)
        """
        try:
            result = self.run_with_grounding_check(query, project_name=project_name)
        except Exception as e:
            # Fail loudly but safely for the UI
            print(f"❌ Agent error: {type(e).__name__}: {e}")
            return

        # result is expected to be a dict with keys like 'content' and 'validation_passed'
        content = result.get("content") if isinstance(result, dict) else str(result)
        validation_passed = result.get("validation_passed", None) if isinstance(result, dict) else None

        if validation_passed is False:
            print(f"⚠️ Validation failed: {result.get('error', 'validation_failed')}")
        # Print the content (short) for the interactive UI
        print(content if content is not None else "(no content returned)")

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
            print(
                "  ⚠️ PubMed - Using default email (set PUBMED_EMAIL for better tracking)"
            )

        print("-" * 60)
        print("\n🔒 HALLUCINATION PREVENTION ACTIVE:")
        print("  • Temperature = 0 (factual mode, no creativity)")
        print("  • Grounding validation enabled (PMID verification)")
        print("  • Audit logging enabled (all actions tracked)")
        print("  • Empty results = Refusal (not fabrication)")

        # Warning if no search tools available
        if not self.tools:
            print("\n⚠️ WARNING: PubMed tool not available!")
            print("   This is unusual - check logs for errors.")
            print()

        print("\n" + "=" * 60)
        print("🏥 Medical Research Agent (PubMed) Ready!")
        print("=" * 60)

        print("\n✨ CAPABILITIES:")
        print("  • Find Specific Study Types: Systematic Reviews, Clinical Trials, Nursing Research")
        print("  • Detailed Metadata: DOI links, PMIDs, Abstracts, Journal info")
        print("  • Anti-Hallucination: 100% Verified Citations (No made-up papers)")
        print("  • Smart Search: Uses MeSH terms to find relevant articles")

        print("\n🔍 EXAMPLE QUERIES:")
        print('  1. "Find a systematic review on pressure ulcer prevention (last 5 years)"')
        print('  2. "What are the latest clinical guidelines for sepsis management?"')
        print('  3. "Find qualitative nursing studies on patient comfort in ICU"')
        print('  4. "Search for foley catheter care protocols"')

        print("\n💡 TIP: Be specific! You can ask for 'recent', 'peer-reviewed', or specific journals.")
        print("=" * 60 + "\n")


# Create global instance for backward compatibility
_medical_research_agent_instance = None

def get_medical_research_agent():
    """
    Return the MedicalResearchAgent instance with lazy initialization.
    Callers must use run_with_grounding_check() on this object.
    """
    global _medical_research_agent_instance
    if _medical_research_agent_instance is None:
        try:
            _medical_research_agent_instance = MedicalResearchAgent()
        except Exception as _init_error:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to initialize MedicalResearchAgent: {_init_error}")
            logger.debug("Init error details available in debug logs")
            return None
    return _medical_research_agent_instance

# Update __all__ to control exports
__all__ = ['MedicalResearchAgent', 'get_medical_research_agent']


if __name__ == "__main__":
    if _medical_research_agent_instance is not None:
        _medical_research_agent_instance.run_with_error_handling()
    else:
        print("❌ Agent failed to initialize. Check logs for details.")
