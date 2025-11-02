"""
Nursing Research Agent - Specialized for Healthcare Improvement Projects
Focused on PICOT development, literature review, evidence-based practice
"""

from datetime import datetime
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from agno.tools.serpapi import SerpApiTools

# ************* Nursing Research Agent *************
nursing_research_agent = Agent(
    name="Nursing Research Agent",
    role="Healthcare improvement project research specialist",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        # Exa for recent healthcare articles and research
        ExaTools(
            api_key="f786797a-3063-4869-ab3f-bb95b282f8ab",
            start_published_date="2020-01-01",  # Last 5 years of research
            type="neural",  # Better for academic/clinical content
        ),
        # SerpAPI for general healthcare standards and guidelines
        SerpApiTools(
            api_key="cf91e3f9c1ba39340e3b4dc3a905215d78790c2f9004520209b35878921f8a7b"
        ),
    ],
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
    db=SqliteDb(db_file="tmp/nursing_research_agent.db"),
)

# ************* Usage Examples *************
if __name__ == "__main__":
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
    print('   response = nursing_research_agent.run("""')
    print('   Help me develop a PICOT question for reducing patient falls')
    print('   in a medical-surgical unit""")')
    
    print("\n2. Literature Search:")
    print('   response = nursing_research_agent.run("""')
    print('   Find 3 recent research articles about catheter-associated')
    print('   urinary tract infection prevention""")')
    
    print("\n3. Standards Research:")
    print('   response = nursing_research_agent.run("""')
    print('   What are the Joint Commission requirements for medication')
    print('   reconciliation?""")')
    
    print("\n" + "-" * 60)

