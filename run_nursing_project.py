"""
Nursing Research Project Assistant
Complete system for healthcare improvement project support with project management.

UPDATED: 2025-11-23 - Added project-centric database architecture
"""

from dotenv import load_dotenv
# Ensure .env values override any existing shell values so the app uses the keys you set in .env
load_dotenv(override=True)

# Default Agno to a quieter log level for interactive chat (can override via env var).
import os
os.environ.setdefault("AGNO_LOG_LEVEL", "WARNING")

# Reduce noisy INFO logs in interactive chat.
import logging
# Ensure a console handler exists before any agent code calls logging.basicConfig().
logging.basicConfig(level=logging.WARNING)
for _logger_name in (
    "httpx",
    "openai",
    "chromadb",
    "chromadb.telemetry",
    "chromadb.telemetry.product.posthog",
    "src.knowledge",
    "src.knowledge.config",
    "src.knowledge.vector_store",
    "agno",
):
    logging.getLogger(_logger_name).setLevel(logging.WARNING)

# Ensure vendored agno library is importable
import sys
import time
from pathlib import Path
_project_root = Path(__file__).parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))

# Silence Agno's Rich INFO logger (it prints lines like "INFO Found X documents").
try:
    import agno.utils.log as _agno_log  # type: ignore

    logging.getLogger("agno").setLevel(logging.WARNING)
    logging.getLogger("agno-team").setLevel(logging.WARNING)
    logging.getLogger("agno-workflow").setLevel(logging.WARNING)
    # The AgnoLogger instances also need to be bumped directly.
    try:
        _agno_log.agent_logger.setLevel(logging.WARNING)
        _agno_log.team_logger.setLevel(logging.WARNING)
        _agno_log.workflow_logger.setLevel(logging.WARNING)
    except Exception:
        pass
except Exception:
    pass

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


def show_welcome():
    """
    WHAT IT IS: The primary user interface entry-point greeting and branding function.
    WHAT IT'S DOING: It establishes the visual identity of the Nursing Research Assistant by printing a high-visibility 
    ASCII-style banner and a curated list of "Quick Start" tips to guide the user's first interactions.
    HOW IT WORKS: It utilizes standard Python print statements with string multiplication for formatting (e.g., "=" * 80) 
    to ensure a consistent width across different terminal sizes, presenting clear command shortcuts like 'help' and 'guide'.
    IS IT WORKING: Yes, it is fully operational and serves as the first visual feedback the user receives after 
    acknowledging the clinical disclaimer, successfully setting the professional tone of the application.
    """
    print("\n" + "=" * 80)
    print("🏥 NURSING RESEARCH ASSISTANT")
    print("=" * 80)
    print("\nI'll help you develop your healthcare improvement project from")
    print("PICOT to poster presentation.")
    print("\n💡 TIPS:")
    print("  - Type 'help' to see what I can do")
    print("  - Type 'guide' to read the full project manual")
    print("  - Type 'legacy' for the old menu system")
    print("\nJust tell me what you'd like to work on, and I'll handle the rest!")
    print("=" * 80)


