"""
Nursing Research Project Assistant
Complete system for healthcare improvement project support with project management.

UPDATED: 2025-11-23 - Added project-centric database architecture
"""

from dotenv import load_dotenv
# Ensure .env values override any existing shell values so the app uses the keys you set in .env
load_dotenv(override=True)

# Ensure vendored agno library is importable
import os
import sys
import time
from pathlib import Path
_project_root = Path(__file__).parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))

from project_manager import (
    get_project_manager,
    cli_create_project,
    cli_list_projects,
    cli_switch_project,
    cli_archive_project
)

# Agent imports from agents/ module
from agents.base_agent import BaseAgent
from agents.nursing_research_agent import nursing_research_agent
from agents.nursing_project_timeline_agent import project_timeline_agent
from agents.medical_research_agent import get_medical_research_agent
from agents.academic_research_agent import academic_research_agent
from agents.research_writing_agent import research_writing_agent
from agents.data_analysis_agent import data_analysis_agent
from agents.citation_validation_agent import get_citation_validation_agent

# Orchestration imports - NEW CONVERSATIONAL INTERFACE
from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator
from src.orchestration.conversation_context import ConversationContext
from src.orchestration.api_validators import InvalidAPIKeyError, validate_openai_key

# Legacy orchestration imports (kept for fallback)
from src.orchestration.context_manager import ContextManager
from src.orchestration.orchestrator import WorkflowOrchestrator
from src.orchestration.query_router import QueryRouter, Intent
from src.workflows.research_workflow import ResearchWorkflow
from src.workflows.parallel_search import ParallelSearchWorkflow
from src.workflows.timeline_planner import TimelinePlannerWorkflow
from src.workflows.validated_research_workflow import ValidatedResearchWorkflow
from src.workflows.registry import get_workflow


def show_welcome():
    """Display welcome message."""
    print("\n" + "=" * 80)
    print("🏥 NURSING RESEARCH ASSISTANT")
    print("=" * 80)
    print("\nI'll help you develop your healthcare improvement project from")
    print("PICOT to poster presentation.")
    print("\nJust tell me what you'd like to work on, and I'll handle the rest!")
    print("=" * 80)


def show_project_menu():
    """Display project management menu."""
    print("\n" + "="*80)
    print("PROJECT MANAGEMENT")
    print("="*80)

    pm = get_project_manager()
    active_project = pm.get_active_project()

    if active_project:
        print(f"\n★ ACTIVE PROJECT: {active_project}")
    else:
        print("\n⚠️  No active project selected")

    print("\nProject Commands:")
    print("  new <project_name>     - Create new project")
    print("  list                   - List all projects")
    print("  switch <project_name>  - Switch to project")
    print("  archive <project_name> - Archive project")
    print("  agents                 - Launch agents (requires active project)")
    print("  exit                   - Exit program")
    print("\n" + "="*80)


def project_management_loop():
    """Main project management loop."""
    while True:
        show_project_menu()

        command = input("\n📋 Command: ").strip().lower()

        if not command:
            continue

        # Parse command
        parts = command.split(maxsplit=1)
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else None

        if cmd in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye!")
            break

        elif cmd == 'new':
            if not arg:
                print("❌ Usage: new <project_name>")
                continue
            cli_create_project(arg, add_milestones=True)

        elif cmd == 'list':
            cli_list_projects()

        elif cmd == 'switch':
            if not arg:
                print("❌ Usage: switch <project_name>")
                continue
            cli_switch_project(arg)

        elif cmd == 'archive':
            if not arg:
                print("❌ Usage: archive <project_name>")
                continue
            confirm = input(f"⚠️  Archive '{arg}'? This will move it to archives. (yes/no): ")
            if confirm.lower() == 'yes':
                cli_archive_project(arg)
            else:
                print("❌ Cancelled")

        elif cmd == 'agents':
            # Check for active project
            pm = get_project_manager()
            active_project = pm.get_active_project()

            if not active_project:
                print("\n❌ No active project. Create or switch to a project first.")
                print("   Commands: 'new <name>' or 'switch <name>'")
                continue

            # Launch agent selector
            print(f"\n✅ Using project: {active_project}")
            agent_selection_loop()

        else:
            print(f"❌ Unknown command: {cmd}")
            print("   Valid commands: new, list, switch, archive, agents, exit")


