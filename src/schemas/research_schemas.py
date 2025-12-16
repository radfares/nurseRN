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
    Enhanced Structured PICOT question output targeting ≥90/100 quality score.

    Includes all fields required by PICOT_RUBRIC.md for "Excellent" rating.
    Based on rubric categories: Specificity (25pts), Measurability (20pts),
    Achievability (20pts), Relevance (20pts), Time-Bound (15pts).
    """
    # Core PICOT components
    population: str = Field(
        description="Population (P) - Who is the patient population? Include age range, diagnosis/condition, and setting",
        min_length=10
    )
    intervention: str = Field(
        description="Intervention (I) - What is the intervention or therapy? Include specific protocol details",
        min_length=10
    )
    comparison: str = Field(
        description="Comparison (C) - What is the alternative or comparison? Explicitly state current practice",
        min_length=5
    )
    outcome: str = Field(
        description="Outcome (O) - What is the desired outcome? Include measurable metric with units",
        min_length=10
    )
    timeframe: str = Field(
        description="Timeframe (T) - What is the time period? Include specific start and end dates",
        min_length=10
    )
    full_question: str = Field(
        description="Complete PICOT question in proper format with all components",
        min_length=50
    )

    # Enhanced Specificity fields (Rubric: 25 pts)
    setting: str = Field(
        description="Specific clinical setting (e.g., '32-bed medical-surgical unit, Community General Hospital')"
    )
    inclusion_criteria: str = Field(
        description="Patient inclusion criteria (e.g., 'Morse Fall Scale score ≥45 (high fall risk)')"
    )
    exclusion_criteria: Optional[str] = Field(
        default=None,
        description="Patient exclusion criteria if applicable"
    )
    intervention_components: List[str] = Field(
        description="List of 3-5 specific intervention protocol components",
        min_items=3,
        max_items=8
    )
    delivered_by: str = Field(
        description="Who delivers the intervention (e.g., 'RNs and CNAs, all shifts')"
    )

    # Measurability fields (Rubric: 20 pts)
    baseline_rate: str = Field(
        description="Current baseline measurement with units and timeframe (e.g., '5.2 falls per 1,000 patient-days (Q1-Q3 2025)')"
    )
    benchmark: Optional[str] = Field(
        default=None,
        description="National/industry benchmark if available (e.g., 'NDNQI benchmark: 3.44 per 1,000 pt-days')"
    )
    numeric_target: str = Field(
        description="Specific numeric target/reduction (e.g., '≥30% reduction to ≤3.64 per 1,000 pt-days')"
    )
    secondary_outcomes: Optional[List[str]] = Field(
        default=None,
        description="2-3 secondary outcomes to measure",
        max_items=5
    )
    data_source: str = Field(
        description="Where/how data will be collected (e.g., 'Incident reporting system + EHR audit')"
    )

    # Achievability fields (Rubric: 20 pts)
    sample_size_estimate: str = Field(
        description="Estimated sample size with justification (e.g., 'n=120 patients over study period based on 85% occupancy, 4.2 day LOS, 40% high-risk prevalence')"
    )

    # Time-Bound fields (Rubric: 15 pts)
    start_date: str = Field(
        description="Project start date (e.g., 'January 6, 2026')"
    )
    end_date: str = Field(
        description="Project end date (e.g., 'June 30, 2026')"
    )
    milestones: List[str] = Field(
        description="4-6 key milestones with dates (IRB approval, training, go-live, audits, analysis)",
        min_items=4,
        max_items=8
    )

    # Relevance fields (Rubric: 20 pts)
    institutional_alignment: str = Field(
        description="How this aligns with institutional goals/standards (e.g., 'Joint Commission NPSG 09.02.01, Hospital strategic goal: Top quartile patient safety by 2027')"
    )
    evidence_summary: str = Field(
        description="Brief evidence base (2-3 key studies with outcomes, e.g., 'Meade et al., 2006, AJN: 50-60% fall reduction')"
    )

    # Legacy fields for backwards compatibility
    clinical_significance: str = Field(
        description="Why this question matters clinically and to patient care",
        min_length=50
    )
    search_terms: List[str] = Field(
        description="Recommended search terms for literature review",
        min_items=3,
        max_items=10
    )

    # NO HARDCODED EXAMPLES - This is production research software
    # Examples would contain fake data inappropriate for real research


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

    # NO HARDCODED EXAMPLES - Real research data only


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

    # NO HARDCODED EXAMPLES - Real research data only


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

    # NO HARDCODED EXAMPLES - Real research data only


# Export all schemas
__all__ = [
    'EvidenceLevel',
    'PICOTQuestion',
    'ResearchArticle',
    'LiteratureSynthesis',
    'DataAnalysisPlan',
]
