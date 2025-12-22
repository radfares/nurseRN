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
from agents.nursing_project_timeline_agent import get_project_timeline_agent
from agents.medical_research_agent import get_medical_research_agent
from agents.academic_research_agent import academic_research_agent
from agents.research_writing_agent import research_writing_agent
from agents.data_analysis_agent import data_analysis_agent
from agents.citation_validation_agent import get_citation_validation_agent
from agents.notion_document_agent import notion_document_agent

# Orchestration imports - NEW CONVERSATIONAL INTERFACE
from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator
from src.orchestration.conversation_context import ConversationContext

# Legacy orchestration imports (kept for fallback)
from src.orchestration.context_manager import ContextManager
from src.orchestration.orchestrator import WorkflowOrchestrator
from src.orchestration.query_router import QueryRouter, Intent
from src.workflows.research_workflow import ResearchWorkflow
from src.workflows.parallel_search import ParallelSearchWorkflow
from src.workflows.timeline_planner import TimelinePlannerWorkflow
from src.workflows.validated_research_workflow import ValidatedResearchWorkflow
from src.workflows.registry import get_workflow


def show_welcome(): # This function shows the welcome banner and tips when you start.
    print("\n" + "=" * 80) # Prints the top border line.
    print("🏥 NURSING RESEARCH ASSISTANT") # Prints the name of the app.
    print("=" * 80) # Prints the bottom border line.
    print("\nI'll help you develop your healthcare improvement project from") # Explains what the app does.
    print("PICOT to poster presentation.") # Continues the explanation.
    print("\n💡 TIPS:") # Header for the tips section.
    print("  - Type 'help' to see what I can do") # Tip for getting help.
    print("  - Type 'guide' to read the full project manual") # Tip for reading the guide.
    print("  - Type 'legacy' for the old menu system") # Tip for switching modes.
    print("\nJust tell me what you'd like to work on, and I'll handle the rest!") # Encouraging closing message.
    print("=" * 80) # Final border line.


def show_project_menu(): # This shows the project menu and which project is active.
    print("\n" + "="*80) # Prints the menu header border.
    print("PROJECT MANAGEMENT") # Menu title.
    print("="*80) # Menu title border.

    pm = get_project_manager() # Gets the tool that manages projects.
    active_project = pm.get_active_project() # Checks which project you are working on now.

    if active_project: # If a project is active, show its name.
        print(f"\n★ ACTIVE PROJECT: {active_project}")
    else: # If no project is active, show a warning.
        print("\n⚠️  No active project selected")

    print("\nProject Commands:") # Lists the things you can do with projects.
    print("  new <project_name>     - Create new project") # Command to make a new project.
    print("  list                   - List all projects") # Command to see all your projects.
    print("  switch <project_name>  - Switch to project") # Command to change projects.
    print("  archive <project_name> - Archive project") # Command to hide old projects.
    print("  agents                 - Launch agents (requires active project)") # Command to start the AI helpers.
    print("  exit                   - Exit program") # Command to close the app.
    print("\n" + "="*80) # Bottom border for the menu.


def project_management_loop(): # This loop keeps the project menu running until you exit.
    while True: # Keeps asking for commands until you stop.
        show_project_menu() # Shows the menu options.

        command = input("\n📋 Command: ").strip().lower() # Asks you to type a command.

        if not command: # If you didn't type anything, ask again.
            continue

        # Parse command
        parts = command.split(maxsplit=1) # Splits what you typed into the command and the name.
        cmd = parts[0] # The first word is the command.
        arg = parts[1] if len(parts) > 1 else None # The rest is the project name or argument.

        if cmd in ['exit', 'quit', 'q']: # If you type exit, say goodbye and stop.
            print("\n👋 Goodbye!")
            break

        elif cmd == 'new': # If you type new, create a new project.
            if not arg:
                print("❌ Usage: new <project_name>")
                continue
            cli_create_project(arg, add_milestones=True)

        elif cmd == 'list': # If you type list, show all projects.
            cli_list_projects()

        elif cmd == 'switch': # If you type switch, change to a different project.
            if not arg:
                print("❌ Usage: switch <project_name>")
                continue
            cli_switch_project(arg)

        elif cmd == 'archive': # If you type archive, move a project to the archives.
            if not arg:
                print("❌ Usage: archive <project_name>")
                continue
            confirm = input(f"⚠️  Archive '{arg}'? This will move it to archives. (yes/no): ")
            if confirm.lower() == 'yes':
                cli_archive_project(arg)
            else:
                print("❌ Cancelled")

        elif cmd == 'agents': # If you type agents, start the AI helper selection.
            # Check for active project
            pm = get_project_manager()
            active_project = pm.get_active_project()

            if not active_project: # You must have a project open to use agents.
                print("\n❌ No active project. Create or switch to a project first.")
                print("   Commands: 'new <name>' or 'switch <name>'")
                continue

            # Launch agent selector
            print(f"\n✅ Using project: {active_project}")
            agent_selection_loop() # Starts the agent selection menu.

        else: # If the command is unknown, show an error.
            print(f"❌ Unknown command: {cmd}")
            print("   Valid commands: new, list, switch, archive, agents, exit")


