"""
Nursing Research Project Assistant
Complete system for healthcare improvement project support
"""

from nursing_research_agent import nursing_research_agent
from nursing_project_timeline_agent import project_timeline_agent
from medical_research_agent import medical_research_agent
from academic_research_agent import academic_research_agent
from research_writing_agent import research_writing_agent

def main():
    print("=" * 80)
    print("🏥 Nursing Research Project Assistant")
    print("=" * 80)
    print("\nProject: Healthcare Improvement (Nov 2025 - June 2026)")
    print("\nAvailable Assistants:")
    print("\n1. Research Agent (Exa + SerpAPI)")
    print("   - PICOT question development")
    print("   - Web searches and recent articles")
    print("   - Healthcare standards (Joint Commission, Patient Safety)")
    print("   - Evidence-based practice guidelines")
    print("   - Best for: General research, standards, web information")
    
    print("\n2. Timeline Assistant")
    print("   - Monthly milestone tracking")
    print("   - Deliverable reminders")
    print("   - Next steps guidance")
    print("   - Project planning help")
    print("   - Best for: Staying on track, what's due, project planning")
    
    print("\n3. Medical Research Agent (PubMed) 🆕")
    print("   - Search PubMed database (millions of medical articles)")
    print("   - Peer-reviewed clinical studies")
    print("   - Nursing research and systematic reviews")
    print("   - Evidence-based medical literature")
    print("   - Best for: Finding your 3 required research articles!")
    
    print("\n4. Academic Research Agent (Arxiv) 🆕")
    print("   - Search Arxiv database (academic papers)")
    print("   - Statistical methods and data analysis")
    print("   - Research methodologies")
    print("   - Theoretical frameworks")
    print("   - Best for: Advanced methods, analysis techniques")
    
    print("\n5. Research Writing Agent 🆕")
    print("   - PICOT question writing and refinement")
    print("   - Literature review synthesis")
    print("   - Intervention planning (step-by-step)")
    print("   - Poster content writing")
    print("   - Data collection planning")
    print("   - Academic writing help")
    print("   - Best for: Writing, organizing, structuring your project!")
    
    print("\n" + "=" * 80)
    
    # Choose agent
    while True:
        choice = input("\nChoose assistant (1/2/3/4/5) or 'exit': ").strip()
        
        if choice.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye! Good luck with your project!")
            return
        
        if choice == '1':
            agent = nursing_research_agent
            agent_name = "Research Agent (Exa + SerpAPI)"
            print("\n💡 TIP: Ask about PICOT questions, standards, or general research")
            break
        elif choice == '2':
            agent = project_timeline_agent
            agent_name = "Timeline Assistant"
            print("\n💡 TIP: Ask 'What do I need to do this month?' or 'What's next?'")
            break
        elif choice == '3':
            agent = medical_research_agent
            agent_name = "Medical Research Agent (PubMed)"
            print("\n💡 TIP: Ask 'Find peer-reviewed studies about [your topic]'")
            break
        elif choice == '4':
            agent = academic_research_agent
            agent_name = "Academic Research Agent (Arxiv)"
            print("\n💡 TIP: Ask about research methods, statistics, or theoretical papers")
            break
        elif choice == '5':
            agent = research_writing_agent
            agent_name = "Research Writing Agent"
            print("\n💡 TIP: Ask 'Help me write...' or 'How do I structure...'")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
    
    # Interactive chat
    print(f"\n✅ Using: {agent_name}")
    print("\nType your questions below.")
    print("Type 'exit' to quit or 'switch' to change assistant.")
    print("-" * 80)
    
    while True:
        try:
            query = input("\n📝 Your question: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye! Good luck with your project!")
                break
            
            if query.lower() == 'switch':
                print("\n🔄 Switching assistants...")
                main()
                return
            
            print(f"\n💭 {agent_name} is thinking...\n")
            
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
    print("\n🎓 Welcome to your Nursing Research Project Assistant!")
    print("\nThis system will help you through your improvement project from")
    print("November 2025 to June 2026, including:")
    print("  ✓ PICOT development")
    print("  ✓ Literature searches")
    print("  ✓ Timeline tracking")
    print("  ✓ Milestone guidance")
    print("\n" + "=" * 80 + "\n")
    
    main()

