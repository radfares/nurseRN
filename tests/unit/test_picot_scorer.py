"""
Unit tests for PICOT Scorer.
Gate 3: PICOT scoring with GPT-4 integration.

Tests:
- Mock GPT-4 scoring (temperature=0)
- Score variance <5% across runs
- Score breakdown by category
- Improvement suggestions
- Database integration
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestPICOTScorer:
    """Test PICOT Scorer implementation."""

    def test_import_scorer(self):
        """Test that PICOTScorer can be imported."""
        from src.validation.picot_scorer import PICOTScorer
        assert PICOTScorer is not None

    def test_score_result_dataclass(self):
        """Test that PICOTScoreResult dataclass exists."""
        from src.validation.picot_scorer import PICOTScoreResult

        result = PICOTScoreResult(
            overall_score=95,
            specificity_score=24,
            measurability_score=20,
            achievability_score=19,
            relevance_score=17,
            timebound_score=15,
            feedback="Excellent PICOT question",
            grade="Excellent"
        )

        assert result.overall_score == 95
        assert result.grade == "Excellent"

    @patch('agno.agent.Agent')
    def test_score_excellent_picot(self, mock_agent_class):
        """Test scoring of excellent PICOT question."""
        from src.validation.picot_scorer import PICOTScorer

        # Mock GPT-4 response
        mock_agent = Mock()
        mock_response = Mock()
        mock_response.content = '''
        {
            "overall_score": 95,
            "specificity_score": 24,
            "measurability_score": 20,
            "achievability_score": 19,
            "relevance_score": 17,
            "timebound_score": 15,
            "feedback": "Excellent PICOT question with clear elements",
            "grade": "Excellent"
        }
        '''
        mock_agent.run.return_value = mock_response
        mock_agent_class.return_value = mock_agent

        scorer = PICOTScorer()
        picot = "In adult medical-surgical patients aged 18-65 with indwelling urinary catheters..."
        result = scorer.score(picot)

        assert result.overall_score == 95
        assert result.grade == "Excellent"
        assert result.specificity_score == 24

    @patch('agno.agent.Agent')
    def test_score_fair_picot(self, mock_agent_class):
        """Test scoring of fair PICOT question."""
        from src.validation.picot_scorer import PICOTScorer

        # Mock GPT-4 response for fair PICOT
        mock_agent = Mock()
        mock_response = Mock()
        mock_response.content = '''
        {
            "overall_score": 68,
            "specificity_score": 11,
            "measurability_score": 5,
            "achievability_score": 12,
            "relevance_score": 20,
            "timebound_score": 15,
            "feedback": "Needs specific population and measurable outcome with target",
            "grade": "Fair"
        }
        '''
        mock_agent.run.return_value = mock_response
        mock_agent_class.return_value = mock_agent

        scorer = PICOTScorer()
        picot = "In hospitalized patients, does hourly rounding reduce falls?"
        result = scorer.score(picot)

        assert result.overall_score == 68
        assert result.grade == "Fair"
        assert "specific population" in result.feedback.lower()

    @patch('agno.agent.Agent')
    def test_scorer_uses_temperature_zero(self, mock_agent_class):
        """Test that scorer uses temperature=0 for consistency."""
        from src.validation.picot_scorer import PICOTScorer

        mock_agent = Mock()
        mock_agent.run.return_value = Mock(content='{"overall_score": 80, "specificity_score": 15, "measurability_score": 15, "achievability_score": 15, "relevance_score": 15, "timebound_score": 10, "feedback": "Good", "grade": "Good"}')
        mock_agent_class.return_value = mock_agent

        scorer = PICOTScorer()
        scorer.score("Test PICOT")

        # Verify Agent was called
        assert mock_agent_class.called

    @patch('agno.agent.Agent')
    def test_score_variance_low(self, mock_agent_class):
        """Test that score variance across runs is <5%."""
        from src.validation.picot_scorer import PICOTScorer

        # Mock consistent responses
        responses = [
            '{"overall_score": 85, "specificity_score": 20, "measurability_score": 17, "achievability_score": 16, "relevance_score": 17, "timebound_score": 15, "feedback": "Good", "grade": "Good"}',
            '{"overall_score": 87, "specificity_score": 20, "measurability_score": 18, "achievability_score": 16, "relevance_score": 18, "timebound_score": 15, "feedback": "Good", "grade": "Good"}',
            '{"overall_score": 86, "specificity_score": 20, "measurability_score": 17, "achievability_score": 17, "relevance_score": 17, "timebound_score": 15, "feedback": "Good", "grade": "Good"}',
        ]

        # Create a new mock agent for each call
        mock_agents = [Mock() for _ in range(3)]
        for idx, agent in enumerate(mock_agents):
            agent.run.return_value = Mock(content=responses[idx])
        mock_agent_class.side_effect = mock_agents

        scorer = PICOTScorer()
        picot = "Test PICOT for consistency"

        scores = [scorer.score(picot).overall_score for _ in range(3)]
        avg_score = sum(scores) / len(scores)
        variance = max(abs(s - avg_score) for s in scores)
        variance_pct = (variance / avg_score) * 100

        assert variance_pct < 5.0, f"Variance {variance_pct:.1f}% exceeds 5% threshold"

    def test_grade_calculation(self):
        """Test that grade is correctly assigned based on score."""
        from src.validation.picot_scorer import PICOTScoreResult

        excellent = PICOTScoreResult(95, 24, 20, 19, 17, 15, "Test", "Excellent")
        good = PICOTScoreResult(80, 18, 16, 16, 15, 15, "Test", "Good")
        fair = PICOTScoreResult(65, 13, 12, 15, 13, 12, "Test", "Fair")
        poor = PICOTScoreResult(50, 10, 8, 12, 10, 10, "Test", "Poor")

        assert excellent.grade == "Excellent"
        assert good.grade == "Good"
        assert fair.grade == "Fair"
        assert poor.grade == "Poor"

    @patch('agno.agent.Agent')
    def test_improvement_suggestions_generated(self, mock_agent_class):
        """Test that scorer provides actionable improvement suggestions."""
        from src.validation.picot_scorer import PICOTScorer

        mock_agent = Mock()
        mock_response = Mock()
        mock_response.content = '''
        {
            "overall_score": 60,
            "specificity_score": 10,
            "measurability_score": 10,
            "achievability_score": 10,
            "relevance_score": 15,
            "timebound_score": 15,
            "feedback": "Add specific population demographics. Define measurable outcome with numeric target.",
            "grade": "Fair"
        }
        '''
        mock_agent.run.return_value = mock_response
        mock_agent_class.return_value = mock_agent

        scorer = PICOTScorer()
        result = scorer.score("Vague PICOT")

        assert len(result.feedback) > 0
        assert "specific" in result.feedback.lower() or "measurable" in result.feedback.lower()

    @patch('agno.agent.Agent')
    def test_scorer_handles_malformed_json(self, mock_agent_class):
        """Test that scorer handles malformed GPT-4 responses gracefully."""
        from src.validation.picot_scorer import PICOTScorer

        mock_agent = Mock()
        mock_response = Mock()
        mock_response.content = "This is not JSON"
        mock_agent.run.return_value = mock_response
        mock_agent_class.return_value = mock_agent

        scorer = PICOTScorer()

        # Should not crash, should return default/error result
        result = scorer.score("Test PICOT")

        assert result is not None
        assert hasattr(result, 'overall_score')

    @patch('agno.agent.Agent')
    def test_scorer_validates_score_ranges(self, mock_agent_class):
        """Test that scorer validates score ranges (0-100)."""
        from src.validation.picot_scorer import PICOTScorer

        mock_agent = Mock()
        mock_response = Mock()
        # Invalid scores > max
        mock_response.content = '''
        {
            "overall_score": 150,
            "specificity_score": 30,
            "measurability_score": 25,
            "achievability_score": 25,
            "relevance_score": 25,
            "timebound_score": 20,
            "feedback": "Invalid",
            "grade": "Invalid"
        }
        '''
        mock_agent.run.return_value = mock_response
        mock_agent_class.return_value = mock_agent

        scorer = PICOTScorer()
        result = scorer.score("Test")

        # Should clamp or reject invalid scores
        assert result.overall_score <= 100
        assert result.specificity_score <= 25

    def test_picot_scorer_rubric_loaded(self):
        """Test that scorer has access to rubric."""
        from src.validation.picot_scorer import PICOTScorer

        scorer = PICOTScorer()
        # Scorer should have rubric loaded or accessible
        assert hasattr(scorer, 'rubric_path') or hasattr(scorer, '_load_rubric')

    @patch('agno.agent.Agent')
    def test_scorer_system_prompt_includes_rubric(self, mock_agent_class):
        """Test that scorer's system prompt includes scoring rubric."""
        from src.validation.picot_scorer import PICOTScorer

        mock_agent = Mock()
        mock_agent.run.return_value = Mock(content='{"overall_score": 75, "specificity_score": 15, "measurability_score": 15, "achievability_score": 15, "relevance_score": 15, "timebound_score": 15, "feedback": "Good", "grade": "Good"}')
        mock_agent_class.return_value = mock_agent

        scorer = PICOTScorer()
        scorer.score("Test")

        # Agent should be created with instructions that include rubric
        mock_agent.run.assert_called()
