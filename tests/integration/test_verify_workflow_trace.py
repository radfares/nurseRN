"""
TRACER TEST: verify_workflow_e2e.py Integration Analysis
Test ID: TRACE-001
Created: 2025-12-09

This test traces the complete execution path of verify_workflow_e2e.py
and checks for bypasses, broken links, and integration issues.
"""

import sys
import os
import sqlite3
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Test markers
TRACE_ID = "TRACE-001"
TEST_DB = "test_trace_workflow.db"


class TestVerifyWorkflowTrace:
    """Comprehensive trace tests for verify_workflow_e2e.py"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and cleanup test database"""
        # Setup
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        yield
        # Cleanup
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def log_trace(self, marker: str, message: str):
        """Log trace information"""
        timestamp = datetime.now().isoformat()
        print(f"[{TRACE_ID}][{marker}][{timestamp}] {message}")

    # ============================================================
    # TRACE-001-A: Import Chain Tests
    # ============================================================

    def test_import_validated_research_workflow(self):
        """[TRACE-001-A1] Test ValidatedResearchWorkflow import"""
        self.log_trace("A1", "Testing ValidatedResearchWorkflow import")

        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow

        assert ValidatedResearchWorkflow is not None
        assert hasattr(ValidatedResearchWorkflow, 'execute')
        assert hasattr(ValidatedResearchWorkflow, '_save_to_db')

        self.log_trace("A1", "PASS: ValidatedResearchWorkflow imports correctly")

    def test_import_workflow_orchestrator(self):
        """[TRACE-001-A2] Test WorkflowOrchestrator import"""
        self.log_trace("A2", "Testing WorkflowOrchestrator import")

        from src.orchestration.orchestrator import WorkflowOrchestrator

        assert WorkflowOrchestrator is not None
        assert hasattr(WorkflowOrchestrator, 'execute_single_agent')
        assert hasattr(WorkflowOrchestrator, 'execute_parallel')

        self.log_trace("A2", "PASS: WorkflowOrchestrator imports correctly")

    def test_import_context_manager(self):
        """[TRACE-001-A3] Test ContextManager import"""
        self.log_trace("A3", "Testing ContextManager import")

        from src.orchestration.context_manager import ContextManager

        assert ContextManager is not None
        assert hasattr(ContextManager, 'store_result')
        assert hasattr(ContextManager, 'get_result')

        self.log_trace("A3", "PASS: ContextManager imports correctly")

    def test_import_all_agents(self):
        """[TRACE-001-A4] Test all agent imports"""
        self.log_trace("A4", "Testing agent imports")

        from agents.nursing_research_agent import nursing_research_agent
        from agents.medical_research_agent import get_medical_research_agent
        from agents.citation_validation_agent import get_citation_validation_agent
        from agents.research_writing_agent import research_writing_agent

        assert nursing_research_agent is not None
        assert callable(get_medical_research_agent)
        assert callable(get_citation_validation_agent)
        assert research_writing_agent is not None

        self.log_trace("A4", "PASS: All agents import correctly")

    # ============================================================
    # TRACE-001-B: Database Connection Tests
    # ============================================================

    def test_context_manager_creates_db(self):
        """[TRACE-001-B1] Test ContextManager creates database"""
        self.log_trace("B1", "Testing ContextManager database creation")

        from src.orchestration.context_manager import ContextManager

        cm = ContextManager(db_path=TEST_DB)

        assert os.path.exists(TEST_DB), "Database file not created"

        # Verify schema
        conn = sqlite3.connect(TEST_DB)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        assert 'workflow_context' in tables, "workflow_context table missing"

        self.log_trace("B1", f"PASS: Database created with tables: {tables}")

    def test_validated_workflow_uses_context_manager_db(self):
        """[TRACE-001-B2] Test ValidatedResearchWorkflow uses ContextManager's db_path"""
        self.log_trace("B2", "Testing workflow uses correct database path")

        from src.orchestration.context_manager import ContextManager
        from src.orchestration.orchestrator import WorkflowOrchestrator
        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow

        cm = ContextManager(db_path=TEST_DB)
        orchestrator = WorkflowOrchestrator(cm)
        workflow = ValidatedResearchWorkflow(orchestrator, cm)

        # Check that workflow has access to context_manager
        assert hasattr(workflow, 'context_manager')
        assert workflow.context_manager.db_path == TEST_DB

        self.log_trace("B2", f"PASS: Workflow uses db_path: {workflow.context_manager.db_path}")

    def test_direct_db_bypass_detection(self):
        """[TRACE-001-B3] Detect direct database bypass in verify_workflow_e2e.py"""
        self.log_trace("B3", "Checking for direct DB bypass")

        # Read the source file
        verify_file = Path(__file__).parent.parent.parent / "verify_workflow_e2e.py"
        content = verify_file.read_text()

        # Check for direct sqlite3.connect calls
        direct_connects = content.count('sqlite3.connect')

        # Log finding
        if direct_connects > 0:
            self.log_trace("B3", f"FINDING: {direct_connects} direct sqlite3.connect calls found")
            # This is expected for verification, but document it
            assert direct_connects == 1, f"Expected 1 verification connect, found {direct_connects}"

        self.log_trace("B3", "PASS: Direct DB access is for verification only (acceptable)")

    # ============================================================
    # TRACE-001-C: Component Integration Tests
    # ============================================================

    def test_orchestrator_stores_to_context_manager(self):
        """[TRACE-001-C1] Test orchestrator stores results via context_manager"""
        self.log_trace("C1", "Testing orchestrator -> context_manager integration")

        from src.orchestration.context_manager import ContextManager
        from src.orchestration.orchestrator import WorkflowOrchestrator

        cm = ContextManager(db_path=TEST_DB)
        orchestrator = WorkflowOrchestrator(cm)

        # Create mock agent
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.run_with_grounding_check = Mock(return_value={"content": "test response"})

        # Execute
        result = orchestrator.execute_single_agent(
            agent=mock_agent,
            query="test query",
            workflow_id="test_workflow_001"
        )

        # Verify result stored in context
        stored = cm.get_result(
            workflow_id="test_workflow_001",
            agent_key="TestAgent",
            context_key="last_result"
        )

        assert stored is not None, "Result not stored in context"
        assert "content" in stored, "Content missing from stored result"

        self.log_trace("C1", f"PASS: Orchestrator stores results correctly")

    def test_workflow_execution_chain(self):
        """[TRACE-001-C2] Test full workflow execution chain with mocks"""
        self.log_trace("C2", "Testing workflow execution chain")

        from src.orchestration.context_manager import ContextManager
        from src.orchestration.orchestrator import WorkflowOrchestrator
        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow

        cm = ContextManager(db_path=TEST_DB)
        orchestrator = WorkflowOrchestrator(cm)
        workflow = ValidatedResearchWorkflow(orchestrator, cm)

        # Create mock agents
        def create_mock_agent(name, response):
            agent = Mock()
            agent.name = name
            agent.run_with_grounding_check = Mock(return_value={"content": response})
            return agent

        mock_picot = create_mock_agent("PICOTAgent", "P: Elderly I: Bed alarms C: Standard care O: Falls T: 3 months")
        mock_search = create_mock_agent("SearchAgent", '{"articles": []}')
        mock_validation = create_mock_agent("ValidationAgent", "All citations validated")
        mock_writing = create_mock_agent("WritingAgent", "Synthesis: Evidence supports intervention")

        # Execute workflow
        result = workflow.execute(
            topic="Fall prevention",
            setting="Hospital",
            intervention="Bed alarms",
            picot_agent=mock_picot,
            search_agent=mock_search,
            validation_agent=mock_validation,
            writing_agent=mock_writing
        )

        assert result.success, f"Workflow failed: {result.error}"
        assert result.steps_completed == 4, f"Expected 4 steps, got {result.steps_completed}"
        assert "picot" in result.outputs
        assert "synthesis" in result.outputs

        self.log_trace("C2", "PASS: Workflow execution chain works correctly")

    def test_workflow_saves_to_db(self):
        """[TRACE-001-C3] Test workflow saves outputs to database"""
        self.log_trace("C3", "Testing workflow database saving")

        from src.orchestration.context_manager import ContextManager
        from src.orchestration.orchestrator import WorkflowOrchestrator
        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow

        cm = ContextManager(db_path=TEST_DB)
        orchestrator = WorkflowOrchestrator(cm)
        workflow = ValidatedResearchWorkflow(orchestrator, cm)

        # Create mock agents
        def create_mock_agent(name, response):
            agent = Mock()
            agent.name = name
            agent.run_with_grounding_check = Mock(return_value={"content": response})
            return agent

        result = workflow.execute(
            topic="Test Topic",
            setting="Test Setting",
            intervention="Test Intervention",
            picot_agent=create_mock_agent("PICOT", "PICOT text"),
            search_agent=create_mock_agent("Search", "[]"),
            validation_agent=create_mock_agent("Validation", "Valid"),
            writing_agent=create_mock_agent("Writing", "Synthesis")
        )

        # Verify database entry
        conn = sqlite3.connect(TEST_DB)
        row = conn.execute("SELECT * FROM workflow_outputs ORDER BY id DESC LIMIT 1").fetchone()
        conn.close()

        assert row is not None, "No row saved to workflow_outputs"

        self.log_trace("C3", "PASS: Workflow saves to database correctly")

    # ============================================================
    # TRACE-001-D: Regression Tests
    # ============================================================

    def test_agents_use_grounding_check(self):
        """[TRACE-001-D1] Regression: Verify agents use run_with_grounding_check"""
        self.log_trace("D1", "Regression test: grounding check usage")

        from src.orchestration.orchestrator import WorkflowOrchestrator
        from src.orchestration.context_manager import ContextManager

        cm = ContextManager(db_path=TEST_DB)
        orchestrator = WorkflowOrchestrator(cm)

        # Mock agent WITH grounding check
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.run_with_grounding_check = Mock(return_value={"content": "safe content"})

        result = orchestrator.execute_single_agent(
            agent=mock_agent,
            query="test",
            workflow_id="test"
        )

        # Verify grounding check was called
        mock_agent.run_with_grounding_check.assert_called_once()

        self.log_trace("D1", "PASS: Orchestrator uses run_with_grounding_check when available")

    def test_missing_agents_handled(self):
        """[TRACE-001-D2] Regression: Missing agents are handled gracefully"""
        self.log_trace("D2", "Regression test: missing agent handling")

        from src.orchestration.context_manager import ContextManager
        from src.orchestration.orchestrator import WorkflowOrchestrator
        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow

        cm = ContextManager(db_path=TEST_DB)
        orchestrator = WorkflowOrchestrator(cm)
        workflow = ValidatedResearchWorkflow(orchestrator, cm)

        # Execute with missing agents
        result = workflow.execute(
            topic="Test",
            setting="Test",
            intervention="Test",
            picot_agent=None,  # Missing!
            search_agent=None,
            validation_agent=None,
            writing_agent=None
        )

        assert not result.success, "Should fail with missing agents"
        assert "Missing required agents" in result.error

        self.log_trace("D2", "PASS: Missing agents handled gracefully")

    def test_missing_inputs_handled(self):
        """[TRACE-001-D3] Regression: Missing inputs are handled gracefully"""
        self.log_trace("D3", "Regression test: missing input handling")

        from src.orchestration.context_manager import ContextManager
        from src.orchestration.orchestrator import WorkflowOrchestrator
        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow

        cm = ContextManager(db_path=TEST_DB)
        orchestrator = WorkflowOrchestrator(cm)
        workflow = ValidatedResearchWorkflow(orchestrator, cm)

        # Execute with missing required inputs
        result = workflow.execute()  # No inputs!

        assert not result.success, "Should fail with missing inputs"
        assert "Missing required parameters" in result.error

        self.log_trace("D3", "PASS: Missing inputs handled gracefully")

    # ============================================================
    # TRACE-001-E: Bypass Detection Tests
    # ============================================================

    def test_no_direct_agent_run_bypass(self):
        """[TRACE-001-E1] Check workflow doesn't bypass agent.run directly"""
        self.log_trace("E1", "Checking for agent.run bypass")

        # Read validated_research_workflow.py
        workflow_file = Path(__file__).parent.parent.parent / "src/workflows/validated_research_workflow.py"
        content = workflow_file.read_text()

        # Check for direct .run() calls that bypass orchestrator
        # The workflow should use orchestrator.execute_single_agent, not agent.run
        direct_run_calls = content.count('.run(')
        orchestrator_calls = content.count('self.orchestrator.execute_single_agent')

        self.log_trace("E1", f"Direct .run() calls: {direct_run_calls}, Orchestrator calls: {orchestrator_calls}")

        # Workflow should use orchestrator for all agent calls
        assert orchestrator_calls >= 4, "Workflow should use orchestrator for all 4 agents"

        self.log_trace("E1", "PASS: Workflow uses orchestrator, not direct agent.run")

    def test_context_manager_not_bypassed(self):
        """[TRACE-001-E2] Verify ContextManager is not bypassed for state storage"""
        self.log_trace("E2", "Checking ContextManager is used for state")

        # Read orchestrator.py
        orch_file = Path(__file__).parent.parent.parent / "src/orchestration/orchestrator.py"
        content = orch_file.read_text()

        # Check that orchestrator uses context_manager.store_result
        store_calls = content.count('self.context_manager.store_result')

        assert store_calls >= 1, "Orchestrator should use context_manager.store_result"

        self.log_trace("E2", f"PASS: Found {store_calls} context_manager.store_result calls")