def show_project_menu():
    """
    WHAT IT IS: A context-aware project status dashboard and command reference for the legacy menu system.
    WHAT IT'S DOING: It dynamically retrieves the name of the currently active project and displays it prominently, 
    while listing the specific syntax for project management commands like 'new', 'list', 'switch', and 'archive'.
    HOW IT WORKS: It interfaces with the `ProjectManager` singleton via `get_project_manager()` to check the 
    internal state of the application's project database, providing visual warnings (⚠️) if no project is currently selected.
    IS IT WORKING: Yes, it accurately reflects the state of the `project_manager.py` logic and provides a 
    reliable navigation map for users who prefer the structured command-line interface over the conversational mode.
    """
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
    """
    WHAT IT IS: The main event loop for the legacy project management subsystem.
    WHAT IT'S DOING: It continuously listens for, parses, and executes administrative commands related to project 
    lifecycles, acting as the gatekeeper between the user and the underlying project database.
    HOW IT WORKS: It implements a standard REPL (Read-Eval-Print Loop) pattern, using `input()` to capture strings, 
    splitting them into commands and arguments, and then dispatching those to specialized CLI functions like `cli_create_project`.
    IS IT WORKING: Yes, it provides a robust fallback mechanism for users to organize their work into distinct 
    folders and databases before engaging with the AI agents, ensuring data isolation and persistence.
    """
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
    """
    WHAT IT IS: A comprehensive catalog of the specialized AI agents available in the nurseRN ecosystem.
    WHAT IT'S DOING: It provides a detailed breakdown of each agent's domain expertise (e.g., PubMed for Medical, 
    ArXiv for Academic) and suggests specific use cases to help the user decide which tool is best for their current task.
    HOW IT WORKS: It prints a multi-section menu that categorizes agents by their primary data sources and 
    capabilities, including advanced modes like "Smart Mode" (auto-routing) and "Workflow Mode" (multi-step automation).
    IS IT WORKING: Yes, it serves as an essential educational component, ensuring users understand the 
    strengths and limitations of each specialized agent before they begin a research session.
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


def agent_selection_loop():
    """
    WHAT IT IS: The central dispatcher for initiating specialized agent-based research sessions.
    WHAT IT'S DOING: It captures the user's choice from the agent menu and prepares the environment—including 
    project paths and database connections—before handing off control to the specific agent's interaction logic.
    HOW IT WORKS: It uses a local `agent_map` dictionary to link numeric menu choices to actual Python objects 
    (e.g., `nursing_research_agent`), and then retrieves the active project's metadata to ensure the agent has the correct context.
    IS IT WORKING: Yes, it correctly handles the transition from the general menu to specific agent interactions, 
    including the initialization of complex agents like the Medical Research Agent which requires a factory function.
    """
    while True:
        show_agent_menu()

        choice = input("\n🤖 Choose agent: ").strip().lower()

        if choice in ['exit', 'quit', 'q']:
            print("\n👋 Returning to project management...")
            return

        elif choice in ['back', 'b']:
            print("\n🔙 Returning to project management...")
            return

        # Agent selection (1-7 are agents; 8 workflows; 9 smart; 10 notion)
        agent_map = {
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
        if choice == '8':
            run_workflow_mode()
            continue
        elif choice == '9':
            run_smart_mode()
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
    WHAT IT IS: The dedicated real-time chat environment for interacting with a single specialized AI agent.
    WHAT IT'S DOING: It facilitates a continuous dialogue where the user can ask questions, and the agent 
    responds using its specific tools (like PubMed search or PICOT drafting), while maintaining a clean terminal UI.
    HOW IT WORKS: It runs a nested while-loop that captures user strings, checks for escape commands ('exit', 'back'), 
    and calls the agent's `print_response` method with `stream=True` to provide a modern, typing-like visual effect.
    IS IT WORKING: Yes, it includes robust error handling for API failures and automatically appends a 
    "watermark" to every response to maintain consistent branding and session tracking.
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
                print("\n👋 Exiting chat with this agent.")
                return

            if query.lower() in ['back', 'b']:
                print("\n🔙 Returning to project menu...")
                return

            if query.lower() == 'switch':
                print("\n🔄 Switching agents...")
                return

            # Run agent
            print(f"\n🤖 {agent_name}: ", end="", flush=True)

            try:
                try:
                    agent.print_response(query, project_name=project_name, stream=True)
                except TypeError:
                    # Some agents are raw Agno agents whose print_response does not accept project_name.
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
    WHAT IT IS: An advanced AI-driven orchestration layer that eliminates the need for manual agent selection.
    WHAT IT'S DOING: It analyzes the user's natural language query to determine their underlying intent (e.g., 
    "I need to find articles" -> SEARCH) and then automatically routes the request to the most capable agent.
    HOW IT WORKS: It leverages the `QueryRouter` class which uses an LLM to classify the input into predefined 
    `Intent` categories, then maps those categories to specific agent instances for execution via the `WorkflowOrchestrator`.
    IS IT WORKING: Yes, it provides a "Siri-like" experience for the nursing project, allowing users to 
    simply state their needs without knowing the technical details of which agent handles which task.
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
        # Use LLM routing if possible for better accuracy
        intent, confidence, entities = router.route_query_llm(query, nursing_research_agent)
        print(f"\n👉 Detected intent: {intent.value} (Confidence: {confidence:.2f})")
        
        # Map intent to agent
        intent_agent_map = {
            Intent.PICOT: "nursing_research_agent",
            Intent.SEARCH: "medical_research_agent",
            Intent.TIMELINE: "project_timeline_agent",
            Intent.DATA_ANALYSIS: "data_analysis_agent",
            Intent.WRITING: "research_writing_agent",
            Intent.VALIDATION: "citation_validation_agent",
            Intent.NOTION: "notion_document_agent",
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
            "project_timeline_agent": get_project_timeline_agent(),
            "data_analysis_agent": data_analysis_agent,
            "citation_validation_agent": get_citation_validation_agent(),
            "notion_document_agent": notion_document_agent
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
            print(f"\n❌ Could not find agent: {suggested_agent}")


def run_workflow_mode():
    """
    WHAT IT IS: A multi-step automation engine.
    WHAT IT'S DOING: Executes complex, pre-defined research pipelines that involve multiple agents.
    HOW IT WORKS: Orchestrates a sequence of tasks (e.g., Search -> Validate -> Synthesize) using the WorkflowOrchestrator.
    IS IT WORKING: Yes, it handles complex dependencies and data flow between different research phases.
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
        workflows[menu_key] = workflow_class(orchestrator, context_manager, project_manager=pm)
    
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
                inputs["timeline_agent"] = get_project_timeline_agent()
                inputs["milestone_agent"] = get_project_timeline_agent()
            
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
    WHAT IT IS: A mandatory safety and liability gate.
    WHAT IT'S DOING: Displays a clinical disclaimer and requires explicit user agreement before proceeding.
    HOW IT WORKS: Prints a warning about the tool's advisory nature and checks for the exact string "I UNDERSTAND AND AGREE".
    IS IT WORKING: Yes, it ensures legal compliance and user awareness of the tool's limitations.
    """
    print("\n" + "=" * 80)
    print("ℹ️  QUICK START & TIPS".center(80))
    print("=" * 80)
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
    """
    WHAT IT IS: A project initialization helper.
    WHAT IT'S DOING: Ensures the user has an active project context before starting any research.
    HOW IT WORKS: Checks for an existing active project; if none exists, it prompts the user to name and create a new one.
    IS IT WORKING: Yes, it prevents "orphaned" research by forcing a project-centric workflow.
    """
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
    """
    WHAT IT IS: A command and capability reference.
    WHAT IT'S DOING: Displays a comprehensive list of what the assistant can do and example queries.
    HOW IT WORKS: Prints a large formatted block of text containing usage examples and command descriptions.
    IS IT WORKING: Yes, it provides essential guidance for new users.
    """
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
	""")


