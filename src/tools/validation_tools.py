"""
Validation Tools for Citation Validation Agent

Provides tools for:
- Evidence level grading (Johns Hopkins hierarchy)
- Currency assessment (flags old articles)
- Quality scoring (study design indicators)
- Full article validation pipeline

Created: 2025-12-07 (Phase 5 - Citation Validation, Phase 2)
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from src.models.evidence_types import EvidenceLevel, ValidationResult
from src.services.citation_apis import PubMedRetractionChecker


class ValidationTools:
    """
    Tools for validating research citations.
    
    Provides rule-based evidence grading, currency checking,
    and quality scoring for nursing research articles.
    """
    
    # Keywords for evidence level detection
    EVIDENCE_KEYWORDS = {
        EvidenceLevel.LEVEL_I: [
            "systematic review", "meta-analysis", "meta analysis",
            "cochrane review", "umbrella review", "integrative review"
        ],
        EvidenceLevel.LEVEL_II: [
            "randomized controlled trial", "rct", "randomised controlled trial",
            "double-blind", "double blind", "placebo-controlled", "placebo controlled"
        ],
        EvidenceLevel.LEVEL_III: [
            "controlled trial", "quasi-experimental", "non-randomized",
            "nonrandomized", "controlled clinical trial"
        ],
        EvidenceLevel.LEVEL_IV: [
            "cohort study", "case-control", "case control", "longitudinal study",
            "prospective study", "retrospective study", "observational study"
        ],
        EvidenceLevel.LEVEL_V: [
            "systematic review of qualitative", "meta-synthesis", "metasynthesis",
            "qualitative synthesis", "qualitative meta"
        ],
        EvidenceLevel.LEVEL_VI: [
            "qualitative study", "descriptive study", "cross-sectional",
            "cross sectional", "survey study", "case study", "case report",
            "phenomenological", "grounded theory", "ethnographic"
        ],
        EvidenceLevel.LEVEL_VII: [
            "expert opinion", "editorial", "commentary", "consensus statement",
            "clinical opinion", "narrative review", "letter to editor"
        ],
    }
    
    def __init__(self):
        """Initialize validation tools with retraction checker."""
        self.retraction_checker = PubMedRetractionChecker()
    
    def grade_evidence(
        self,
        abstract: str,
        title: str = "",
        publication_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Grade evidence level based on study design.
        
        Uses rule-based keyword matching with confidence scoring.
        Checks title, abstract, and PubMed publication type tags.
        
        Args:
            abstract: Article abstract text
            title: Article title
            publication_types: PubMed publication type tags (e.g., ["Randomized Controlled Trial"])
            
        Returns:
            Dict with:
            - evidence_level: EvidenceLevel enum value
            - confidence: float 0.0-1.0
            - matched_keywords: list of matched terms
            - all_matches: dict of all levels with matches
        """
        text = f"{title} {abstract}".lower()
        pub_types = [pt.lower() for pt in (publication_types or [])]
        
        matches = {}
        
        # Check each evidence level for keyword matches
        for level, keywords in self.EVIDENCE_KEYWORDS.items():
            matched = []
            for kw in keywords:
                # Check in text
                if kw in text:
                    matched.append(kw)
                # Check in publication types
                elif any(kw in pt for pt in pub_types):
                    matched.append(f"{kw} (pub_type)")
            if matched:
                matches[level] = matched
        
        # No matches found
        if not matches:
            return {
                "evidence_level": EvidenceLevel.UNKNOWN,
                "confidence": 0.0,
                "matched_keywords": [],
                "all_matches": {}
            }
        
        # Priority order (Level I is highest quality, check first)
        priority_order = [
            EvidenceLevel.LEVEL_I,
            EvidenceLevel.LEVEL_II,
            EvidenceLevel.LEVEL_III,
            EvidenceLevel.LEVEL_IV,
            EvidenceLevel.LEVEL_V,
            EvidenceLevel.LEVEL_VI,
            EvidenceLevel.LEVEL_VII,
        ]
        
        # Select highest evidence level found
        for level in priority_order:
            if level in matches:
                # Confidence based on number of matching keywords
                confidence = min(1.0, len(matches[level]) * 0.3 + 0.4)
                return {
                    "evidence_level": level,
                    "confidence": round(confidence, 2),
                    "matched_keywords": matches[level],
                    "all_matches": {k.name: v for k, v in matches.items()}
                }
        
        return {
            "evidence_level": EvidenceLevel.UNKNOWN,
            "confidence": 0.0,
            "matched_keywords": [],
            "all_matches": {}
        }
    
    def check_currency(
        self,
        publication_date: str,
        max_age_years: int = 5,
        reference_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Check if article is current or outdated.
        
        Currency thresholds:
        - current: within max_age_years
        - aging: max_age_years to max_age_years+2
        - outdated: older than max_age_years+2
        
        Args:
            publication_date: Date string (YYYY-MM-DD or YYYY format)
            max_age_years: Threshold for "current" status (default 5)
            reference_date: Date to compare against (default: now)
            
        Returns:
            Dict with:
            - currency_flag: "current" | "aging" | "outdated" | "unknown"
            - age_years: float years since publication
            - is_current: bool
            - publication_date: original date string
        """
        ref_date = reference_date or datetime.now()
        
        try:
            # Parse date - handle multiple formats
            if len(publication_date) == 4:
                # YYYY format
                pub_date = datetime(int(publication_date), 1, 1)
            elif len(publication_date) >= 10:
                # YYYY-MM-DD or longer format
                pub_date = datetime.fromisoformat(publication_date[:10])
            elif len(publication_date) == 7:
                # YYYY-MM format
                pub_date = datetime.strptime(publication_date, "%Y-%m")
            else:
                raise ValueError(f"Unrecognized date format: {publication_date}")
            
            # Calculate age
            age_days = (ref_date - pub_date).days
            age_years = age_days / 365.25
            
            # Determine currency flag
            if age_years <= max_age_years:
                flag = "current"
            elif age_years <= max_age_years + 2:
                flag = "aging"
            else:
                flag = "outdated"
            
            return {
                "currency_flag": flag,
                "age_years": round(age_years, 1),
                "is_current": flag == "current",
                "publication_date": publication_date
            }
            
        except (ValueError, TypeError) as e:
            return {
                "currency_flag": "unknown",
                "age_years": None,
                "is_current": False,
                "publication_date": publication_date,
                "error": str(e)
            }
    
    def calculate_quality_score(
        self,
        evidence_level: EvidenceLevel,
        currency_flag: str,
        is_retracted: bool = False,
        issues: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Calculate quality score based on evidence level and currency.
        
        Args:
            evidence_level: Graded evidence level
            currency_flag: Currency assessment result
            is_retracted: Whether article is retracted
            issues: List of identified issues
            
        Returns:
            Dict with:
            - quality_score: float 0.0-1.0
            - recommendation: "include" | "review" | "exclude"
        """
        issues = issues or []
        
        # Base score from evidence level
        level_scores = {
            EvidenceLevel.LEVEL_I: 1.0,
            EvidenceLevel.LEVEL_II: 0.9,
            EvidenceLevel.LEVEL_III: 0.75,
            EvidenceLevel.LEVEL_IV: 0.65,
            EvidenceLevel.LEVEL_V: 0.55,
            EvidenceLevel.LEVEL_VI: 0.45,
            EvidenceLevel.LEVEL_VII: 0.35,
            EvidenceLevel.UNKNOWN: 0.25,
        }
        quality_score = level_scores.get(evidence_level, 0.25)
        
        # Penalize for currency
        if currency_flag == "outdated":
            quality_score *= 0.7
        elif currency_flag == "aging":
            quality_score *= 0.85
        elif currency_flag == "unknown":
            quality_score *= 0.9
        
        # Retracted = automatic exclude
        if is_retracted:
            quality_score = 0.0
        
        # Penalize for issues
        if issues:
            quality_score *= max(0.5, 1.0 - (len(issues) * 0.1))
        
        quality_score = round(quality_score, 2)
        
        # Determine recommendation
        if is_retracted:
            recommendation = "exclude"
        elif quality_score >= 0.65:
            recommendation = "include"
        elif quality_score >= 0.40:
            recommendation = "review"
        else:
            recommendation = "exclude"
        
        return {
            "quality_score": quality_score,
            "recommendation": recommendation
        }
    
    def validate_article(
        self,
        pmid: str,
        title: str,
        abstract: str,
        publication_date: str,
        publication_types: Optional[List[str]] = None,
        max_age_years: int = 5,
        check_retraction: bool = True,
        is_retracted: bool = False,
        retraction_reason: Optional[str] = None
    ) -> ValidationResult:
        """
        Perform full validation on a single article.
        
        Combines evidence grading, currency checking, and quality scoring
        into a single ValidationResult.
        
        Args:
            pmid: PubMed ID
            title: Article title
            abstract: Article abstract
            publication_date: Publication date (YYYY-MM-DD or YYYY)
            publication_types: PubMed publication type tags
            max_age_years: Currency threshold
            check_retraction: Whether to check PubMed for retractions (default True)
            is_retracted: Pre-checked retraction status (overrides API check)
            retraction_reason: Reason for retraction if applicable
            
        Returns:
            ValidationResult with complete assessment
        """
        issues = []
        
        # Step 1: Grade evidence level
        grade_result = self.grade_evidence(abstract, title, publication_types)
        evidence_level = grade_result["evidence_level"]
        evidence_confidence = grade_result["confidence"]
        
        if evidence_level == EvidenceLevel.UNKNOWN:
            issues.append("Could not determine evidence level from study design")
        
        # Step 2: Check currency
        currency_result = self.check_currency(publication_date, max_age_years)
        currency_flag = currency_result.get("currency_flag", "unknown")
        
        if currency_flag == "outdated":
            age = currency_result.get("age_years", "?")
            issues.append(f"Article is {age} years old (outdated)")
        elif currency_flag == "aging":
            issues.append("Article approaching outdated status")
        elif currency_flag == "unknown":
            issues.append("Could not determine publication date")
        
        # Step 3: Check for retraction if not already provided
        if not is_retracted and check_retraction and pmid and pmid != "unknown":
            retraction_status = self.retraction_checker.check_retraction(pmid)
            is_retracted = retraction_status.is_retracted
            if is_retracted:
                retraction_reason = retraction_status.retraction_reason
        
        # Handle retraction
        if is_retracted:
            issues.insert(0, "⚠️ ARTICLE HAS BEEN RETRACTED")
        
        # Step 4: Calculate quality score
        quality_result = self.calculate_quality_score(
            evidence_level=evidence_level,
            currency_flag=currency_flag,
            is_retracted=is_retracted,
            issues=issues
        )
        
        return ValidationResult(
            pmid=pmid,
            title=title,
            evidence_level=evidence_level,
            is_retracted=is_retracted,
            retraction_reason=retraction_reason,
            currency_flag=currency_flag,
            quality_score=quality_result["quality_score"],
            quality_confidence=evidence_confidence,
            issues=issues,
            recommendation=quality_result["recommendation"]
        )
    
    def validate_batch(
        self,
        articles: List[Dict[str, Any]],
        max_age_years: int = 5
    ) -> List[ValidationResult]:
        """
        Validate a batch of articles.
        
        Args:
            articles: List of article dicts with pmid, title, abstract, publication_date
            max_age_years: Currency threshold
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        for article in articles:
            result = self.validate_article(
                pmid=article.get("pmid", "unknown"),
                title=article.get("title", ""),
                abstract=article.get("abstract", ""),
                publication_date=article.get("publication_date", ""),
                publication_types=article.get("publication_types"),
                max_age_years=max_age_years,
                is_retracted=article.get("is_retracted", False),
                retraction_reason=article.get("retraction_reason")
            )
            results.append(result)
        return results