def show_agent_menu():
    """Display agent selection menu."""
    print("\n" + "="*80)
    print("AGENT SELECTION")
    print("="*80)
    print("\nAvailable Agents:")

    print("\n1. Nursing Research Agent (Exa + SerpAPI)")
    print("   - PICOT question development")
    print("   - Web searches and recent articles")
    print("   - Healthcare standards (Joint Commission, Patient Safety)")
    print("   - Best for: General research, standards, guidelines")

    print("\n2. Medical Research Agent (PubMed)")
    print("   - Search PubMed database (millions of articles)")
    print("   - Peer-reviewed clinical studies")
    print("   - Nursing research and systematic reviews")
    print("   - Best for: Finding your 3 required research articles!")

    print("\n3. Academic Research Agent (ArXiv)")
    print("   - Academic papers and preprints")
    print("   - Statistical methods and data analysis")
    print("   - Research methodologies")
    print("   - Best for: Advanced methods, analysis techniques")

    print("\n4. Research Writing Agent")
    print("   - PICOT question writing and refinement")
    print("   - Literature review synthesis")
    print("   - Intervention planning")
    print("   - Poster content writing")
    print("   - Best for: Writing, organizing, structuring!")

    print("\n5. Project Timeline Agent")
    print("   - Monthly milestone tracking")
    print("   - Deliverable reminders")
    print("   - Next steps guidance")
    print("   - Best for: Staying on track, what's due")

    print("\n6. Data Analysis Planner")
    print("   - Sample size calculations")
    print("   - Statistical test selection")
    print("   - Data collection templates (CSV)")
    print("   - Results interpretation")
    print("   - Best for: Planning statistics, sample sizes!")

    print("\n7. Citation Validation Agent")
    print("   - Evidence level grading (Johns Hopkins I-VII)")
    print("   - Retraction detection via PubMed")
    print("   - Currency assessment (flags old articles)")
    print("   - Quality scoring and recommendations")
    print("   - Best for: Validating research quality!")

    print("\n8. Smart Mode (Auto-Routing) 🧠")
    print("   - Automatically routes your query to the best agent")
    print("   - Detects intent (Research, Search, Planning)")
    print("   - Best for: When you're not sure which agent to use")

    print("\n9. Workflow Mode (Templates) ⚡")
    print("   - Run pre-defined multi-step workflows")
    print("   - Validated Research (Search + Validate + Write) ⭐")
    print("   - Basic Research (PICOT -> Search -> Writing)")
    print("   - Parallel Search (Multiple databases)")
    print("   - Timeline Planner")
    print("   - Best for: Complex tasks requiring multiple steps")

    print("\n" + "="*80)
    print("\nCommands: 1-7 (select agent), 8 (smart mode), 9 (workflows), 'back', 'exit'")


def agent_selection_loop():
    """Agent selection and interaction loop."""
    while True:
        show_agent_menu()

        choice = input("\n🤖 Choose agent: ").strip().lower()

        if choice in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye!")
            exit(0)

        elif choice in ['back', 'b']:
            print("\n🔙 Returning to project management...")
            return

        # Agent selection
        agent_map = {
            '1': (nursing_research_agent, "Nursing Research Agent"),
            '2': (get_medical_research_agent(), "Medical Research Agent (PubMed)"),
            '3': (academic_research_agent, "Academic Research Agent (ArXiv)"),
            '4': (research_writing_agent, "Research Writing Agent"),
            '5': (project_timeline_agent, "Project Timeline Agent"),
            '6': (data_analysis_agent, "Data Analysis Planner"),
            '7': (get_citation_validation_agent(), "Citation Validation Agent")
        }

        # Handle new modes
        if choice == '8':
            run_smart_mode()
            continue
        elif choice == '9':
            run_workflow_mode()
            continue

        if choice not in agent_map:
            print(f"❌ Invalid choice: {choice}")
            continue

        agent, agent_name = agent_map[choice]

        # Get active project
        pm = get_project_manager()
        active_project = pm.get_active_project()
        project_db = pm.get_project_db_path()

        print(f"\n✅ Selected: {agent_name}")
        print(f"📁 Project: {active_project}")
        print(f"💾 Database: {project_db}")

        # Run agent interaction
        run_agent_interaction(agent, agent_name, active_project)