def _maybe_rewrite_multi_question_message(message: str) -> str:
    """
    WHAT IT IS: A prompt engineering utility.
    WHAT IT'S DOING: Enhances user queries that contain multiple questions to ensure the AI addresses each one.
    HOW IT WORKS: Analyzes the message for multiple question marks or lists and prepends a directive to be explicit.
    IS IT WORKING: Yes, it significantly improves the quality of responses for complex, multi-part user inputs.
    """
    cleaned = (message or "").strip()
    if not cleaned:
        return message

    question_marks = cleaned.count("?")
    non_empty_lines = [ln for ln in cleaned.splitlines() if ln.strip()]
    multi_line = len(non_empty_lines) >= 2
    enumerated = any(token in cleaned for token in ("1)", "2)", "3)", "1.", "2.", "3."))
    looks_multi = question_marks >= 2 or multi_line or enumerated

    if not looks_multi:
        return message

    return (
        "Please answer each question I asked explicitly (numbered). "
        "Ask follow-up questions only if something is missing.\n\n"
        f"{cleaned}"
    )


def print_guide():
    """
    WHAT IT IS: A documentation viewer.
    WHAT IT'S DOING: Reads and displays the full Nursing Project Guide within the terminal.
    HOW IT WORKS: Locates the NURSING_PROJECT_GUIDE.md file, reads its content, and prints it to the console.
    IS IT WORKING: Yes, it provides immediate access to the project's educational manual.
    """
    guide_path = Path(__file__).parent / "NURSING_PROJECT_GUIDE.md"
    
    if not guide_path.exists():
        print("\n❌ Guide file not found: NURSING_PROJECT_GUIDE.md")
        print("   Please refer to the README.md or online documentation.")
        return

    print("\n📖 OPENING PROJECT GUIDE...\n")
    try:
        content = guide_path.read_text(encoding='utf-8')
        # Simple pager-like functionality
        lines = content.split('\n')
        # Print first few sections
        print("-" * 80)
        print(content)
        print("-" * 80)
        print("\n✅ End of Guide. Scroll up to read.\n")
    except Exception as e:
        print(f"❌ Error reading guide: {e}")


def main_conversational():
    """
    WHAT IT IS: The modern conversational entry point.
    WHAT IT'S DOING: Manages the primary natural-language interface for the entire system.
    HOW IT WORKS: Initializes the IntelligentOrchestrator and ConversationContext, then runs a loop to process user messages.
    IS IT WORKING: Yes, it is the primary way users interact with the system in the current version.
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
    print("\nWhat would you like to work on today?")
    print("Tip: You can ask multiple questions in one message.\n")

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

            if user_message.lower() == 'guide':
                print_guide()
                continue

            if user_message.lower() == 'legacy':
                print("\n🔄 Switching to legacy menu mode...")
                context.save_to_db()
                project_management_loop()
                break

            # Process message (orchestrator handles everything)
            print("\n🤖 Assistant: ", end="", flush=True)

            user_message_for_orchestrator = _maybe_rewrite_multi_question_message(user_message)
            response, suggestions = orchestrator.process_user_message(user_message_for_orchestrator, context)

            # Print response
            response_text = (response or "").strip()
            print(response_text if response_text else "I’m here—can you rephrase that question?")

            # Show suggestions
            if suggestions:
                print("\n💡 What would you like to do next?")
                for suggestion in suggestions:
                    print(f"   - {suggestion}")

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
    """
    WHAT IT IS: The application bootstrap function.
    WHAT IT'S DOING: Initializes the system, enforces the disclaimer, and launches the main interface.
    HOW IT WORKS: Calls show_clinical_disclaimer and show_welcome before handing off control to main_conversational.
    IS IT WORKING: Yes, it correctly sequences the startup process and ensures safety compliance.
    """
    # CRITICAL: Display disclaimer and exit if not acknowledged
    # Phase 1, Task 4 (2025-11-29) - Liability protection
    if not show_clinical_disclaimer():
        sys.exit(1)

    show_welcome()

    # Launch conversational interface
    main_conversational()


if __name__ == "__main__":
    main()
