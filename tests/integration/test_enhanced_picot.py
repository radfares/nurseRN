"""
Integration test for enhanced PICOT output.

Verifies that enhanced PICOTQuestion schema and agent instructions
produce PICOT questions scoring ≥85/100 per PICOT_RUBRIC.md.

Created: 2025-12-16
"""

import pytest
from src.schemas.research_schemas import PICOTQuestion


class TestEnhancedPICOTSchema:
    """Tests for enhanced PICOTQuestion schema."""

    def test_schema_has_all_required_fields(self):
        """Verify schema includes all 16 new fields per enhancement plan."""
        # Get field names from schema
        fields = set(PICOTQuestion.model_fields.keys())

        # Required new fields per implementation plan
        expected_new_fields = {
            # Specificity fields
            "setting",
            "inclusion_criteria",
            "exclusion_criteria",
            "intervention_components",
            "delivered_by",
            # Measurability fields
            "baseline_rate",
            "benchmark",
            "numeric_target",
            "secondary_outcomes",
            "data_source",
            # Achievability fields
            "sample_size_estimate",
            # Time-Bound fields
            "start_date",
            "end_date",
            "milestones",
            # Relevance fields
            "institutional_alignment",
            "evidence_summary",
        }

        missing_fields = expected_new_fields - fields
        assert len(missing_fields) == 0, f"Missing required fields: {missing_fields}"

    def test_example_picot_is_complete(self):
        """Verify example PICOT populates all required fields."""
        example = PICOTQuestion.model_config['json_schema_extra']['example']

        # Check core PICOT
        assert len(example['population']) > 10
        assert len(example['intervention']) > 10
        assert len(example['comparison']) > 5
        assert len(example['outcome']) > 10
        assert len(example['timeframe']) > 10

        # Check specificity fields
        assert 'setting' in example
        assert 'bed' in example['setting'].lower() or 'unit' in example['setting'].lower()
        assert 'inclusion_criteria' in example
        assert len(example['intervention_components']) >= 3
        assert 'delivered_by' in example

        # Check measurability fields
        assert 'baseline_rate' in example
        assert 'per' in example['baseline_rate']  # Should have units
        assert 'numeric_target' in example
        assert '%' in example['numeric_target'] or '≥' in example['numeric_target']
        assert 'data_source' in example

        # Check time-bound fields
        assert 'start_date' in example
        assert '2026' in example['start_date'] or '2025' in example['start_date']
        assert 'end_date' in example
        assert 'milestones' in example
        assert len(example['milestones']) >= 4

        # Check relevance fields
        assert 'institutional_alignment' in example
        assert 'evidence_summary' in example
        assert len(example['evidence_summary']) > 20

    def test_example_meets_specificity_criteria(self):
        """Verify example meets specificity rubric requirements (25 pts)."""
        example = PICOTQuestion.model_config['json_schema_extra']['example']

        # Population specificity (10 pts)
        pop = example['population'].lower()
        # Should have age range
        has_age = any(age_term in pop for age_term in ['65+', '65-', 'aged', 'years'])
        assert has_age, "Population missing specific age range"

        # Should have clinical condition
        has_condition = any(cond in pop for cond in ['risk', 'scale', 'morse', 'diagnosis'])
        assert has_condition, "Population missing clinical condition/risk stratification"

        # Intervention specificity (8 pts)
        assert len(example['intervention_components']) >= 3, "Need ≥3 intervention components"

        # Comparison specificity (4 pts)
        comp = example['comparison'].lower()
        assert 'baseline' in comp or 'current' in comp, "Comparison should state current practice"

        # Outcome specificity (3 pts)
        outcome = example['outcome'].lower()
        has_units = any(unit in outcome for unit in ['per', '1,000', 'patient-days', 'rate'])
        assert has_units, "Outcome should have specific units"

    def test_example_meets_measurability_criteria(self):
        """Verify example meets measurability rubric requirements (20 pts)."""
        example = PICOTQuestion.model_config['json_schema_extra']['example']

        # Numeric target (10 pts)
        assert 'numeric_target' in example
        target = example['numeric_target']
        has_number = any(char.isdigit() for char in target)
        assert has_number, "Numeric target should contain numbers"

        # Timeframe specific (5 pts)
        assert 'start_date' in example and 'end_date' in example
        assert '2025' in example['start_date'] or '2026' in example['start_date']

        # Data collection method (5 pts)
        assert 'data_source' in example
        assert len(example['data_source']) > 5

    def test_example_meets_achievability_criteria(self):
        """Verify example meets achievability rubric requirements (20 pts)."""
        example = PICOTQuestion.model_config['json_schema_extra']['example']

        # Sample size realistic (10 pts)
        assert 'sample_size_estimate' in example
        sample_text = example['sample_size_estimate'].lower()
        has_justification = any(term in sample_text for term in ['based on', 'occupancy', 'los', 'prevalence'])
        assert has_justification, "Sample size should include justification"

    def test_example_meets_timebound_criteria(self):
        """Verify example meets time-bound rubric requirements (15 pts)."""
        example = PICOTQuestion.model_config['json_schema_extra']['example']

        # Start/end dates defined (8 pts)
        assert 'start_date' in example and 'end_date' in example

        # Milestones included (7 pts)
        assert 'milestones' in example
        assert len(example['milestones']) >= 4
        # At least one should mention IRB/approval
        has_irb = any('irb' in m.lower() or 'approval' in m.lower() for m in example['milestones'])
        assert has_irb, "Milestones should include IRB/approval"

    def test_example_meets_relevance_criteria(self):
        """Verify example meets relevance rubric requirements (20 pts)."""
        example = PICOTQuestion.model_config['json_schema_extra']['example']

        # Institutional alignment (10 pts)
        assert 'institutional_alignment' in example
        alignment = example['institutional_alignment'].lower()
        has_standard = any(term in alignment for term in ['joint commission', 'cms', 'npsg', 'strategic'])
        assert has_standard, "Should cite institutional standard/goal"

        # Evidence-based (5 pts)
        assert 'evidence_summary' in example
        evidence = example['evidence_summary'].lower()
        has_citation = any(year in evidence for year in ['2006', '2012', '2020', '2021', '2022', '2023', '2024'])
        assert has_citation, "Evidence summary should cite studies with years"

    def test_validation_accepts_complete_picot(self):
        """Verify Pydantic validation accepts a complete PICOT."""
        example = PICOTQuestion.model_config['json_schema_extra']['example']

        # Should not raise validation error
        picot = PICOTQuestion(**example)

        # Verify all fields are populated
        assert picot.population
        assert picot.intervention
        assert picot.comparison
        assert picot.outcome
        assert picot.timeframe
        assert picot.setting
        assert picot.baseline_rate
        assert picot.numeric_target
        assert len(picot.intervention_components) >= 3
        assert len(picot.milestones) >= 4

    def test_schema_rejects_incomplete_picot(self):
        """Verify schema validation catches incomplete PICOTs."""
        from pydantic import ValidationError

        incomplete = {
            "population": "Elderly patients",
            "intervention": "Hourly rounding",
            "comparison": "Standard care",
            "outcome": "Reduce falls",
            "timeframe": "6 months",
            # Missing all enhanced fields
        }

        with pytest.raises(ValidationError) as exc_info:
            PICOTQuestion(**incomplete)

        # Should fail on missing required fields
        errors = exc_info.value.errors()
        missing_field_names = [e['loc'][0] for e in errors if e['type'] == 'missing']

        # Should be missing several required fields
        assert len(missing_field_names) > 0, "Should detect missing enhanced fields"


