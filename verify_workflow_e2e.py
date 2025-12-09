import sys
import os
import asyncio
import sqlite3
import json
from pathlib import Path

# 1. Setup Path
sys.path.append(os.getcwd())
_project_root = Path(__file__).parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))

async def run_probe():
    print("\n🏥 STARTING FINAL SIMULATION")
    print("==========================")
    
    try:
        # Import everything 
        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow
        from src.orchestration.orchestrator import WorkflowOrchestrator
        from src.orchestration.context_manager import ContextManager
        from agents.nursing_research_agent import nursing_research_agent
        from agents.medical_research_agent import get_medical_research_agent
        from agents.citation_validation_agent import get_citation_validation_agent
        from agents.research_writing_agent import research_writing_agent

        # Init
        # We use 'project.db' so it saves to your real database
        cm = ContextManager(db_path="project.db")
        wf = ValidatedResearchWorkflow(WorkflowOrchestrator(cm), cm)
        
        # Inject Agents
        payload = {
            "topic": "Fall prevention", "setting": "Geriatric Ward", "intervention": "Bed alarms",
            "picot_agent": nursing_research_agent,
            "search_agent": get_medical_research_agent(),      
            "validation_agent": get_citation_validation_agent(), 
            "writing_agent": research_writing_agent,           
        }

        print("⏳ Agents are working... (This hits the LLM, wait ~30s)")
        result = wf.execute(**payload)
        
        if result.success:
            print("\n✅ WORKFLOW SUCCEEDED")
            print("-" * 30)
            
            # Print a snippet of the synthesis
            synthesis = result.outputs.get('synthesis', '')
            print(f"📝 Synthesis Preview:\n{synthesis[:300]}...\n")

            # Verify DB
            conn = sqlite3.connect("project.db")
            row = conn.execute("SELECT id, created_at FROM workflow_outputs ORDER BY id DESC LIMIT 1").fetchone()
            conn.close()
            
            if row:
                print(f"🎉 DATABASE SUCCESS: Report saved! (Record ID: {row[0]})")
                print("We are done. Go rest.")
            else:
                print("⚠️ Workflow finished, but DB save check failed.")
        else:
            print(f"❌ FAILED: {result.error}")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_probe())