def run_agent_interaction(agent, agent_name: str, project_name: str):
    """
    Run interactive chat with agent.

    Args:
        agent: Agent instance
        agent_name: Display name
        project_name: Active project name
    """
    print(f"\n" + "="*80)
    print(f"CHAT WITH {agent_name.upper()}")
    print("="*80)
    print(f"\nProject: {project_name}")
    
    # Show agent-specific usage examples and capabilities
    if hasattr(agent, 'show_usage_examples'):
        try:
            agent.show_usage_examples()
        except Exception as e:
            print(f"⚠️  Could not show usage examples: {e}")

    print("\nTips:")
    print("  - Type your questions naturally")
    print("  - Type 'exit' to stop chatting")
    print("  - Type 'switch' to choose different agent")
    print("  - Type 'back' to return to project menu")
    print("\n" + "="*80)

    while True:
        try:
            query = input(f"\n💬 You: ").strip()

            if not query:
                continue

            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                exit(0)

            if query.lower() in ['back', 'b']:
                print("\n🔙 Returning to project menu...")
                return

            if query.lower() == 'switch':
                print("\n🔄 Switching agents...")
                return

            # Run agent
            print(f"\n🤖 {agent_name}: ", end="", flush=True)

            try:
                agent.print_response(query, stream=True)
            except Exception as e:
                print(f"\n❌ Agent error: {e}")
                print("\n💡 Make sure OPENAI_API_KEY is set in your environment")
                print("   and all required API keys are configured.")

            # Phase 1, Task 5 (2025-11-29): Print watermark after every agent response
            BaseAgent.print_watermark()

            print("\n" + "-"*80)

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted. Type 'exit' to quit or continue chatting.")
            continue

        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            break


def run_smart_mode():
    """
    Run Smart Mode (Auto-Routing).
    Uses QueryRouter to determine intent and route to appropriate agent.
    """
    print("\n" + "="*80)
    print("🧠 SMART MODE (AUTO-ROUTING)")
    print("="*80)
    
    pm = get_project_manager()
    active_project = pm.get_active_project()
    project_db = pm.get_project_db_path()
    
    if not active_project:
        print("\n❌ No active project. Please select a project first.")
        return

    print(f"\nActive Project: {active_project}")
    print("Type 'exit' to return to menu.")
    
    # Initialize orchestration
    context_manager = ContextManager(db_path=project_db)
    orchestrator = WorkflowOrchestrator(context_manager)
    router = QueryRouter()
    
    while True:
        query = input("\n🧠 How can I help you? ").strip()
        
        if not query:
            continue
            
        if query.lower() in ['exit', 'quit', 'q', 'back']:
            print("\n🔙 Returning to menu...")
            break
            
        print("\n🤔 Analyzing intent...", end="", flush=True)
        
        # Route query
        intent, confidence, entities = router.route_query(query)
        print(f"\n👉 Detected intent: {intent.value} (Confidence: {confidence:.2f})")
        
        # Map intent to agent
        intent_agent_map = {
            Intent.PICOT: "nursing_research_agent",
            Intent.SEARCH: "medical_research_agent",
            Intent.TIMELINE: "project_timeline_agent",
            Intent.DATA_ANALYSIS: "data_analysis_agent",
            Intent.WRITING: "research_writing_agent",
            Intent.UNKNOWN: "nursing_research_agent"
        }
        
        suggested_agent = intent_agent_map.get(intent, "nursing_research_agent")
        print(f"👉 Routing to: {suggested_agent}")
        
        # Map router agent names to actual agents
        agent_map = {
            "nursing_research_agent": nursing_research_agent,
            "medical_research_agent": get_medical_research_agent(),
            "academic_research_agent": academic_research_agent,
            "research_writing_agent": research_writing_agent,
            "project_timeline_agent": project_timeline_agent,
            "data_analysis_agent": data_analysis_agent
        }
        
        target_agent = agent_map.get(suggested_agent)
        
        if target_agent:
            print(f"\n🤖 {suggested_agent}: ", end="", flush=True)
            try:
                # Execute via orchestrator for consistent logging/result handling
                result = orchestrator.execute_single_agent(
                    agent=target_agent,
                    query=query,
                    workflow_id=f"smart_mode_{int(time.time())}"
                )
                
                if result.success:
                    print(result.content)
                else:
                    print(f"\n❌ Execution failed: {result.error}")
                    
                BaseAgent.print_watermark()
                print("\n" + "-"*80)
                
            except Exception as e:
                print(f"\n❌ Error: {e}")
        else:
            print(f"\n❌ Could not find agent: {route.suggested_agent}")


