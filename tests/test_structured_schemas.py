"""
Test structured output schemas for nursing research agents.

This test verifies that all schemas can be instantiated and validated correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.schemas.research_schemas import (
    EvidenceLevel,
    PICOTQuestion,
    ResearchArticle,
    LiteratureSynthesis,
    DataAnalysisPlan,
)


def test_picot_question_schema():
    """Test PICOTQuestion schema validation."""
    print("\n🧪 Testing PICOTQuestion Schema...")
    
    picot = PICOTQuestion(
        population="Elderly patients (65+) in acute care hospitals",
        intervention="Hourly rounding by nursing staff",
        comparison="Standard nursing care without structured rounding",
        outcome="Reduction in patient falls",
        timeframe="Over 6 months",
        full_question="In elderly hospitalized patients (P), does hourly nursing rounding (I) compared to standard care (C) reduce patient falls (O) over 6 months (T)?",
        clinical_significance="Patient falls are a leading cause of injury and extended hospital stays in elderly patients. Hourly rounding is a low-cost intervention that could significantly reduce fall rates and improve patient safety outcomes.",
        search_terms=["patient falls", "elderly hospitalized", "hourly rounding", "fall prevention"]
    )
    
    print(f"✅ PICOTQuestion created successfully")
    print(f"   Population: {picot.population[:50]}...")
    print(f"   Search terms: {len(picot.search_terms)} terms")
    
    # Test JSON serialization
    json_data = picot.model_dump()
    print(f"✅ Serialized to JSON: {len(json_data)} fields")
    
    return True


def test_research_article_schema():
    """Test ResearchArticle schema validation."""
    print("\n🧪 Testing ResearchArticle Schema...")
    
    article = ResearchArticle(
        pmid="12345678",
        doi="10.1001/jama.2020.12345",
        title="Effect of Hourly Rounding on Patient Falls in Acute Care Settings",
        authors=["Smith J", "Johnson M", "Williams K"],
        year=2020,
        journal="JAMA Internal Medicine",
        evidence_level=EvidenceLevel.LEVEL_I,
        is_retracted=False,
        relevance_score=0.95,
        key_findings=[
            "Hourly rounding reduced falls by 50% (p<0.001)",
            "No significant increase in nursing workload",
            "Patient satisfaction scores improved by 20%"
        ]
    )
    
    print(f"✅ ResearchArticle created successfully")
    print(f"   Title: {article.title[:50]}...")
    print(f"   Evidence Level: {article.evidence_level.value}")
    print(f"   Authors: {len(article.authors)}")
    
    return True


def test_literature_synthesis_schema():
    """Test LiteratureSynthesis schema validation."""
    print("\n🧪 Testing LiteratureSynthesis Schema...")
    
    synthesis = LiteratureSynthesis(
        topic="Hourly rounding for fall prevention in elderly hospitalized patients",
        picot_question="In elderly hospitalized patients, does hourly nursing rounding compared to standard care reduce patient falls over 6 months?",
        articles_reviewed=12,
        evidence_summary="Systematic review of 12 studies (5 RCTs, 7 quasi-experimental) shows consistent evidence that hourly rounding reduces falls by 30-50% in acute care settings. Effects are most pronounced in elderly patients and when rounding includes specific safety checks.",
        key_findings=[
            "Hourly rounding reduces falls by 30-50% across multiple studies",
            "Most effective when including toileting assistance and environment checks",
            "Minimal increase in nursing workload when integrated into workflow"
        ],
        recommendations=[
            "Implement structured hourly rounding in all acute care units with elderly patients",
            "Include specific safety checklist items: toileting, positioning, environment"
        ],
        evidence_quality="Moderate to high quality evidence from multiple RCTs and well-designed quasi-experimental studies.",
        gaps_identified=[
            "Long-term sustainability beyond 6 months unclear",
            "Cost-effectiveness analysis needed"
        ],
        confidence_level=0.85,
        citations=["12345678", "23456789", "34567890"]
    )
    
    print(f"✅ LiteratureSynthesis created successfully")
    print(f"   Topic: {synthesis.topic[:50]}...")
    print(f"   Articles reviewed: {synthesis.articles_reviewed}")
    print(f"   Confidence level: {synthesis.confidence_level}")
    
    return True


def test_data_analysis_plan_schema():
    """Test DataAnalysisPlan schema validation."""
    print("\n🧪 Testing DataAnalysisPlan Schema...")
    
    plan = DataAnalysisPlan(
        study_design="Quasi-experimental pre-post intervention study",
        sample_size_required=388,
        sample_size_justification="Based on power analysis for detecting 30% reduction in fall rate with 80% power, alpha=0.05",
        statistical_tests=[
            "Interrupted time series analysis for fall rate trends",
            "Chi-square test for categorical outcomes"
        ],
        power=0.80,
        alpha=0.05,
        effect_size=0.30,
        effect_size_justification="Based on meta-analysis showing hourly rounding reduces falls by 30-50%",
        data_collection_plan=[
            "Collect baseline fall data for 3 months pre-intervention",
            "Implement hourly rounding intervention",
            "Collect fall data for 6 months post-intervention"
        ],
        analysis_timeline="9 months total: 3 months baseline, 6 months intervention"
    )
    
    print(f"✅ DataAnalysisPlan created successfully")
    print(f"   Study design: {plan.study_design}")
    print(f"   Sample size: {plan.sample_size_required}")
    print(f"   Power: {plan.power}, Alpha: {plan.alpha}")
    
    return True


def test_schema_validation_errors():
    """Test that schemas properly reject invalid data."""
    print("\n🧪 Testing Schema Validation (Error Cases)...")
    
    # Test missing required fields
    try:
        PICOTQuestion(
            population="Elderly patients",
            intervention="Hourly rounding"
            # Missing required fields
        )
        print("❌ Failed: Should have raised validation error")
        return False
    except Exception as e:
        print(f"✅ Correctly rejected invalid data: {type(e).__name__}")
    
    # Test invalid evidence level
    try:
        article = ResearchArticle(
            pmid="123",
            title="Test Article",
            authors=["Test"],
            year=2020,
            journal="Test Journal",
            evidence_level=EvidenceLevel.LEVEL_I,
            relevance_score=1.5,  # Invalid: > 1.0
            key_findings=["Test"]
        )
        print("❌ Failed: Should have raised validation error for relevance_score")
        return False
    except Exception as e:
        print(f"✅ Correctly rejected invalid relevance_score: {type(e).__name__}")
    
    return True


def run_all_tests():
    """Run all schema tests."""
    print("=" * 70)
    print("🚀 Testing Structured Output Schemas")
    print("=" * 70)
    
    tests = [
        ("PICOTQuestion", test_picot_question_schema),
        ("ResearchArticle", test_research_article_schema),
        ("LiteratureSynthesis", test_literature_synthesis_schema),
        ("DataAnalysisPlan", test_data_analysis_plan_schema),
        ("Validation Errors", test_schema_validation_errors),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test_name} test failed")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} test raised exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
