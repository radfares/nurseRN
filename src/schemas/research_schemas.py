"""
Structured output schemas for nursing research agents.

Enforces consistent, high-quality outputs across all agents.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class EvidenceLevel(str, Enum):
    """Johns Hopkins Evidence Levels"""
    LEVEL_I = "I"
    LEVEL_II = "II"
    LEVEL_III = "III"
    LEVEL_IV = "IV"
    LEVEL_V = "V"
    LEVEL_VI = "VI"
    LEVEL_VII = "VII"


class PICOTQuestion(BaseModel):
    """Structured PICOT question output"""
    population: str = Field(description="Population (P) - specific patient group")
    intervention: str = Field(description="Intervention (I) - what you plan to do")
    comparison: str = Field(description="Comparison (C) - alternative or control")
    outcome: str = Field(description="Outcome (O) - measurable result")
    timeframe: str = Field(description="Timeframe (T) - duration of study/intervention")
    full_question: str = Field(description="Complete PICOT question in sentence form")
    clinical_significance: str = Field(description="Why this matters clinically")
    search_terms: List[str] = Field(description="Recommended search terms for literature review", min_length=3)


class ResearchArticle(BaseModel):
    """Structured article information"""
    pmid: str = Field(description="PubMed ID")
    title: str = Field(description="Article title")
    authors: List[str] = Field(description="Author names")
    year: int = Field(description="Publication year")
    journal: str = Field(description="Journal name")
    evidence_level: Optional[EvidenceLevel] = Field(default=None, description="Johns Hopkins evidence level")
    is_retracted: bool = Field(default=False, description="Retraction status")
    relevance_score: float = Field(description="Relevance to query (0.0-1.0)", ge=0.0, le=1.0)
    key_findings: List[str] = Field(description="Main findings from the article", min_length=1)
    abstract: Optional[str] = Field(default=None, description="Article abstract")


class LiteratureSynthesis(BaseModel):
    """Structured synthesis output"""
    topic: str = Field(description="Research topic")
    picot_question: str = Field(description="PICOT question addressed")
    articles_reviewed: int = Field(description="Number of articles reviewed", ge=0)
    evidence_summary: str = Field(description="Summary of evidence (2-3 paragraphs)")
    key_findings: List[str] = Field(description="Main findings across all articles", min_length=3)
    recommendations: List[str] = Field(description="Clinical recommendations based on evidence", min_length=2)
    evidence_quality: str = Field(description="Overall evidence quality assessment")
    gaps_identified: List[str] = Field(description="Research gaps identified", min_length=1)
    confidence_level: float = Field(description="Confidence in recommendations (0.0-1.0)", ge=0.0, le=1.0)
    citations: List[str] = Field(description="PMIDs cited in synthesis", min_length=1)


class DataAnalysisPlan(BaseModel):
    """Structured data analysis output"""
    study_design: str = Field(description="Study design type (e.g., RCT, cohort, case-control)")
    sample_size_required: int = Field(description="Required sample size", gt=0)
    statistical_tests: List[str] = Field(description="Recommended statistical tests", min_length=1)
    power: float = Field(description="Statistical power", ge=0.0, le=1.0)
    alpha: float = Field(description="Significance level", ge=0.0, le=1.0)
    effect_size: float = Field(description="Expected effect size")
    data_collection_plan: List[str] = Field(description="Data collection steps", min_length=2)
    analysis_timeline: str = Field(description="Timeline for analysis")
    assumptions: List[str] = Field(description="Statistical assumptions", min_length=1)


class ValidationResult(BaseModel):
    """Structured validation output"""
    pmid: str = Field(description="PubMed ID")
    evidence_level: EvidenceLevel = Field(description="Johns Hopkins evidence level")
    is_retracted: bool = Field(description="Retraction status")
    is_current: bool = Field(description="Published within last 5 years")
    quality_score: float = Field(description="Overall quality score (0.0-1.0)", ge=0.0, le=1.0)
    recommendation: str = Field(description="Include, exclude, or review with caution")
    rationale: str = Field(description="Reason for recommendation")


__all__ = [
    'EvidenceLevel',
    'PICOTQuestion',
    'ResearchArticle',
    'LiteratureSynthesis',
    'DataAnalysisPlan',
    'ValidationResult',
]
