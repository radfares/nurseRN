"""
Evidence Types for Citation Validation

Defines evidence hierarchy and validation result structures
following nursing research frameworks (Johns Hopkins EBP).

Created: 2025-12-07 (Phase 5 - Citation Validation)
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


class EvidenceLevel(Enum):
    """
    Johns Hopkins EBP Evidence Hierarchy
    
    Level I is highest quality (systematic reviews/meta-analyses)
    Level VII is lowest (expert opinion)
    """
    LEVEL_I = ("I", "Systematic Review / Meta-Analysis")
    LEVEL_II = ("II", "Randomized Controlled Trial")
    LEVEL_III = ("III", "Controlled Trial (non-randomized)")
    LEVEL_IV = ("IV", "Case-Control / Cohort Study")
    LEVEL_V = ("V", "Systematic Review of Qualitative")
    LEVEL_VI = ("VI", "Single Qualitative / Descriptive")
    LEVEL_VII = ("VII", "Expert Opinion")
    UNKNOWN = ("?", "Unable to Determine")
    
    @property
    def code(self) -> str:
        """Short code for the evidence level (I, II, III, etc.)"""
        return self.value[0]
    
    @property
    def description(self) -> str:
        """Human-readable description of the evidence level"""
        return self.value[1]
    
    def __str__(self) -> str:
        return f"Level {self.code}: {self.description}"


@dataclass
class ValidationResult:
    """
    Result of validating a single citation.
    
    Contains evidence grading, retraction status, quality scoring,
    and recommendation for inclusion/exclusion.
    """
    pmid: str
    title: str
    evidence_level: EvidenceLevel
    is_retracted: bool = False
    retraction_reason: Optional[str] = None
    journal_sjr: Optional[float] = None
    currency_flag: str = "current"  # "current" | "aging" | "outdated" | "unknown"
    quality_score: float = 0.0  # 0.0 - 1.0
    quality_confidence: float = 0.0  # How confident is the grading
    issues: List[str] = field(default_factory=list)
    recommendation: str = "review"  # "include" | "review" | "exclude"
    validated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "pmid": self.pmid,
            "title": self.title,
            "evidence_level": self.evidence_level.code,
            "evidence_description": self.evidence_level.description,
            "is_retracted": self.is_retracted,
            "retraction_reason": self.retraction_reason,
            "journal_sjr": self.journal_sjr,
            "currency_flag": self.currency_flag,
            "quality_score": self.quality_score,
            "quality_confidence": self.quality_confidence,
            "issues": self.issues,
            "recommendation": self.recommendation,
            "validated_at": self.validated_at.isoformat()
        }


@dataclass
class ValidationReport:
    """
    Aggregated validation report for multiple citations.
    """
    total_articles: int
    validated_count: int
    include_count: int
    review_count: int
    exclude_count: int
    retracted_count: int
    results: List[ValidationResult] = field(default_factory=list)
    
    def summary(self) -> str:
        """Generate human-readable summary"""
        return (
            f"📊 Validation Report\n"
            f"   Total: {self.total_articles} | Validated: {self.validated_count}\n"
            f"   ✅ Include: {self.include_count} | ⚠️ Review: {self.review_count} | ❌ Exclude: {self.exclude_count}\n"
            f"   🚨 Retracted: {self.retracted_count}"
        )
