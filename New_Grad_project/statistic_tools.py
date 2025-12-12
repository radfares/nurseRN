# statistic_tools.py
#
# Title: Agentic Statistical Toolkit for Nursing Research
# Author: Gemini 1.5 Pro, based on 'Statistics for Nursing Research' by Grove & Cipher.
# Created: 2025-12-08
# Last Modified: 2025-12-12 03:22:00 UTC
# Version: 1.0.1
#
# Purpose:
# This file contains statistical rules and decision logic distilled from
# foundational nursing research statistics. It is designed to be a production-ready
# toolkit for AI agents to make informed, automated statistical decisions.
#
# Do not modify this file without updating the version and timestamp.

from typing import Dict, List, Optional, Union

# ============================================================================ 
# Module 1: Levels of Measurement & Test Selection
# Source: Nominal.md
# ============================================================================ 

MEASUREMENT_LEVELS: Dict[str, Dict[str, Union[str, List[str]]]] = {
    "nominal": {
        "description": "Categorical data where items are assigned to groups with no inherent order. Think 'naming' or 'labeling'.",
        "examples": [
            "Gender (Male, Female, Non-binary)",
            "Blood Type (A, B, AB, O)",
            "Marital Status (Single, Married, Divorced)",
            "Race/Ethnicity"
        ]
    },
    "ordinal": {
        "description": "Categorical data where there is a meaningful order or rank, but the intervals between ranks are not necessarily equal.",
        "examples": [
            "Pain Scale (1-10)",
            "Patient Satisfaction (Very Satisfied, Satisfied, Neutral, Dissatisfied)",
            "Cancer Staging (Stage I, Stage II, Stage III, Stage IV)",
            "Likert Scales (Strongly Agree to Strongly Disagree)"
        ]
    },
    "interval": {
        "description": "Continuous data with a meaningful order and equal intervals between values, but no true zero point.",
        "examples": [
            "Temperature in Celsius or Fahrenheit",
            "IQ Scores",
            "Calendar Years (e.g., 2023, 2024)"
        ]
    },
    "ratio": {
        "description": "Continuous data with a meaningful order, equal intervals, and a true zero point, allowing for meaningful ratios.",
        "examples": [
            "Height",
            "Weight",
            "Blood Pressure",
            "Heart Rate",
            "Age",
            "Dosage of Medication (in mg)"
        ]
    }
}

# Decision logic for selecting a statistical test based on data type and number of groups
# This is a simplified decision tree for common scenarios in nursing research.
STATISTICAL_TEST_DECISION_TREE: Dict[str, Dict[str, str]] = {
    "nominal": {
        "2_groups": "Chi-square test",
        "3_or_more_groups": "Chi-square test",
        "correlation": "Not applicable (use Spearman for ranked data)",
        "paired_samples": "McNemar's test"
    },
    "ordinal": {
        "2_groups": "Mann-Whitney U test",
        "3_or_more_groups": "Kruskal-Wallis test",
        "correlation": "Spearman's rank-order correlation (rho)",
        "paired_samples": "Wilcoxon signed-rank test"
    },
    "interval": {
        "2_groups": "Independent t-test",
        "3_or_more_groups": "Analysis of Variance (ANOVA)",
        "correlation": "Pearson product-moment correlation (r)",
        "paired_samples": "Paired t-test"
    },
    "ratio": {
        "2_groups": "Independent t-test",
        "3_or_more_groups": "Analysis of Variance (ANOVA)",
        "correlation": "Pearson product-moment correlation (r)",
        "paired_samples": "Paired t-test"
    }
}

def get_statistical_test(
    measurement_level: str,
    num_groups: int = 2,
    is_correlation: bool = False,
    is_paired: bool = False
) -> Optional[str]:
    """
    Recommends a statistical test based on the level of measurement and study design.

    Args:
        measurement_level: The level of measurement of the dependent variable.
                           Must be one of 'nominal', 'ordinal', 'interval', 'ratio'.
        num_groups: The number of independent groups being compared (e.g., control vs. intervention).
        is_correlation: Set to True if you are examining the relationship between two variables.
        is_paired: Set to True if the samples are paired or related (e.g., pre-test/post-test).

    Returns:
        The name of the recommended statistical test as a string, or None if no match is found.
    """
    level = measurement_level.lower()
    if level not in STATISTICAL_TEST_DECISION_TREE:
        return None

    if is_correlation:
        return STATISTICAL_TEST_DECISION_TREE[level].get("correlation")
    
    if is_paired:
        return STATISTICAL_TEST_DECISION_TREE[level].get("paired_samples")

    if num_groups <= 2:
        return STATISTICAL_TEST_DECISION_TREE[level].get("2_groups")
    else:
        return STATISTICAL_TEST_DECISION_TREE[level].get("3_or_more_groups")


