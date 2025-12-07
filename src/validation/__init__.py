"""
Validation Module

Clinical validation for nurseRN QI projects.
Includes validators for sample size, timeline, budget, and PICOT quality.

Part of Phase 5: Validation & Testing System
"""

from src.validation.clinical_checks import (
    ValidationIssue,
    ValidationResult,
    ClinicalValidator,
    SEVERITY_LEVELS
)

__all__ = [
    "ValidationIssue",
    "ValidationResult",
    "ClinicalValidator",
    "SEVERITY_LEVELS"
]
