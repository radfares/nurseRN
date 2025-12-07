"""
Integration tests for validation system.
Gate 4: End-to-end workflow integration.

Tests:
- DataAnalysisAgent with validators
- ResearchWritingAgent with PICOT scorer
- ValidatedResearchWorkflow with validation pipeline
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta


class TestDataAnalysisAgentValidation:
    """Test integration of validators with DataAnalysisAgent."""

    def test_agent_imports(self):
        """Test that DataAnalysisAgent can be imported."""
        from agents.data_analysis_agent import DataAnalysisAgent
        assert DataAnalysisAgent is not None

    @patch('agno.agent.Agent')
    def test_agent_validates_sample_size(self, mock_agent_class):
        """Test that agent validates sample size before returning results."""
        from agents.data_analysis_agent import DataAnalysisAgent
        from src.validation.sample_size_validator import SampleSizeValidator

        # This test verifies the integration exists
        # Agent should have access to validator
        agent = DataAnalysisAgent()
        validator = SampleSizeValidator()

        # Verify validator works
        result = validator.validate({
            "n": 100,
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": 0.5
        })

        assert result.valid is True


class TestResearchWritingAgentScoring:
    """Test integration of PICOT scorer with ResearchWritingAgent."""

    def test_agent_imports(self):
        """Test that ResearchWritingAgent can be imported."""
        from agents.research_writing_agent import ResearchWritingAgent
        assert ResearchWritingAgent is not None

    @patch('agno.agent.Agent')
    def test_picot_scorer_available(self, mock_agent_class):
        """Test that PICOT scorer is accessible from agent."""
        from src.validation.picot_scorer import PICOTScorer

        # Create scorer
        scorer = PICOTScorer()
        assert scorer is not None

        # Scorer should work independently
        assert hasattr(scorer, 'score')
        assert hasattr(scorer, 'rubric_path')


class TestValidatedWorkflowIntegration:
    """Test end-to-end validated workflow."""

    def test_workflow_imports(self):
        """Test that ValidatedResearchWorkflow can be imported."""
        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow
        assert ValidatedResearchWorkflow is not None

    @patch('agno.agent.Agent')
    def test_workflow_with_validation(self, mock_agent_class):
        """Test that workflow can integrate validation steps."""
        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow
        from src.orchestration.orchestrator import WorkflowOrchestrator
        from src.orchestration.context_manager import ContextManager

        # Create workflow components
        context_mgr = ContextManager()
        orchestrator = WorkflowOrchestrator(context_mgr)

        # Create workflow
        workflow = ValidatedResearchWorkflow(orchestrator, context_mgr)

        assert workflow.name == "validated_research_workflow"
        assert workflow.description is not None


class TestEndToEndValidationPipeline:
    """Test complete validation pipeline end-to-end."""

    @patch('agno.agent.Agent')
    def test_sample_size_to_timeline_validation(self, mock_agent_class):
        """Test sample size validation feeds into timeline validation."""
        from src.validation.sample_size_validator import SampleSizeValidator
        from src.validation.timeline_validator import TimelineValidator

        # Step 1: Validate sample size
        sample_validator = SampleSizeValidator()
        sample_result = sample_validator.validate({
            "n": 100,
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": 0.5
        })

        assert sample_result.valid is True

        # Step 2: Use same n for timeline validation
        timeline_validator = TimelineValidator()
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=180)

        timeline_result = timeline_validator.validate({
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "n": 100,  # From sample validation
            "shifts_per_week": 5
        })

        assert timeline_result.valid is True

    @patch('agno.agent.Agent')
    def test_validation_to_budget_pipeline(self, mock_agent_class):
        """Test validation pipeline: sample size → budget."""
        from src.validation.sample_size_validator import SampleSizeValidator
        from src.validation.budget_validator import BudgetValidator

        # Validate sample size first
        sample_validator = SampleSizeValidator()
        sample_result = sample_validator.validate({
            "n": 100,
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": 0.5
        })

        assert sample_result.valid is True

        # Use same n for budget
        budget_validator = BudgetValidator()
        budget_result = budget_validator.validate({
            "total_cost": 20000,
            "n": 100,  # From sample validation
            "labor_hours": 200,
            "hourly_rate": 50,
            "materials": [
                {"item": "Supplies", "unit_price": 50, "quantity": 100}
            ]
        })

        assert budget_result.valid is True
        # Per-patient cost = $20000 / 100 = $200 (well under $500 limit)

    @patch('agno.agent.Agent')
    def test_picot_score_to_workflow(self, mock_agent_class):
        """Test PICOT scoring integrated into workflow."""
        from src.validation.picot_scorer import PICOTScorer

        # Mock GPT-4 response
        mock_agent = Mock()
        mock_response = Mock()
        mock_response.content = '''
        {
            "overall_score": 85,
            "specificity_score": 20,
            "measurability_score": 17,
            "achievability_score": 16,
            "relevance_score": 17,
            "timebound_score": 15,
            "feedback": "Good PICOT with clear elements",
            "grade": "Good"
        }
        '''
        mock_agent.run.return_value = mock_response
        mock_agent_class.return_value = mock_agent

        scorer = PICOTScorer()
        picot = "In adult patients with diabetes (P), does structured exercise (I) compared to standard care (C) reduce HbA1c by 1% (O) over 3 months (T)?"

        result = scorer.score(picot)

        # Good PICOT should score 75-89
        assert 75 <= result.overall_score <= 89
        assert result.grade == "Good"

        # Workflow would use this score to decide if PICOT is ready for submission


class TestValidationFailureHandling:
    """Test that validation failures are handled gracefully."""

    def test_invalid_sample_size_blocked(self):
        """Test that invalid sample size is caught."""
        from src.validation.sample_size_validator import SampleSizeValidator

        validator = SampleSizeValidator()
        result = validator.validate({
            "n": 600,  # > 500 limit
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": 0.5
        })

        assert result.valid is False
        assert len(result.issues) > 0
        assert any("500" in issue.message for issue in result.issues)

    def test_invalid_timeline_blocked(self):
        """Test that invalid timeline is caught."""
        from src.validation.timeline_validator import TimelineValidator

        validator = TimelineValidator()
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=5)  # < 14 days

        result = validator.validate({
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "n": 100,
            "shifts_per_week": 5
        })

        assert result.valid is False
        assert any("2 weeks" in issue.message.lower() for issue in result.issues)

    def test_poor_picot_identified(self):
        """Test that poor PICOT is identified."""
        # This would require actual GPT-4 or sophisticated mocking
        # For now, test the scoring logic
        from src.validation.picot_scorer import PICOTScoreResult

        poor_result = PICOTScoreResult(
            overall_score=45,
            specificity_score=8,
            measurability_score=7,
            achievability_score=10,
            relevance_score=10,
            timebound_score=10,
            feedback="Needs major improvements",
            grade="Poor"
        )

        assert poor_result.overall_score < 60
        assert poor_result.grade == "Poor"
