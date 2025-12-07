"""
Clinical Validator Base Classes

Provides base infrastructure for all clinical validators.
Defines severity levels, validation issues, and results.

Part of Phase 5: Task 18.2
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any

# Severity levels for validation issues
SEVERITY_LEVELS = ["error", "warning", "info"]


@dataclass
class ValidationIssue:
    """
    Represents a single validation issue.

    Attributes:
        severity: One of 'error', 'warning', 'info'
        message: Human-readable description of the issue
        suggestion: Actionable recommendation to fix the issue
    """
    severity: str
    message: str
    suggestion: str

    def __post_init__(self):
        """Validate severity level."""
        if self.severity not in SEVERITY_LEVELS:
            raise ValueError(
                f"Invalid severity '{self.severity}'. "
                f"Must be one of {SEVERITY_LEVELS}"
            )


@dataclass
class ValidationResult:
    """
    Result of a validation operation.

    Attributes:
        valid: True if validation passed (no errors)
        issues: List of ValidationIssue objects
    """
    valid: bool
    issues: List[ValidationIssue]

    def has_errors(self) -> bool:
        """
        Check if result contains any errors.

        Returns:
            True if any issue has severity='error'
        """
        return any(issue.severity == "error" for issue in self.issues)


class ClinicalValidator(ABC):
    """
    Abstract base class for all clinical validators.

    Subclasses must implement the validate() method.
    Provides common validation infrastructure.
    """

    @abstractmethod
    def validate(self, context: Dict[str, Any]) -> ValidationResult:
        """
        Validate the given context.

        Args:
            context: Dictionary containing data to validate

        Returns:
            ValidationResult with validation outcomes
        """
        pass