def run_workflow_mode():
    """
    Run Workflow Mode (Templates).
    Select and execute pre-defined workflows.
    """
    print("\n" + "="*80)
    print("⚡ WORKFLOW MODE (TEMPLATES)")
    print("="*80)
    
    pm = get_project_manager()
    active_project = pm.get_active_project()
    project_db = pm.get_project_db_path()
    
    if not active_project:
        print("\n❌ No active project. Please select a project first.")
        return

    # Initialize orchestration
    context_manager = ContextManager(db_path=project_db)
    orchestrator = WorkflowOrchestrator(context_manager)
    
    workflows = {}
    workflow_specs = {
        "1": ("validated_research", ValidatedResearchWorkflow),
        "2": ("research", ResearchWorkflow),
        "3": ("parallel_search", ParallelSearchWorkflow),
        "4": ("timeline_planner", TimelinePlannerWorkflow),
    }
    for menu_key, (registry_key, fallback_class) in workflow_specs.items():
        workflow_class = get_workflow(registry_key) or fallback_class
        workflows[menu_key] = workflow_class(orchestrator, context_manager)
    
    while True:
        print("\nAvailable Workflows:")
        print("1. Validated Research Workflow (Recommended) ⭐")
        print("   (PICOT → Search → Validation → Filtering → Synthesis)")
        print("2. Basic Research Workflow")
        print("3. Parallel Search (PubMed + CINAHL + Cochrane)")
        print("4. Timeline Planner (Milestones & Schedule)")
        print("5. Back to Main Menu")
        
        choice = input("\n⚡ Select workflow (1-5): ").strip()
        
        if choice == '5' or choice.lower() in ['back', 'exit', 'q']:
            print("\n🔙 Returning to menu...")
            break
            
        if choice not in workflows:
            print("❌ Invalid choice")
            continue
            
        workflow = workflows[choice]
        print(f"\n🚀 Starting {workflow.name}...")
        print(f"📝 {workflow.description}")
        
        # Collect inputs based on workflow type
        inputs = {}
        try:
            if isinstance(workflow, ValidatedResearchWorkflow):
                inputs["topic"] = input("Enter research topic: ").strip()
                inputs["setting"] = input("Enter clinical setting: ").strip()
                inputs["intervention"] = input("Enter intervention: ").strip()
                
                # Inject real agents
                inputs["picot_agent"] = nursing_research_agent
                inputs["search_agent"] = get_medical_research_agent()
                inputs["validation_agent"] = get_citation_validation_agent()
                inputs["writing_agent"] = research_writing_agent

            elif isinstance(workflow, ResearchWorkflow):
                inputs["topic"] = input("Enter research topic: ").strip()
                inputs["setting"] = input("Enter clinical setting: ").strip()
                inputs["intervention"] = input("Enter intervention: ").strip()
                
                # Inject real agents
                inputs["picot_agent"] = nursing_research_agent
                inputs["search_agent"] = get_medical_research_agent()
                inputs["writing_agent"] = research_writing_agent
                
            elif isinstance(workflow, ParallelSearchWorkflow):
                inputs["query"] = input("Enter search query: ").strip()
                # Inject real agents (using same agent for demo if others not available, 
                # but ideally we'd have distinct ones. For now using what we have)
                # In a real scenario, we'd have distinct agents for CINAHL/Cochrane.
                # We'll use the medical agent for all to demonstrate parallelism 
                # (orchestrator handles the threading)
                med_agent = get_medical_research_agent()
                inputs["pubmed_agent"] = med_agent
                inputs["cinahl_agent"] = med_agent 
                inputs["cochrane_agent"] = med_agent
                
            elif isinstance(workflow, TimelinePlannerWorkflow):
                inputs["project_type"] = input("Enter project type (e.g., DNP Capstone): ").strip()
                inputs["start_date"] = input("Enter start date (YYYY-MM-DD): ").strip()
                inputs["end_date"] = input("Enter end date (YYYY-MM-DD): ").strip()
                inputs["timeline_agent"] = project_timeline_agent
                inputs["milestone_agent"] = project_timeline_agent
            
            print("\n⏳ Executing workflow... (this may take a moment)")
            result = workflow.execute(**inputs)
            
            if result.success:
                print("\n✅ Workflow Completed Successfully!")
                print("\nOutputs:")
                for key, value in result.outputs.items():
                    print(f"\n--- {key.upper()} ---")
                    if isinstance(value, list):
                        for item in value:
                            print(f"- {item}")
                    else:
                        print(str(value)[:500] + "..." if len(str(value)) > 500 else value)
            else:
                print(f"\n❌ Workflow Failed: {result.error}")
                
        except Exception as e:
            print(f"\n❌ Error preparing workflow: {e}")
            
        print("\n" + "-"*80)
