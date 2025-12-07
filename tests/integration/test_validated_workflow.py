"""
Integration tests for ValidatedResearchWorkflow.
Verifies the pipeline: PICOT → Search → Validation → Filtering → Synthesis.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.workflows.validated_research_workflow import ValidatedResearchWorkflow
from src.orchestration.orchestrator import WorkflowOrchestrator
from src.orchestration.orchestrator import WorkflowOrchestrator, AgentResult

class TestValidatedResearchWorkflow:
    """Test the validated research workflow pipeline."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        orchestrator = Mock(spec=WorkflowOrchestrator)
        return orchestrator
        
    @pytest.fixture
    def mock_agents(self):
        return {
            "picot_agent": Mock(),
            "search_agent": Mock(),
            "validation_agent": Mock(),
            "writing_agent": Mock()
        }

    def test_workflow_success_path(self, mock_orchestrator, mock_agents):
        """Test successful execution of the full pipeline."""
        workflow = ValidatedResearchWorkflow(mock_orchestrator, Mock())
        
        # Mock agent responses
        mock_orchestrator.execute_single_agent.side_effect = [
            # 1. PICOT response
            AgentResult(agent_name="picot", success=True, content="PICOT Question: In acute care..."),
            # 2. Search response
            AgentResult(agent_name="search", success=True, content='[{"pmid": "123", "title": "Study 1"}]'),
            # 3. Validation response
            AgentResult(agent_name="validation", success=True, content="Validated: Study 1 (Level I)"),
            # 4. Writing response
            AgentResult(agent_name="writing", success=True, content="Evidence Synthesis: ...")
        ]
        
        result = workflow.execute(
            topic="falls",
            setting="hospital",
            intervention="bed alarm",
            **mock_agents
        )
        
        assert result.success
        assert "picot" in result.outputs
        assert "raw_search_results" in result.outputs
        assert "validation_report" in result.outputs
        assert "synthesis" in result.outputs
        
        # Verify execution order
        assert mock_orchestrator.execute_single_agent.call_count == 4
        
        # Verify validation step received search results
        validation_call = mock_orchestrator.execute_single_agent.call_args_list[2]
        assert "Study 1" in validation_call.kwargs["query"]

    def test_validation_failure_handling(self, mock_orchestrator, mock_agents):
        """Test handling of validation step failure."""
        workflow = ValidatedResearchWorkflow(mock_orchestrator, Mock())
        
        # Mock failure at validation step
        mock_orchestrator.execute_single_agent.side_effect = [
            AgentResult(agent_name="picot", success=True, content="PICOT"),
            AgentResult(agent_name="search", success=True, content="Search Results"),
            AgentResult(agent_name="validation", success=False, error="Validation API Error")
        ]
        
        result = workflow.execute(
            topic="falls",
            setting="hospital",
            intervention="bed alarm",
            **mock_agents
        )
        
        assert not result.success
        assert "Validation step failed" in result.error
        
    def test_missing_inputs(self, mock_orchestrator):
        """Test input validation."""
        workflow = ValidatedResearchWorkflow(mock_orchestrator, Mock())
        
        # Should return failure result, not raise exception
        result = workflow.execute(topic="falls")  # Missing other inputs
            
        assert not result.success
        assert "Missing required parameter" in result.error
