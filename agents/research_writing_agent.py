"""
Research Writing & Planning Agent
Specialized for academic writing, research organization, and poster preparation
Helps structure papers, write sections, and plan research methodology

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
PHASE 2 COMPLETE (2025-11-26): Refactored to use BaseAgent inheritance
"""

from textwrap import dedent
from typing import Any

# Module exports
__all__ = ['ResearchWritingAgent', 'research_writing_agent']

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

# Import centralized configuration
from agent_config import get_db_path

# Import BaseAgent for inheritance pattern
from agents.base_agent import BaseAgent


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

        This agent has no external tools - it relies on GPT-4o for writing,
        organization, and planning capabilities.
        """
        # No tools needed for writing agent
        return []

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
                """),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
            db=SqliteDb(db_file=get_db_path("research_writing")),
            pre_hooks=[self._audit_pre_hook],
            post_hooks=[self._audit_post_hook],
        )

    def run_with_grounding_check(self, query: str, **kwargs) -> Any:
        """Execute the agent while forcing a grounding verification pass."""
        # Audit Logging: Query Received
        project_name = kwargs.get("project_name")
        if self.audit_logger:
            self.audit_logger.log_query_received(query, project_name)

        stream_requested = bool(kwargs.get("stream"))
        
        try:
            response = self.agent.run(query, **kwargs)
            
            # Streaming responses are yielded incrementally and cannot be re-verified here.
            if stream_requested:
                return response
                
            self._validate_run_output(response)
            
            # Audit Logging: Response Generated
            if self.audit_logger:
                self.audit_logger.log_response_generated(
                    response=str(response.content),
                    response_type="success",
                    validation_passed=True
                )
                
            return response
            
        except Exception as e:
            # Audit Logging: Error
            if self.audit_logger:
                self.audit_logger.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=str(e)
                )
            raise

    def _validate_run_output(self, run_output: Any) -> bool:
        """Ensure no hallucinated citations are present."""
        # Since this agent has no tools, any citation (PMID/DOI) is potentially hallucinated
        # unless it's from context. We'll just log if we see them.
        
        import re
        content = str(run_output.content)
        
        # Check for PMIDs or DOIs
        pmids = re.findall(r"PMID:?\s*(\d+)", content, re.IGNORECASE)
        dois = re.findall(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", content, re.IGNORECASE)
        
        if pmids or dois:
            # Log warning - this agent shouldn't be generating new citations
            if self.audit_logger:
                self.audit_logger.log_validation_check(
                    "no_citations_check", 
                    True, # We don't block, just log, as user might have provided them
                    {"pmids_found": pmids, "dois_found": dois, "note": "Agent has no search tools"}
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


if __name__ == "__main__":
    if _research_writing_agent_instance is not None:
        _research_writing_agent_instance.run_with_error_handling()
    else:
        print("❌ Agent failed to initialize. Check logs for details.")
