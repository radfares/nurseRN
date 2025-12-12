"""
Nursing Research Project Assistant
Complete system for healthcare improvement project support with project management.

UPDATED: 2025-11-23 - Added project-centric database architecture
"""

from dotenv import load_dotenv
# Ensure .env values override any existing shell values so the app uses the keys you set in .env
load_dotenv(override=True)

# Ensure vendored agno library is importable
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

# Orchestration imports
from src.orchestration.context_manager import ContextManager
from src.orchestration.orchestrator import WorkflowOrchestrator
from src.orchestration.query_router import QueryRouter, Intent
from src.workflows.research_workflow import ResearchWorkflow
from src.workflows.parallel_search import ParallelSearchWorkflow
from src.workflows.timeline_planner import TimelinePlannerWorkflow
from src.workflows.validated_research_workflow import ValidatedResearchWorkflow


def show_welcome():
    """Display welcome message."""
    print("\n" + "=" * 80)
    print("🏥 NURSING RESEARCH PROJECT ASSISTANT")
    print("=" * 80)
    print("\nProject-Centric Multi-Agent System")
    print("Timeline: November 2025 - June 2026")
    print("\nFeatures:")
    print("  ✓ Project management (create, switch, archive)")
    print("  ✓ 6 specialized AI agents")
    print("  ✓ Centralized project database")
    print("  ✓ PICOT development, literature search, data analysis")
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
    
    workflows = {
        "1": ValidatedResearchWorkflow(orchestrator, context_manager),
        "2": ResearchWorkflow(orchestrator, context_manager),
        "3": ParallelSearchWorkflow(orchestrator, context_manager),
        "4": TimelinePlannerWorkflow(orchestrator, context_manager)
    }
    
    while True:
        print("\nAvailable Workflows:")
        print("1. Validated Research Workflow (Recommended) ⭐")
        print("   (PICOT → Search → Validation → Filtering → Synthesis)")
        print("2. Basic Research Workflow")
        print("3. Parallel Search (PubMed + CINAHL + Cochrane)")
(Content truncated due to size limit. Use page ranges or line ranges to read remaining content)