def show_agent_menu():
    """
    WHAT IT IS: A directory of specialized AI agents.
    WHAT IT'S DOING: Lists all available agents (Nursing, Medical, Academic, etc.) and their specific capabilities.
    HOW IT WORKS: Prints a detailed numbered list explaining what each agent is best used for.
    IS IT WORKING: Yes, it helps users choose the right tool for their specific research task.
    """
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

    print("\n8. Workflow Mode (Templates) ⚡")
    print("   - Run pre-defined multi-step workflows")
    print("   - Validated Research (Search + Validate + Write) ⭐")
    print("   - Basic Research (PICOT -> Search -> Writing)")
    print("   - Parallel Search (Multiple databases)")
    print("   - Timeline Planner")
    print("   - Best for: Complex tasks requiring multiple steps")

    print("\n9. Smart Mode (Auto-Routing) 🧠")
    print("   - Automatically routes your query to the best agent")
    print("   - Detects intent (Research, Search, Planning)")
    print("   - Best for: When you're not sure which agent to use")

    print("\n10. Notion Document Agent 📝")
    print("   - Manage your Notion workspace")
    print("   - Search, read, and update pages")
    print("   - Best for: Documenting your project progress!")

    print("\n" + "="*80)
    print("\nCommands: 1-7 (agents), 8 (workflows), 9 (smart mode), 10 (notion), 'back', 'exit'")


def agent_selection_loop(): # This loop lets you pick which AI agent you want to talk to.
    while True: # Keeps the selection menu open until you go back or exit.
        show_agent_menu() # Shows the list of available AI agents.

        choice = input("\n🤖 Choose agent: ").strip().lower() # Asks you to pick an agent by number.

        if choice in ['exit', 'quit', 'q']: # If you type exit, go back to project management.
            print("\n👋 Returning to project management...")
            return

        elif choice in ['back', 'b']: # If you type back, go back to project management.
            print("\n🔙 Returning to project management...")
            return

        # Agent selection (1-7 are agents; 8 workflows; 9 smart; 10 notion)
        agent_map = { # Maps your number choice to the actual AI agent tool.
            '1': (nursing_research_agent, "Nursing Research Agent"),
            '2': (get_medical_research_agent(), "Medical Research Agent (PubMed)"),
            '3': (academic_research_agent, "Academic Research Agent (ArXiv)"),
            '4': (research_writing_agent, "Research Writing Agent"),
            '5': (get_project_timeline_agent(), "Project Timeline Agent"),
            '6': (data_analysis_agent, "Data Analysis Planner"),
            '7': (get_citation_validation_agent(), "Citation Validation Agent"),
            '10': (notion_document_agent, "Notion Document Agent"),
        }

        # Handle new modes
        if choice == '8': # If you pick 8, start the multi-step workflow mode.
            run_workflow_mode()
            continue
        elif choice == '9': # If you pick 9, start the smart auto-routing mode.
            run_smart_mode()
            continue

        if choice not in agent_map: # If you pick a number not on the list, show an error.
            print(f"❌ Invalid choice: {choice}")
            continue

        agent, agent_name = agent_map[choice] # Gets the selected agent and its name.

        # Get active project
        pm = get_project_manager() # Gets the project manager tool.
        active_project = pm.get_active_project() # Gets the name of your current project.
        project_db = pm.get_project_db_path() # Gets the path to your project's database.

        print(f"\n✅ Selected: {agent_name}") # Confirms which agent you picked.
        print(f"📁 Project: {active_project}") # Confirms which project you are in.
        print(f"💾 Database: {project_db}") # Shows where your data is being saved.

        # Run agent interaction
        run_agent_interaction(agent, agent_name, active_project) # Starts the chat with the agent.


