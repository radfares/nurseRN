"""
Academic Research Agent - Arxiv Database Access
Specialized for academic papers across all scientific fields
Great for finding theoretical research and cutting-edge studies

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
WEEK 1 REFACTORING (2025-11-22): Added circuit breaker protection and resilience
PHASE 2 COMPLETE (2025-11-23): Refactored to use BaseAgent inheritance
"""

import os
import re
import sys
import traceback
from typing import Any
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

# Import centralized configuration
from agent_config import get_db_path, is_reasoning_block_enabled

# Import BaseAgent for inheritance pattern
from agents.base_agent import BaseAgent

# Import resilience infrastructure
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.services.api_tools import (
    create_arxiv_tools_safe,
    create_semantic_scholar_tools_safe,
    build_tools_list,
    get_api_status
)
# Import LiteratureTools for saving findings to project database
from src.tools.literature_tools import LiteratureTools
# Import DocumentReaderTools for reading PDFs, PPTX, websites
from src.tools.readers_tools.document_reader_service import create_document_reader_tools_safe


ARXIV_ID_PATTERNS = [
    r"\d{4}\.\d{4,5}",      # New format: 2103.12345
    r"[a-z\-]+/\d{7}",      # Old format: math/0001001
]
ARXIV_ID_PATTERN = f"({'|'.join(ARXIV_ID_PATTERNS)})"
REASONING_DISABLED_VALUES = {"0", "false", "off", "no", "disable", "disabled"}


