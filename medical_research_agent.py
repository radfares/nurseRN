"""
Medical Research Agent - PubMed Database Access
Specialized for searching biomedical and nursing literature
Perfect for finding peer-reviewed clinical studies
"""

from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.pubmed import PubmedTools

# ************* Medical Research Agent (PubMed) *************
medical_research_agent = Agent(
    name="Medical Research Agent",
    role="Search PubMed for biomedical and nursing research",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        PubmedTools(
            enable_search_pubmed=True,  # Search medical literature
        )
    ],
    description=dedent("""\
        You are a Medical Literature Search Specialist with access to PubMed,
        the premier database for biomedical and healthcare research. You help
        find peer-reviewed studies, clinical trials, systematic reviews, and
        nursing research articles.
        """),
    instructions=dedent("""\
        EXPERTISE: PubMed Medical Literature Search
        
        SEARCH STRATEGY:
        1. Use specific medical terminology and MeSH terms when possible
        2. Focus on peer-reviewed, evidence-based research
        3. Prioritize recent publications (last 5-10 years) unless specified
        4. Look for systematic reviews and meta-analyses when available
        5. Include clinical trials and observational studies
        
        SEARCH TYPES:
        - Clinical studies and trials
        - Systematic reviews and meta-analyses
        - Nursing research and quality improvement
        - Evidence-based practice guidelines
        - Case studies and cohort studies
        
        RESPONSE FORMAT:
        For each article found:
        - Title and authors
        - Publication year and journal
        - PubMed ID (PMID)
        - Abstract summary
        - Key findings relevant to the query
        - Study design and methodology
        - Clinical implications
        
        QUALITY INDICATORS:
        - Peer-reviewed journals
        - High-impact publications
        - Large sample sizes
        - Recent research (prefer last 5 years)
        - Relevant to clinical practice
        
        EXAMPLES OF GOOD SEARCHES:
        - "Fall prevention interventions elderly hospitalized patients"
        - "Catheter-associated urinary tract infection prevention"
        - "Pressure ulcer prevention protocols nursing homes"
        - "Medication reconciliation effectiveness"
        - "Patient safety culture healthcare"
        """),
    add_history_to_context=True,
    add_datetime_to_context=True,
    markdown=True,
    db=SqliteDb(db_file="tmp/medical_research_agent.db"),
)

# ************* Usage Examples *************
if __name__ == "__main__":
    print("🏥 Medical Research Agent (PubMed) Ready!")
    print("\nSpecialized for biomedical and nursing literature")
    print("\nExample queries:")
    print("-" * 60)
    
    print("\n1. Find clinical studies:")
    print('   response = medical_research_agent.run("""')
    print('   Find recent studies on fall prevention in elderly')
    print('   hospitalized patients""")')
    
    print("\n2. Search for specific conditions:")
    print('   response = medical_research_agent.run("""')
    print('   Find evidence-based interventions for catheter-associated')
    print('   urinary tract infections""")')
    
    print("\n3. Literature review:")
    print('   response = medical_research_agent.run("""')
    print('   Find 3 recent peer-reviewed articles about pressure')
    print('   ulcer prevention in critical care""")')
    
    print("\n" + "-" * 60)
    print("\n💡 TIP: PubMed has millions of biomedical articles!")
    print("Be specific about your topic for best results.")

