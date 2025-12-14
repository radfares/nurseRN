"""
Budget Validator

Validates project budgets for nursing QI projects.

Rules (from V2 plan):
- Rule 1: Total cost ≤ $100,000 (typical QI budget cap)
- Rule 2: Per-patient cost realistic ($0-$500 range)
- Rule 3: Labor hours × hourly_rate calculated correctly
- Rule 4: Material costs itemized with unit prices

Part of Phase 5: Task 18.5
"""

from typing import Dict, Any, List, Optional
from src.validation.clinical_checks import ClinicalValidator, ValidationResult, ValidationIssue


class BudgetValidator(ClinicalValidator):
    """Validates project budget for feasibility."""

    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate budget against clinical rules.

        Args:
            context: Dictionary with keys:
                - total_cost: Total project cost ($)
                - n: Sample size
                - labor_hours: Total labor hours
                - hourly_rate: Labor hourly rate ($)
                - materials: List of dicts with item, unit_price, quantity

        Returns:
            ValidationResult with any issues found
        """
        issues = []

        total_cost = context.get("total_cost", 0)
        n = context.get("n", 1)
        labor_hours = context.get("labor_hours", 0)
        hourly_rate = context.get("hourly_rate", 0)
        materials = context.get("materials")

        # Rule 1: Total cost ≤ $100,000
        if total_cost > 100000:
            issues.append(ValidationIssue(
                severity="error",
                message=f"Total cost ${total_cost:,} exceeds $100,000 budget cap for QI projects",
                suggestion="Reduce scope or seek additional funding sources"
            ))

        # Rule 2: Per-patient cost $0-$500
        per_patient = total_cost / n if n > 0 else 0
        if per_patient > 500:
            issues.append(ValidationIssue(
                severity="error",
                message=f"Per-patient cost ${per_patient:.2f} exceeds realistic range of $500",
                suggestion="Review cost breakdown or increase sample size to reduce per-patient cost"
            ))

        # Rule 3: Labor calculation validation
        expected_labor_cost = labor_hours * hourly_rate
        if expected_labor_cost > 0:
            # Allow 20% variance for materials/overhead
            if total_cost < expected_labor_cost * 0.8:
                issues.append(ValidationIssue(
                    severity="warning",
                    message=f"Labor cost (${expected_labor_cost:,}) seems inconsistent with total cost (${total_cost:,})",
                    suggestion="Verify labor hours and total cost calculation"
                ))

        # Rule 4: Materials itemization
        if materials is None:
            issues.append(ValidationIssue(
                severity="error",
                message="Materials costs must be itemized with unit prices",
                suggestion="Provide itemized list of materials with unit_price and quantity for each item"
            ))
        elif isinstance(materials, list):
            # Verify materials are properly itemized
            for idx, item in enumerate(materials):
                if not isinstance(item, dict):
                    issues.append(ValidationIssue(
                        severity="error",
                        message=f"Material item {idx} must be a dictionary with item, unit_price, quantity",
                        suggestion="Format materials as list of dicts: [{'item': 'X', 'unit_price': Y, 'quantity': Z}]"
                    ))
                elif not all(key in item for key in ["item", "unit_price", "quantity"]):
                    issues.append(ValidationIssue(
                        severity="error",
                        message=f"Material '{item.get('item', 'unknown')}' missing required fields",
                        suggestion="Each material must have: item, unit_price, quantity"
                    ))

        # Valid if no errors
        valid = not any(issue.severity == "error" for issue in issues)

        return ValidationResult(valid=valid, issues=issues)
