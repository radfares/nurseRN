# tests/test_statistic_tools.py

import pytest
from New_Grad_project.statistic_tools import (
    get_statistical_test,
    interpret_correlation,
    REGRESSION_ASSUMPTIONS,
    MISSING_DATA_METHODS
)

# ============================================================================
# Tests for get_statistical_test()
# ============================================================================

@pytest.mark.parametrize("level, groups, expected", [
    ("nominal", 2, "Chi-square test"),
    ("nominal", 3, "Chi-square test"),
    ("ordinal", 2, "Mann-Whitney U test"),
    ("ordinal", 3, "Kruskal-Wallis test"),
    ("interval", 2, "Independent t-test"),
    ("interval", 3, "Analysis of Variance (ANOVA)"),
    ("ratio", 2, "Independent t-test"),
    ("ratio", 3, "Analysis of Variance (ANOVA)"),
])
def test_get_statistical_test_by_groups(level, groups, expected):
    """Tests the correct test selection based on measurement level and number of groups."""
    assert get_statistical_test(measurement_level=level, num_groups=groups) == expected

@pytest.mark.parametrize("level, expected", [
    ("nominal", "Not applicable (use Spearman for ranked data)"),
    ("ordinal", "Spearman's rank-order correlation (rho)"),
    ("interval", "Pearson product-moment correlation (r)"),
    ("ratio", "Pearson product-moment correlation (r)"),
])
def test_get_statistical_test_correlation(level, expected):
    """Tests the correct test selection for correlations."""
    assert get_statistical_test(measurement_level=level, is_correlation=True) == expected

@pytest.mark.parametrize("level, expected", [
    ("nominal", "McNemar's test"),
    ("ordinal", "Wilcoxon signed-rank test"),
    ("interval", "Paired t-test"),
    ("ratio", "Paired t-test"),
])
def test_get_statistical_test_paired(level, expected):
    """Tests the correct test selection for paired samples."""
    assert get_statistical_test(measurement_level=level, is_paired=True) == expected

def test_get_statistical_test_invalid_level():
    """Tests that an invalid measurement level returns None."""
    assert get_statistical_test(measurement_level="invalid_level") is None

# ============================================================================
# Tests for interpret_correlation()
# ============================================================================

@pytest.mark.parametrize("r_value, expected_interpretation", [
    (0.9, "A very strong positive correlation."),
    (-0.9, "A very strong negative correlation."),
    (0.7, "A strong positive correlation."),
    (-0.7, "A strong negative correlation."),
    (0.5, "A moderate positive correlation."),
    (-0.5, "A moderate negative correlation."),
    (0.3, "A weak positive correlation."),
    (-0.3, "A weak negative correlation."),
    (0.1, "A very weak positive correlation."),
    (-0.1, "A very weak negative correlation."),
    (0.0, "Very weak or no correlation"),
    (1.0, "A very strong positive correlation."),
    (-1.0, "A very strong negative correlation."),
])
def test_interpret_correlation_valid_values(r_value, expected_interpretation):
    """Tests the interpretation of various valid r-values."""
    assert interpret_correlation(r_value) == expected_interpretation

@pytest.mark.parametrize("invalid_r", [1.1, -1.1, 2, -50])
def test_interpret_correlation_invalid_values(invalid_r):
    """Tests that r-values outside the [-1, 1] range return an error message."""
    assert "Invalid r-value" in interpret_correlation(invalid_r)

# ============================================================================
# Basic smoke tests for data structures
# ============================================================================

def test_regression_assumptions_is_list():
    """Ensures REGRESSION_ASSUMPTIONS is a non-empty list of strings."""
    assert isinstance(REGRESSION_ASSUMPTIONS, list)
    assert len(REGRESSION_ASSUMPTIONS) > 0
    assert all(isinstance(item, str) for item in REGRESSION_ASSUMPTIONS)

def test_missing_data_methods_is_dict():
    """Ensures MISSING_DATA_METHODS is a non-empty dictionary."""
    assert isinstance(MISSING_DATA_METHODS, dict)
    assert len(MISSING_DATA_METHODS) > 0
    assert all(isinstance(key, str) for key in MISSING_DATA_METHODS.keys())
    assert all(isinstance(value, str) for value in MISSING_DATA_METHODS.values())
