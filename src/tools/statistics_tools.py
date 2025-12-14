"""
Statistics Tools for Data Analysis Agent

Provides sample size calculation, power analysis, and statistical test selection.
Enables real calculations instead of LLM-only advice.

Created: 2025-12-07 (Phase B - Agent Optimization)
"""
import math
import json
import logging
from typing import Optional
from scipy import stats

from agno.tools import Toolkit

logger = logging.getLogger(__name__)


class StatisticsTools(Toolkit):
    """
    Tools for statistical calculations in nursing research.
    
    Features:
    - Sample size calculation
    - Power analysis
    - Statistical test selection
    - Effect size estimation
    """
    
    def __init__(self):
        super().__init__(name="statistics_tools")
        
        # Register tools
        self.register(self.calculate_sample_size)
        self.register(self.calculate_power)
        self.register(self.suggest_statistical_test)
        self.register(self.calculate_effect_size)
        
        logger.info("✅ StatisticsTools initialized with 4 tools")
    
    def calculate_sample_size(
        self,
        effect_size: float = 0.5,
        power: float = 0.80,
        alpha: float = 0.05,
        test_type: str = "two_tailed",
        groups: int = 2
    ) -> str:
        """
        Calculate required sample size for a study.
        
        Args:
            effect_size: Cohen's d (0.2=small, 0.5=medium, 0.8=large)
            power: Desired statistical power (typically 0.80)
            alpha: Significance level (typically 0.05)
            test_type: "one_tailed" or "two_tailed"
            groups: Number of groups (1 for one-sample, 2 for two-sample)
            
        Returns:
            JSON with sample size per group and total
        """
        try:
            # Calculate z-scores
            z_alpha = stats.norm.ppf(1 - alpha / (1 if test_type == "one_tailed" else 2))
            z_beta = stats.norm.ppf(power)
            
            # Sample size formula for two-sample t-test
            if groups == 2:
                n_per_group = 2 * ((z_alpha + z_beta) ** 2) / (effect_size ** 2)
            else:
                # One-sample t-test
                n_per_group = ((z_alpha + z_beta) ** 2) / (effect_size ** 2)
            
            n_per_group = math.ceil(n_per_group)
            total_n = n_per_group * groups
            
            # Recommendations
            recommendations = []
            if n_per_group < 30:
                recommendations.append("Consider non-parametric tests with small samples")
            if effect_size < 0.3:
                recommendations.append("Small effect size = larger sample needed")
            if power < 0.80:
                recommendations.append("Power < 0.80 may miss real effects")
            
            return json.dumps({
                "n_per_group": n_per_group,
                "total_sample_size": total_n,
                "effect_size": effect_size,
                "power": power,
                "alpha": alpha,
                "test_type": test_type,
                "groups": groups,
                "recommendations": recommendations,
                "formula_used": "n = 2((Zα + Zβ)² / d²)" if groups == 2 else "n = (Zα + Zβ)² / d²"
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def calculate_power(
        self,
        n_per_group: int,
        effect_size: float = 0.5,
        alpha: float = 0.05,
        test_type: str = "two_tailed",
        groups: int = 2
    ) -> str:
        """
        Calculate statistical power given sample size.
        
        Args:
            n_per_group: Sample size per group
            effect_size: Cohen's d (0.2=small, 0.5=medium, 0.8=large)
            alpha: Significance level
            test_type: "one_tailed" or "two_tailed"
            groups: Number of groups
            
        Returns:
            JSON with power and interpretation
        """
        try:
            # Calculate z-score for alpha
            z_alpha = stats.norm.ppf(1 - alpha / (1 if test_type == "one_tailed" else 2))
            
            # Calculate z-beta from sample size formula rearranged
            if groups == 2:
                z_beta = effect_size * math.sqrt(n_per_group / 2) - z_alpha
            else:
                z_beta = effect_size * math.sqrt(n_per_group) - z_alpha
            
            # Convert z-beta to power
            power = stats.norm.cdf(z_beta)
            
            # Interpretation
            if power >= 0.90:
                interpretation = "Excellent power - very likely to detect effect"
            elif power >= 0.80:
                interpretation = "Good power - standard for research"
            elif power >= 0.60:
                interpretation = "Moderate power - may miss some real effects"
            else:
                interpretation = "Low power - high risk of Type II error"
            
            return json.dumps({
                "power": round(power, 3),
                "power_percent": f"{power * 100:.1f}%",
                "interpretation": interpretation,
                "n_per_group": n_per_group,
                "effect_size": effect_size,
                "alpha": alpha,
                "is_adequate": bool(power >= 0.80)  # Convert numpy bool to Python bool
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def suggest_statistical_test(
        self,
        data_type: str,
        groups: int = 2,
        paired: bool = False,
        normality_assumed: bool = True
    ) -> str:
        """
        Suggest appropriate statistical test based on study design.
        
        Args:
            data_type: "continuous", "categorical", "ordinal"
            groups: Number of groups to compare (1, 2, or 3+)
            paired: Whether measurements are paired/matched
            normality_assumed: Whether data is normally distributed
            
        Returns:
            JSON with recommended tests and assumptions
        """
        tests = {
            "continuous": {
                (1, False, True): {
                    "test": "One-sample t-test",
                    "alternative": "One-sample Wilcoxon signed-rank",
                    "use_when": "Comparing sample mean to known value"
                },
                (2, False, True): {
                    "test": "Independent samples t-test",
                    "alternative": "Mann-Whitney U test",
                    "use_when": "Comparing two independent groups"
                },
                (2, True, True): {
                    "test": "Paired t-test",
                    "alternative": "Wilcoxon signed-rank test",
                    "use_when": "Pre-post or matched pairs design"
                },
                (3, False, True): {
                    "test": "One-way ANOVA",
                    "alternative": "Kruskal-Wallis H test",
                    "use_when": "Comparing 3+ independent groups"
                },
            },
            "categorical": {
                (2, False, True): {
                    "test": "Chi-square test of independence",
                    "alternative": "Fisher's exact test (small samples)",
                    "use_when": "Testing association between categories"
                },
                (2, True, True): {
                    "test": "McNemar's test",
                    "alternative": "Cochran's Q (3+ measures)",
                    "use_when": "Paired categorical data"
                },
            },
            "ordinal": {
                (2, False, False): {
                    "test": "Mann-Whitney U test",
                    "alternative": "Kolmogorov-Smirnov test",
                    "use_when": "Comparing two groups on ordinal data"
                },
                (2, True, False): {
                    "test": "Wilcoxon signed-rank test",
                    "alternative": "Sign test",
                    "use_when": "Paired ordinal data"
                },
            }
        }
        
        # Clamp groups to 3 if more
        lookup_groups = min(groups, 3)
        key = (lookup_groups, paired, normality_assumed)
        
        if data_type in tests and key in tests[data_type]:
            result = tests[data_type][key]
            result["data_type"] = data_type
            result["groups"] = groups
            result["paired"] = paired
            result["normality_assumed"] = normality_assumed
        else:
            result = {
                "test": "Unable to determine",
                "recommendation": "Consult a statistician for complex designs",
                "data_type": data_type,
                "groups": groups
            }
        
        # Add common assumptions
        result["common_assumptions"] = [
            "Random sampling",
            "Independent observations (unless paired)",
            "Adequate sample size (n ≥ 30 for parametric)"
        ]
        
        return json.dumps(result, indent=2)
    
    def calculate_effect_size(
        self,
        mean1: float,
        mean2: float,
        sd_pooled: Optional[float] = None,
        sd1: Optional[float] = None,
        sd2: Optional[float] = None,
        n1: Optional[int] = None,
        n2: Optional[int] = None
    ) -> str:
        """
        Calculate Cohen's d effect size.
        
        Args:
            mean1: Mean of group 1 (or pre-test)
            mean2: Mean of group 2 (or post-test)
            sd_pooled: Pooled standard deviation (if known)
            sd1: Standard deviation of group 1
            sd2: Standard deviation of group 2
            n1: Sample size of group 1
            n2: Sample size of group 2
            
        Returns:
            JSON with effect size and interpretation
        """
        try:
            # Calculate pooled SD if not provided
            if sd_pooled is None:
                if sd1 is not None and sd2 is not None:
                    if n1 is not None and n2 is not None:
                        # Weighted pooled SD
                        numerator = (n1 - 1) * sd1**2 + (n2 - 1) * sd2**2
                        sd_pooled = math.sqrt(numerator / (n1 + n2 - 2))
                    else:
                        # Simple pooled SD
                        sd_pooled = math.sqrt((sd1**2 + sd2**2) / 2)
                else:
                    return json.dumps({"error": "Need sd_pooled OR (sd1 and sd2)"})
            
            # Calculate Cohen's d
            cohens_d = abs(mean1 - mean2) / sd_pooled
            
            # Interpretation (Cohen's conventions)
            if cohens_d < 0.2:
                interpretation = "Negligible effect"
                clinical = "Unlikely to be clinically meaningful"
            elif cohens_d < 0.5:
                interpretation = "Small effect"
                clinical = "May have modest clinical significance"
            elif cohens_d < 0.8:
                interpretation = "Medium effect"
                clinical = "Likely to be clinically meaningful"
            else:
                interpretation = "Large effect"
                clinical = "Strong clinical significance expected"
            
            return json.dumps({
                "cohens_d": round(cohens_d, 3),
                "interpretation": interpretation,
                "clinical_significance": clinical,
                "mean_difference": round(abs(mean1 - mean2), 3),
                "sd_pooled": round(sd_pooled, 3),
                "convention": "0.2=small, 0.5=medium, 0.8=large (Cohen, 1988)"
            }, indent=2)
            
        except Exception as e:
            return json.dumps({"error": str(e)})


def create_statistics_tools() -> StatisticsTools:
    """Factory function to create StatisticsTools instance."""
    return StatisticsTools()
