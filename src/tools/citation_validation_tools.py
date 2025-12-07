"""
Citation Validation Tools - Evidence Grading & Retraction Detection

Provides validation capabilities for CitationValidationAgent.
Implements real logic for evidence grading, retraction checking, and quality scoring.

Created: 2025-12-07 (Phase 0 - Agent 7 Implementation)
"""

import re
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from xml.etree import ElementTree

import httpx
from agno.tools import Toolkit

from src.models.evidence_types import EvidenceLevel, ValidationResult

logger = logging.getLogger(__name__)


# =============================================================================
# Evidence Level Detection Patterns
# =============================================================================

# Patterns to detect study design from title/abstract
STUDY_DESIGN_PATTERNS = {
    EvidenceLevel.LEVEL_I: [
        r'\bsystematic\s+review\b',
        r'\bmeta[\-\s]?analysis\b',
        r'\bcochrane\s+(review|database)\b',
        r'\bprisma\b',
        r'\bforest\s+plot\b',
    ],
    EvidenceLevel.LEVEL_II: [
        r'\brandomized\s+controlled\s+trial\b',
        r'\brct\b',
        r'\brandomised\s+controlled\s+trial\b',
        r'\bdouble[\-\s]?blind\b',
        r'\bplacebo[\-\s]?controlled\b',
        r'\brandom\s+assignment\b',
        r'\brandom\s+allocation\b',
    ],
    EvidenceLevel.LEVEL_III: [
        r'\bcontrolled\s+trial\b',
        r'\bquasi[\-\s]?experiment',
        r'\bnon[\-\s]?randomized\b',
        r'\bpre[\-\s]?test[\-\s]?post[\-\s]?test\b',
        r'\binterrupted\s+time\s+series\b',
    ],
    EvidenceLevel.LEVEL_IV: [
        r'\bcohort\s+study\b',
        r'\bcase[\-\s]?control\b',
        r'\blongitudinal\b',
        r'\bprospective\b',
        r'\bretrospective\b',
        r'\bcross[\-\s]?sectional\b',
    ],
    EvidenceLevel.LEVEL_V: [
        r'\bsystematic\s+review\s+of\s+qualitative\b',
        r'\bmeta[\-\s]?synthesis\b',
        r'\bqualitative\s+meta[\-\s]?analysis\b',
    ],
    EvidenceLevel.LEVEL_VI: [
        r'\bqualitative\b',
        r'\bdescriptive\s+study\b',
        r'\bphenomenol',
        r'\bgrounded\s+theory\b',
        r'\bethnograph',
        r'\bcase\s+study\b',
        r'\bsurvey\b',
        r'\bpilot\s+study\b',
    ],
    EvidenceLevel.LEVEL_VII: [
        r'\bexpert\s+opinion\b',
        r'\bconsensus\s+statement\b',
        r'\beditorial\b',
        r'\bcommentary\b',
        r'\bletter\s+to\s+(the\s+)?editor\b',
        r'\bguideline\b',
        r'\brecommendation\b',
    ],
}


