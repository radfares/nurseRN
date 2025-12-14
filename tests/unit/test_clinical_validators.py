"""
Unit tests for clinical validators.
Gate 2: Validator implementations (SampleSize, Timeline, Budget).

Tests validate the rules from V2 plan:
- Sample Size: n ≤ 500, n ≤ capacity, n ≥ 30, effect size [-3, 3]
- Timeline: duration ≥ 2 weeks, duration ≤ 24 months, feasibility, no past dates
- Budget: total ≤ $100k, per-patient $0-$500, labor calculation, itemized
"""

import pytest
from datetime import datetime, timedelta


class TestSampleSizeValidator:
    """Test SampleSizeValidator implementation."""

    def test_import_validator(self):
        """Test that SampleSizeValidator can be imported."""
        from src.validation.sample_size_validator import SampleSizeValidator
        assert SampleSizeValidator is not None

    def test_sample_size_valid(self):
        """Test validation passes for valid sample size."""
        from src.validation.sample_size_validator import SampleSizeValidator

        validator = SampleSizeValidator()
        result = validator.validate({
            "n": 100,
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": 0.5
        })

        assert result.valid is True
        assert len(result.issues) == 0

    def test_sample_size_too_large_absolute(self):
        """Test Rule 1: n > 500 rejected."""
        from src.validation.sample_size_validator import SampleSizeValidator

        validator = SampleSizeValidator()
        result = validator.validate({
            "n": 600,
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": 0.5
        })

        assert result.valid is False
        assert any("500" in issue.message for issue in result.issues)
        assert any(issue.severity == "error" for issue in result.issues)

    def test_sample_size_exceeds_capacity(self):
        """Test Rule 2: n > capacity rejected."""
        from src.validation.sample_size_validator import SampleSizeValidator

        validator = SampleSizeValidator()
        # Capacity = 30 beds × 2 patients/bed/month × 6 months = 360
        result = validator.validate({
            "n": 400,
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": 0.5
        })

        assert result.valid is False
        assert any("capacity" in issue.message.lower() for issue in result.issues)

    def test_sample_size_too_small(self):
        """Test Rule 3: n < 30 rejected."""
        from src.validation.sample_size_validator import SampleSizeValidator

        validator = SampleSizeValidator()
        result = validator.validate({
            "n": 20,
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": 0.5
        })

        assert result.valid is False
        assert any("30" in issue.message for issue in result.issues)

    def test_effect_size_out_of_range_high(self):
        """Test Rule 4: effect size > 3 rejected."""
        from src.validation.sample_size_validator import SampleSizeValidator

        validator = SampleSizeValidator()
        result = validator.validate({
            "n": 100,
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": 4.0
        })

        assert result.valid is False
        assert any("effect size" in issue.message.lower() for issue in result.issues)

    def test_effect_size_out_of_range_low(self):
        """Test Rule 4: effect size < -3 rejected."""
        from src.validation.sample_size_validator import SampleSizeValidator

        validator = SampleSizeValidator()
        result = validator.validate({
            "n": 100,
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": -4.0
        })

        assert result.valid is False
        assert any("effect size" in issue.message.lower() for issue in result.issues)

    def test_edge_case_n_equals_500(self):
        """Test boundary: n = 500 exactly is valid."""
        from src.validation.sample_size_validator import SampleSizeValidator

        validator = SampleSizeValidator()
        result = validator.validate({
            "n": 500,
            "unit_beds": 100,
            "duration_months": 12,
            "effect_size": 0.5
        })

        assert result.valid is True

    def test_edge_case_n_equals_30(self):
        """Test boundary: n = 30 exactly is valid."""
        from src.validation.sample_size_validator import SampleSizeValidator

        validator = SampleSizeValidator()
        result = validator.validate({
            "n": 30,
            "unit_beds": 30,
            "duration_months": 6,
            "effect_size": 0.5
        })

        assert result.valid is True


