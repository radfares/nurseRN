"""
Structured output schemas for nursing research agents.

Enforces consistent, high-quality outputs across all agents using Pydantic models.

Created: 2025-12-12
Purpose: Ensure output completeness, consistency, and parseability
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class EvidenceLevel(str, Enum):
    """Johns Hopkins Evidence Level Classification"""
    LEVEL_I = "I"      # Experimental studies, RCTs
    LEVEL_II = "II"    # Quasi-experimental studies
    LEVEL_III = "III"  # Non-experimental studies
    LEVEL_IV = "IV"    # Expert opinion
    LEVEL_V = "V"      # Case reports, program evaluation


class PICOTQuestion(BaseModel):
    """
    Structured PICOT question output.

    Ensures all PICOT components are present and clinically relevant.
    """
    population: str = Field(
        description="Population (P) - Who is the patient population?",
        min_length=5
    )
    intervention: str = Field(
        description="Intervention (I) - What is the intervention or therapy?",
        min_length=5
    )
    comparison: str = Field(
        description="Comparison (C) - What is the alternative or comparison?",
        min_length=3
    )
    outcome: str = Field(
        description="Outcome (O) - What is the desired outcome?",
        min_length=5
    )
    timeframe: str = Field(
        description="Timeframe (T) - What is the time period?",
        min_length=3
    )
    full_question: str = Field(
        description="Complete PICOT question in proper format",
        min_length=20
    )
    clinical_significance: str = Field(
        description="Why this question matters clinically and to patient care",
        min_length=50
    )
    search_terms: List[str] = Field(
        description="Recommended search terms for literature review",
        min_items=3,
        max_items=10
    )

    class Config:
        json_schema_extra = {
            "example": {
                "population": "Elderly patients (65+) in acute care hospitals",
                "intervention": "Hourly rounding by nursing staff",
                "comparison": "Standard nursing care without structured rounding",
                "outcome": "Reduction in patient falls",
                "timeframe": "Over 6 months",
                "full_question": "In elderly hospitalized patients (P), does hourly nursing rounding (I) compared to standard care (C) reduce patient falls (O) over 6 months (T)?",
                "clinical_significance": "Patient falls are a leading cause of injury and extended hospital stays in elderly patients. Hourly rounding is a low-cost intervention that could significantly reduce fall rates and improve patient safety outcomes.",
                "search_terms": ["patient falls", "elderly hospitalized", "hourly rounding", "fall prevention", "nursing intervention", "acute care"]
            }
        }


class ResearchArticle(BaseModel):
    """
    Structured article information with evidence quality indicators.

    Used by research agents to return consistent article metadata.
    """
    pmid: Optional[str] = Field(
        default=None,
        description="PubMed ID (if available)"
    )
    doi: Optional[str] = Field(
        default=None,
        description="Digital Object Identifier"
    )
    title: str = Field(
        description="Article title",
        min_length=10
    )
    authors: List[str] = Field(
        description="Author names",
        min_items=1
    )
    year: int = Field(
        description="Publication year",
        ge=1900,
        le=2030
    )
    journal: str = Field(
        description="Journal or source name",
        min_length=3
    )
    evidence_level: EvidenceLevel = Field(
        description="Johns Hopkins evidence level classification"
    )
    is_retracted: bool = Field(
        default=False,
        description="Whether the article has been retracted"
    )
    relevance_score: float = Field(
        description="Relevance to research question (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    key_findings: List[str] = Field(
        description="Main findings from the article",
        min_items=1,
        max_items=5
    )
    abstract: Optional[str] = Field(
        default=None,
        description="Article abstract (if available)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "pmid": "12345678",
                "doi": "10.1001/jama.2020.12345",
                "title": "Effect of Hourly Rounding on Patient Falls in Acute Care Settings",
                "authors": ["Smith J", "Johnson M", "Williams K"],
                "year": 2020,
                "journal": "JAMA Internal Medicine",
                "evidence_level": "I",
                "is_retracted": False,
                "relevance_score": 0.95,
                "key_findings": [
                    "Hourly rounding reduced falls by 50% (p<0.001)",
                    "No significant increase in nursing workload",
                    "Patient satisfaction scores improved by 20%"
                ]
            }
        }


class LiteratureSynthesis(BaseModel):
    """
    Structured synthesis of literature findings.

    Ensures comprehensive synthesis with quality indicators and gaps identified.
    """
    topic: str = Field(
        description="Research topic being synthesized",
        min_length=10
    )
    picot_question: str = Field(
        description="PICOT question this synthesis addresses",
        min_length=20
    )
    articles_reviewed: int = Field(
        description="Total number of articles reviewed",
        ge=1
    )
    evidence_summary: str = Field(
        description="Comprehensive summary of the evidence",
        min_length=100
    )
    key_findings: List[str] = Field(
        description="Main findings across all studies",
        min_items=3,
        max_items=10
    )
    recommendations: List[str] = Field(
        description="Clinical practice recommendations based on evidence",
        min_items=2,
        max_items=8
    )
    evidence_quality: str = Field(
        description="Overall quality assessment of the evidence base",
        min_length=20
    )
    gaps_identified: List[str] = Field(
        description="Research gaps and areas needing further study",
        min_items=1,
        max_items=5
    )
    confidence_level: float = Field(
        description="Overall confidence in findings (0.0-1.0)",
        ge=0.0,
        le=1.0
    )
    citations: List[str] = Field(
        description="PMIDs or DOIs of cited articles",
        min_items=1
    )

    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Hourly rounding for fall prevention in elderly hospitalized patients",
                "picot_question": "In elderly hospitalized patients, does hourly nursing rounding compared to standard care reduce patient falls over 6 months?",
                "articles_reviewed": 12,
                "evidence_summary": "Systematic review of 12 studies (5 RCTs, 7 quasi-experimental) shows consistent evidence that hourly rounding reduces falls by 30-50% in acute care settings. Effects are most pronounced in elderly patients and when rounding includes specific safety checks.",
                "key_findings": [
                    "Hourly rounding reduces falls by 30-50% across multiple studies",
                    "Most effective when including toileting assistance and environment checks",
                    "Minimal increase in nursing workload when integrated into workflow",
                    "Improves patient satisfaction and nurse-patient communication"
                ],
                "recommendations": [
                    "Implement structured hourly rounding in all acute care units with elderly patients",
                    "Include specific safety checklist items: toileting, positioning, environment",
                    "Provide staff training on effective rounding techniques"
                ],
                "evidence_quality": "Moderate to high quality evidence from multiple RCTs and well-designed quasi-experimental studies. Some heterogeneity in implementation protocols.",
                "gaps_identified": [
                    "Long-term sustainability beyond 6 months unclear",
                    "Cost-effectiveness analysis needed",
                    "Optimal rounding frequency not yet determined"
                ],
                "confidence_level": 0.85,
                "citations": ["12345678", "23456789", "34567890"]
            }
        }


class DataAnalysisPlan(BaseModel):
    """
    Structured data analysis and statistical planning output.

    Ensures complete analysis plan with justified statistical approaches.
    """
    study_design: str = Field(
        description="Type of study design (RCT, quasi-experimental, etc.)",
        min_length=5
    )
    sample_size_required: int = Field(
        description="Required sample size based on power analysis",
        ge=1
    )
    sample_size_justification: str = Field(
        description="Explanation of how sample size was calculated",
        min_length=50
    )
    statistical_tests: List[str] = Field(
        description="Recommended statistical tests with justification",
        min_items=1,
        max_items=5
    )
    power: float = Field(
        description="Statistical power (typically 0.80 or higher)",
        ge=0.0,
        le=1.0
    )
    alpha: float = Field(
        description="Significance level (typically 0.05)",
        ge=0.0,
        le=1.0
    )
    effect_size: float = Field(
        description="Expected effect size (Cohen's d or similar)",
        gt=0.0
    )
    effect_size_justification: str = Field(
        description="Basis for expected effect size (literature, pilot data, etc.)",
        min_length=30
    )
    data_collection_plan: List[str] = Field(
        description="Step-by-step data collection procedures",
        min_items=2,
        max_items=10
    )
    analysis_timeline: str = Field(
        description="Timeline for data collection and analysis",
        min_length=20
    )
    potential_confounders: List[str] = Field(
        default_factory=list,
        description="Potential confounding variables to control for"
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Anticipated study limitations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "study_design": "Quasi-experimental pre-post intervention study",
                "sample_size_required": 388,
                "sample_size_justification": "Based on power analysis for detecting 30% reduction in fall rate with 80% power, alpha=0.05, assuming baseline fall rate of 5 per 1000 patient days",
                "statistical_tests": [
                    "Interrupted time series analysis for fall rate trends",
                    "Chi-square test for categorical outcomes",
                    "Independent t-test for pre-post comparison"
                ],
                "power": 0.80,
                "alpha": 0.05,
                "effect_size": 0.30,
                "effect_size_justification": "Based on meta-analysis showing hourly rounding reduces falls by 30-50%",
                "data_collection_plan": [
                    "Collect baseline fall data for 3 months pre-intervention",
                    "Implement hourly rounding intervention",
                    "Collect fall data for 6 months post-intervention",
                    "Record all falls with incident reports",
                    "Document rounding compliance via electronic records"
                ],
                "analysis_timeline": "9 months total: 3 months baseline, 6 months intervention",
                "potential_confounders": [
                    "Patient acuity levels",
                    "Staffing ratios",
                    "Seasonal variations",
                    "Environmental changes"
                ],
                "limitations": [
                    "Lack of randomization",
                    "Potential Hawthorne effect",
                    "Single-site study limiting generalizability"
                ]
            }
        }


# Export all schemas
__all__ = [
    'EvidenceLevel',
    'PICOTQuestion',
    'ResearchArticle',
    'LiteratureSynthesis',
    'DataAnalysisPlan',
]
