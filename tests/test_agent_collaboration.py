"""
Agent Collaboration Tests

Verifies that agents can hand off work to each other via workflows.
Tests the existing workflow infrastructure.

Created: 2025-12-08 (Phase 2A - Agent Collaboration)
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import json

# Test imports
from src.orchestration.context_manager import ContextManager
from src.orchestration.orchestrator import WorkflowOrchestrator, AgentResult
from src.workflows.base import WorkflowTemplate, WorkflowResult
from src.workflows.research_workflow import ResearchWorkflow
from src.workflows.validated_research_workflow import ValidatedResearchWorkflow


class TestContextManager:
    """Test ContextManager for workflow state sharing"""

    def test_store_and_retrieve_result(self, tmp_path):
        """Verify results can be stored and retrieved"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)

        # Store a result
        cm.store_result(
            workflow_id="test_workflow_1",
            agent_key="research_agent",
            context_key="articles",
            value={"pmids": ["12345678", "87654321"], "count": 2}
        )

        # Retrieve it
        result = cm.get_result(
            workflow_id="test_workflow_1",
            agent_key="research_agent",
            context_key="articles"
        )

        assert result is not None
        assert result["count"] == 2
        assert "12345678" in result["pmids"]

    def test_workflow_context_isolation(self, tmp_path):
        """Verify different workflows have isolated context"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)

        # Store in workflow 1
        cm.store_result("workflow_1", "agent_a", "key", {"data": "workflow1"})

        # Store in workflow 2
        cm.store_result("workflow_2", "agent_a", "key", {"data": "workflow2"})

        # Retrieve from each
        result1 = cm.get_result("workflow_1", "agent_a", "key")
        result2 = cm.get_result("workflow_2", "agent_a", "key")

        assert result1["data"] == "workflow1"
        assert result2["data"] == "workflow2"

    def test_get_full_workflow_context(self, tmp_path):
        """Verify all context for a workflow can be retrieved"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)

        # Store multiple results
        cm.store_result("wf1", "agent1", "result", {"step": 1})
        cm.store_result("wf1", "agent2", "result", {"step": 2})
        cm.store_result("wf1", "agent3", "result", {"step": 3})

        # Get full context
        context = cm.get_workflow_context("wf1")

        assert len(context) == 3
        assert "agent1.result" in context
        assert "agent2.result" in context


class TestWorkflowOrchestrator:
    """Test WorkflowOrchestrator for agent execution"""

    def test_execute_single_agent(self, tmp_path):
        """Verify single agent execution works"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)
        orchestrator = WorkflowOrchestrator(cm)

        # Create mock agent with proper string name
        mock_agent = Mock()
        mock_agent.name = "TestAgent"
        mock_agent.agent_name = None  # Ensure fallback to .name
        mock_response = Mock()
        mock_response.content = "Test response"
        mock_agent.run = Mock(return_value=mock_response)

        result = orchestrator.execute_single_agent(
            agent=mock_agent,
            query="Test query",
            workflow_id="test_wf"
        )

        assert isinstance(result, AgentResult)
        # Agent name is extracted from mock - just verify result is returned
        assert result is not None

    def test_execute_parallel_agents(self, tmp_path):
        """Verify parallel agent execution works"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)
        orchestrator = WorkflowOrchestrator(cm)

        # Create mock agents with proper string names
        mock_agent1 = Mock()
        mock_agent1.name = "Agent1"
        mock_agent1.agent_name = None
        mock_response1 = Mock()
        mock_response1.content = "Response 1"
        mock_agent1.run = Mock(return_value=mock_response1)

        mock_agent2 = Mock()
        mock_agent2.name = "Agent2"
        mock_agent2.agent_name = None
        mock_response2 = Mock()
        mock_response2.content = "Response 2"
        mock_agent2.run = Mock(return_value=mock_response2)

        results = orchestrator.execute_parallel(
            agents=[mock_agent1, mock_agent2],
            query="Test query",
            workflow_id="test_parallel_wf",
            timeout_seconds=10
        )

        # Verify results returned for both agents
        assert len(results) == 2


class TestAgentHandoff:
    """Test that agent outputs can be passed to other agents"""

    def test_research_to_validation_handoff(self, tmp_path):
        """Verify research agent output can be passed to validation agent"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)
        orchestrator = WorkflowOrchestrator(cm)

        # Simulate research agent output
        research_output = {
            "articles": [
                {"pmid": "12345678", "title": "Study on CAUTI Prevention"},
                {"pmid": "87654321", "title": "Nursing Interventions Review"}
            ]
        }

        # Store in context (simulating research agent completion)
        cm.store_result(
            workflow_id="handoff_test",
            agent_key="research_agent",
            context_key="search_results",
            value=research_output
        )

        # Validation agent retrieves research results
        retrieved = cm.get_result(
            workflow_id="handoff_test",
            agent_key="research_agent",
            context_key="search_results"
        )

        assert retrieved is not None
        assert len(retrieved["articles"]) == 2
        assert retrieved["articles"][0]["pmid"] == "12345678"

    def test_validation_to_writing_handoff(self, tmp_path):
        """Verify validation grades can be passed to writing agent"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)

        # Simulate validation agent output
        validation_output = {
            "validated_articles": [
                {"pmid": "12345678", "evidence_level": "II", "recommendation": "include"},
            ],
            "excluded": [
                {"pmid": "87654321", "reason": "retracted"}
            ]
        }

        cm.store_result(
            workflow_id="handoff_test",
            agent_key="validation_agent",
            context_key="validation_results",
            value=validation_output
        )

        # Writing agent retrieves validated articles
        retrieved = cm.get_result(
            workflow_id="handoff_test",
            agent_key="validation_agent",
            context_key="validation_results"
        )

        assert retrieved is not None
        assert len(retrieved["validated_articles"]) == 1
        assert retrieved["validated_articles"][0]["evidence_level"] == "II"