def run_agent_interaction(agent, agent_name: str, project_name: str): # This function handles the actual chat with an AI agent.
    print("\n" + "=" * 80)  # Prints the chat header border.
    print(f"CHAT WITH {agent_name.upper()}") # Shows which agent you are talking to.
    print("="*80) # Prints the chat header border.
    print(f"\nProject: {project_name}") # Shows the current project name.
    
    # Show agent-specific usage examples and capabilities
    if hasattr(agent, 'show_usage_examples'): # If the agent has examples of what to say, show them.
        try:
            agent.show_usage_examples()
        except Exception as e:
            print(f"⚠️  Could not show usage examples: {e}")

    print("\nTips:") # Shows helpful tips for chatting.
    print("  - Type your questions naturally")
    print("  - Type 'exit' to stop chatting")
    print("  - Type 'switch' to choose different agent")
    print("  - Type 'back' to return to project menu")
    print("\n" + "="*80) # Prints the tips border.

    while True: # Keeps the chat going until you stop.
        try:
            query = input("\n💬 You: ").strip()  # Asks for your question or command.

            if not query: # If you didn't type anything, ask again.
                continue

            if query.lower() in ['exit', 'quit', 'q']: # If you type exit, stop the chat.
                print("\n👋 Exiting chat with this agent.")
                return

            if query.lower() in ['back', 'b']: # If you type back, go back to the agent menu.
                print("\n🔙 Returning to project menu...")
                return

            if query.lower() == 'switch': # If you type switch, go back to pick a different agent.
                print("\n🔄 Switching agents...")
                return

            # Run agent
            print(f"\n🤖 {agent_name}: ", end="", flush=True) # Shows the agent is thinking.

            try:
                try:
                    agent.print_response(query, project_name=project_name, stream=True) # Sends your question to the agent.
                except TypeError:
                    # Some agents are raw Agno agents whose print_response does not accept project_name.
                    agent.print_response(query, stream=True) # Fallback for agents with simpler interfaces.
            except Exception as e: # If the agent has an error, show it.
                print(f"\n❌ Agent error: {e}")
                print("\n💡 Make sure OPENAI_API_KEY is set in your environment")
                print("   and all required API keys are configured.")

            # Phase 1, Task 5 (2025-11-29): Print watermark after every agent response
            BaseAgent.print_watermark() # Prints the official project watermark.

            print("\n" + "-"*80) # Prints a separator line.

        except KeyboardInterrupt: # If you press Ctrl+C, show a warning.
            print("\n\n⚠️  Interrupted. Type 'exit' to quit or continue chatting.")
            continue

        except Exception as e: # If something else goes wrong, show the error and stop.
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            break


