"""
Research Agent - Optimized for Cost and Performance
Uses OpenAI GPT-4o + Exa for web search
"""

from datetime import datetime
from textwrap import dedent

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat
from agno.tools.exa import ExaTools

# ************* Create Research Agent *************
research_agent = Agent(
    name="Research Agent",
    role="Assist with research and information synthesis",
    model=OpenAIChat(id="gpt-4o"),  # Using your OpenAI credits
    tools=[
        ExaTools(
            api_key="f786797a-3063-4869-ab3f-bb95b282f8ab",  # Your Exa API key
            start_published_date=datetime.now().strftime("%Y-%m-%d"),  # Only recent articles
            type="keyword",
        )
    ],
    description=dedent("""\
        You are the Research Agent — a research assistant that helps users explore any topic.
        You can search for up-to-date information, summarize key findings, and explain concepts clearly and accurately.
        """),
    instructions=dedent("""\
        1. Understand the user's query and identify the main research goal.
        2. Use ExaTools to run up to three targeted searches for relevant, recent information.
        3. Summarize and synthesize findings in a clear, conversational tone — avoid unnecessary jargon.
        4. Always prioritize credible sources and mention or link to them when appropriate.
        5. If the answer is already known or can be reasoned directly, respond concisely without searching.
        """),
    add_history_to_context=True,
    add_datetime_to_context=True,
    enable_agentic_memory=True,
    markdown=True,
    # Using SQLite for easy setup (no PostgreSQL needed)
    db=SqliteDb(db_file="tmp/research_agent.db"),
)

# ************* Usage Examples *************
if __name__ == "__main__":
    print("🔬 Research Agent Ready!")
    print("\nExample usage:")
    print("-" * 60)
    
    # Example 1: Simple query
    print("\n1. Basic research query:")
    print('   response = research_agent.run("What are the latest developments in AI?")')
    
    # Example 2: Interactive mode
    print("\n2. Interactive mode:")
    print("   while True:")
    print('       query = input("Ask me anything: ")')
    print('       if query.lower() == "exit": break')
    print("       response = research_agent.run(query)")
    print("       print(response.content)")
    
    # Example 3: With streaming
    print("\n3. With streaming (shows response as it generates):")
    print('   research_agent.print_response("Your query", stream=True)')
    
    print("\n" + "-" * 60)
    print("\n⚠️  NOTE: This will use your OpenAI and Exa API credits!")
    print("To run, import this file or add your code below.")

