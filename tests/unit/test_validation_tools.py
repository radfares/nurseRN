"""
Unit tests for Validation Tools - Phase 2
Tests evidence grading, currency checking, quality scoring, and validation logic.

Gate 2 Checkpoint Tests:
- G2.1: Evidence grading tests
- G2.2: Currency checking tests
- G2.3: Quality scoring tests
- G2.4: Article validation tests
"""

import pytest
from datetime import datetime


class TestEvidenceGrading:
    """Test evidence level grading logic"""
    
    def test_grade_systematic_review(self):
        """Systematic reviews should be Level I"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.grade_evidence(
            abstract="This systematic review and meta-analysis examined 25 studies...",
            title="Systematic Review of Fall Prevention in Hospitals"
        )
        
        assert result["evidence_level"] == EvidenceLevel.LEVEL_I
        assert result["confidence"] >= 0.5
        assert "systematic review" in result["matched_keywords"]
    
    def test_grade_meta_analysis(self):
        """Meta-analyses should also be Level I"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.grade_evidence(
            abstract="We conducted a meta-analysis of 50 randomized trials..."
        )
        
        assert result["evidence_level"] == EvidenceLevel.LEVEL_I
    
    def test_grade_rct(self):
        """RCTs should be Level II"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.grade_evidence(
            abstract="This randomized controlled trial enrolled 500 patients...",
            title="RCT of New Nursing Intervention"
        )
        
        assert result["evidence_level"] == EvidenceLevel.LEVEL_II
    
    def test_grade_double_blind(self):
        """Double-blind studies should be Level II"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.grade_evidence(
            abstract="In this double-blind placebo-controlled trial..."
        )
        
        assert result["evidence_level"] == EvidenceLevel.LEVEL_II
    
    def test_grade_cohort_study(self):
        """Cohort studies should be Level IV"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.grade_evidence(
            abstract="This prospective cohort study followed 1000 patients for 5 years..."
        )
        
        assert result["evidence_level"] == EvidenceLevel.LEVEL_IV
    
    def test_grade_qualitative_study(self):
        """Qualitative studies should be Level VI"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.grade_evidence(
            abstract="This phenomenological qualitative study explored nurses' experiences..."
        )
        
        assert result["evidence_level"] == EvidenceLevel.LEVEL_VI
    
    def test_grade_expert_opinion(self):
        """Expert opinion should be Level VII"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.grade_evidence(
            abstract="In this editorial, we offer our expert opinion on the matter..."
        )
        
        assert result["evidence_level"] == EvidenceLevel.LEVEL_VII
    
    def test_grade_unknown_design(self):
        """Unrecognized designs should be UNKNOWN"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.grade_evidence(
            abstract="This paper discusses various healthcare topics without methodology."
        )
        
        assert result["evidence_level"] == EvidenceLevel.UNKNOWN
        assert result["confidence"] == 0.0
    
    def test_grade_with_publication_types(self):
        """Should detect level from PubMed publication types"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.grade_evidence(
            abstract="We studied the intervention effects on patients.",
            publication_types=["Randomized Controlled Trial", "Research Support"]
        )
        
        assert result["evidence_level"] == EvidenceLevel.LEVEL_II


class TestCurrencyChecking:
    """Test publication currency assessment"""
    
    def test_current_article(self):
        """Recent article should be 'current'"""
        from src.tools.validation_tools import ValidationTools
        
        tool = ValidationTools()
        result = tool.check_currency(
            publication_date="2024-06-15",
            max_age_years=5,
            reference_date=datetime(2025, 1, 1)
        )
        
        assert result["currency_flag"] == "current"
        assert result["is_current"] == True
        assert result["age_years"] < 1
    
    def test_aging_article(self):
        """Article slightly over threshold should be 'aging'"""
        from src.tools.validation_tools import ValidationTools
        
        tool = ValidationTools()
        result = tool.check_currency(
            publication_date="2019-06-01",
            max_age_years=5,
            reference_date=datetime(2025, 1, 1)
        )
        
        assert result["currency_flag"] == "aging"
    
    def test_outdated_article(self):
        """Old article should be 'outdated'"""
        from src.tools.validation_tools import ValidationTools
        
        tool = ValidationTools()
        result = tool.check_currency(
            publication_date="2015-01-01",
            max_age_years=5,
            reference_date=datetime(2025, 1, 1)
        )
        
        assert result["currency_flag"] == "outdated"
        assert result["age_years"] >= 10.0
    
    def test_year_only_format(self):
        """Should handle YYYY format"""
        from src.tools.validation_tools import ValidationTools
        
        tool = ValidationTools()
        result = tool.check_currency(
            publication_date="2024",
            max_age_years=5,
            reference_date=datetime(2025, 6, 1)
        )
        
        assert result["currency_flag"] == "current"
    
    def test_invalid_date(self):
        """Invalid dates should return 'unknown'"""
        from src.tools.validation_tools import ValidationTools
        
        tool = ValidationTools()
        result = tool.check_currency(
            publication_date="not-a-date"
        )
        
        assert result["currency_flag"] == "unknown"
        assert "error" in result


class TestQualityScoring:
    """Test quality score calculation"""
    
    def test_high_quality_level_i(self):
        """Level I current article should score highest"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.calculate_quality_score(
            evidence_level=EvidenceLevel.LEVEL_I,
            currency_flag="current"
        )
        
        assert result["quality_score"] == 1.0
        assert result["recommendation"] == "include"
    
    def test_medium_quality_level_iv(self):
        """Level IV current article should be medium quality"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.calculate_quality_score(
            evidence_level=EvidenceLevel.LEVEL_IV,
            currency_flag="current"
        )
        
        assert 0.5 <= result["quality_score"] <= 0.7
        assert result["recommendation"] == "include"
    
    def test_outdated_penalty(self):
        """Outdated articles should be penalized"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.calculate_quality_score(
            evidence_level=EvidenceLevel.LEVEL_II,
            currency_flag="outdated"
        )
        
        assert result["quality_score"] < 0.9  # Penalized from 0.9
    
    def test_retracted_excluded(self):
        """Retracted articles should always be excluded"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.calculate_quality_score(
            evidence_level=EvidenceLevel.LEVEL_I,
            currency_flag="current",
            is_retracted=True
        )
        
        assert result["quality_score"] == 0.0
        assert result["recommendation"] == "exclude"
    
    def test_low_quality_excluded(self):
        """Low quality articles should be excluded"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.calculate_quality_score(
            evidence_level=EvidenceLevel.LEVEL_VII,
            currency_flag="outdated"
        )
        
        assert result["recommendation"] == "exclude"