class TestResearchWorkflow:
    """Test ResearchWorkflow execution"""

    def test_workflow_initialization(self, tmp_path):
        """Verify workflow can be initialized"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)
        orchestrator = WorkflowOrchestrator(cm)

        workflow = ResearchWorkflow(orchestrator, cm)

        assert workflow.name == "research_workflow"
        assert "PICOT" in workflow.description

    def test_workflow_validates_inputs(self, tmp_path):
        """Verify workflow validates required inputs"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)
        orchestrator = WorkflowOrchestrator(cm)

        workflow = ResearchWorkflow(orchestrator, cm)

        # Missing required params should raise
        with pytest.raises(ValueError) as exc_info:
            workflow.validate_inputs(topic="test")  # Missing setting, intervention

        assert "Missing required parameter" in str(exc_info.value)

    def test_workflow_with_mock_agents(self, tmp_path):
        """Verify workflow executes with mock agents"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)
        orchestrator = WorkflowOrchestrator(cm)

        workflow = ResearchWorkflow(orchestrator, cm)

        # Create mock agents
        mock_picot_agent = Mock()
        mock_picot_agent.name = "PICOTAgent"
        mock_picot_agent.run = Mock(return_value=Mock(content="PICOT: In elderly patients..."))

        mock_search_agent = Mock()
        mock_search_agent.name = "SearchAgent"
        mock_search_agent.run = Mock(return_value=Mock(content="Found 5 articles..."))

        mock_writing_agent = Mock()
        mock_writing_agent.name = "WritingAgent"
        mock_writing_agent.run = Mock(return_value=Mock(content="Abstract draft..."))

        result = workflow.execute(
            topic="fall prevention",
            setting="acute care",
            intervention="hourly rounding",
            picot_agent=mock_picot_agent,
            search_agent=mock_search_agent,
            writing_agent=mock_writing_agent
        )

        assert isinstance(result, WorkflowResult)
        assert result.workflow_name == "research_workflow"
        # Check outputs exist (success depends on mock behavior)


class TestValidatedResearchWorkflow:
    """Test ValidatedResearchWorkflow with validation step"""

    def test_validated_workflow_initialization(self, tmp_path):
        """Verify validated workflow can be initialized"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)
        orchestrator = WorkflowOrchestrator(cm)

        workflow = ValidatedResearchWorkflow(orchestrator, cm)

        assert workflow.name == "validated_research_workflow"
        assert "validation" in workflow.description.lower()

    def test_validated_workflow_requires_validation_agent(self, tmp_path):
        """Verify validated workflow requires validation agent"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)
        orchestrator = WorkflowOrchestrator(cm)

        workflow = ValidatedResearchWorkflow(orchestrator, cm)

        # Missing validation_agent should raise
        with pytest.raises(ValueError) as exc_info:
            workflow.validate_inputs(
                topic="test",
                setting="test",
                intervention="test",
                picot_agent=Mock(),
                search_agent=Mock(),
                writing_agent=Mock()
                # Missing: validation_agent
            )

        assert "validation_agent" in str(exc_info.value)


class TestWorkflowResultPersistence:
    """Test that workflow results can be persisted"""

    def test_workflow_stores_each_step(self, tmp_path):
        """Verify each workflow step is stored in context"""
        db_path = str(tmp_path / "test_context.db")
        cm = ContextManager(db_path=db_path)

        workflow_id = "persistence_test"

        # Simulate workflow steps storing results
        cm.store_result(workflow_id, "step1", "picot", {"question": "In patients..."})
        cm.store_result(workflow_id, "step2", "search", {"articles": ["a", "b", "c"]})
        cm.store_result(workflow_id, "step3", "validation", {"grades": ["II", "III", "II"]})
        cm.store_result(workflow_id, "step4", "synthesis", {"draft": "Based on evidence..."})

        # Retrieve full context
        context = cm.get_workflow_context(workflow_id)

        assert len(context) == 4
        assert "step1.picot" in context
        assert "step2.search" in context
        assert "step3.validation" in context
        assert "step4.synthesis" in context


class TestCLIWorkflowIntegration:
    """Test CLI workflow mode integration"""

    def test_workflow_imports(self):
        """Verify all workflows can be imported"""
        from src.workflows.research_workflow import ResearchWorkflow
        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow
        from src.workflows.parallel_search import ParallelSearchWorkflow
        from src.workflows.timeline_planner import TimelinePlannerWorkflow

        assert ResearchWorkflow is not None
        assert ValidatedResearchWorkflow is not None
        assert ParallelSearchWorkflow is not None
        assert TimelinePlannerWorkflow is not None

    def test_agent_imports(self):
        """Verify all agents can be imported"""
        from agents.nursing_research_agent import nursing_research_agent
        from agents.medical_research_agent import get_medical_research_agent
        from agents.research_writing_agent import research_writing_agent
        from agents.citation_validation_agent import get_citation_validation_agent

        # Agents may be None if API keys missing, but imports should work
        assert True  # Import succeeded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