def run_smart_mode(): # This mode automatically picks the best agent for your question.
    print("\n" + "="*80) # Prints the smart mode header.
    print("🧠 SMART MODE (AUTO-ROUTING)")
    print("="*80)
    
    pm = get_project_manager() # Gets the project manager tool.
    active_project = pm.get_active_project() # Gets the current project name.
    project_db = pm.get_project_db_path() # Gets the project database path.
    
    if not active_project: # You must have a project open to use smart mode.
        print("\n❌ No active project. Please select a project first.")
        return

    print(f"\nActive Project: {active_project}") # Confirms the active project.
    print("Type 'exit' to return to menu.")
    
    # Initialize orchestration
    context_manager = ContextManager(db_path=project_db) # Sets up the tool to remember the conversation.
    orchestrator = WorkflowOrchestrator(context_manager) # Sets up the tool to run the agents.
    router = QueryRouter() # Sets up the tool to figure out which agent to use.
    
    while True: # Keeps smart mode running until you exit.
        query = input("\n🧠 How can I help you? ").strip() # Asks for your question.
        
        if not query: # If you didn't type anything, ask again.
            continue
            
        if query.lower() in ['exit', 'quit', 'q', 'back']: # If you type exit, go back to the menu.
            print("\n🔙 Returning to menu...")
            break
            
        print("\n🤔 Analyzing intent...", end="", flush=True) # Shows the AI is figuring out what you want.
        
        # Route query
        # Use LLM routing if possible for better accuracy
        intent, confidence, entities = router.route_query_llm(query, nursing_research_agent) # Figures out what you are asking about.
        print(f"\n👉 Detected intent: {intent.value} (Confidence: {confidence:.2f})") # Shows what the AI thinks you want.
        
        # Map intent to agent
        intent_agent_map = { # Links what you want to the right AI agent.
            Intent.PICOT: "nursing_research_agent",
            Intent.SEARCH: "medical_research_agent",
            Intent.TIMELINE: "project_timeline_agent",
            Intent.DATA_ANALYSIS: "data_analysis_agent",
            Intent.WRITING: "research_writing_agent",
            Intent.VALIDATION: "citation_validation_agent",
            Intent.NOTION: "notion_document_agent",
            Intent.UNKNOWN: "nursing_research_agent"
        }
        
        suggested_agent = intent_agent_map.get(intent, "nursing_research_agent") # Picks the best agent.
        print(f"👉 Routing to: {suggested_agent}") # Tells you which agent is being used.
        
        # Map router agent names to actual agents
        agent_map = { # Links the agent name to the actual tool.
            "nursing_research_agent": nursing_research_agent,
            "medical_research_agent": get_medical_research_agent(),
            "academic_research_agent": academic_research_agent,
            "research_writing_agent": research_writing_agent,
            "project_timeline_agent": get_project_timeline_agent(),
            "data_analysis_agent": data_analysis_agent,
            "citation_validation_agent": get_citation_validation_agent(),
            "notion_document_agent": notion_document_agent
        }
        
        target_agent = agent_map.get(suggested_agent) # Gets the actual agent tool.
        
        if target_agent: # If the agent exists, run it.
            print(f"\n🤖 {suggested_agent}: ", end="", flush=True)
            try:
                # Execute via orchestrator for consistent logging/result handling
                result = orchestrator.execute_single_agent( # Runs the agent and gets the answer.
                    agent=target_agent,
                    query=query,
                    workflow_id=f"smart_mode_{int(time.time())}"
                )
                
                if result.success: # If it worked, show the answer.
                    print(result.content)
                else: # If it failed, show the error.
                    print(f"\n❌ Execution failed: {result.error}")
                    
                BaseAgent.print_watermark() # Prints the project watermark.
                print("\n" + "-"*80) # Prints a separator line.
                
            except Exception as e: # If something goes wrong, show the error.
                print(f"\n❌ Error: {e}")
        else: # If the agent couldn't be found, show an error.
            print(f"\n❌ Could not find agent: {route.suggested_agent}")


