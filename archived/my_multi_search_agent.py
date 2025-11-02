"""
Multi-Search Research Agent
Combines both Exa and SerpAPI for comprehensive research
Uses the best tool for each situation
"""

from datetime import datetime
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools
from agno.tools.serpapi import SerpApiTools

# ************* Create Multi-Search Agent *************
multi_search_agent = Agent(
    name="Multi-Search Research Agent",
    role="Comprehensive research using multiple search engines",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        # Exa - Great for recent articles and content discovery
        ExaTools(
            api_key="f786797a-3063-4869-ab3f-bb95b282f8ab",
            start_published_date=datetime.now().strftime("%Y-%m-%d"),
            type="keyword",
        ),
        # SerpAPI - Great for Google results, featured snippets, knowledge panels
        SerpApiTools(
            api_key="cf91e3f9c1ba39340e3b4dc3a905215d78790c2f9004520209b35878921f8a7b"
        ),
    ],
    description=dedent("""\
        You are an Elite Research Agent with access to multiple search engines.
        You combine Exa (for recent articles) and Google/SerpAPI (for comprehensive results)
        to provide the most accurate and complete research possible.
        """),
    instructions=dedent("""\
        1. Analyze the user's query to determine the best search strategy:
           - Use Exa for: Recent news, specific articles, content from today
           - Use SerpAPI for: General info, definitions, historical data, broad topics
           - Use BOTH when comprehensive research is needed
        
        2. Search Strategy:
           - For breaking news → Use Exa (recent articles only)
           - For definitions/facts → Use SerpAPI (Google knowledge panels)
           - For comprehensive research → Use both and cross-reference
        
        3. Synthesize results:
           - Compare information from both sources
           - Highlight agreements and differences
           - Prioritize the most recent and credible information
        
        4. Always cite sources with links
        5. Mention which search engine provided which information
        6. If results conflict, note the discrepancy
        """),
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    markdown=True,
    db=SqliteDb(db_file="tmp/multi_search_agent.db"),
)

# ************* Usage Examples *************
if __name__ == "__main__":
    print("🚀 Multi-Search Research Agent Ready!")
    print("\nThis agent intelligently uses both Exa and SerpAPI for best results.")
    print("\nCapabilities:")
    print("  ✓ Recent news and articles (Exa)")
    print("  ✓ Google search results (SerpAPI)")
    print("  ✓ Featured snippets and knowledge panels")
    print("  ✓ Cross-referenced information")
    print("\nExample usage:")
    print("-" * 60)
    
    print("\n1. Comprehensive research:")
    print('   response = multi_search_agent.run("What is quantum computing?")')
    print("   # Uses SerpAPI for definition, Exa for recent articles")
    
    print("\n2. Breaking news:")
    print('   response = multi_search_agent.run("Latest developments in AI today")')
    print("   # Prioritizes Exa for recent content")
    
    print("\n3. With streaming:")
    print('   multi_search_agent.print_response("Your query", stream=True)')
    
    print("\n" + "-" * 60)
    print("\n⚠️  NOTE: Uses both Exa and SerpAPI credits!")
    print("The agent decides which tool(s) to use based on your query.")