class CitationValidationTools(Toolkit):
    """
    Tools for validating research citations.
    
    Provides:
    - Evidence level grading (Johns Hopkins hierarchy)
    - Retraction detection via PubMed
    - Currency assessment
    - Quality scoring
    """
    
    def __init__(
        self,
        email: str = "nursing.research@example.com",
        max_age_years: int = 5,
        min_evidence_level: str = "IV",
        **kwargs
    ):
        """
        Initialize validation tools.
        
        Args:
            email: Email for NCBI API (required by their policy)
            max_age_years: Threshold for "outdated" articles
            min_evidence_level: Minimum acceptable evidence level (I-VII)
        """
        self.email = email
        self.max_age_years = max_age_years
        self.min_evidence_level = min_evidence_level
        
        tools = [
            self.grade_evidence_level,
            self.check_retraction_status,
            self.assess_currency,
            self.validate_single_article,
        ]
        
        super().__init__(name="citation_validation", tools=tools, **kwargs)
    
    def grade_evidence_level(
        self, 
        title: str, 
        abstract: str = "",
        publication_type: str = ""
    ) -> str:
        """
        Grade evidence level based on study design.
        
        Uses Johns Hopkins EBP hierarchy (I-VII).
        Analyzes title, abstract, and publication type to determine study design.
        
        Args:
            title: Article title
            abstract: Article abstract (optional but improves accuracy)
            publication_type: PubMed publication type if available
            
        Returns:
            JSON string with evidence_level, confidence, and reasoning
        """
        import json
        
        text = f"{title} {abstract} {publication_type}".lower()
        
        # Check patterns in order of evidence strength
        for level in [
            EvidenceLevel.LEVEL_I,
            EvidenceLevel.LEVEL_II, 
            EvidenceLevel.LEVEL_III,
            EvidenceLevel.LEVEL_IV,
            EvidenceLevel.LEVEL_V,
            EvidenceLevel.LEVEL_VI,
            EvidenceLevel.LEVEL_VII,
        ]:
            patterns = STUDY_DESIGN_PATTERNS.get(level, [])
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    # Calculate confidence based on match specificity
                    confidence = 0.85 if abstract else 0.65
                    
                    return json.dumps({
                        "evidence_level": level.code,
                        "description": level.description,
                        "confidence": confidence,
                        "matched_pattern": pattern,
                        "reasoning": f"Detected '{pattern}' in {'abstract' if abstract else 'title'}"
                    })
        
        # Default to unknown if no pattern matches
        return json.dumps({
            "evidence_level": EvidenceLevel.UNKNOWN.code,
            "description": EvidenceLevel.UNKNOWN.description,
            "confidence": 0.0,
            "matched_pattern": None,
            "reasoning": "No study design indicators found"
        })
    
    def check_retraction_status(self, pmid: str) -> str:
        """
        Check if an article has been retracted via PubMed.
        
        Queries NCBI's retraction database to verify article status.
        
        Args:
            pmid: PubMed ID to check
            
        Returns:
            JSON string with is_retracted, retraction_date, and reason
        """
        import json
        
        if not pmid or pmid == "unknown":
            return json.dumps({
                "pmid": pmid,
                "is_retracted": False,
                "checked": False,
                "error": "Invalid or missing PMID"
            })
        
        # Clean PMID
        pmid = str(pmid).strip()
        
        try:
            # Query PubMed for retraction status
            # NCBI EUtilities: search for retraction notices linked to this PMID
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                "db": "pubmed",
                "term": f"{pmid}[PMID] AND retracted publication[pt]",
                "retmax": 1,
                "email": self.email,
            }
            
            time.sleep(0.34)  # NCBI rate limit
            response = httpx.get(url, params=params, timeout=10.0)
            
            if response.status_code == 200:
                root = ElementTree.fromstring(response.content)
                count_elem = root.find(".//Count")
                count = int(count_elem.text) if count_elem is not None else 0
                
                if count > 0:
                    return json.dumps({
                        "pmid": pmid,
                        "is_retracted": True,
                        "checked": True,
                        "retraction_reason": "Publication marked as retracted in PubMed",
                        "warning": "⚠️ DO NOT USE - Article has been retracted"
                    })
                else:
                    return json.dumps({
                        "pmid": pmid,
                        "is_retracted": False,
                        "checked": True,
                        "status": "No retraction found"
                    })
            else:
                return json.dumps({
                    "pmid": pmid,
                    "is_retracted": False,
                    "checked": False,
                    "error": f"PubMed API returned status {response.status_code}"
                })
                
        except Exception as e:
            logger.error(f"Error checking retraction for PMID {pmid}: {e}")
            return json.dumps({
                "pmid": pmid,
                "is_retracted": False,
                "checked": False,
                "error": str(e)
            })
    
    def assess_currency(self, publication_date: str) -> str:
        """
        Assess if an article is current, aging, or outdated.
        
        Uses configurable thresholds (default: 5 years for current).
        
        Args:
            publication_date: Publication date (YYYY, YYYY-MM, or YYYY-MM-DD format)
            
        Returns:
            JSON string with currency_status, age_years, and recommendation
        """
        import json
        
        if not publication_date:
            return json.dumps({
                "currency_status": "unknown",
                "age_years": None,
                "recommendation": "Cannot assess - no publication date"
            })
        
        try:
            # Extract year from various date formats
            year_match = re.search(r'(\d{4})', str(publication_date))
            if not year_match:
                return json.dumps({
                    "currency_status": "unknown",
                    "age_years": None,
                    "recommendation": "Cannot parse publication date"
                })
            
            pub_year = int(year_match.group(1))
            current_year = datetime.now().year
            age_years = current_year - pub_year
            
            # Determine currency status
            if age_years <= self.max_age_years:
                status = "current"
                recommendation = "✅ Article is current (within 5 years)"
            elif age_years <= self.max_age_years + 2:
                status = "aging"
                recommendation = "⚠️ Article is aging - consider finding more recent sources"
            else:
                status = "outdated"
                recommendation = "❌ Article may be outdated - use only if landmark study"
            
            return json.dumps({
                "currency_status": status,
                "age_years": age_years,
                "publication_year": pub_year,
                "recommendation": recommendation
            })
            
        except Exception as e:
            logger.error(f"Error assessing currency for date '{publication_date}': {e}")
            return json.dumps({
                "currency_status": "unknown",
                "age_years": None,
                "error": str(e)
            })
    
    def validate_single_article(
        self,
        pmid: str,
        title: str,
        abstract: str = "",
        publication_date: str = "",
        publication_type: str = ""
    ) -> str:
        """
        Perform full validation on a single article.
        
        Combines evidence grading, retraction check, and currency assessment.
        Returns a comprehensive validation result with recommendation.
        
        Args:
            pmid: PubMed ID
            title: Article title
            abstract: Article abstract
            publication_date: Publication date
            publication_type: Article/publication type
            
        Returns:
            JSON string with complete validation result
        """
        import json
        
        issues = []
        quality_score = 0.5  # Start neutral
        
        # 1. Grade evidence level
        evidence_result = json.loads(self.grade_evidence_level(title, abstract, publication_type))
        evidence_level = evidence_result.get("evidence_level", "?")
        evidence_confidence = evidence_result.get("confidence", 0.0)
        
        # Adjust quality based on evidence level
        level_scores = {"I": 1.0, "II": 0.9, "III": 0.8, "IV": 0.7, "V": 0.6, "VI": 0.5, "VII": 0.3, "?": 0.2}
        quality_score = level_scores.get(evidence_level, 0.2)
        
        # 2. Check retraction status
        retraction_result = json.loads(self.check_retraction_status(pmid))
        is_retracted = retraction_result.get("is_retracted", False)
        
        if is_retracted:
            issues.append("⚠️ RETRACTED - Do not use")
            quality_score = 0.0  # Instant disqualification
        
        # 3. Assess currency
        currency_result = json.loads(self.assess_currency(publication_date))
        currency_status = currency_result.get("currency_status", "unknown")
        age_years = currency_result.get("age_years")
        
        if currency_status == "outdated":
            issues.append(f"Article is {age_years} years old (outdated)")
            quality_score *= 0.7
        elif currency_status == "aging":
            issues.append(f"Article is {age_years} years old (aging)")
            quality_score *= 0.85
        
        # 4. Determine recommendation
        if is_retracted:
            recommendation = "exclude"
        elif quality_score >= 0.7:
            recommendation = "include"
        elif quality_score >= 0.4:
            recommendation = "review"
        else:
            recommendation = "exclude"
        
        # Build comprehensive result
        result = {
            "pmid": pmid,
            "title": title,
            "evidence_level": evidence_level,
            "evidence_description": evidence_result.get("description", "Unknown"),
            "evidence_confidence": evidence_confidence,
            "is_retracted": is_retracted,
            "currency_status": currency_status,
            "age_years": age_years,
            "quality_score": round(quality_score, 2),
            "issues": issues,
            "recommendation": recommendation,
            "validated_at": datetime.now().isoformat()
        }
        
        return json.dumps(result)


def create_citation_validation_tools(
    email: str = "nursing.research@example.com",
    max_age_years: int = 5,
    min_evidence_level: str = "IV"
) -> CitationValidationTools:
    """
    Factory function to create CitationValidationTools instance.
    
    Args:
        email: Email for NCBI API
        max_age_years: Threshold for outdated articles
        min_evidence_level: Minimum acceptable evidence level
        
    Returns:
        Configured CitationValidationTools instance
    """
    return CitationValidationTools(
        email=email,
        max_age_years=max_age_years,
        min_evidence_level=min_evidence_level
    )
