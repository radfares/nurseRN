"""
Unit tests for validation module base classes.
Gate 1: Core validation infrastructure.

Tests:
1. ValidationIssue dataclass creation
2. ValidationResult dataclass creation
3. ClinicalValidator abstract class structure
4. Severity levels (error, warning, info)
5. Suggestion generation
"""

import pytest
from dataclasses import dataclass
from typing import List


def test_validation_issue_imports():
    """Test that ValidationIssue can be imported."""
    from src.validation.clinical_checks import ValidationIssue
    assert ValidationIssue is not None


def test_validation_result_imports():
    """Test that ValidationResult can be imported."""
    from src.validation.clinical_checks import ValidationResult
    assert ValidationResult is not None


def test_clinical_validator_imports():
    """Test that ClinicalValidator can be imported."""
    from src.validation.clinical_checks import ClinicalValidator
    assert ClinicalValidator is not None


def test_validation_issue_creation():
    """Test ValidationIssue dataclass creation."""
    from src.validation.clinical_checks import ValidationIssue

    issue = ValidationIssue(
        severity="error",
        message="Sample size too large",
        suggestion="Reduce sample size to 200"
    )

    assert issue.severity == "error"
    assert issue.message == "Sample size too large"
    assert issue.suggestion == "Reduce sample size to 200"


def test_validation_result_creation():
    """Test ValidationResult dataclass creation."""
    from src.validation.clinical_checks import ValidationResult, ValidationIssue

    issues = [
        ValidationIssue(severity="error", message="Error 1", suggestion="Fix 1"),
        ValidationIssue(severity="warning", message="Warning 1", suggestion="Fix 2")
    ]

    result = ValidationResult(
        valid=False,
        issues=issues
    )

    assert result.valid is False
    assert len(result.issues) == 2
    assert result.issues[0].severity == "error"


def test_validation_result_empty_issues():
    """Test ValidationResult with no issues."""
    from src.validation.clinical_checks import ValidationResult

    result = ValidationResult(
        valid=True,
        issues=[]
    )

    assert result.valid is True
    assert len(result.issues) == 0


def test_clinical_validator_is_abstract():
    """Test that ClinicalValidator cannot be instantiated directly."""
    from src.validation.clinical_checks import ClinicalValidator

    # Should raise TypeError because it's abstract
    with pytest.raises(TypeError):
        ClinicalValidator()


def test_severity_levels():
    """Test that severity levels are validated."""
    from src.validation.clinical_checks import ValidationIssue, SEVERITY_LEVELS

    assert "error" in SEVERITY_LEVELS
    assert "warning" in SEVERITY_LEVELS
    assert "info" in SEVERITY_LEVELS


def test_validation_issue_invalid_severity():
    """Test that invalid severity levels raise error."""
    from src.validation.clinical_checks import ValidationIssue

    # Should validate severity in __post_init__
    with pytest.raises(ValueError):
        ValidationIssue(
            severity="invalid",
            message="Test",
            suggestion="Test"
        )


def test_validation_result_has_errors_property():
    """Test ValidationResult has_errors property."""
    from src.validation.clinical_checks import ValidationResult, ValidationIssue

    result_with_errors = ValidationResult(
        valid=False,
        issues=[
            ValidationIssue(severity="error", message="E1", suggestion="S1")
        ]
    )

    result_without_errors = ValidationResult(
        valid=True,
        issues=[
            ValidationIssue(severity="warning", message="W1", suggestion="S1")
        ]
    )

    assert result_with_errors.has_errors() is True
    assert result_without_errors.has_errors() is False
