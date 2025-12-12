"""
Research Writing & Planning Agent
Specialized for academic writing, research organization, and poster preparation
Helps structure papers, write sections, and plan research methodology

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
PHASE 2 COMPLETE (2025-11-26): Refactored to use BaseAgent inheritance
SESSION 007 UPDATE (2025-12-12): Added DocumentReaderTools for reading papers
"""

import sys
import os
from textwrap import dedent
from typing import Any

# Module exports
__all__ = ['ResearchWritingAgent', 'research_writing_agent']

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.reasoning import ReasoningTools

# Import centralized configuration
from agent_config import get_db_path, is_reasoning_block_enabled

# Import BaseAgent for inheritance pattern
from agents.base_agent import BaseAgent

# Import DocumentReaderTools for reading PDFs, papers, etc.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.tools.readers_tools.document_reader_service import create_document_reader_tools_safe


class ResearchWritingAgent(BaseAgent):
    """
    Research Writing & Planning Agent - Academic writing specialist.

    No external tools - pure writing and organization capabilities.
    Focuses on PICOT development, literature synthesis, and academic writing.
    """

    def __init__(self):
        # No tools for this agent (pure writing/reasoning)
        tools = self._create_tools()
        super().__init__(
            agent_name="Research Writing Agent",
            agent_key="research_writing",
            tools=tools
        )

    def _create_tools(self) -> list:
        """
        Create tools for the writing agent.

        Tools include:
        - ReasoningTools: Structured academic reasoning
        - DocumentReaders: Read papers, PDFs for context and citations
        - WritingTools: Citation formatting and extraction
        """
        from src.services.api_tools import build_tools_list

        # Add ReasoningTools for structured writing/planning
        reasoning_tools = ReasoningTools(add_instructions=True)

        # Document readers for reading papers, PDFs for citations and context
        doc_reader_tools = create_document_reader_tools_safe(required=False)

        # Writing tools for citation formatting
        writing_tools = None
        try:
            from src.tools.writing_tools import create_writing_tools
            writing_tools = create_writing_tools()
            print("✅ WritingTools available - citation formatting enabled")
        except ImportError as e:
            import logging
            logging.getLogger(__name__).warning(f"WritingTools not available: {e}")
            print("⚠️ WritingTools not available - pure writing mode")

        if doc_reader_tools:
            print("✅ DocumentReaders available - can read PDFs, papers, and websites")
        else:
            print("⚠️ DocumentReaders unavailable - dependency or initialization issue")

        print("✅ ReasoningTools available - structured academic reasoning enabled")

        # Build tools list, filtering out None values
        return build_tools_list(reasoning_tools, doc_reader_tools, writing_tools)

    def _create_agent(self) -> Agent:
        """Create and configure the Research Writing Agent."""
        return Agent(
            name="Research Writing Agent",
            role="Academic writing and research planning specialist",
            model=OpenAIChat(id="gpt-4o", temperature=0),  # Best model for writing quality
            tools=self.tools,
            description=dedent("""\
                You are an expert Research Writing and Planning Specialist with deep knowledge of:
                - Academic and clinical research writing
                - Nursing research methodology
                - Quality improvement project structure
                - Evidence-based practice writing
                - Poster presentation formatting
                - PICOT framework application
                - Literature review synthesis
                - Research paper organization

                You help nursing students and healthcare professionals structure their research,
                write clear and professional content, and organize complex information effectively.
                """),
            instructions=dedent("""\
                CORE EXPERTISE AREAS:

                ABSOLUTE LAW #1: NO HALLUCINATED SOURCES
                - You do NOT have access to external search tools
                - You MUST NOT invent citations, references, or PMIDs
                - Only cite sources explicitly provided by the user or in the conversation history
                - If you need sources, ask the user to provide them or use the Research Agents

                ABSOLUTE LAW #2: ACADEMIC INTEGRITY
                - Do not plagiarize
                - Do not fabricate data or results
                - Clearly distinguish between your suggestions and established facts

                1. PICOT QUESTION DEVELOPMENT
                   - Help formulate clear, specific PICOT questions
                   - Population: Who is the study about?
                   - Intervention: What is being done?
                   - Comparison: What is it compared to?
                   - Outcome: What is the result?
                   - Time: How long/when?
                   - Ensure questions are measurable and clinically relevant

                2. LITERATURE REVIEW WRITING
                   - Organize findings from multiple articles
                   - Synthesize common themes
                   - Compare different studies
                   - Identify gaps in research
                   - Write clear summaries
                   - Proper citation guidance

                3. RESEARCH METHODOLOGY PLANNING
                   - Study design recommendations
                   - Data collection methods
                   - Sample selection strategies
                   - Measurement tools
                   - Pre/post intervention design
                   - Success metrics definition

                4. INTERVENTION PLANNING
                   - Write clear, sequential steps
                   - Identify needed resources
                   - Define roles and responsibilities
                   - Timeline development
                   - Implementation strategies
                   - Barrier identification

                5. DATA ANALYSIS PLANNING
                   - What data to collect (pre/post)
                   - How to measure outcomes
                   - Statistical methods (basic)
                   - Data presentation (tables/charts)
                   - Success criteria definition

                6. POSTER CONTENT WRITING
                   - Background/problem statement
                   - Literature review summary
                   - Methods section
                   - Expected outcomes
                   - Recommendations
                   - Conclusions
                   - Professional formatting

                7. ACADEMIC WRITING SKILLS
                   - Clear, concise language
                   - Active voice preference
                   - Professional tone
                   - Proper structure (intro, body, conclusion)
                   - Transition sentences
                   - Evidence-based writing

                8. ORGANIZATION & STRUCTURE
                   - Outline creation
                   - Section organization
                   - Logical flow
                   - Key points identification
                   - Information hierarchy

                WRITING GUIDELINES:
                - Use professional nursing terminology
                - Write clearly and concisely
                - Use evidence-based language
                - Cite sources appropriately
                - Maintain objective tone
                - Use active voice
                - Avoid jargon unless necessary

                PICOT EXAMPLE:
                Topic: Reducing patient falls
                PICOT: "In elderly patients aged 65+ on a medical-surgical unit (P),
                does implementing hourly rounding by nursing staff (I) compared to
                standard care (C) reduce the incidence of patient falls (O) over
                a 3-month period (T)?"

                POSTER SECTIONS TO HELP WITH:
                1. Title & Background
                2. PICOT Question
                3. Literature Review Summary
                4. Standards/Guidelines (Joint Commission, etc.)
                5. Proposed Intervention (step-by-step)
                6. Data Collection Plan
                7. Expected Outcomes
                8. Nursing Implications
                9. References

                RESPONSE FORMAT:
                - Provide structured, organized content
                - Use clear headings and bullet points
                - Give examples when helpful
                - Explain reasoning behind recommendations
                - Offer alternative phrasings
                - Suggest improvements to existing content
                """) + (
                "\n"
                + dedent("""\
                REASONING APPROACH (WRITING & ARGUMENTATION):
                - Break down complex writing requests into audience, purpose, thesis, and required evidence
                - State assumptions about voice, constraints, and required sources; ask for clarifications before drafting
                - Outline before drafting; sequence claims logically and ensure each claim traces to provided sources
                - Present alternatives (structures, framings, or thesis options) and note trade-offs in tone, length, or rigor
                - Balance viewpoints: present counterarguments fairly and resolve with evidence or rationale
                - Highlight uncertainties or gaps in provided citations; flag when additional sources are needed
                - Keep integrity rules enforced (no fabricated citations); reasoning supplements but never overrides them
                - Deliver concise, organized output and annotate where user decisions are needed
                """)
                if is_reasoning_block_enabled()
                else ""
            ),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
            db=SqliteDb(db_file=get_db_path("research_writing")),
            pre_hooks=[self._audit_pre_hook],
            post_hooks=[self._audit_post_hook],
        )

    def run_with_grounding_check(self, query: str, **kwargs) -> Any:
        """Execute the agent with citation fabrication prevention."""
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
                self.audit_logger.log_error(
                    error_type="CitationFabricationBlocked",
                    error_message=str(validation_error),
                    stack_trace=traceback.format_exc()
                )

            return {
                "content": (
                    "CITATION SAFETY SYSTEM ACTIVATED\n\n"
                    f"{str(validation_error)}\n\n"
                    "I am a writing assistant without access to research databases.\n"
                    "For citations, please use:\n"
                    "- Medical Research Agent (PubMed)\n"
                    "- Nursing Research Agent (PubMed + more)\n"
                    "- Academic Research Agent (Arxiv)"
                ),
                "validation_passed": False
            }

        except Exception as e:
            if self.audit_logger:
                self.audit_logger.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=traceback.format_exc()
                )
            raise

    def _validate_run_output(self, run_output: Any) -> bool:
        """
        Ensure no hallucinated citations are present.

        ALLOWS citations if they were provided in the input prompt.
        BLOCKS if new PMIDs/DOIs are fabricated (this agent has no search tools).
        """
        import re

        content = str(run_output.content) if hasattr(run_output, 'content') else str(run_output)

        # Get the input messages to extract provided citations
        input_citations = set()
        if hasattr(run_output, 'messages') and run_output.messages:
            for msg in run_output.messages:
                msg_content = str(msg.content) if hasattr(msg, 'content') else str(msg)
                # Extract PMIDs from input
                input_pmids = re.findall(r"PMID:?\s*(\d+)", msg_content, re.IGNORECASE)
                input_pmids.extend(re.findall(r'\[(\d{7,8})\]\(https?://pubmed', msg_content))
                input_pmids.extend(re.findall(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d{7,8})', msg_content))
                input_citations.update(input_pmids)
                # Extract DOIs from input
                input_dois = re.findall(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", msg_content, re.IGNORECASE)
                input_citations.update(input_dois)

        # Extract citations from output
        output_pmids = re.findall(r"PMID:?\s*(\d+)", content, re.IGNORECASE)
        output_pmids.extend(re.findall(r'\[(\d{7,8})\]\(https?://pubmed', content))
        output_pmids.extend(re.findall(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d{7,8})', content))
        output_dois = re.findall(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", content, re.IGNORECASE)

        # Check for fabricated citations (in output but NOT in input)
        output_citations = set(output_pmids) | set(output_dois)
        fabricated = output_citations - input_citations

        if fabricated:
            if self.audit_logger:
                self.audit_logger.log_validation_check(
                    "no_citations_check",
                    False,
                    {
                        "fabricated_citations": list(fabricated),
                        "input_citations": list(input_citations),
                        "output_citations": list(output_citations),
                        "reason": "Agent fabricated citations not in input"
                    }
                )

            raise ValueError(
                f"CITATION FABRICATION BLOCKED\n"
                f"This agent has no search tools and cannot generate new citations.\n"
                f"Fabricated citations: {list(fabricated)}\n"
                f"Allowed citations from input: {list(input_citations)}\n"
                f"Use Medical Research Agent or Nursing Research Agent for new citations."
            )

        if self.audit_logger:
            self.audit_logger.log_validation_check(
                "no_citations_check",
                True,
                {"citations_used": list(output_citations), "from_input": True}
            )

        return True

    def show_usage_examples(self) -> None:
        """Display usage examples for the Research Writing Agent."""
        print("\n✍️ Research Writing & Planning Agent Ready!")
        print("\nSpecialized for academic writing and research organization")
        print("\nExample queries:")
        print("-" * 60)

        print("\n1. PICOT Development:")
        print('   response = research_writing_agent.run("""')
        print('   Help me write a PICOT question about reducing')
        print('   catheter-associated infections in ICU patients""")')

        print("\n2. Literature Review:")
        print('   response = research_writing_agent.run("""')
        print('   I have 3 articles about fall prevention. Help me')
        print('   synthesize their findings into a cohesive literature')
        print('   review section""")')

        print("\n3. Intervention Planning:")
        print('   response = research_writing_agent.run("""')
        print('   Help me write a step-by-step intervention plan')
        print('   for implementing a fall prevention program""")')

        print("\n4. Poster Section Writing:")
        print('   response = research_writing_agent.run("""')
        print('   Write a background/problem statement for my')
        print('   poster about pressure ulcer prevention""")')

        print("\n5. Data Collection Plan:")
        print('   response = research_writing_agent.run("""')
        print('   What data should I collect before and after my')
        print('   intervention? How should I measure success?""")')

        print("\n6. Methodology Help:")
        print('   response = research_writing_agent.run("""')
        print('   What research design should I use for a quality')
        print('   improvement project on medication errors?""")')

        print("\n7. Writing Review:")
        print('   response = research_writing_agent.run("""')
        print('   Review this paragraph and suggest improvements:')
        print('   [paste your writing]""")')

        print("\n8. With Streaming:")
        print('   research_writing_agent.print_response("""')
        print('   Help me write an abstract for my fall prevention study""",')
        print('   stream=True)')

        print("\n" + "-" * 60)
        print("\n💡 TIP: This agent remembers your conversation!")
        print("Build your project iteratively - start with PICOT,")
        print("then literature review, then intervention, etc.")
        print("Use stream=True for real-time response generation.")


# Create global instance for backward compatibility
# Wrapped in try/except for graceful degradation if initialization fails
try:
    _research_writing_agent_instance = ResearchWritingAgent()
    research_writing_agent = _research_writing_agent_instance.agent
except Exception as _init_error:
    import logging
    logging.error(f"Failed to initialize ResearchWritingAgent: {_init_error}")
    _research_writing_agent_instance = None
    research_writing_agent = None
    # Re-raise only if running as main module
    if __name__ == "__main__":
        raise


def get_research_writing_agent():
    """Factory function to get the ResearchWritingAgent instance.

    Returns:
        ResearchWritingAgent wrapper instance, or None if initialization failed.
    """
    return _research_writing_agent_instance


if __name__ == "__main__":
    if _research_writing_agent_instance is not None:
        _research_writing_agent_instance.run_with_error_handling()
    else:
        print("❌ Agent failed to initialize. Check logs for details.")
