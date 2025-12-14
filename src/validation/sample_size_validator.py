"""
Sample Size Validator

Validates sample sizes for nursing QI projects.

Rules (from V2 plan):
- Rule 1: n ≤ 500 (nursing QI scale)
- Rule 2: n ≤ (unit_beds × 2 × duration_months) [capacity check]
- Rule 3: n ≥ 30 (minimum for statistical power)
- Rule 4: Effect size Cohen's d within [-3, 3]

Part of Phase 5: Task 18.3
"""

from typing import Dict, Any
from src.validation.clinical_checks import ClinicalValidator, ValidationResult, ValidationIssue


class SampleSizeValidator(ClinicalValidator):
    """Validates sample size for clinical feasibility."""

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate sample size against clinical rules.

        Args:
            context: Dictionary with keys:
                - n: Sample size
                - unit_beds: Number of beds in unit
                - duration_months: Project duration in months
                - effect_size: Cohen's d effect size

        Returns:
            ValidationResult with any issues found
        """
        issues = []
        n = context.get("n", 0)
        unit_beds = context.get("unit_beds", 0)
        duration_months = context.get("duration_months", 0)
        effect_size = context.get("effect_size", 0)

        # Rule 1: n ≤ 500
        if n > 500:
            issues.append(ValidationIssue(
                severity="error",
                message=f"Sample size {n} exceeds 500 (unrealistic for unit-level QI)",
                suggestion="Consider pre/post design or longer timeframe to reduce required sample size"
            ))

        # Rule 2: Capacity check
        max_capacity = unit_beds * 2 * duration_months
        if n > max_capacity:
            issues.append(ValidationIssue(
                severity="error",
                message=f"Sample size {n} exceeds unit capacity ({max_capacity} max)",
                suggestion="Reduce sample size or extend timeline"
            ))

        # Rule 3: n ≥ 30
        if n < 30:
            issues.append(ValidationIssue(
                severity="error",
                message=f"Sample size {n} is below minimum of 30 for statistical power",
                suggestion="Increase sample size to at least 30 or consider alternative study design"
            ))

        # Rule 4: Effect size within [-3, 3]
        if effect_size < -3 or effect_size > 3:
            issues.append(ValidationIssue(
                severity="error",
                message=f"Effect size {effect_size} is outside valid range [-3, 3]",
                suggestion="Review effect size calculation or use literature-based estimate"
            ))

        # Valid if no errors
        valid = not any(issue.severity == "error" for issue in issues)

        return ValidationResult(valid=valid, issues=issues)
