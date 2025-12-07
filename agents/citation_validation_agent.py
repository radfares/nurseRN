"""
Citation Validation Agent - Evidence Grading & Quality Assessment

Validates research citations for evidence-based practice standards.
Integrates with existing search agents to filter low-quality sources.

Features:
- Evidence level grading (Johns Hopkins hierarchy I-VII)
- Retraction detection (PubMed + CrossRef)
- Currency assessment (flags articles >5 years old)
- Quality scoring (study design, sample size indicators)

Created: 2025-12-07 (Phase 5 - Citation Validation)
"""

import os
import time
import traceback
from textwrap import dedent
from typing import Any, Dict, List, Optional

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

from agent_config import get_db_path
from agents.base_agent import BaseAgent
from src.models.evidence_types import EvidenceLevel, ValidationResult, ValidationReport
from src.services.agent_audit_logger import get_audit_logger


class CitationValidationAgent(BaseAgent):
    """
    Citation Validation Agent for evidence-based practice.
    
    Validates research citations against nursing research quality standards.
    Uses Johns Hopkins EBP evidence hierarchy for grading.
    
    VALIDATION FEATURES:
    - Evidence level grading (Level I systematic reviews → Level VII expert opinion)
    - Retraction detection via PubMed retraction database
    - Currency checking (flags articles older than threshold)
    - Quality scoring based on study design indicators
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize the Citation Validation Agent.
        
        Args:
            db_connection: Optional database connection for caching results
        """
        tools = self._create_tools()
        super().__init__(
            agent_name="Citation Validation Agent",
            agent_key="citation_validation",
            tools=tools,
        )
        self.db = db_connection
        self.audit_logger = get_audit_logger(
            "citation_validation", "Citation Validation Agent"
        )
    
    def _create_tools(self) -> list:
        """
        Create validation tools.
        
        Tools:
        - grade_evidence_level: Assign evidence level based on study design
        - check_retraction_status: Query PubMed for retraction status
        - assess_currency: Assess if article is current or outdated
        - validate_single_article: Full validation pipeline
        """
        try:
            from src.tools.citation_validation_tools import create_citation_validation_tools
            validation_tools = create_citation_validation_tools(
                email=os.getenv("PUBMED_EMAIL", "nursing.research@example.com"),
                max_age_years=5,
                min_evidence_level="IV"
            )
            self.validation_tools = validation_tools  # Store for direct access
            return [validation_tools]
        except ImportError as e:
            import logging
            logging.getLogger(__name__).warning(f"Could not import validation tools: {e}")
            self.validation_tools = None
            return []
    
    def _create_agent(self) -> Agent:
        """Create and configure the Citation Validation Agent."""
        return Agent(
            name="Citation Validation Agent",
            role="Validate research citations for evidence-based practice standards",
            model=OpenAIChat(
                id="gpt-4o",
                temperature=0,  # Strict factual mode for validation
            ),
            tools=self.tools,
            description=dedent("""\
                You are a Citation Validation Specialist who evaluates research
                articles for evidence-based practice standards. You assess
                evidence levels using the Johns Hopkins EBP hierarchy, check for
                retractions, and score study quality to help nurses identify
                the most reliable sources for clinical practice.
                """),
            instructions=dedent("""\
                VALIDATION PROTOCOL:
                ====================
                
                1. EVIDENCE LEVEL GRADING (Johns Hopkins Hierarchy)
                   - Level I: Systematic reviews, meta-analyses
                   - Level II: Randomized controlled trials
                   - Level III: Controlled trials (non-randomized)
                   - Level IV: Case-control, cohort studies
                   - Level V: Systematic reviews of qualitative
                   - Level VI: Single qualitative, descriptive studies
                   - Level VII: Expert opinion, consensus statements
                
                2. RETRACTION CHECK
                   - Query PubMed retraction database
                   - Flag any retracted or corrected articles
                   - Automatically exclude retracted articles
                
                3. CURRENCY ASSESSMENT
                   - Current: Within 5 years
                   - Aging: 5-7 years old
                   - Outdated: >7 years old
                   - Exception: Seminal/landmark studies
                
                4. QUALITY SCORING (0.0 - 1.0)
                   - Based on evidence level
                   - Adjusted for currency
                   - Penalized for identified issues
                
                5. RECOMMENDATION
                   - INCLUDE: High quality, no issues
                   - REVIEW: Medium quality, minor concerns
                   - EXCLUDE: Low quality, retracted, or major issues
                
                OUTPUT FORMAT:
                ==============
                For each article, provide:
                - Evidence Level (I-VII)
                - Quality Score (0.0-1.0)
                - Currency Status
                - Issues Found
                - Recommendation (Include/Review/Exclude)
                
                Always be transparent about confidence levels and limitations.
                """),
            add_history_to_context=True,
            add_datetime_to_context=True,
            markdown=True,
            db=SqliteDb(db_file=get_db_path("citation_validation")),
        )
    
    def validate_articles(
        self,
        articles: List[Dict[str, Any]],
        min_evidence_level: str = "IV",
        max_age_years: int = 5
    ) -> ValidationReport:
        """
        Validate a list of articles for evidence-based practice standards.
        
        Args:
            articles: List of article dicts with pmid, title, abstract, date
            min_evidence_level: Minimum acceptable evidence level (I-VII)
            max_age_years: Maximum age before flagging as outdated
            
        Returns:
            ValidationReport with per-article results and summary
        """
        import json
        
        results = []
        include_count = 0
        review_count = 0
        exclude_count = 0
        retracted_count = 0
        
        # Map level codes to EvidenceLevel enum
        level_map = {
            "I": EvidenceLevel.LEVEL_I,
            "II": EvidenceLevel.LEVEL_II,
            "III": EvidenceLevel.LEVEL_III,
            "IV": EvidenceLevel.LEVEL_IV,
            "V": EvidenceLevel.LEVEL_V,
            "VI": EvidenceLevel.LEVEL_VI,
            "VII": EvidenceLevel.LEVEL_VII,
            "?": EvidenceLevel.UNKNOWN,
        }
        
        for article in articles:
            pmid = article.get("pmid", "unknown")
            title = article.get("title", "Unknown Title")
            abstract = article.get("abstract", "")
            pub_date = article.get("publication_date", article.get("date", ""))
            pub_type = article.get("publication_type", "")
            
            # Use real validation tools if available
            if hasattr(self, 'validation_tools') and self.validation_tools:
                try:
                    validation_json = self.validation_tools.validate_single_article(
                        pmid=pmid,
                        title=title,
                        abstract=abstract,
                        publication_date=pub_date,
                        publication_type=pub_type
                    )
                    v_data = json.loads(validation_json)
                    
                    level_code = v_data.get("evidence_level", "?")
                    evidence_level = level_map.get(level_code, EvidenceLevel.UNKNOWN)
                    
                    result = ValidationResult(
                        pmid=pmid,
                        title=title,
                        evidence_level=evidence_level,
                        is_retracted=v_data.get("is_retracted", False),
                        currency_flag=v_data.get("currency_status", "unknown"),
                        quality_score=v_data.get("quality_score", 0.0),
                        issues=v_data.get("issues", []),
                        recommendation=v_data.get("recommendation", "review")
                    )
                except Exception as e:
                    # Fallback on error
                    result = ValidationResult(
                        pmid=pmid,
                        title=title,
                        evidence_level=EvidenceLevel.UNKNOWN,
                        issues=[f"Validation error: {str(e)}"],
                        recommendation="review"
                    )
            else:
                # Fallback if tools not available
                result = ValidationResult(
                    pmid=pmid,
                    title=title,
                    evidence_level=EvidenceLevel.UNKNOWN,
                    issues=["Validation tools not available"],
                    recommendation="review"
                )
            
            results.append(result)
            
            if result.recommendation == "include":
                include_count += 1
            elif result.recommendation == "review":
                review_count += 1
            else:
                exclude_count += 1
            
            if result.is_retracted:
                retracted_count += 1
        
        return ValidationReport(
            total_articles=len(articles),
            validated_count=len(results),
            include_count=include_count,
            review_count=review_count,
            exclude_count=exclude_count,
            retracted_count=retracted_count,
            results=results
        )
    
    def show_usage_examples(self):
        """Display usage examples for the Citation Validation Agent."""
        print("\n" + "=" * 60)
        print("📋 Citation Validation Agent Ready!")
        print("=" * 60)
        
        print("\n✨ CAPABILITIES:")
        print("  • Evidence Level Grading (Johns Hopkins I-VII)")
        print("  • Retraction Detection (PubMed database)")
        print("  • Currency Assessment (flags >5 year old articles)")
        print("  • Quality Scoring (0.0-1.0 scale)")
        print("  • Include/Review/Exclude Recommendations")
        
        print("\n🔍 EXAMPLE QUERIES:")
        print('  1. "Validate this systematic review for inclusion"')
        print('  2. "Check if PMID 12345678 has been retracted"')
        print('  3. "Grade the evidence level of these search results"')
        print('  4. "Filter articles to Level III or higher"')
        
        print("\n📊 EVIDENCE HIERARCHY:")
        print("  Level I   - Systematic Reviews / Meta-Analyses (Highest)")
        print("  Level II  - Randomized Controlled Trials")
        print("  Level III - Controlled Trials (non-randomized)")
        print("  Level IV  - Case-Control / Cohort Studies")
        print("  Level V   - Systematic Review of Qualitative")
        print("  Level VI  - Single Qualitative / Descriptive")
        print("  Level VII - Expert Opinion (Lowest)")
        
        print("\n💡 TIP: Use with Medical Research Agent for validated literature searches.")
        print("=" * 60 + "\n")


# Create global instance for backward compatibility
_citation_validation_agent_instance = None


def get_citation_validation_agent() -> Optional[CitationValidationAgent]:
    """
    Return the CitationValidationAgent instance with lazy initialization.
    
    Returns:
        CitationValidationAgent instance or None if initialization fails
    """
    global _citation_validation_agent_instance
    if _citation_validation_agent_instance is None:
        try:
            _citation_validation_agent_instance = CitationValidationAgent()
        except Exception as init_error:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to initialize CitationValidationAgent: {init_error}")
            return None
    return _citation_validation_agent_instance


__all__ = ['CitationValidationAgent', 'get_citation_validation_agent']


if __name__ == "__main__":
    agent = get_citation_validation_agent()
    if agent is not None:
        agent.run_with_error_handling()
    else:
        print("❌ Agent failed to initialize. Check logs for details.")
