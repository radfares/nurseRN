"""
Unit tests for Citation Validation Agent - Phase 1
Tests core infrastructure: data types, agent skeleton, basic initialization.

Gate 1 Checkpoint Tests:
- G1.1: Evidence types unit tests
- G1.2: Agent initialization tests
- G1.3: Import validation (implicit)
"""

import pytest
from datetime import datetime


class TestEvidenceTypes:
    """Test evidence level enum and validation result dataclass"""
    
    def test_evidence_level_values(self):
        """Verify all evidence levels are defined correctly"""
        from src.models.evidence_types import EvidenceLevel
        
        assert EvidenceLevel.LEVEL_I.code == "I"
        assert "Systematic Review" in EvidenceLevel.LEVEL_I.description
        assert EvidenceLevel.LEVEL_VII.code == "VII"
        assert EvidenceLevel.UNKNOWN.code == "?"
    
    def test_evidence_level_string_representation(self):
        """Verify evidence levels have readable string format"""
        from src.models.evidence_types import EvidenceLevel
        
        level_str = str(EvidenceLevel.LEVEL_II)
        assert "Level II" in level_str
        assert "Randomized" in level_str
    
    def test_evidence_level_ordering(self):
        """Verify all 7 levels plus UNKNOWN are defined"""
        from src.models.evidence_types import EvidenceLevel
        
        all_levels = [e for e in EvidenceLevel if e != EvidenceLevel.UNKNOWN]
        assert len(all_levels) == 7
    
    def test_validation_result_creation(self):
        """Verify ValidationResult can be created with defaults"""
        from src.models.evidence_types import EvidenceLevel, ValidationResult
        
        result = ValidationResult(
            pmid="12345678",
            title="Test Article",
            evidence_level=EvidenceLevel.LEVEL_II
        )
        
        assert result.pmid == "12345678"
        assert result.is_retracted == False
        assert result.recommendation == "review"
        assert isinstance(result.validated_at, datetime)
    
    def test_validation_result_with_issues(self):
        """Verify ValidationResult handles issues list correctly"""
        from src.models.evidence_types import EvidenceLevel, ValidationResult
        
        result = ValidationResult(
            pmid="12345678",
            title="Test Article",
            evidence_level=EvidenceLevel.LEVEL_IV,
            issues=["Small sample size", "Single-site study"],
            recommendation="review"
        )
        
        assert len(result.issues) == 2
        assert "Small sample size" in result.issues
    
    def test_validation_result_to_dict(self):
        """Verify ValidationResult can be serialized to dict"""
        from src.models.evidence_types import EvidenceLevel, ValidationResult
        
        result = ValidationResult(
            pmid="12345678",
            title="Test Article",
            evidence_level=EvidenceLevel.LEVEL_I,
            quality_score=0.95
        )
        
        d = result.to_dict()
        assert d["pmid"] == "12345678"
        assert d["evidence_level"] == "I"
        assert d["quality_score"] == 0.95
        assert "validated_at" in d


class TestValidationReport:
    """Test validation report aggregation"""
    
    def test_validation_report_creation(self):
        """Verify ValidationReport can be created"""
        from src.models.evidence_types import ValidationReport
        
        report = ValidationReport(
            total_articles=10,
            validated_count=10,
            include_count=5,
            review_count=3,
            exclude_count=2,
            retracted_count=1
        )
        
        assert report.total_articles == 10
        assert report.include_count == 5
    
    def test_validation_report_summary(self):
        """Verify report generates readable summary"""
        from src.models.evidence_types import ValidationReport
        
        report = ValidationReport(
            total_articles=10,
            validated_count=10,
            include_count=5,
            review_count=3,
            exclude_count=2,
            retracted_count=1
        )
        
        summary = report.summary()
        assert "Total: 10" in summary
        assert "Include: 5" in summary
        assert "Retracted: 1" in summary


class TestCitationValidationAgentInit:
    """Test agent initialization"""
    
    def test_agent_inherits_from_base(self):
        """Verify agent inherits from BaseAgent"""
        from agents.citation_validation_agent import CitationValidationAgent
        from agents.base_agent import BaseAgent
        
        assert issubclass(CitationValidationAgent, BaseAgent)
    
    def test_agent_has_required_attributes(self):
        """Verify agent has required attributes after init"""
        from agents.citation_validation_agent import CitationValidationAgent
        
        agent = CitationValidationAgent()
        
        assert hasattr(agent, 'agent_name')
        assert hasattr(agent, 'audit_logger')
        assert hasattr(agent, 'tools')
        assert agent.agent_name == "Citation Validation Agent"
    
    def test_agent_creates_audit_logger(self):
        """Verify audit logger is initialized"""
        from agents.citation_validation_agent import CitationValidationAgent
        
        agent = CitationValidationAgent()
        
        assert agent.audit_logger is not None
    
    def test_get_agent_function(self):
        """Verify get_citation_validation_agent returns agent"""
        from agents.citation_validation_agent import get_citation_validation_agent
        
        agent = get_citation_validation_agent()
        
        assert agent is not None
        assert agent.agent_name == "Citation Validation Agent"


class TestCitationValidationAgentMethods:
    """Test agent methods"""
    
    def test_validate_articles_returns_report(self):
        """Verify validate_articles returns ValidationReport"""
        from agents.citation_validation_agent import CitationValidationAgent
        from src.models.evidence_types import ValidationReport
        
        agent = CitationValidationAgent()
        
        articles = [
            {"pmid": "12345678", "title": "Test Article 1"},
            {"pmid": "87654321", "title": "Test Article 2"}
        ]
        
        report = agent.validate_articles(articles)
        
        assert isinstance(report, ValidationReport)
        assert report.total_articles == 2
        assert report.validated_count == 2
    
    def test_show_usage_examples_runs(self):
        """Verify show_usage_examples doesn't crash"""
        from agents.citation_validation_agent import CitationValidationAgent
        
        agent = CitationValidationAgent()
        
        # Should not raise
        agent.show_usage_examples()
