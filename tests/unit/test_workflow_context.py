"""
Unit Tests for WorkflowContext
Tests state tracking and validation for guided workflow.

Created: 2025-11-29 (Phase 1, Task 1)
"""

import pytest
from datetime import datetime
from src.orchestration.workflow_context import WorkflowContext, WorkflowError


class TestWorkflowContextCreation:
    """Test WorkflowContext instantiation."""

    def test_create_with_project_name(self):
        """Test creating context with project name."""
        ctx = WorkflowContext(project_name="test_project")
        assert ctx.project_name == "test_project"

    def test_defaults_are_none(self):
        """Test that all optional fields default to None or empty."""
        ctx = WorkflowContext(project_name="test")
        assert ctx.picot_id is None
        assert ctx.picot_text is None
        assert ctx.search_query is None
        assert ctx.finding_ids == []
        assert ctx.draft_id is None
        assert ctx.plan_id is None
        assert ctx.sample_size is None
        assert ctx.statistical_method is None
        assert ctx.export_path is None

    def test_started_at_is_set(self):
        """Test that started_at timestamp is automatically set."""
        ctx = WorkflowContext(project_name="test")
        assert isinstance(ctx.started_at, datetime)
        assert ctx.started_at <= datetime.now()


class TestValidationForSearch:
    """Test validate_for_search() method."""

    def test_fails_without_picot(self):
        """Test that validation fails when PICOT missing."""
        ctx = WorkflowContext(project_name="test")
        with pytest.raises(WorkflowError) as exc_info:
            ctx.validate_for_search()
        assert "PICOT not created" in str(exc_info.value)
        assert "Step 1" in str(exc_info.value)

    def test_passes_with_picot_text(self):
        """Test that validation passes when PICOT exists."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_text = "In elderly patients, does hourly rounding reduce falls?"
        assert ctx.validate_for_search() is True

    def test_passes_with_both_picot_fields(self):
        """Test that validation passes with both picot_text and picot_id."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_text = "Test PICOT question"
        ctx.picot_id = 1
        assert ctx.validate_for_search() is True


class TestValidationForWriting:
    """Test validate_for_writing() method."""

    def test_fails_without_findings(self):
        """Test that validation fails when no literature found."""
        ctx = WorkflowContext(project_name="test")
        with pytest.raises(WorkflowError) as exc_info:
            ctx.validate_for_writing()
        assert "no literature found" in str(exc_info.value)
        assert "Step 2" in str(exc_info.value)

    def test_passes_with_findings(self):
        """Test that validation passes when findings exist."""
        ctx = WorkflowContext(project_name="test")
        ctx.finding_ids = [1, 2, 3]
        assert ctx.validate_for_writing() is True

    def test_passes_with_single_finding(self):
        """Test that validation passes with even one finding."""
        ctx = WorkflowContext(project_name="test")
        ctx.finding_ids = [42]
        assert ctx.validate_for_writing() is True


class TestValidationForCalculation:
    """Test validate_for_calculation() method."""

    def test_fails_without_picot(self):
        """Test that validation fails without PICOT."""
        ctx = WorkflowContext(project_name="test")
        ctx.finding_ids = [1, 2, 3]  # Has findings but no PICOT
        with pytest.raises(WorkflowError) as exc_info:
            ctx.validate_for_calculation()
        assert "PICOT not created" in str(exc_info.value)

    def test_fails_without_findings(self):
        """Test that validation fails without literature."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_text = "Test PICOT"  # Has PICOT but no findings
        with pytest.raises(WorkflowError) as exc_info:
            ctx.validate_for_calculation()
        assert "no literature" in str(exc_info.value)

    def test_passes_with_both_prerequisites(self):
        """Test that validation passes with PICOT and findings."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_text = "Test PICOT"
        ctx.finding_ids = [1, 2, 3]
        assert ctx.validate_for_calculation() is True


