"""
All Agents Interactive Runner
Choose which agent to use for your research
"""

from my_research_agent import research_agent
from my_serp_agent import serp_agent
from my_multi_search_agent import multi_search_agent

def main():
    print("=" * 80)
    print("🤖 Research Agent System")
    print("=" * 80)
    print("\nAvailable Agents:")
    print("\n1. Research Agent (Exa)")
    print("   - Best for: Recent articles, keyword search")
    print("   - Cost: ~$0.02-0.05 per query")
    
    print("\n2. Google Search Agent (SerpAPI)")
    print("   - Best for: General search, Google results, knowledge panels")
    print("   - Cost: ~$0.02-0.05 per query")
    
    print("\n3. Multi-Search Agent (Exa + SerpAPI)")
    print("   - Best for: Comprehensive research, cross-referenced results")
    print("   - Cost: ~$0.03-0.08 per query (uses both)")
    
    print("\n" + "=" * 80)
    
    # Choose agent
    while True:
        choice = input("\nChoose agent (1/2/3) or 'exit': ").strip()
        
        if choice.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye!")
            return
        
        if choice == '1':
            agent = research_agent
            agent_name = "Research Agent (Exa)"
            break
        elif choice == '2':
            agent = serp_agent
            agent_name = "Google Search Agent (SerpAPI)"
            break
        elif choice == '3':
            agent = multi_search_agent
            agent_name = "Multi-Search Agent"
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    # Interactive chat with chosen agent
    print(f"\n✅ Using: {agent_name}")
    print("\nType your questions below. Type 'exit' to quit or 'switch' to change agent.")
    print("-" * 80)
    
    while True:
        try:
            query = input("\n📝 Your question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == 'switch':
                print("\n🔄 Switching agents...")
                main()
                return
            
            print(f"\n🔍 {agent_name} is researching...\n")
            
            # Run with streaming
            agent.print_response(query, stream=True)
            
            print("\n" + "-" * 80)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure OPENAI_API_KEY is set in your environment")
            break

if __name__ == "__main__":
    main()