class AcademicResearchAgent(BaseAgent):
    """Academic Research Agent with Arxiv database access."""

    def __init__(self):
        tools = self._create_tools()
        super().__init__(
            agent_name="Academic Research Agent",
            agent_key="academic_research",
            tools=tools
        )

    def _build_reasoning_tools(self):
        """Create ReasoningTools when enabled via environment flag."""
        reasoning_flag = os.getenv("ENABLE_REASONING_TOOLS", "off").strip().lower()
        if reasoning_flag in REASONING_DISABLED_VALUES:
            return None
        return ReasoningTools(add_instructions=True)

    def _build_literature_tools(self):
        """Create LiteratureTools with safe fallback."""
        try:
            tool = LiteratureTools()
            print("✅ LiteratureTools available (save findings to project DB)")
            return tool
        except Exception as exc:
            print(f"⚠️ LiteratureTools unavailable: {exc}")
            return None

    @staticmethod
    def _log_tool_status(name: str, available: bool, success_msg: str, failure_msg: str) -> None:
        """Standardized tool availability logging before logger is ready."""
        icon = "✅" if available else "⚠️"
        detail = success_msg if available else failure_msg
        print(f"{icon} {name} {detail}")

    def _reasoning_instructions(self) -> str:
        """Optional reasoning block instructions."""
        if not is_reasoning_block_enabled():
            return ""
        return "\n" + dedent("""\
            REASONING APPROACH (ACADEMIC):
            - Break down complex questions into sub-questions (theory, method, domain) before choosing queries
            - State assumptions about domain/scope and confirm missing details instead of inferring them
            - Map each claim to Arxiv tool output and prefer primary sources over commentary
            - Compare methodological alternatives and frameworks, noting trade-offs in rigor, data needs, and bias
            - Evaluate evidence quality: study design, reproducibility signals, code/data availability, peer review status
            - Surface uncertainties and research gaps explicitly; propose follow-up searches or adjacent fields to explore
            - Keep refusals in place when verification fails; this reasoning supports but never overrides grounding rules
            - Present concise summaries, highlighting limitations and future work alongside key findings
            """)

    def _create_tools(self) -> list:
        """Create Arxiv tools with safe fallback + DocumentReaders + LiteratureTools for saving."""
        reasoning_tools = self._build_reasoning_tools()
        arxiv_tool = create_arxiv_tools_safe(required=False)
        semantic_scholar_tool = create_semantic_scholar_tools_safe(required=False)
        doc_reader_tools = create_document_reader_tools_safe(required=False)
        literature_tools = self._build_literature_tools()

        # Build tools list, filtering out None values (ReasoningTools first)
        tools = build_tools_list(
            reasoning_tools,
            arxiv_tool,
            semantic_scholar_tool,
            doc_reader_tools,
            literature_tools
        )

        # Log tool availability (using print since self.logger not available yet)
        self._log_tool_status(
            "Arxiv search",
            bool(arxiv_tool),
            "available",
            "unavailable (tool creation failed)"
        )
        self._log_tool_status(
            "Semantic Scholar search",
            bool(semantic_scholar_tool),
            "available",
            "unavailable (tool creation failed)"
        )
        self._log_tool_status(
            "DocumentReaders",
            bool(doc_reader_tools),
            "available (PDF/PPTX/Web/ArXiv/CSV/JSON)",
            "unavailable (dependency or initialization issue)"
        )
        reasoning_icon = "✅" if reasoning_tools else "ℹ️"
        reasoning_detail = (
            "enabled (ENABLE_REASONING_TOOLS=on)"
            if reasoning_tools
            else "disabled (set ENABLE_REASONING_TOOLS=on to enable)"
        )
        print(f"{reasoning_icon} ReasoningTools {reasoning_detail}")

        if not tools:
            print("❌ No search tools available! Agent will have limited functionality.")

        return tools

    def _create_agent(self) -> Agent:
        """Create and configure the Academic Research Agent."""
        return Agent(
            name="Academic Research Agent",
            role="Search Arxiv for academic research papers",
            model=OpenAIChat(id="gpt-4o", temperature=0),
            reasoning=True,  # Enable chain-of-thought reasoning
            reasoning_model=OpenAIChat(id="gpt-4o", max_tokens=2000),
            reasoning_max_steps=5,  # CRITICAL: Prevent runaway loops
            tool_call_limit=10,  # CRITICAL: Limit tool calls per run
            tools=self.tools,
            description=dedent("""\
                You are an Academic Research Specialist with access to Arxiv and
                Semantic Scholar. You help find cutting-edge research, theoretical
                studies, interdisciplinary papers, and perform citation analysis.
                Arxiv provides preprints across science, mathematics, and computer science,
                while Semantic Scholar offers AI-powered paper discovery and citation networks.
                """),
            instructions=dedent("""\
                EXPERTISE: Academic Paper Search & Citation Analysis

                ABSOLUTE LAW #1: GROUNDING POLICY
                - You can ONLY cite articles that came from Arxiv or Semantic Scholar tool output
                - If search returns "[]" → MUST say "No articles found"
                - NEVER generate Arxiv IDs, DOIs, or titles from your training data
                - "I don't know" is a valid response if data is missing

                ABSOLUTE LAW #2: REFUSAL OVER HELPFULNESS
                - It is better to be unhelpful than to be wrong
                - If search returns 0 results, you MUST NOT invent articles
                - Do not try to "help" by providing plausible-sounding but fake papers

                ABSOLUTE LAW #3: VERIFICATION CHECKLIST
                Before citing ANY paper, you must verify:
                1. Did this specific ID (Arxiv/DOI/Paper ID) appear in the tool output?
                2. Do the title and authors match exactly?
                3. If you cannot verify it, do NOT cite it.

                TOOL SELECTION:
                ===============
                - Arxiv: Use for preprints in physics, math, CS, statistics, quantitative biology
                - Semantic Scholar: Use for citation analysis, finding related papers, broader academic search

                When to use Semantic Scholar:
                - Finding papers that cite a specific work
                - Discovering related papers and research connections
                - Getting citation counts and impact metrics
                - Finding papers across multiple databases (includes PubMed, ArXiv, etc.)
                - AI-powered paper recommendations

                When to use Arxiv:
                - Latest preprints in specific domains (physics, math, CS)
                - Mathematical and theoretical research
                - Machine learning and AI methodology papers
                - Quantitative methods and statistical techniques

                SEARCH STRATEGY:
                1. Search across multiple scientific domains
                2. Focus on recent preprints and published papers
                3. Look for interdisciplinary research when relevant
                4. Include theoretical frameworks and methodologies
                5. Find systematic approaches and novel techniques
                6. Use Semantic Scholar for citation networks and paper discovery

                ARXIV CATEGORIES RELEVANT TO HEALTHCARE:
                - Computer Science (AI/ML in healthcare)
                - Statistics (clinical statistics, data analysis)
                - Quantitative Biology (biological systems)
                - Physics (medical imaging, biophysics)
                - Mathematics (epidemiological models)

                RESPONSE FORMAT:
                For each paper found:
                - Title and authors
                - Publication date and Arxiv ID
                - Abstract summary
                - Key contributions and findings
                - Methodology overview
                - Potential applications to healthcare
                - Links to full paper

                USE CASES FOR NURSING PROJECT:
                - Statistical methods for data analysis
                - Machine learning for patient outcome prediction
                - Data visualization techniques
                - Epidemiological modeling
                - Quality improvement methodologies
                - Systems analysis approaches

                EXAMPLES OF GOOD SEARCHES:

                Arxiv searches:
                - "Statistical analysis healthcare quality improvement"
                - "Machine learning patient fall prediction"
                - "Data analysis methods clinical trials"
                - "Epidemiological models hospital infections"
                - "Quality metrics healthcare systems"

                Semantic Scholar searches:
                - "Find papers citing PMID:12345678" (citation analysis)
                - "Papers related to transformer models in healthcare"
                - "Machine learning patient outcome prediction" (broad search)
                - "Find highly-cited papers on deep learning medical imaging"
                """) + self._reasoning_instructions(),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
            db=SqliteDb(db_file=get_db_path("academic_research")),
            pre_hooks=[self._audit_pre_hook],
            post_hooks=[self._audit_post_hook],
        )

    def run_with_grounding_check(self, query: str, **kwargs) -> Any:
        """Execute the agent with mandatory grounding validation."""
        project_name = kwargs.get("project_name")
        if self.audit_logger:
            self.audit_logger.log_query_received(query, project_name)

        stream_requested = bool(kwargs.get("stream"))

        try:
            response = self.agent.run(query, **kwargs)

            if stream_requested:
                return response

            self._validate_run_output(response)

            if self.audit_logger:
                self.audit_logger.log_response_generated(
                    response=str(response.content),
                    response_type="success",
                    validation_passed=True
                )

            return response

        except ValueError as validation_error:
            if self.audit_logger:
                self.audit_logger.log_response_generated(
                    response="GROUNDING VIOLATION BLOCKED",
                    response_type="validation_failed",
                    validation_passed=False
                )
                self.audit_logger.log_error(
                    error_type="GroundingViolation",
                    error_message=str(validation_error),
                    stack_trace=traceback.format_exc()
                )

            return {
                "content": (
                    "SAFETY SYSTEM ACTIVATED\n\n"
                    f"{str(validation_error)}\n\n"
                    "I cannot provide unverified academic citations.\n"
                    "Please try a different search query."
                ),
                "validation_passed": False,
                "hallucination_detected": True
            }

        except Exception as e:
            if self.audit_logger:
                self.audit_logger.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise

    def run(self, *args, **kwargs):
        """Block direct run() calls to enforce grounding validation."""
        raise RuntimeError(
            "Direct run() is disabled. Use run_with_grounding_check() for verified outputs."
        )

    def _extract_verified_arxiv_ids_from_output(self, run_output: Any) -> set:
        """
        Extract Arxiv IDs from actual tool results in RunOutput.
        """
        verified_ids = set()

        try:
            if not hasattr(run_output, "messages") or not run_output.messages:
                if self.audit_logger:
                    self.audit_logger.log_error(
                        error_type="MissingMessages",
                        error_message="RunOutput has no messages field",
                        stack_trace=""
                    )
                return verified_ids

            for message in run_output.messages:
                message_str = str(message)
                for pattern in ARXIV_ID_PATTERNS:
                    ids = re.findall(pattern, message_str, re.IGNORECASE)
                    verified_ids.update(ids)

        except Exception as e:
            if self.audit_logger:
                self.audit_logger.log_error(
                    error_type="ArxivIDExtractionError",
                    error_message=f"Failed to extract Arxiv IDs: {str(e)}",
                    stack_trace=traceback.format_exc()
                )

        return verified_ids

    def _validate_run_output(self, run_output: Any) -> bool:
        """
        Ensure every cited paper is grounded in actual tool output.
        BLOCKS execution if hallucinated Arxiv IDs detected.
        """
        content = str(run_output.content) if hasattr(run_output, 'content') else str(run_output)
        cited_ids = set(re.findall(ARXIV_ID_PATTERN, content, re.IGNORECASE))

        verified_ids = self._extract_verified_arxiv_ids_from_output(run_output)

        unverified_ids = cited_ids - verified_ids
        hallucination_detected = bool(unverified_ids)

        if self.audit_logger:
            self.audit_logger.log_validation_check(
                "grounding",
                not hallucination_detected,
                {
                    "cited_ids": list(cited_ids),
                    "verified_ids": list(verified_ids),
                    "unverified_ids": list(unverified_ids)
                }
            )

        if hallucination_detected:
            raise ValueError(
                f"GROUNDING VIOLATION: Unverified Arxiv IDs detected: {sorted(unverified_ids)}\n"
                f"Only {len(verified_ids)} IDs were verified from tool results."
            )

        return True

    def show_usage_examples(self):
        """Display usage examples for the Academic Research Agent."""
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

        # Arxiv info
        print("  ✅ Arxiv - No authentication required (free access)")
        print("  ✅ Semantic Scholar - No authentication required (free access)")

        print("-" * 60)

        # Warning if no search tools available
        if not self.tools:
            print("\n⚠️ WARNING: Arxiv tool not available!")
            print("   This is unusual - check logs for errors.")
            print()

        print("\n📚 Academic Research Agent (Arxiv + Semantic Scholar) Ready!")
        print("\nSpecialized for academic research, theoretical studies, and citation analysis")
        print("\nExample queries:")
        print("-" * 60)

        print("\n1. Find statistical methods (Arxiv):")
        print('   response = academic_research_agent.run_with_grounding_check("""')
        print('   Find papers on statistical analysis methods for')
        print('   healthcare quality improvement""")')

        print("\n2. Search for AI/ML applications (Arxiv):")
        print('   response = academic_research_agent.run_with_grounding_check("""')
        print('   Find research on machine learning for predicting')
        print('   patient outcomes""")')

        print("\n3. Citation analysis (Semantic Scholar):")
        print('   response = academic_research_agent.run_with_grounding_check("""')
        print('   Find papers that cite the transformer architecture paper')
        print('   and show citation counts""")')

        print("\n4. Paper discovery (Semantic Scholar):")
        print('   response = academic_research_agent.run_with_grounding_check("""')
        print('   Find highly-cited papers on deep learning in medical imaging""")')

        print("\n5. With Streaming:")
        print('   academic_research_agent.print_response("""')
        print('   Find statistical methods papers""", stream=True)')

        print("\n" + "-" * 60)
        print("\n💡 TIP: Use Arxiv for preprints and theoretical research!")
        print("💡 TIP: Use Semantic Scholar for citation analysis and paper discovery!")
        print("Use stream=True for real-time response generation.")


# Create global instance for backward compatibility
_academic_research_agent_instance = AcademicResearchAgent()
# Export the wrapper (preferred) so grounding/audit hooks remain active
academic_research_agent = _academic_research_agent_instance
# Legacy/raw agent for direct agno access if needed
academic_research_agent_raw = _academic_research_agent_instance.agent


def get_academic_research_agent():
    """Factory function to get the AcademicResearchAgent instance.

    Returns:
        AcademicResearchAgent wrapper instance.
    """
    return _academic_research_agent_instance


if __name__ == "__main__":
    _academic_research_agent_instance.run_with_error_handling()