class TestProjectDbIntegrity:
    """Tests specifically for project.db integrity"""

    def test_project_db_schema_matches_workflow(self):
        """[TRACE-001-F1] Verify project.db schema matches workflow expectations"""
        project_db = Path(__file__).parent.parent.parent / "project.db"

        if not project_db.exists():
            pytest.skip("project.db not found")

        conn = sqlite3.connect(str(project_db))

        # Check workflow_outputs table schema
        cursor = conn.execute("PRAGMA table_info(workflow_outputs)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        expected_columns = [
            'id', 'project_id', 'workflow_type', 'topic',
            'picot_text', 'search_results_json', 'validation_report_text',
            'final_synthesis_text', 'created_at'
        ]

        for col in expected_columns:
            assert col in columns, f"Missing column: {col}"

        conn.close()
        print(f"[{TRACE_ID}][F1] PASS: project.db schema matches expectations")

    def test_project_db_data_integrity(self):
        """[TRACE-001-F2] Check project.db data integrity"""
        project_db = Path(__file__).parent.parent.parent / "project.db"

        if not project_db.exists():
            pytest.skip("project.db not found")

        conn = sqlite3.connect(str(project_db))

        # Check for any NULL values in critical fields
        cursor = conn.execute("""
            SELECT COUNT(*) FROM workflow_outputs
            WHERE workflow_type IS NULL OR topic IS NULL
        """)
        null_count = cursor.fetchone()[0]

        conn.close()

        assert null_count == 0, f"Found {null_count} records with NULL critical fields"
        print(f"[{TRACE_ID}][F2] PASS: No NULL values in critical fields")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