# ============================================================================ 
# Module 2: Correlation Interpretation
# Source: statspart2.md
# ============================================================================ 

def interpret_correlation(r_value: float) -> str:
    """
    Interprets the strength and direction of a Pearson's r correlation coefficient.

    Args:
        r_value: The Pearson's r value, which must be between -1.0 and 1.0.

    Returns:
        A string describing the correlation.
    """
    if not -1.0 <= r_value <= 1.0:
        return "Invalid r-value. It must be between -1.0 and 1.0."

    abs_r = abs(r_value)

    # Handle the special case for very weak or no correlation first
    if abs_r < 0.2: # This now covers both 0.0 and 0.1 ranges correctly
        if abs_r < 0.1:
             return "Very weak or no correlation"
        strength = "very weak"
    elif abs_r >= 0.8:
        strength = "very strong"
    elif abs_r >= 0.6:
        strength = "strong"
    elif abs_r >= 0.4:
        strength = "moderate"
    else: # This case is now 0.2 <= abs_r < 0.4
        strength = "weak"

    direction = "positive" if r_value > 0 else "negative"
    
    return f"A {strength} {direction} correlation."


# ============================================================================ 
# Module 3: Multiple Linear Regression Assumptions
# Source: statspart4.md
# ============================================================================ 

REGRESSION_ASSUMPTIONS: List[str] = [
    "Linear relationship: The relationship between the independent and dependent variables is linear.",
    "Multivariate normality: The variables are normally distributed in the population.",
    "No or little multicollinearity: The independent variables are not highly correlated with each other.",
    "No auto-correlation: The residuals are independent.",
    "Homoscedasticity: The variance of the residuals is constant across all levels of the independent variables."
]


# ============================================================================ 
# Module 4: Missing Data Handling
# Source: statspart3.md
# ============================================================================ 

MISSING_DATA_METHODS: Dict[str, str] = {
    "listwise_deletion": "Delete entire cases (rows) that have any missing data. Simple, but can reduce statistical power and introduce bias if data is not MCAR.",
    "pairwise_deletion": "Use all available data for each specific calculation (e.g., a correlation). Can be problematic as it uses different sample sizes for different calculations.",
    "mean_imputation": "Replace missing values with the mean of the available data for that variable. Simple, but artificially reduces variance.",
    "median_imputation": "Replace missing values with the median. More robust to outliers than mean imputation.",
    "mode_imputation": "Replace missing categorical values with the mode (most frequent category).",
    "multiple_imputation": "(Recommended) Create multiple complete datasets by imputing missing values multiple times, run analysis on each, and then pool the results. Accounts for the uncertainty of the missing data."
}

if __name__ == '__main__':
    # Example usage for agents
    print("--- Testing Statistical Toolkit ---")

    # Example 1: Choosing a test for a study comparing the blood pressure (ratio) of two groups.
    test1 = get_statistical_test(measurement_level="ratio", num_groups=2)
    print(f"Study 1 (Ratio, 2 groups): Recommended test is '{test1}'") # Expected: Independent t-test

    # Example 2: Choosing a test for a study looking at the correlation between patient satisfaction (ordinal) and wait time (ratio).
    # Note: We'd use the lower level of measurement for the test.
    test2 = get_statistical_test(measurement_level="ordinal", is_correlation=True)
    print(f"Study 2 (Ordinal, Correlation): Recommended test is '{test2}'") # Expected: Spearman's rank-order correlation (rho)

    # Example 3: Interpreting a correlation coefficient
    interpretation1 = interpret_correlation(0.75)
    print(f"Interpretation for r = 0.75: {interpretation1}") # Expected: A strong positive correlation. 
    
    interpretation2 = interpret_correlation(-0.25)
    print(f"Interpretation for r = -0.25: {interpretation2}") # Expected: A weak negative correlation.

    # Example 4: Listing assumptions for a regression model
    print("\nAssumptions for Multiple Linear Regression:")
    for i, assumption in enumerate(REGRESSION_ASSUMPTIONS, 1):
        print(f"{i}. {assumption}")

    # Example 5: Listing methods for handling missing data
    print("\nCommon Methods for Handling Missing Data:")
    for method, description in MISSING_DATA_METHODS.items():
        print(f"- {method.replace('_', ' ').title()}: {description}")
