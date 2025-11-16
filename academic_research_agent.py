"""
Academic Research Agent - Arxiv Database Access
Specialized for academic papers across all scientific fields
Great for finding theoretical research and cutting-edge studies

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
"""

import logging
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.arxiv import ArxivTools

# PHASE 1: Import centralized configuration
from agent_config import get_db_path

# PHASE 1: Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ************* Academic Research Agent (Arxiv) *************
academic_research_agent = Agent(
    name="Academic Research Agent",
    role="Search Arxiv for academic research papers",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        ArxivTools(
            enable_search_arxiv=True,  # Search academic papers
        )
    ],
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
    # PHASE 1: Database path using centralized config
    # OLD (commented for reference): db=SqliteDb(db_file="tmp/academic_research_agent.db")
    db=SqliteDb(db_file=get_db_path("academic_research")),
)

logger.info(f"Academic Research Agent initialized: {get_db_path('academic_research')}")

# ************* Usage Examples *************
if __name__ == "__main__":
    # PHASE 1: Add error handling for agent execution
    try:
        logger.info("Starting Academic Research Agent")

        print("📚 Academic Research Agent (Arxiv) Ready!")
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

        print("\n" + "-" * 60)
        print("\n💡 TIP: Arxiv is great for theoretical and methodological research!")
        print("Use it when you need advanced analysis techniques.")

        logger.info("Academic Research Agent ready")

    except KeyboardInterrupt:
        logger.info("Agent interrupted by user")
        print("\n\nInterrupted by user. Goodbye!")

    except Exception as e:
        logger.error(f"Agent execution failed: {type(e).__name__}: {str(e)}", exc_info=True)
        print(f"\n❌ Error: An unexpected error occurred.")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nPlease check the logs for details or contact support.")
        raise  # Re-raise to preserve stack trace for debugging