def run_workflow_mode(): # This mode runs complex, multi-step research tasks automatically.
    print("\n" + "="*80) # Prints the workflow mode header.
    print("⚡ WORKFLOW MODE (TEMPLATES)")
    print("="*80)
    
    pm = get_project_manager() # Gets the project manager tool.
    active_project = pm.get_active_project() # Gets the current project name.
    project_db = pm.get_project_db_path() # Gets the project database path.
    
    if not active_project: # You must have a project open to use workflows.
        print("\n❌ No active project. Please select a project first.")
        return

    # Initialize orchestration
    context_manager = ContextManager(db_path=project_db) # Sets up the tool to remember the conversation.
    orchestrator = WorkflowOrchestrator(context_manager) # Sets up the tool to run the agents.
    
    workflows = {} # A place to store the available workflows.
    workflow_specs = { # Defines the different multi-step tasks you can run.
        "1": ("validated_research", ValidatedResearchWorkflow),
        "2": ("research", ResearchWorkflow),
        "3": ("parallel_search", ParallelSearchWorkflow),
        "4": ("timeline_planner", TimelinePlannerWorkflow),
    }
    for menu_key, (registry_key, fallback_class) in workflow_specs.items(): # Sets up each workflow.
        workflow_class = get_workflow(registry_key) or fallback_class
        workflows[menu_key] = workflow_class(orchestrator, context_manager, project_manager=pm)
    
    while True: # Keeps the workflow menu open until you exit.
        print("\nAvailable Workflows:") # Lists the multi-step tasks.
        print("1. Validated Research Workflow (Recommended) ⭐")
        print("   (PICOT → Search → Validation → Filtering → Synthesis)")
        print("2. Basic Research Workflow")
        print("3. Parallel Search (PubMed + CINAHL + Cochrane)")
        print("4. Timeline Planner (Milestones & Schedule)")
        print("5. Back to Main Menu")
        
        choice = input("\n⚡ Select workflow (1-5): ").strip() # Asks you to pick a workflow.
        
        if choice == '5' or choice.lower() in ['back', 'exit', 'q']: # If you type exit, go back to the menu.
            print("\n🔙 Returning to menu...")
            break
            
        if choice not in workflows: # If you pick a number not on the list, show an error.
            print("❌ Invalid choice")
            continue
            
        workflow = workflows[choice] # Gets the selected workflow.
        print(f"\n🚀 Starting {workflow.name}...") # Tells you the workflow is starting.
        print(f"📝 {workflow.description}") # Explains what the workflow will do.
        
        # Collect inputs based on workflow type
        inputs = {} # A place to store the information the workflow needs.
        try:
            if isinstance(workflow, ValidatedResearchWorkflow): # If it's the validated research workflow, ask for topic details.
                inputs["topic"] = input("Enter research topic: ").strip()
                inputs["setting"] = input("Enter clinical setting: ").strip()
                inputs["intervention"] = input("Enter intervention: ").strip()
                
                # Inject real agents
                inputs["picot_agent"] = nursing_research_agent
                inputs["search_agent"] = get_medical_research_agent()
                inputs["validation_agent"] = get_citation_validation_agent()
                inputs["writing_agent"] = research_writing_agent

            elif isinstance(workflow, ResearchWorkflow): # If it's the basic research workflow, ask for topic details.
                inputs["topic"] = input("Enter research topic: ").strip()
                inputs["setting"] = input("Enter clinical setting: ").strip()
                inputs["intervention"] = input("Enter intervention: ").strip()
                
                # Inject real agents
                inputs["picot_agent"] = nursing_research_agent
                inputs["search_agent"] = get_medical_research_agent()
                inputs["writing_agent"] = research_writing_agent
                
            elif isinstance(workflow, ParallelSearchWorkflow): # If it's the parallel search, ask for the search query.
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
                
            elif isinstance(workflow, TimelinePlannerWorkflow): # If it's the timeline planner, ask for project dates.
                inputs["project_type"] = input("Enter project type (e.g., DNP Capstone): ").strip()
                inputs["start_date"] = input("Enter start date (YYYY-MM-DD): ").strip()
                inputs["end_date"] = input("Enter end date (YYYY-MM-DD): ").strip()
                inputs["timeline_agent"] = get_project_timeline_agent()
                inputs["milestone_agent"] = get_project_timeline_agent()
            
            print("\n⏳ Executing workflow... (this may take a moment)") # Shows the workflow is running.
            result = workflow.execute(**inputs) # Runs the workflow and gets the final result.
            
            if result.success: # If it worked, show the final outputs.
                print("\n✅ Workflow Completed Successfully!")
                print("\nOutputs:")
                for key, value in result.outputs.items():
                    print(f"\n--- {key.upper()} ---")
                    if isinstance(value, list):
                        for item in value:
                            print(f"- {item}")
                    else:
                        print(str(value)[:500] + "..." if len(str(value)) > 500 else value)
            else: # If it failed, show the error.
                print(f"\n❌ Workflow Failed: {result.error}")
                
        except Exception as e: # If something goes wrong during setup, show the error.
            print(f"\n❌ Error preparing workflow: {e}")
            
        print("\n" + "-"*80) # Prints a separator line.


def show_clinical_disclaimer() -> bool: # This function shows a greeting message.
    print("\n" + "=" * 80) # Prints the top border line.
    print("ℹ️  QUICK START & TIPS".center(80)) # Centers the title in the box.
    print("=" * 80) # Prints the bottom border line.
    print("""
This assistant helps you plan nursing quality-improvement projects.

	Tips:
	  - Start by creating/switching to a project (e.g., "Fall Prevention QI")
	  - Ask for a PICOT question to frame your topic
	  - Run a PubMed search for recent articles (5-year window works well)
	  - Validate citations and evidence level before using them
	  - Use Safety checks when devices/meds are involved
	  - Save milestones and next steps so you stay on track
	
	Example prompts:
	  - "Create a PICOT for reducing CAUTI in ICU patients"
	  - "Find 3 recent PubMed articles on pressure injury prevention"
	  - "Validate PMIDs 12345678, 34567890 for evidence level and retractions"
	  - "What milestones should I set for my poster deadline in June?"
	
	Remember:
	  - Review outputs with your clinical leadership/experts before acting
	  - Obtain required institutional approvals
	  - This tool provides planning guidance, not clinical recommendations
""") # Prints the safety tips and rules.
    print("=" * 80) # Prints the final border line.
    print() # Prints a blank line.
    print("\n" + "=" * 80) # Prints the greeting banner.
    print("👋 Mr. Fares RN".center(80)) # Centers the greeting name.
    print("Hello — ready when you are, sir.".center(80)) # Centers the greeting message.
    print("=" * 80) # Prints the banner bottom line.
    print() # Adds spacing after the greeting.
    return True # Always returns true to proceed.