class TestValidateArticle:
    """Test full article validation"""
    
    def test_high_quality_systematic_review(self):
        """High-quality systematic review should get 'include'"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.validate_article(
            pmid="12345678",
            title="Systematic Review of Nursing Interventions for Fall Prevention",
            abstract="This systematic review and meta-analysis examined 50 RCTs on fall prevention...",
            publication_date="2024-03-15"
        )
        
        assert result.evidence_level == EvidenceLevel.LEVEL_I
        assert result.recommendation == "include"
        assert result.quality_score >= 0.8
        assert len(result.issues) == 0
    
    def test_medium_quality_cohort(self):
        """Medium quality cohort study should get 'include' or 'review'"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.validate_article(
            pmid="87654321",
            title="Cohort Study of Sepsis Outcomes",
            abstract="This retrospective cohort study analyzed 500 patients...",
            publication_date="2023-06-01"
        )
        
        assert result.evidence_level == EvidenceLevel.LEVEL_IV
        assert result.recommendation in ["include", "review"]
    
    def test_low_quality_outdated_opinion(self):
        """Outdated expert opinion should get 'exclude'"""
        from src.tools.validation_tools import ValidationTools
        from src.models.evidence_types import EvidenceLevel
        
        tool = ValidationTools()
        result = tool.validate_article(
            pmid="11111111",
            title="Editorial Commentary on Nursing Practice",
            abstract="In this editorial, we offer our expert opinion on emerging trends...",
            publication_date="2010-01-01"
        )
        
        assert result.evidence_level == EvidenceLevel.LEVEL_VII
        assert result.recommendation == "exclude"
        assert len(result.issues) >= 1
    
    def test_retracted_article(self):
        """Retracted article should always be excluded"""
        from src.tools.validation_tools import ValidationTools
        
        tool = ValidationTools()
        result = tool.validate_article(
            pmid="99999999",
            title="Study with Fabricated Data",
            abstract="This systematic review examined...",
            publication_date="2024-01-01",
            is_retracted=True,
            retraction_reason="Data fabrication"
        )
        
        assert result.is_retracted == True
        assert result.recommendation == "exclude"
        assert result.quality_score == 0.0
        assert "RETRACTED" in result.issues[0]


class TestValidateBatch:
    """Test batch validation"""
    
    def test_batch_validation(self):
        """Should validate multiple articles"""
        from src.tools.validation_tools import ValidationTools
        
        tool = ValidationTools()
        
        articles = [
            {
                "pmid": "111",
                "title": "Systematic Review",
                "abstract": "This systematic review examined...",
                "publication_date": "2024-01-01"
            },
            {
                "pmid": "222",
                "title": "Case Study",
                "abstract": "This case study presents...",
                "publication_date": "2023-06-01"
            }
        ]
        
        results = tool.validate_batch(articles)
        
        assert len(results) == 2
        assert results[0].pmid == "111"
        assert results[1].pmid == "222"
