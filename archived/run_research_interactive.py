"""
Interactive Research Agent Runner
Run this to chat with your research agent
"""

from my_research_agent import research_agent

def main():
    print("=" * 80)
    print("🔬 Research Agent - Interactive Mode")
    print("=" * 80)
    print("\nI can search the web and provide well-researched answers!")
    print("Using: OpenAI GPT-4o + Exa Search")
    print("\nType 'exit' or 'quit' to stop.\n")
    print("-" * 80)
    
    while True:
        try:
            # Get user input
            query = input("\n📝 Your question: ").strip()
            
            if not query:
                continue
                
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            print("\n🔍 Researching...\n")
            
            # Run the agent with streaming for real-time response
            research_agent.print_response(query, stream=True)
            
            print("\n" + "-" * 80)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure you have set:")
            print("  - OPENAI_API_KEY environment variable")
            print("  - Exa API key is in my_research_agent.py")
            break

if __name__ == "__main__":
    main()

