"""
Nursing Research Agent - Specialized for Healthcare Improvement Projects
Focused on PICOT development, literature review, evidence-based practice

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
CRITICAL SECURITY FIX: Moved API keys to environment variables
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
WEEK 1 REFACTORING (2025-11-22): Added circuit breaker protection and resilience
FOCUS AREA 2 (2025-11-22): Refactored to use BaseAgent inheritance
  - Eliminates ~25 lines of duplicated code
  - Common setup handled by base class
"""

import os
import sys
from datetime import datetime
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIChat

# FOCUS AREA 2: Use BaseAgent class instead of utility functions
from base_agent import BaseAgent

# WEEK 1 REFACTORING: Import resilience infrastructure
# Add parent directory to path to import src modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.services.api_tools import (
    create_exa_tools_safe,
    create_serp_tools_safe,
    build_tools_list,
    get_api_status
)

class NursingResearchAgent(BaseAgent):
    """Nursing Research Agent using BaseAgent inheritance."""

    def __init__(self):
        # FOCUS AREA 2: Call parent constructor with agent name and config key
        super().__init__("Nursing Research Agent", "nursing_research")

        # WEEK 1 REFACTORING: Create tools with resilience (moved to __init__)
        # Tools are created safely with fallback behavior if API keys missing
        self.exa_tool = create_exa_tools_safe(required=False)
        self.serp_tool = create_serp_tools_safe(required=False)

        # Build tools list, filtering out None values
        self.available_tools = build_tools_list(self.exa_tool, self.serp_tool)

        # Log tool availability
        if self.exa_tool:
            self.logger.info("✅ Exa search available")
        else:
            self.logger.warning("⚠️  Exa search unavailable (EXA_API_KEY not set)")

        if self.serp_tool:
            self.logger.info("✅ SerpAPI search available")
        else:
            self.logger.warning("⚠️  SerpAPI search unavailable (SERP_API_KEY not set)")

        if not self.available_tools:
            self.logger.error("❌ No search tools available! Agent will have limited functionality.")

    def _create_agent(self) -> Agent:
        return Agent(
            name="Nursing Research Agent",
            role="Healthcare improvement project research specialist",
            model=OpenAIChat(id="gpt-4o"),
            tools=self.available_tools,  # Use safely-created tools
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
            db=self.db,  # Use database from base class
        )

    def show_usage_examples(self):
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
        if not self.available_tools:
            print("\n⚠️  WARNING: No search tools configured!")
            print("   Agent can still help with PICOT development and guidance,")
            print("   but cannot perform literature or web searches.")
            print("\n   To enable full functionality:")
            print('   export EXA_API_KEY="your-exa-key"')
            print('   export SERP_API_KEY="your-serp-key"')
            print()
        elif len(self.available_tools) < 2:
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
        print('   response = agent.run("""')
        print('   Help me develop a PICOT question for reducing patient falls')
        print('   in a medical-surgical unit""")')

        print("\n2. Literature Search:")
        print('   response = agent.run("""')
        print('   Find 3 recent research articles about catheter-associated')
        print('   urinary tract infection prevention""")')

        print("\n3. Standards Research:")
        print('   response = agent.run("""')
        print('   What are the Joint Commission requirements for medication')
        print('   reconciliation?""")')

        print("\n4. With Streaming (real-time responses):")
        print('   agent.print_response("""')
        print('   Find 3 recent studies on fall prevention""", stream=True)')

        print("\n" + "-" * 60)
        print("\n💡 TIP: Use stream=True for real-time response generation")


# Create module-level instance for backwards compatibility
nursing_research_agent = None

def get_agent():
    """Get or create the nursing research agent instance."""
    global nursing_research_agent
    if nursing_research_agent is None:
        agent_instance = NursingResearchAgent()
        nursing_research_agent = agent_instance.agent
    return nursing_research_agent


if __name__ == "__main__":
    # Create agent instance and run with error handling
    agent_instance = NursingResearchAgent()
    agent_instance.run_with_error_handling(agent_instance.show_usage_examples)