def show_clinical_disclaimer() -> bool:
    """
    Display clinical disclaimer and require acknowledgment.

    Returns:
        True if user acknowledges disclaimer, False otherwise

    Created: Phase 1, Task 4 (2025-11-29)
    Priority: CRITICAL - Liability protection
    """
    print("\n" + "=" * 80)
    print("⚠️  CLINICAL DISCLAIMER ⚠️".center(80))
    print("=" * 80)
    print("""
This system is a QUALITY IMPROVEMENT PLANNING TOOL for nursing professionals.

IT IS NOT:
  ❌ A substitute for clinical judgment
  ❌ A replacement for institutional approvals
  ❌ Medical advice or clinical decision support
  ❌ A validated clinical decision tool

ALL OUTPUTS MUST BE REVIEWED BY:
  • Nurse Manager (workflow feasibility)
  • Clinical experts (Infection Control, Safety, Quality Dept)
  • Statistician (if using sample size calculations)
  • IRB/Ethics Committee (for research classification)

BY USING THIS TOOL YOU ACKNOWLEDGE:
  1. You are a licensed healthcare professional
  2. You will obtain appropriate institutional approvals
  3. You will validate all recommendations with experts
  4. You are solely responsible for project outcomes
  5. This tool provides planning guidance, not clinical recommendations

IMPORTANT:
  • All statistical calculations are estimates and require expert review
  • Budget estimates are rough approximations only
  • Literature search results must be independently verified
  • No guarantee of committee approval or project success
""")
    print("=" * 80)
    print()

    response = input("Type 'I UNDERSTAND AND AGREE' to continue (or 'exit' to quit): ").strip()

    if response.upper() == "I UNDERSTAND AND AGREE":
        print("\n✅ Disclaimer acknowledged. Proceeding to system...\n")
        return True
    elif response.lower() == "exit":
        print("\n👋 Exiting. Goodbye!\n")
        return False
    else:
        print("\n❌ You must type exactly 'I UNDERSTAND AND AGREE' to use this system.")
        print("   (You typed: '{}')".format(response))
        return False


