"""
Timeline Validator

Validates project timelines for nursing QI projects.

Rules (from V2 plan):
- Rule 1: Duration ≥ 2 weeks (minimum viable timeline)
- Rule 2: Duration ≤ 24 months (QI project scope)
- Rule 3: Data collection rate feasible (n / duration / shifts_per_week)
- Rule 4: Milestone deadlines not in past

Part of Phase 5: Task 18.4
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from src.validation.clinical_checks import ClinicalValidator, ValidationResult, ValidationIssue


class TimelineValidator(ClinicalValidator):
    """Validates project timeline for feasibility."""

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate timeline against clinical rules.

        Args:
            context: Dictionary with keys:
                - start_date: ISO format date string (YYYY-MM-DD)
                - end_date: ISO format date string (YYYY-MM-DD)
                - n: Sample size
                - shifts_per_week: Number of data collection shifts per week

        Returns:
            ValidationResult with any issues found
        """
        issues = []

        # Parse dates
        try:
            start_date = datetime.fromisoformat(context.get("start_date", "")).date()
            end_date = datetime.fromisoformat(context.get("end_date", "")).date()
        except (ValueError, AttributeError):
            issues.append(ValidationIssue(
                severity="error",
                message="Invalid date format",
                suggestion="Use ISO format YYYY-MM-DD for dates"
            ))
            return ValidationResult(valid=False, issues=issues)

        n = context.get("n", 0)
        shifts_per_week = context.get("shifts_per_week", 5)

        # Calculate duration
        duration_days = (end_date - start_date).days
        today = datetime.now().date()

        # Rule 1: Duration ≥ 2 weeks (14 days)
        if duration_days < 14:
            issues.append(ValidationIssue(
                severity="error",
                message=f"Duration of {duration_days} days is below minimum of 2 weeks",
                suggestion="Extend project timeline to at least 14 days"
            ))

        # Rule 2: Duration ≤ 24 months (730 days)
        if duration_days > 730:
            issues.append(ValidationIssue(
                severity="error",
                message=f"Duration of {duration_days} days exceeds 24 months maximum for QI projects",
                suggestion="Reduce project scope or split into multiple phases"
            ))

        # Rule 3: Data collection rate feasibility
        # Max 10 patients per shift is realistic
        weeks = duration_days / 7
        total_shifts = weeks * shifts_per_week
        if total_shifts > 0:
            patients_per_shift = n / total_shifts
            if patients_per_shift > 10:
                issues.append(ValidationIssue(
                    severity="error",
                    message=f"Data collection rate of {patients_per_shift:.1f} patients per shift is infeasible",
                    suggestion="Extend timeline or reduce sample size to achieve feasible collection rate (<10/shift)"
                ))

        # Rule 4: Start date not in past
        if start_date < today:
            issues.append(ValidationIssue(
                severity="error",
                message=f"Start date {start_date} is in the past",
                suggestion="Update start date to today or a future date"
            ))

        # Valid if no errors
        valid = not any(issue.severity == "error" for issue in issues)

        return ValidationResult(valid=valid, issues=issues)