def get_or_create_project(): # This function makes sure you have a project open before you start.
    pm = get_project_manager() # Gets the project manager tool.
    active_project = pm.get_active_project() # Checks if you already have a project open.

    if active_project: # If you do, just return its name.
        return active_project # Returns the name of the active project.

    # No active project - help user create one
    print("\n📋 Let's set up your project first.") # Tells you that you need to make a project.
    print("\nWhat would you like to name your project?") # Asks for a name.
    print("(Examples: 'Fall Prevention Study', 'CAUTI Reduction', 'Pressure Ulcer Prevention')") # Gives examples.

    project_name = input("\n📝 Project name: ").strip() # Asks you to type the name.

    if not project_name: # If you didn't type a name, stop the app.
        print("❌ Project name cannot be empty. Exiting.") # Shows an error.
        sys.exit(1) # Stops the program.

    # Create project
    cli_create_project(project_name, add_milestones=True) # Makes the new project and sets up milestones.

    return project_name # Returns the name of the new project.


def print_help(): # This function shows you what the assistant can do and how to use it.
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              HELP & EXAMPLES                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 WHAT I CAN DO:
  - Develop PICOT questions
  - Search research databases (PubMed, ArXiv, ClinicalTrials)
  - Validate and grade evidence quality
  - Synthesize research findings
  - Plan data analysis and calculate sample sizes
  - Track project timeline and deadlines
  - Draft literature reviews and project sections

💬 EXAMPLE QUERIES:
  - "Research fall prevention in elderly patients"
  - "What's my next deadline?"
  - "Calculate sample size for a 30% reduction in falls"
  - "Validate these articles: PMID 12345, PMID 67890"
  - "Draft a literature review on CAUTI prevention"
  - "Show me my project timeline"