class TestValidationForExport:
    """Test validate_for_export() method."""

    def test_fails_without_picot(self):
        """Test that export validation fails without PICOT."""
        ctx = WorkflowContext(project_name="test")
        ctx.finding_ids = [1, 2, 3]
        ctx.sample_size = 100
        with pytest.raises(WorkflowError) as exc_info:
            ctx.validate_for_export()
        assert "PICOT missing" in str(exc_info.value)

    def test_fails_without_findings(self):
        """Test that export validation fails without literature."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_text = "Test PICOT"
        ctx.sample_size = 100
        with pytest.raises(WorkflowError) as exc_info:
            ctx.validate_for_export()
        assert "no literature findings" in str(exc_info.value)

    def test_fails_without_sample_size(self):
        """Test that export validation fails without sample size."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_text = "Test PICOT"
        ctx.finding_ids = [1, 2, 3]
        # No sample_size set
        with pytest.raises(WorkflowError) as exc_info:
            ctx.validate_for_export()
        assert "sample size not calculated" in str(exc_info.value)

    def test_passes_with_all_prerequisites(self):
        """Test that export validation passes with all requirements."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_text = "Test PICOT"
        ctx.finding_ids = [1, 2, 3]
        ctx.sample_size = 100
        assert ctx.validate_for_export() is True


class TestProgressTracking:
    """Test get_progress() method."""

    def test_zero_percent_on_creation(self):
        """Test that new context shows 0% progress."""
        ctx = WorkflowContext(project_name="test")
        progress = ctx.get_progress()
        assert progress['percent_complete'] == 0
        assert progress['steps_complete'] == 0
        assert progress['total_steps'] == 5

    def test_twenty_percent_after_picot(self):
        """Test that progress is 20% after PICOT completion."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_id = 1
        progress = ctx.get_progress()
        assert progress['percent_complete'] == 20
        assert progress['steps_complete'] == 1
        assert progress['step_1_picot'] is True

    def test_forty_percent_after_search(self):
        """Test that progress is 40% after PICOT + Search."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_id = 1
        ctx.finding_ids = [1, 2, 3]
        progress = ctx.get_progress()
        assert progress['percent_complete'] == 40
        assert progress['steps_complete'] == 2
        assert progress['step_1_picot'] is True
        assert progress['step_2_search'] is True

    def test_sixty_percent_after_writing(self):
        """Test that progress is 60% after PICOT + Search + Writing."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_id = 1
        ctx.finding_ids = [1, 2, 3]
        ctx.draft_id = 1
        progress = ctx.get_progress()
        assert progress['percent_complete'] == 60
        assert progress['steps_complete'] == 3

    def test_eighty_percent_after_calculation(self):
        """Test that progress is 80% after first 4 steps."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_id = 1
        ctx.finding_ids = [1, 2, 3]
        ctx.draft_id = 1
        ctx.sample_size = 100
        progress = ctx.get_progress()
        assert progress['percent_complete'] == 80
        assert progress['steps_complete'] == 4

    def test_hundred_percent_after_export(self):
        """Test that progress is 100% after all steps."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_id = 1
        ctx.finding_ids = [1, 2, 3]
        ctx.draft_id = 1
        ctx.sample_size = 100
        ctx.export_path = "/path/to/proposal.pdf"
        progress = ctx.get_progress()
        assert progress['percent_complete'] == 100
        assert progress['steps_complete'] == 5
        assert all([
            progress['step_1_picot'],
            progress['step_2_search'],
            progress['step_3_writing'],
            progress['step_4_calculate'],
            progress['step_5_export']
        ])


class TestStringRepresentation:
    """Test __str__() method."""

    def test_string_includes_project_name(self):
        """Test that string representation includes project name."""
        ctx = WorkflowContext(project_name="fall_prevention")
        result = str(ctx)
        assert "fall_prevention" in result

    def test_string_includes_progress(self):
        """Test that string representation includes progress percentage."""
        ctx = WorkflowContext(project_name="test")
        ctx.picot_id = 1
        ctx.finding_ids = [1, 2]
        result = str(ctx)
        assert "40%" in result
        assert "2/5" in result


class TestWorkflowError:
    """Test WorkflowError exception."""

    def test_is_exception(self):
        """Test that WorkflowError is an Exception."""
        error = WorkflowError("Test message")
        assert isinstance(error, Exception)

    def test_message_preserved(self):
        """Test that error message is preserved."""
        message = "Cannot proceed - missing prerequisites"
        error = WorkflowError(message)
        assert str(error) == message

    def test_can_be_caught(self):
        """Test that WorkflowError can be caught specifically."""
        ctx = WorkflowContext(project_name="test")
        caught = False
        try:
            ctx.validate_for_search()
        except WorkflowError:
            caught = True
        except Exception:
            caught = False
        assert caught is True
