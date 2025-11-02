"""
SerpAPI Research Agent - Google Search Powered
Uses OpenAI GPT-4o + SerpAPI for comprehensive Google search results
"""

from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.serpapi import SerpApiTools

# ************* Create SerpAPI Research Agent *************
serp_agent = Agent(
    name="Google Search Agent",
    role="Search Google and provide comprehensive research with rich results",
    model=OpenAIChat(id="gpt-4o"),
    tools=[
        SerpApiTools(
            api_key="cf91e3f9c1ba39340e3b4dc3a905215d78790c2f9004520209b35878921f8a7b"
        )
    ],
    description=dedent("""\
        You are a Google Search Expert — you can search Google and provide detailed results
        including snippets, related questions, images, and more. You excel at finding 
        comprehensive, accurate information from the world's most popular search engine.
        """),
    instructions=dedent("""\
        1. Use SerpAPI to search Google for the user's query
        2. Analyze search results including:
           - Top organic results and their snippets
           - Featured snippets and knowledge panels
           - People Also Ask questions
           - Related searches
        3. Synthesize information from multiple sources
        4. Always cite sources with links
        5. Highlight the most relevant and credible information
        6. If the query needs current data, mention the search date
        """),
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    markdown=True,
    db=SqliteDb(db_file="tmp/serp_agent.db"),
)

# ************* Usage Examples *************
if __name__ == "__main__":
    print("🔍 Google Search Agent Ready!")
    print("\nThis agent uses SerpAPI to search Google and provide comprehensive results.")
    print("\nExample usage:")
    print("-" * 60)
    
    print("\n1. Basic Google search:")
    print('   response = serp_agent.run("Latest news about SpaceX")')
    
    print("\n2. With streaming:")
    print('   serp_agent.print_response("Your query", stream=True)')
    
    print("\n" + "-" * 60)
    print("\n⚠️  NOTE: This will use your OpenAI and SerpAPI credits!")

