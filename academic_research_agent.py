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
    create_arxiv_tools_safe,
    build_tools_list,
    get_api_status
)


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
        """Create Arxiv tools with safe fallback."""
        # Arxiv is free and doesn't require authentication
        arxiv_tool = create_arxiv_tools_safe(required=False)

        # Build tools list, filtering out None values
        tools = build_tools_list(arxiv_tool)

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
            model=OpenAIChat(id="gpt-4o"),
            tools=self.tools,
            description=dedent("""\
                You are an Academic Research Specialist with access to Arxiv,
                a repository of academic papers across science, mathematics, computer science,
                and quantitative fields. You help find cutting-edge research, theoretical
                studies, and interdisciplinary papers.
                """),
            instructions=dedent("""\
                EXPERTISE: Arxiv Academic Paper Search

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
                """),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
            db=SqliteDb(db_file=get_db_path("academic_research")),
        )

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


if __name__ == "__main__":
    _academic_research_agent_instance.run_with_error_handling()
