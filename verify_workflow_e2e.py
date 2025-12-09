import sys
import os
import asyncio
import json
from pathlib import Path

# 1. Setup Path (Crucial for finding the 'agents' folder)
sys.path.append(os.getcwd())

# Add the 'libs/agno' path just like your main app does (to avoid missing dependencies)
_project_root = Path(__file__).parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))

print("🔍 INITIALIZING AGENT PROBE...")

try:
    # 2. Import Workflow Infrastructure
    from src.workflows.validated_research_workflow import ValidatedResearchWorkflow
    from src.orchestration.orchestrator import WorkflowOrchestrator
    from src.orchestration.context_manager import ContextManager
    print("✅ Infrastructure imported.")

    # 3. Import Agents (Using the exact paths from your grep/sed output)
    from agents.nursing_research_agent import nursing_research_agent
    from agents.medical_research_agent import get_medical_research_agent
    from agents.citation_validation_agent import get_citation_validation_agent
    from agents.research_writing_agent import research_writing_agent
    print("✅ Agents imported successfully.")

except ImportError as e:
    print(f"❌ CRITICAL IMPORT ERROR: {e}")
    sys.exit(1)

async def run_probe():
    print("\n🏥 STARTING SIMULATION")
    print("======================")

    payload = {
        "topic": "Fall prevention",
        "setting": "Geriatric Ward",
        "intervention": "Bed alarms"
    }
    
    print(f"INPUT PAYLOAD: {payload}\n")

    try:
        # 1. Initialize System
        # We use a temp DB so we don't mess up your main project.db
        context_manager = ContextManager(db_path="probe_test.db")
        orchestrator = WorkflowOrchestrator(context_manager)
        workflow = ValidatedResearchWorkflow(orchestrator, context_manager)
        
        # 2. Inject Agents (The missing piece!)
        full_payload = {
            **payload,
            # We match the 'inputs' logic from run_nursing_project.py exactly:
            "picot_agent": nursing_research_agent,
            "search_agent": get_medical_research_agent(),      # Function call
            "validation_agent": get_citation_validation_agent(), # Function call
            "writing_agent": research_writing_agent,           # Instance
        }

        print("✅ Agents injected.")
        print("⏳ Executing Workflow... (This hits the LLM, please wait 30-60s)")
        
        # 3. Execute
        # Note: We do NOT use 'await' here because your previous error proved .execute() is synchronous
        result = workflow.execute(**full_payload)
        
        # 4. Inspect Results
        print("\n📦 RAW OUTPUT RECEIVED")
        print("=====================")
        
        if result is None:
            print("❌ Result is None.")
        else:
            # Check success status
            if hasattr(result, 'success'):
                status = "✅ SUCCESS" if result.success else "❌ FAILURE"
                print(f"Status: {status}")
                if not result.success and hasattr(result, 'error'):
                    print(f"Error Message: {result.error}")
            
            # Print the actual content
            print("\n--- OUTPUT CONTENT ---")
            if hasattr(result, 'outputs'):
                print(json.dumps(result.outputs, indent=2, default=str))
            elif hasattr(result, 'to_dict'):
                print(json.dumps(result.to_dict(), indent=2, default=str))
            else:
                print(result)

    except Exception as e:
        print(f"❌ EXECUTION ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(run_probe())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
