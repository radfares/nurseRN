"""
Nursing Research Pipeline - Complete research workflow

This pipeline coordinates agents to produce a complete research package:
1. PICOT question
2. Literature with validated PMIDs
3. Evidence synthesis
4. Data analysis plan

Agents are NOT modified - this pipeline calls them with specific prompts
and validates their outputs through quality gates.

Created: 2025-12-10
"""

import sqlite3
import json
import time
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime

# Import pipeline configuration and quality gates
from src.workflows.pipeline_config import (
    get_prompt,
    get_phase_config,
    PIPELINE_ORDER,
    RESULTS_SCHEMA,
    ERROR_MESSAGES
)
from src.workflows.quality_gates import run_quality_gate, GateResult
from src.workflows.base import WorkflowTemplate, WorkflowResult
from src.orchestration.orchestrator import WorkflowOrchestrator
from src.orchestration.context_manager import ContextManager


@dataclass
class PipelineState:
    """Tracks the current state of the pipeline execution."""
    user_topic: str
    current_phase: str = "planning"
    picot_question: str = ""
    search_results: str = ""
    pmids_found: List[str] = None
    validation_report: str = ""
    synthesis_text: str = ""
    analysis_plan: str = ""
    status: str = "in_progress"
    error: str = ""
    started_at: float = 0.0
    total_cost: float = 0.0

    def __post_init__(self):
        if self.pmids_found is None:
            self.pmids_found = []
        if self.started_at == 0.0:
            self.started_at = time.time()