def get_or_create_project():
    """Get active project or help user create one."""
    pm = get_project_manager()
    active_project = pm.get_active_project()

    if active_project:
        return active_project

    # No active project - help user create one
    print("\n📋 Let's set up your project first.")
    print("\nWhat would you like to name your project?")
    print("(Examples: 'Fall Prevention Study', 'CAUTI Reduction', 'Pressure Ulcer Prevention')")

    project_name = input("\n📝 Project name: ").strip()

    if not project_name:
        print("❌ Project name cannot be empty. Exiting.")
        sys.exit(1)

    # Create project
    cli_create_project(project_name, add_milestones=True)

    return project_name


def print_help():
    """Print help message."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              HELP & EXAMPLES                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 WHAT I CAN DO:
  • Develop PICOT questions
  • Search research databases (PubMed, ArXiv, ClinicalTrials)
  • Validate and grade evidence quality
  • Synthesize research findings
  • Plan data analysis and calculate sample sizes
  • Track project timeline and deadlines
  • Draft literature reviews and project sections

💬 EXAMPLE QUERIES:
  • "Research fall prevention in elderly patients"
  • "What's my next deadline?"
  • "Calculate sample size for a 30% reduction in falls"
  • "Validate these articles: PMID 12345, PMID 67890"
  • "Draft a literature review on CAUTI prevention"
  • "Show me my project timeline"

🔧 COMMANDS:
  • help          - Show this help message
  • exit          - Save and quit
  • legacy        - Switch to legacy menu mode

Just describe what you want in natural language, and I'll figure out how to help!
""")


def main_conversational():
    """
    New conversational interface - main entry point.
    """
    # Get or create project
    project_name = get_or_create_project()

    # Get project database path
    pm = get_project_manager()
    project_db = pm.get_project_db_path()

    # Initialize conversation context
    context = ConversationContext(
        project_name=project_name,
        project_db_path=project_db
    )

    # Load previous conversation if exists
    context.load_from_db()

    # Initialize intelligent orchestrator
    orchestrator = IntelligentOrchestrator()

    print(f"\n✅ Working on project: {project_name}")
    print("\nWhat would you like to work on today?\n")

    # Main conversation loop
    while True:
        try:
            # Get user input
            user_message = input("💬 You: ").strip()

            # Handle exit
            if user_message.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye! Your work has been saved.")
                context.save_to_db()
                break

            # Handle empty input
            if not user_message:
                continue

            # Handle special commands
            if user_message.lower() == 'help':
                print_help()
                continue

            if user_message.lower() == 'legacy':
                print("\n🔄 Switching to legacy menu mode...")
                context.save_to_db()
                project_management_loop()
                break

            # Add to context
            context.add_message("user", user_message)

            # Process message (orchestrator handles everything)
            print("\n🤖 Assistant: ", end="", flush=True)

            response, suggestions = orchestrator.process_user_message(
                user_message,
                context
            )

            # Print response
            print(response)

            # Add to context
            context.add_message("assistant", response)

            # Show suggestions
            if suggestions:
                print("\n💡 What would you like to do next?")
                for suggestion in suggestions:
                    print(f"   • {suggestion}")

            print()  # Blank line before next input

            # Save context periodically
            if len(context.messages) % 4 == 0:  # Every 2 exchanges
                context.save_to_db()

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Your work has been saved.")
            context.save_to_db()
            break

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'help' for assistance.\n")


def main():
    """Main entry point."""
    # CRITICAL: Display disclaimer and exit if not acknowledged
    # Phase 1, Task 4 (2025-11-29) - Liability protection
    if not show_clinical_disclaimer():
        sys.exit(1)

    # Fail-fast (format) validation for OpenAI key to avoid wasting requests.
    # If key is missing, allow the app to start (some features/tests don't require live calls).
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            validate_openai_key(openai_key)
        except InvalidAPIKeyError as e:
            print(f"\n⚠️  {e}")

    show_welcome()

    # Launch conversational interface
    main_conversational()


if __name__ == "__main__":
    main()