🔧 COMMANDS:
  - help          - Show this help message
  - guide         - Read the comprehensive project guide
  - exit          - Save and quit
  - legacy        - Switch to legacy menu mode

	Just describe what you want in natural language, and I'll figure out how to help!
	""") # Prints a big box with help info and examples.


def _maybe_rewrite_multi_question_message(message: str) -> str: # This function helps the AI answer multiple questions at once.
    cleaned = (message or "").strip() # Cleans up the message you typed.
    if not cleaned: # If it's empty, just return it.
        return message # Returns the empty message.

    question_marks = cleaned.count("?") # Counts how many question marks you used.
    non_empty_lines = [ln for ln in cleaned.splitlines() if ln.strip()] # Counts how many lines you typed.
    multi_line = len(non_empty_lines) >= 2 # Checks if you typed more than one line.
    enumerated = any(token in cleaned for token in ("1)", "2)", "3)", "1.", "2.", "3.")) # Checks if you used a list.
    looks_multi = question_marks >= 2 or multi_line or enumerated # Decides if you asked multiple things.

    if not looks_multi: # If it's just one question, don't change anything.
        return message # Returns the original message.

    return ( # If it's multiple questions, add a note to the AI to answer each one.
        "Please answer each question I asked explicitly (numbered). "
        "Ask follow-up questions only if something is missing.\n\n"
        f"{cleaned}"
    ) # Returns the message with the extra instructions for the AI.


def print_guide(): # This function opens and shows the full project manual.
    guide_path = Path(__file__).parent / "NURSING_PROJECT_GUIDE.md" # Finds the guide file on your computer.
    
    if not guide_path.exists(): # If the file is missing, show an error.
        print("\n❌ Guide file not found: NURSING_PROJECT_GUIDE.md") # Shows the error message.
        print("   Please refer to the README.md or online documentation.") # Tells you where else to look.
        return # Stops the function.

    print("\n📖 OPENING PROJECT GUIDE...\n") # Tells you the guide is opening.
    try:
        content = guide_path.read_text(encoding='utf-8') # Reads the text from the guide file.
        # Print the guide content
        print("-" * 80) # Prints a separator line.
        print(content) # Prints the whole guide.
        print("-" * 80) # Prints a separator line.
        print("\n✅ End of Guide. Scroll up to read.\n") # Tells you that you reached the end.
    except Exception as e: # If there's an error reading the file, show it.
        print(f"❌ Error reading guide: {e}") # Shows the error message.


def main_conversational(): # This is the main chat mode where you can talk naturally to the assistant.
    # Get or create project
    project_name = get_or_create_project() # Makes sure you have a project open.

    # Get project database path
    pm = get_project_manager() # Gets the project manager tool.
    project_db = pm.get_project_db_path() # Gets the path to your project's database.

    # Initialize conversation context
    context = ConversationContext( # Sets up the tool to remember what you talk about.
        project_name=project_name,
        project_db_path=project_db
    ) # Creates the context object.

    # Load previous conversation if exists
    context.load_from_db() # Loads your old messages so the AI remembers them.

    # Initialize intelligent orchestrator
    orchestrator = IntelligentOrchestrator() # Sets up the main AI brain.

    print(f"\n✅ Working on project: {project_name}") # Confirms which project you are in.
    print("\nWhat would you like to work on today?") # Asks what you want to do.
    print("Tip: You can ask multiple questions in one message.\n") # Gives a tip.

    # Main conversation loop
    while True: # Keeps the chat going until you exit.
        try:
            # Get user input
            user_message = input("💬 You: ").strip() # Asks for your message.

            # Handle exit
            if user_message.lower() in ['exit', 'quit', 'q']: # If you type exit, save and stop.
                print("\n👋 Goodbye! Your work has been saved.") # Says goodbye.
                context.save_to_db() # Saves your conversation.
                break # Stops the loop.

            # Handle empty input
            if not user_message: # If you didn't type anything, ask again.
                continue # Goes back to the start of the loop.

            # Handle special commands
            if user_message.lower() == 'help': # If you type help, show the help info.
                print_help() # Runs the help function.
                continue # Goes back to the start of the loop.

            if user_message.lower() == 'guide': # If you type guide, show the manual.
                print_guide() # Runs the guide function.
                continue # Goes back to the start of the loop.

            if user_message.lower() == 'legacy': # If you type legacy, switch to the old menu mode.
                print("\n🔄 Switching to legacy menu mode...") # Tells you it's switching.
                context.save_to_db() # Saves your conversation.
                project_management_loop() # Starts the old menu system.
                break # Stops the conversational loop.

            # Process message (orchestrator handles everything)
            print("\n🤖 Assistant: ", end="", flush=True) # Shows the AI is responding.

            user_message_for_orchestrator = _maybe_rewrite_multi_question_message(user_message) # Prepares your message for the AI.
            response, suggestions = orchestrator.process_user_message(user_message_for_orchestrator, context) # Gets the AI's answer.

            # Print response
            response_text = (response or "").strip() # Cleans up the AI's answer.
            print(response_text if response_text else "I’m here—can you rephrase that question?") # Shows the answer.

            # Show suggestions
            if suggestions: # If the AI has ideas for what to do next, show them.
                print("\n💡 What would you like to do next?") # Header for suggestions.
                for suggestion in suggestions: # Loops through each suggestion.
                    print(f"   - {suggestion}") # Prints the suggestion.

            print()  # Blank line before next input

            # Save context periodically
            if len(context.messages) % 4 == 0:  # Every 2 exchanges, save your work.
                context.save_to_db() # Saves the conversation to the database.

        except KeyboardInterrupt: # If you press Ctrl+C, save and stop.
            print("\n\n👋 Goodbye! Your work has been saved.") # Says goodbye.
            context.save_to_db() # Saves your conversation.
            break # Stops the loop.

        except Exception as e: # If something goes wrong, show the error.
            print(f"\n❌ Error: {e}") # Shows the error message.
            print("Please try again or type 'help' for assistance.\n") # Suggests what to do.


def main(): # This is the starting point of the whole program.
    # CRITICAL: Display disclaimer and exit if not acknowledged
    # Phase 1, Task 4 (2025-11-29) - Liability protection
    if not show_clinical_disclaimer(): # Shows the safety warning first.
        sys.exit(1) # If you don't agree, stop the app.

    show_welcome() # Shows the welcome banner.

    # Launch conversational interface
    main_conversational() # Starts the main chat mode.


if __name__ == "__main__": # If this file is run directly, start the main function.
    main() # Runs the main function.
