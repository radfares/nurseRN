"""
Research Writing & Planning Agent
Specialized for academic writing, research organization, and poster preparation
Helps structure papers, write sections, and plan research methodology

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
"""

import logging
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

# PHASE 1: Import centralized configuration
from agent_config import get_db_path

# PHASE 1: Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ************* Research Writing & Planning Agent *************
research_writing_agent = Agent(
    name="Research Writing Agent",
    role="Academic writing and research planning specialist",
    model=OpenAIChat(id="gpt-4o"),  # Best model for writing quality
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
    # PHASE 1: Database path using centralized config
    # OLD (commented for reference): db=SqliteDb(db_file="tmp/research_writing_agent.db")
    db=SqliteDb(db_file=get_db_path("research_writing")),
)

logger.info(f"Research Writing Agent initialized: {get_db_path('research_writing')}")

# ************* Usage Examples *************
if __name__ == "__main__":
    # PHASE 1: Add error handling for agent execution
    try:
        logger.info("Starting Research Writing Agent")

        print("✍️ Research Writing & Planning Agent Ready!")
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

        print("\n" + "-" * 60)
        print("\n💡 TIP: This agent remembers your conversation!")
        print("Build your project iteratively - start with PICOT,")
        print("then literature review, then intervention, etc.")

        logger.info("Research Writing Agent ready")

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