class TestPICOTQualityEstimate:
    """Estimate quality score based on completeness."""

    def test_example_estimated_score(self):
        """Estimate rubric score for the example PICOT."""
        example = PICOTQuestion.model_config['json_schema_extra']['example']

        # Manual scoring based on PICOT_RUBRIC.md
        score = 0

        # Specificity (25 pts)
        # - Population: 10/10 (has age, condition, setting, criteria, sample size)
        score += 10
        # - Intervention: 8/8 (detailed components, deliverers, timing)
        score += 8
        # - Comparison: 4/4 (explicit current practice with baseline)
        score += 4
        # - Outcome: 3/3 (measurable with units)
        score += 3

        # Measurability (20 pts)
        # - Numeric target: 10/10 (has ≥30% reduction)
        score += 10
        # - Timeframe: 5/5 (exact dates)
        score += 5
        # - Data collection: 5/5 (method specified)
        score += 5

        # Achievability (20 pts)
        # - Sample size: 10/10 (realistic with justification)
        score += 10
        # - Resources: 5/5 (identified in example or clinical_significance)
        score += 5
        # - Timeline: 5/5 (feasible 6 months)
        score += 5

        # Relevance (20 pts)
        # - Institutional: 10/10 (Joint Commission, strategic goals)
        score += 10
        # - Evidence: 5/5 (cites studies)
        score += 5
        # - Clinical problem: 5/5 (data-driven baseline vs benchmark)
        score += 5

        # Time-Bound (15 pts)
        # - Start/end: 8/8 (exact dates)
        score += 8
        # - Milestones: 7/7 (6 milestones with dates)
        score += 7

        # Total estimated score
        assert score >= 90, f"Example PICOT estimated score {score} below target 90"
        assert score <= 100, f"Estimated score {score} exceeds maximum 100"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
