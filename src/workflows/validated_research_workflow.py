import json
import sqlite3
import time
from typing import Dict, Any, Optional
from src.workflows.base import WorkflowTemplate, WorkflowResult
from src.orchestration.orchestrator import WorkflowOrchestrator
from src.orchestration.context_manager import ContextManager

class ValidatedResearchWorkflow(WorkflowTemplate):
    """
    Orchestrates the full flow: PICOT -> Search -> Validation -> Synthesis
    With AUTOMATIC DATABASE SAVING.
    """

    def __init__(self, orchestrator: WorkflowOrchestrator, context_manager: ContextManager):
        # Initialize the parent class
        super().__init__(orchestrator, context_manager)
        # FIX 1: Explicitly save the context manager so we can use it later
        self.context_manager = context_manager

    @property
    def name(self) -> str:
        return "validated_research_workflow"

    @property
    def description(self) -> str:
        return "End-to-end evidence synthesis with validation and DB saving"

    def validate_inputs(self, inputs: Dict[str, Any], required_keys: Optional[list] = None) -> bool:
        if required_keys is None:
            required_keys = ["topic", "setting", "intervention"]
        missing = [key for key in required_keys if key not in inputs]
        return len(missing) == 0

    def execute(self, **inputs) -> WorkflowResult:
        start_time = time.time()
        
        # 1. Validate Inputs
        if not self.validate_inputs(inputs):
            return WorkflowResult(
                workflow_name=self.name, 
                success=False, 
                outputs={},
                execution_time=0.0,
                steps_completed=0,
                error="Missing required parameters"
            )

        # 2. Extract Agents
        picot_agent = inputs.get("picot_agent")
        search_agent = inputs.get("search_agent")
        validation_agent = inputs.get("validation_agent")
        writing_agent = inputs.get("writing_agent")

        if not all([picot_agent, search_agent, validation_agent, writing_agent]):
             return WorkflowResult(
                workflow_name=self.name, 
                success=False, 
                outputs={}, 
                execution_time=0.0,
                steps_completed=0,
                error="Missing required agents."
            )

        try:
            # --- AGENT EXECUTION ---
            print(f"\n🔹 Step 1: Generating PICOT...")
            picot_resp = self.orchestrator.execute_single_agent(
                agent=picot_agent,
                query=f"Create a PICOT question for: Topic={inputs['topic']}, Setting={inputs['setting']}, Intervention={inputs['intervention']}",
                workflow_id="picot_gen"
            )
            picot_text = picot_resp.content if picot_resp else "Failed"

            print("\n🔹 Step 2: Searching Literature...")
            search_resp = self.orchestrator.execute_single_agent(
                agent=search_agent,
                query=f"Find 5 recent peer-reviewed studies for this PICOT: {picot_text}. Return ONLY valid JSON.",
                workflow_id="lit_search"
            )
            search_json = search_resp.content if search_resp else "[]"

            print("\n🔹 Step 3: Validating...")
            val_resp = self.orchestrator.execute_single_agent(
                agent=validation_agent,
                query=f"Validate these studies for retraction status and quality: {search_json}",
                workflow_id="validation"
            )
            val_text = val_resp.content if val_resp else "Failed"

            print("\n🔹 Step 4: Writing Synthesis...")
            write_resp = self.orchestrator.execute_single_agent(
                agent=writing_agent,
                query=f"Write a synthesis report based on: {picot_text}, {search_json}, and {val_text}.",
                workflow_id="synthesis"
            )
            syn_text = write_resp.content if write_resp else "Failed"

            # --- PACKAGING OUTPUTS ---
            outputs = {
                "picot": picot_text,
                "raw_search_results": search_json,
                "validation_report": val_text,
                "synthesis": syn_text
            }

            # --- SAVING TO DB ---
            print("\n💾 Saving results to project database...")
            self._save_to_db(inputs, outputs)

            # FIX 2: Calculate time and steps to satisfy the strict WorkflowResult class
            end_time = time.time()
            return WorkflowResult(
                workflow_name=self.name,
                success=True,
                outputs=outputs,
                execution_time=end_time - start_time,
                steps_completed=4
            )

        except Exception as e:
            # FIX 2: Return required fields even on error
            return WorkflowResult(
                workflow_name=self.name,
                success=False,
                outputs={},
                execution_time=0.0,
                steps_completed=0,
                error=str(e)
            )

    def _save_to_db(self, inputs: Dict, outputs: Dict):
        try:
            # Connect to project.db
            db_path = self.context_manager.db_path
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Create Table if needed
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_outputs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT, 
                workflow_type TEXT, 
                topic TEXT, 
                picot_text TEXT,
                search_results_json TEXT, 
                validation_report_text TEXT,
                final_synthesis_text TEXT, 
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            # Insert Data
            cursor.execute("""
                INSERT INTO workflow_outputs 
                (project_id, workflow_type, topic, picot_text, search_results_json, validation_report_text, final_synthesis_text)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                "active_project", 
                self.name, 
                inputs.get("topic"), 
                outputs.get("picot"),
                str(outputs.get("raw_search_results")), 
                outputs.get("validation_report"),
                outputs.get("synthesis")
            ))

            conn.commit()
            conn.close()
            print("✅ Report saved to 'workflow_outputs' table successfully.")

        except Exception as e:
            print(f"⚠️ Warning: Could not save to DB: {e}")