class TestTimelineValidator:
    """Test TimelineValidator implementation."""

    def test_import_validator(self):
        """Test that TimelineValidator can be imported."""
        from src.validation.timeline_validator import TimelineValidator
        assert TimelineValidator is not None

    def test_timeline_valid(self):
        """Test validation passes for valid timeline."""
        from src.validation.timeline_validator import TimelineValidator

        validator = TimelineValidator()
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=90)

        result = validator.validate({
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "n": 100,
            "shifts_per_week": 5
        })

        assert result.valid is True

    def test_duration_too_short(self):
        """Test Rule 1: duration < 2 weeks rejected."""
        from src.validation.timeline_validator import TimelineValidator

        validator = TimelineValidator()
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=10)

        result = validator.validate({
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "n": 50,
            "shifts_per_week": 5
        })

        assert result.valid is False
        assert any("2 weeks" in issue.message.lower() for issue in result.issues)

    def test_duration_too_long(self):
        """Test Rule 2: duration > 24 months rejected."""
        from src.validation.timeline_validator import TimelineValidator

        validator = TimelineValidator()
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=800)  # > 24 months

        result = validator.validate({
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "n": 100,
            "shifts_per_week": 5
        })

        assert result.valid is False
        assert any("24 months" in issue.message.lower() for issue in result.issues)

    def test_data_collection_rate_infeasible(self):
        """Test Rule 3: data collection rate too high."""
        from src.validation.timeline_validator import TimelineValidator

        validator = TimelineValidator()
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=30)

        # 500 samples in 30 days with 5 shifts/week = ~25 patients/shift (infeasible)
        result = validator.validate({
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "n": 500,
            "shifts_per_week": 5
        })

        assert result.valid is False
        assert any("rate" in issue.message.lower() or "per shift" in issue.message.lower() for issue in result.issues)

    def test_start_date_in_past(self):
        """Test Rule 4: start date in past rejected."""
        from src.validation.timeline_validator import TimelineValidator

        validator = TimelineValidator()
        start_date = datetime.now().date() - timedelta(days=10)
        end_date = start_date + timedelta(days=90)

        result = validator.validate({
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "n": 100,
            "shifts_per_week": 5
        })

        assert result.valid is False
        assert any("past" in issue.message.lower() for issue in result.issues)

    def test_edge_case_14_days(self):
        """Test boundary: 14 days (2 weeks) exactly is valid."""
        from src.validation.timeline_validator import TimelineValidator

        validator = TimelineValidator()
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=14)

        result = validator.validate({
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "n": 30,
            "shifts_per_week": 5
        })

        assert result.valid is True


class TestBudgetValidator:
    """Test BudgetValidator implementation."""

    def test_import_validator(self):
        """Test that BudgetValidator can be imported."""
        from src.validation.budget_validator import BudgetValidator
        assert BudgetValidator is not None

    def test_budget_valid(self):
        """Test validation passes for valid budget."""
        from src.validation.budget_validator import BudgetValidator

        validator = BudgetValidator()
        result = validator.validate({
            "total_cost": 50000,
            "n": 100,
            "labor_hours": 200,
            "hourly_rate": 50,
            "materials": [
                {"item": "Supplies", "unit_price": 10, "quantity": 100}
            ]
        })

        assert result.valid is True

    def test_total_cost_exceeds_limit(self):
        """Test Rule 1: total > $100k rejected."""
        from src.validation.budget_validator import BudgetValidator

        validator = BudgetValidator()
        result = validator.validate({
            "total_cost": 150000,
            "n": 100,
            "labor_hours": 200,
            "hourly_rate": 50,
            "materials": []
        })

        assert result.valid is False
        assert any("100" in issue.message for issue in result.issues)

    def test_per_patient_cost_too_high(self):
        """Test Rule 2: per-patient > $500 rejected."""
        from src.validation.budget_validator import BudgetValidator

        validator = BudgetValidator()
        result = validator.validate({
            "total_cost": 60000,
            "n": 100,  # $600 per patient
            "labor_hours": 200,
            "hourly_rate": 50,
            "materials": []
        })

        assert result.valid is False
        assert any("per-patient" in issue.message.lower() or "per patient" in issue.message.lower() for issue in result.issues)

    def test_labor_calculation_incorrect(self):
        """Test Rule 3: labor_hours × hourly_rate validation."""
        from src.validation.budget_validator import BudgetValidator

        validator = BudgetValidator()
        # Labor should be 200 × 50 = 10000, but total is way off
        result = validator.validate({
            "total_cost": 5000,
            "n": 100,
            "labor_hours": 200,
            "hourly_rate": 50,
            "materials": []
        })

        # Should warn if labor calculation doesn't match
        assert any("labor" in issue.message.lower() for issue in result.issues)

    def test_materials_not_itemized(self):
        """Test Rule 4: materials must be itemized."""
        from src.validation.budget_validator import BudgetValidator

        validator = BudgetValidator()
        result = validator.validate({
            "total_cost": 20000,
            "n": 100,
            "labor_hours": 100,
            "hourly_rate": 50,
            "materials": None  # Missing itemization
        })

        assert result.valid is False
        assert any("materials" in issue.message.lower() or "itemized" in issue.message.lower() for issue in result.issues)

    def test_edge_case_100k_exactly(self):
        """Test boundary: $100k exactly is valid."""
        from src.validation.budget_validator import BudgetValidator

        validator = BudgetValidator()
        result = validator.validate({
            "total_cost": 100000,
            "n": 200,
            "labor_hours": 1000,
            "hourly_rate": 50,
            "materials": []
        })

        assert result.valid is True