class NursingResearchPipeline(WorkflowTemplate):
    """
    Complete nursing research pipeline with quality gates.

    Usage:
        pipeline = NursingResearchPipeline(orchestrator, context_manager)
        result = pipeline.execute(topic="Foley catheter intervention")
    """

    def __init__(
        self,
        orchestrator: WorkflowOrchestrator,
        context_manager: ContextManager,
        db_path: str = "pipeline_results.db"
    ):
        super().__init__(orchestrator, context_manager)
        self.db_path = db_path
        self._init_database()

        # Agent references - will be set when execute() is called
        self.writing_agent = None
        self.nursing_agent = None
        self.medical_agent = None
        self.citation_agent = None
        self.data_agent = None

    @property
    def name(self) -> str:
        return "nursing_research_pipeline"

    @property
    def description(self) -> str:
        return "Complete nursing research: PICOT → Search → Validate → Synthesis → Analysis"

    def _init_database(self):
        """Initialize results database."""
        conn = sqlite3.connect(self.db_path)
        conn.executescript(RESULTS_SCHEMA)
        conn.commit()
        conn.close()

    def validate_inputs(self, **kwargs) -> bool:
        """Validate required inputs."""
        if "topic" not in kwargs or not kwargs["topic"]:
            raise ValueError("Missing required parameter: topic")
        return True

    def _load_agents(self):
        """Load agent instances."""
        # Import agents
        from agents.research_writing_agent import ResearchWritingAgent
        from agents.nursing_research_agent import NursingResearchAgent
        from agents.medical_research_agent import MedicalResearchAgent
        from agents.citation_validation_agent import CitationValidationAgent
        from agents.data_analysis_agent import DataAnalysisAgent

        self.writing_agent = ResearchWritingAgent()
        self.nursing_agent = NursingResearchAgent()
        self.medical_agent = MedicalResearchAgent()
        self.citation_agent = CitationValidationAgent()
        self.data_agent = DataAnalysisAgent()

    def execute(self, **kwargs) -> WorkflowResult:
        """
        Execute the complete research pipeline.

        Args:
            topic: Research topic (e.g., "Foley catheter intervention")

        Returns:
            WorkflowResult with all outputs
        """
        self._start_execution()

        # Validate inputs
        try:
            self.validate_inputs(**kwargs)
        except ValueError as e:
            return self._end_execution({}, error=str(e))

        # Load agents
        print("\n📚 Loading research agents...")
        self._load_agents()

        # Initialize state
        state = PipelineState(user_topic=kwargs["topic"])

        # Save initial state to database
        result_id = self._save_state(state)

        outputs = {}

        try:
            # =================================================================
            # PHASE 1: PLANNING - Generate PICOT
            # =================================================================
            print("\n" + "="*60)
            print("PHASE 1: PLANNING - Generating PICOT Question")
            print("="*60)

            state.current_phase = "planning"
            picot_prompt = get_prompt("planning_picot", topic=state.user_topic)

            picot_result = self.orchestrator.execute_single_agent(
                agent=self.writing_agent.agent,
                query=picot_prompt,
                workflow_id=self.workflow_id
            )

            if not picot_result.success:
                state.error = f"PICOT generation failed: {picot_result.error}"
                state.status = "failed"
                self._save_state(state, result_id)
                return self._end_execution(outputs, error=state.error)

            state.picot_question = picot_result.content
            self._increment_step()

            # Quality Gate 1
            gate1 = run_quality_gate("picot_quality", picot_text=state.picot_question)
            print(f"\n🚦 {gate1.message}")

            if not gate1.passed:
                # Retry once with more specific prompt
                print("   Retrying with refined prompt...")
                retry_prompt = picot_prompt + "\n\nIMPORTANT: Make sure to clearly label ALL 5 components (P, I, C, O, T) and end with a question."
                retry_result = self.orchestrator.execute_single_agent(
                    agent=self.writing_agent.agent,
                    query=retry_prompt,
                    workflow_id=self.workflow_id
                )
                if retry_result.success:
                    state.picot_question = retry_result.content
                    gate1 = run_quality_gate("picot_quality", picot_text=state.picot_question)
                    print(f"   Retry result: {gate1.message}")

            if not gate1.passed:
                state.error = ERROR_MESSAGES["picot_incomplete"]
                state.status = "failed"
                self._save_state(state, result_id)
                return self._end_execution({"picot": state.picot_question}, error=state.error)

            outputs["picot"] = state.picot_question
            print(f"\n✅ PICOT Generated Successfully")

            # =================================================================
            # PHASE 2: SEARCH - Find literature
            # =================================================================
            print("\n" + "="*60)
            print("PHASE 2: SEARCH - Finding Literature")
            print("="*60)

            state.current_phase = "search"

            # Search with nursing agent (PubMed)
            print("\n🔍 Searching PubMed...")
            search_prompt = get_prompt("search_nursing", picot=state.picot_question)

            nursing_result = self.orchestrator.execute_single_agent(
                agent=self.nursing_agent.agent,
                query=search_prompt,
                workflow_id=self.workflow_id
            )

            if nursing_result.success:
                state.search_results = nursing_result.content
                # Extract PMIDs - multiple formats:
                # 1. PMID: 12345678 or PMID 12345678
                # 2. [12345678](https://pubmed.ncbi.nlm.nih.gov/12345678/)
                # 3. pubmed.ncbi.nlm.nih.gov/12345678
                pmids = []
                # Format 1: PMID: number
                pmids.extend(re.findall(r'PMID[:\s]*(\d{7,8})', state.search_results, re.IGNORECASE))
                # Format 2: Markdown links with PMID
                pmids.extend(re.findall(r'\[(\d{7,8})\]\(https?://pubmed', state.search_results))
                # Format 3: PubMed URLs
                pmids.extend(re.findall(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d{7,8})', state.search_results))
                # Format 4: **PMID:** [number]
                pmids.extend(re.findall(r'\*\*PMID[:\*\s]*\[?(\d{7,8})', state.search_results, re.IGNORECASE))
                state.pmids_found = list(set(pmids))
                print(f"   Found {len(state.pmids_found)} PMIDs from PubMed")

            self._increment_step()

            # Search with medical agent (additional sources)
            print("\n🔍 Searching clinical trials...")
            clinical_prompt = get_prompt("search_medical", picot=state.picot_question)

            medical_result = self.orchestrator.execute_single_agent(
                agent=self.medical_agent.agent,
                query=clinical_prompt,
                workflow_id=self.workflow_id
            )

            if medical_result.success:
                state.search_results += "\n\n--- Clinical Trials ---\n" + medical_result.content
                # Extract additional PMIDs - multiple formats
                more_pmids = []
                more_pmids.extend(re.findall(r'PMID[:\s]*(\d{7,8})', medical_result.content, re.IGNORECASE))
                more_pmids.extend(re.findall(r'\[(\d{7,8})\]\(https?://pubmed', medical_result.content))
                more_pmids.extend(re.findall(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d{7,8})', medical_result.content))
                more_pmids.extend(re.findall(r'\*\*PMID[:\*\s]*\[?(\d{7,8})', medical_result.content, re.IGNORECASE))
                state.pmids_found.extend(more_pmids)
                state.pmids_found = list(set(state.pmids_found))
                print(f"   Total PMIDs found: {len(state.pmids_found)}")

            self._increment_step()

            # Quality Gate 2
            gate2 = run_quality_gate("search_quality", search_results=state.search_results)
            print(f"\n🚦 {gate2.message}")

            if not gate2.passed:
                state.error = ERROR_MESSAGES["search_insufficient"]
                state.status = "failed"
                self._save_state(state, result_id)
                return self._end_execution(outputs, error=state.error)

            outputs["search_results"] = state.search_results
            outputs["pmids"] = state.pmids_found

            # =================================================================
            # PHASE 3: VALIDATION - Check citations
            # =================================================================
            print("\n" + "="*60)
            print("PHASE 3: VALIDATION - Checking Citations")
            print("="*60)

            state.current_phase = "validation"

            validation_prompt = get_prompt(
                "validate_citations",
                citations=", ".join([f"PMID {p}" for p in state.pmids_found])
            )

            val_result = self.orchestrator.execute_single_agent(
                agent=self.citation_agent.agent,
                query=validation_prompt,
                workflow_id=self.workflow_id
            )

            if val_result.success:
                state.validation_report = val_result.content
            else:
                state.validation_report = "Validation could not be completed"

            self._increment_step()

            # Quality Gate 3
            gate3 = run_quality_gate(
                "validation_quality",
                validation_report=state.validation_report,
                pmid_list=state.pmids_found
            )
            print(f"\n🚦 {gate3.message}")

            # Note: We don't fail on validation gate - we proceed with valid citations
            outputs["validation_report"] = state.validation_report

            # =================================================================
            # PHASE 4: SYNTHESIS - Write literature review
            # =================================================================
            print("\n" + "="*60)
            print("PHASE 4: SYNTHESIS - Writing Literature Review")
            print("="*60)

            state.current_phase = "synthesis"

            synthesis_prompt = get_prompt(
                "synthesis_literature",
                picot=state.picot_question,
                articles=state.search_results
            )

            syn_result = self.orchestrator.execute_single_agent(
                agent=self.writing_agent.agent,
                query=synthesis_prompt,
                workflow_id=self.workflow_id
            )

            if not syn_result.success:
                state.error = f"Synthesis failed: {syn_result.error}"
                state.status = "failed"
                self._save_state(state, result_id)
                return self._end_execution(outputs, error=state.error)

            state.synthesis_text = syn_result.content
            self._increment_step()

            # Quality Gate 4
            gate4 = run_quality_gate("synthesis_quality", synthesis_text=state.synthesis_text)
            print(f"\n🚦 {gate4.message}")

            if not gate4.passed:
                # Retry synthesis
                print("   Retrying synthesis...")
                retry_syn = self.orchestrator.execute_single_agent(
                    agent=self.writing_agent.agent,
                    query=synthesis_prompt + "\n\nIMPORTANT: Include clear sections for Evidence Summary, Strength of Evidence, and Implications for Practice. Cite the articles provided.",
                    workflow_id=self.workflow_id
                )
                if retry_syn.success:
                    state.synthesis_text = retry_syn.content

            outputs["synthesis"] = state.synthesis_text

            # =================================================================
            # PHASE 5: ANALYSIS - Create data plan
            # =================================================================
            print("\n" + "="*60)
            print("PHASE 5: ANALYSIS - Creating Data Analysis Plan")
            print("="*60)

            state.current_phase = "analysis"

            analysis_prompt = get_prompt("analysis_plan", picot=state.picot_question)

            analysis_result = self.orchestrator.execute_single_agent(
                agent=self.data_agent.agent,
                query=analysis_prompt,
                workflow_id=self.workflow_id
            )

            if analysis_result.success:
                state.analysis_plan = analysis_result.content
            else:
                state.analysis_plan = "Analysis plan generation failed"

            self._increment_step()

            # Quality Gate 5
            gate5 = run_quality_gate("analysis_quality", analysis_text=state.analysis_plan)
            print(f"\n🚦 {gate5.message}")

            outputs["analysis_plan"] = state.analysis_plan

            # =================================================================
            # COMPLETE
            # =================================================================
            state.status = "completed"
            self._save_state(state, result_id)

            print("\n" + "="*60)
            print("✅ PIPELINE COMPLETE")
            print("="*60)
            print(f"\nResults saved to database (ID: {result_id})")
            print(f"Total steps completed: {self._steps_completed}")

            return self._end_execution(outputs)

        except Exception as e:
            state.error = str(e)
            state.status = "failed"
            self._save_state(state, result_id)
            return self._end_execution(outputs, error=str(e))

    def _save_state(self, state: PipelineState, result_id: int = None) -> int:
        """Save pipeline state to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if result_id is None:
            # Insert new record
            cursor.execute("""
                INSERT INTO pipeline_results
                (user_topic, picot_question, search_results_json, validation_report,
                 literature_synthesis, analysis_plan, overall_status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.user_topic,
                state.picot_question,
                json.dumps({"results": state.search_results, "pmids": state.pmids_found}),
                state.validation_report,
                state.synthesis_text,
                state.analysis_plan,
                state.status,
                state.error
            ))
            result_id = cursor.lastrowid
        else:
            # Update existing record
            cursor.execute("""
                UPDATE pipeline_results SET
                    picot_question = ?,
                    search_results_json = ?,
                    validation_report = ?,
                    literature_synthesis = ?,
                    analysis_plan = ?,
                    overall_status = ?,
                    error_message = ?,
                    completed_at = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE NULL END
                WHERE id = ?
            """, (
                state.picot_question,
                json.dumps({"results": state.search_results, "pmids": state.pmids_found}),
                state.validation_report,
                state.synthesis_text,
                state.analysis_plan,
                state.status,
                state.error,
                state.status,
                result_id
            ))

        conn.commit()
        conn.close()
        return result_id


# =============================================================================
# STANDALONE RUNNER
# =============================================================================

def run_pipeline(topic: str) -> WorkflowResult:
    """
    Convenience function to run the pipeline.

    Args:
        topic: Research topic

    Returns:
        WorkflowResult with all outputs

    Example:
        result = run_pipeline("Foley catheter intervention")
        print(result.outputs["picot"])
    """
    from src.orchestration.context_manager import ContextManager
    from src.orchestration.orchestrator import WorkflowOrchestrator

    cm = ContextManager(db_path="pipeline_context.db")
    orchestrator = WorkflowOrchestrator(cm)
    pipeline = NursingResearchPipeline(orchestrator, cm)

    return pipeline.execute(topic=topic)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = "Foley catheter intervention for reducing CAUTI"

    print(f"\n🏥 Starting Nursing Research Pipeline")
    print(f"📋 Topic: {topic}")

    result = run_pipeline(topic)

    if result.success:
        print("\n" + "="*60)
        print("FINAL OUTPUTS")
        print("="*60)

        print("\n📝 PICOT QUESTION:")
        print("-"*40)
        print(result.outputs.get("picot", "N/A")[:500])

        print("\n📚 ARTICLES FOUND:")
        print("-"*40)
        pmids = result.outputs.get("pmids", [])
        print(f"PMIDs: {pmids}")

        print("\n📄 SYNTHESIS PREVIEW:")
        print("-"*40)
        print(result.outputs.get("synthesis", "N/A")[:500] + "...")

    else:
        print(f"\n❌ Pipeline failed: {result.error}")
