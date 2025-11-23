"""
Nursing Research Project Assistant
Complete system for healthcare improvement project support with project management.

UPDATED: 2025-11-23 - Added project-centric database architecture
"""

from dotenv import load_dotenv
load_dotenv()

from project_manager import (
    get_project_manager,
    cli_create_project,
    cli_list_projects,
    cli_switch_project,
    cli_archive_project
)

# Legacy imports (will be updated to use project paths)
from nursing_research_agent import nursing_research_agent
from nursing_project_timeline_agent import project_timeline_agent
from medical_research_agent import medical_research_agent
from academic_research_agent import academic_research_agent
from research_writing_agent import research_writing_agent
from data_analysis_agent import data_analysis_agent


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

    print("\n" + "="*80)
    print("\nCommands: 1-6 (select agent), 'back' (return to projects), 'exit'")


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
            '2': (medical_research_agent, "Medical Research Agent (PubMed)"),
            '3': (academic_research_agent, "Academic Research Agent (ArXiv)"),
            '4': (research_writing_agent, "Research Writing Agent"),
            '5': (project_timeline_agent, "Project Timeline Agent"),
            '6': (data_analysis_agent, "Data Analysis Planner")
        }

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

            print("\n" + "-"*80)

        except KeyboardInterrupt:
            print("\n\n⚠️  Interrupted. Type 'exit' to quit or continue chatting.")
            continue

        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            break


def main():
    """Main entry point."""
    show_welcome()

    # Check if any projects exist
    pm = get_project_manager()
    projects = pm.list_projects()
    active_project = pm.get_active_project()

    if not projects:
        print("\n📋 Welcome! Let's create your first project.")
        project_name = input("\n📝 Enter project name: ").strip()

        if project_name:
            cli_create_project(project_name, add_milestones=True)
        else:
            print("\n⚠️  No project created. You can create one later with: new <name>")

    elif not active_project:
        print("\n⚠️  No active project selected.")
        print("\n   Available projects:")
        cli_list_projects()
        print("\n   Use 'switch <project_name>' to select one")

    # Enter project management loop
    project_management_loop()


if __name__ == "__main__":
    main()
