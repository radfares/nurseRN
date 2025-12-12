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
import sys
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
    build_tools_list,
    get_api_status
)
# Import LiteratureTools for saving findings to project database
from src.tools.literature_tools import LiteratureTools


class AcademicResearchAgent(BaseAgent):
    """Academic Research Agent with Arxiv database access."""

    def __init__(self):
        tools = self._create_tools()
        super().__init__(
            agent_name="Academic Research Agent",
            agent_key="academic_research",
            tools=tools
        )

    def _create_tools(self) -> list:
        """Create Arxiv tools with safe fallback + LiteratureTools for saving."""
        # Add ReasoningTools for structured academic reasoning
        reasoning_tools = ReasoningTools(add_instructions=True)
        
        # Arxiv is free and doesn't require authentication
        arxiv_tool = create_arxiv_tools_safe(required=False)

        # LiteratureTools for saving findings to project database
        try:
            literature_tools = LiteratureTools()
            print("✅ LiteratureTools available (save findings to project DB)")
        except Exception as exc:
            literature_tools = None
            print(f"⚠️ LiteratureTools unavailable: {exc}")

        # Build tools list, filtering out None values (ReasoningTools first)
        tools = build_tools_list(reasoning_tools, arxiv_tool, literature_tools)

        # Log tool availability (using print since self.logger not available yet)
        if arxiv_tool:
            print("✅ Arxiv search available")
        else:
            print("⚠️ Arxiv search unavailable (tool creation failed)")

        if not tools:
            print("❌ No search tools available! Agent will have limited functionality.")

        return tools

    def _create_agent(self) -> Agent:
        """Create and configure the Academic Research Agent."""
        return Agent(
            name="Academic Research Agent",
            role="Search Arxiv for academic research papers",
            model=OpenAIChat(id="gpt-4o", temperature=0),
            tools=self.tools,
            description=dedent("""\
                You are an Academic Research Specialist with access to Arxiv,
                a repository of academic papers across science, mathematics, computer science,
                and quantitative fields. You help find cutting-edge research, theoretical
                studies, and interdisciplinary papers.
                """),
            instructions=dedent("""\
                EXPERTISE: Arxiv Academic Paper Search

                ABSOLUTE LAW #1: GROUNDING POLICY
                - You can ONLY cite articles that came from Arxiv tool output
                - If Arxiv returns "[]" → MUST say "No articles found"
                - NEVER generate Arxiv IDs or titles from your training data
                - "I don't know" is a valid response if data is missing

                ABSOLUTE LAW #2: REFUSAL OVER HELPFULNESS
                - It is better to be unhelpful than to be wrong
                - If search returns 0 results, you MUST NOT invent articles
                - Do not try to "help" by providing plausible-sounding but fake papers

                ABSOLUTE LAW #3: VERIFICATION CHECKLIST
                Before citing ANY paper, you must verify:
                1. Did this specific Arxiv ID appear in the tool output?
                2. Do the title and authors match exactly?
                3. If you cannot verify it, do NOT cite it.

                SEARCH STRATEGY:
                1. Search across multiple scientific domains
                2. Focus on recent preprints and published papers
                3. Look for interdisciplinary research when relevant
                4. Include theoretical frameworks and methodologies
                5. Find systematic approaches and novel techniques

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
                - "Statistical analysis healthcare quality improvement"
                - "Machine learning patient fall prediction"
                - "Data analysis methods clinical trials"
                - "Epidemiological models hospital infections"
                - "Quality metrics healthcare systems"
                """) + (
                "\n"
                + dedent("""\
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
                if is_reasoning_block_enabled()
                else ""
            ),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
            db=SqliteDb(db_file=get_db_path("academic_research")),
            pre_hooks=[self._audit_pre_hook],
            post_hooks=[self._audit_post_hook],
        )

    def run_with_grounding_check(self, query: str, **kwargs) -> Any:
        """Execute the agent with mandatory grounding validation."""
        import traceback

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
        import re
        import traceback

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
                arxiv_patterns = [
                    r'\d{4}\.\d{4,5}',       # New format: 2103.12345
                    r'[a-z\-]+/\d{7}'        # Old format: math/0001001
                ]
                for pattern in arxiv_patterns:
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
        import re

        content = str(run_output.content) if hasattr(run_output, 'content') else str(run_output)
        arxiv_pattern = r'(\d{4}\.\d{4,5}|[a-z\-]+/\d{7})'
        cited_ids = set(re.findall(arxiv_pattern, content, re.IGNORECASE))

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

        print("-" * 60)

        # Warning if no search tools available
        if not self.tools:
            print("\n⚠️ WARNING: Arxiv tool not available!")
            print("   This is unusual - check logs for errors.")
            print()

        print("\n📚 Academic Research Agent (Arxiv) Ready!")
        print("\nSpecialized for academic and theoretical research")
        print("\nExample queries:")
        print("-" * 60)

        print("\n1. Find statistical methods:")
        print('   response = academic_research_agent.run("""')
        print('   Find papers on statistical analysis methods for')
        print('   healthcare quality improvement""")')

        print("\n2. Search for AI/ML applications:")
        print('   response = academic_research_agent.run("""')
        print('   Find research on machine learning for predicting')
        print('   patient outcomes""")')

        print("\n3. Methodological papers:")
        print('   response = academic_research_agent.run("""')
        print('   Find papers about data collection and analysis')
        print('   methods in clinical research""")')

        print("\n4. With Streaming:")
        print('   academic_research_agent.print_response("""')
        print('   Find statistical methods papers""", stream=True)')

        print("\n" + "-" * 60)
        print("\n💡 TIP: Arxiv is great for theoretical and methodological research!")
        print("Use it when you need advanced analysis techniques.")
        print("Use stream=True for real-time response generation.")


# Create global instance for backward compatibility
_academic_research_agent_instance = AcademicResearchAgent()
academic_research_agent = _academic_research_agent_instance.agent


def get_academic_research_agent():
    """Factory function to get the AcademicResearchAgent instance.

    Returns:
        AcademicResearchAgent wrapper instance.
    """
    return _academic_research_agent_instance


if __name__ == "__main__":
    _academic_research_agent_instance.run_with_error_handling()
