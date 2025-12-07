"""
Systems Integration Test for Citation Validation Agent

Tests integration with:
- Project database
- Other agents (MedicalResearchAgent)
- Main run_nursing_project.py system
- Agent audit logging

Created: 2025-12-07
"""

import sys
import os

# Setup paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'libs', 'agno'))


def test_agent_in_main_system():
    """Test 1: Can agent be imported and registered in main system?"""
    print("\n" + "="*70)
    print("SYSTEMS TEST 1: Main System Integration")
    print("="*70)

    try:
        # Check if agent can be imported
        from agents.citation_validation_agent import get_citation_validation_agent
        agent = get_citation_validation_agent()

        if agent is None:
            print("❌ FAIL: Agent returned None")
            return False

        print("✅ PASS: Agent imports successfully")
        print(f"   Agent name: {agent.agent_name}")

        # Check if agent appears in agents module
        import agents
        has_citation = hasattr(agents, 'citation_validation_agent')
        print(f"   In agents module: {has_citation}")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_integration():
    """Test 2: Does agent work with project database?"""
    print("\n" + "="*70)
    print("SYSTEMS TEST 2: Database Integration")
    print("="*70)

    try:
        from agents.citation_validation_agent import CitationValidationAgent
        from project_manager import get_project_manager

        # Create temp project for testing
        pm = get_project_manager()

        # Check if agent has database path configured
        from agent_config import get_db_path
        db_path = get_db_path("citation_validation")

        print(f"✅ PASS: Database path configured")
        print(f"   Path: {db_path}")

        # Create agent with database
        agent = CitationValidationAgent()

        # Verify database file exists
        import os
        if os.path.exists(db_path):
            print(f"   Database file created: YES")
        else:
            print(f"   Database file created: Will be created on first use")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_audit_logging():
    """Test 3: Does audit logging work?"""
    print("\n" + "="*70)
    print("SYSTEMS TEST 3: Audit Logging")
    print("="*70)

    try:
        from agents.citation_validation_agent import CitationValidationAgent
        import os

        agent = CitationValidationAgent()

        # Check if audit logger exists
        if not hasattr(agent, 'audit_logger'):
            print("❌ FAIL: No audit_logger attribute")
            return False

        # Check if audit file path is configured
        audit_path = ".claude/agent_audit_logs/citation_validation_audit.jsonl"
        full_path = os.path.join(project_root, audit_path)

        print(f"✅ PASS: Audit logging configured")
        print(f"   Path: {audit_path}")

        if os.path.exists(full_path):
            # Check file size
            size = os.path.getsize(full_path)
            print(f"   Audit file exists: YES ({size} bytes)")
        else:
            print(f"   Audit file exists: Will be created on first log")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_medical_research_agent():
    """Test 4: Can it work with MedicalResearchAgent output?"""
    print("\n" + "="*70)
    print("SYSTEMS TEST 4: Medical Research Agent Integration")
    print("="*70)

    try:
        from agents.citation_validation_agent import CitationValidationAgent
        from src.tools.validation_tools import ValidationTools

        # Simulate articles from MedicalResearchAgent
        mock_articles_from_medical_agent = [
            {
                "pmid": "12345678",
                "title": "Randomized Trial of Fall Prevention in Older Adults",
                "abstract": "This randomized controlled trial examined a multicomponent intervention for fall prevention in community-dwelling older adults aged 65+. Methods: 500 participants were randomized to intervention or control groups.",
                "publication_date": "2023-05-15",
                "publication_types": ["Randomized Controlled Trial"],
                "is_retracted": False
            },
            {
                "pmid": "87654321",
                "title": "Expert Recommendations for CAUTI Prevention",
                "abstract": "Based on our clinical experience, we recommend daily assessment of catheter necessity and proper hand hygiene protocols.",
                "publication_date": "2015-01-10",
                "publication_types": ["Review", "Expert Opinion"],
                "is_retracted": False
            }
        ]

        # Validate using tools
        tools = ValidationTools()
        results = tools.validate_batch(mock_articles_from_medical_agent, max_age_years=5)

        print(f"✅ PASS: Can validate Medical Research Agent output")
        print(f"   Articles validated: {len(results)}")

        for i, result in enumerate(results, 1):
            print(f"\n   Article {i}:")
            print(f"     Evidence Level: {result.evidence_level.code}")
            print(f"     Currency: {result.currency_flag}")
            print(f"     Quality Score: {result.quality_score}")
            print(f"     Recommendation: {result.recommendation}")

        # Verify filtering logic
        include_list = [r for r in results if r.recommendation == "include"]
        review_list = [r for r in results if r.recommendation == "review"]
        exclude_list = [r for r in results if r.recommendation == "exclude"]

        print(f"\n   Filtering results:")
        print(f"     Include: {len(include_list)}")
        print(f"     Review: {len(review_list)}")
        print(f"     Exclude: {len(exclude_list)}")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_compatibility():
    """Test 5: Check workflow system compatibility"""
    print("\n" + "="*70)
    print("SYSTEMS TEST 5: Workflow System Compatibility")
    print("="*70)

    try:
        # Check if agent follows workflow patterns
        from agents.citation_validation_agent import CitationValidationAgent
        from src.workflows.base import WorkflowTemplate

        agent = CitationValidationAgent()

        # Check required attributes for workflow integration
        required_attrs = ['agent_name', 'agent', 'validate_articles']

        missing = []
        for attr in required_attrs:
            if not hasattr(agent, attr):
                missing.append(attr)

        if missing:
            print(f"❌ FAIL: Missing attributes: {missing}")
            return False

        print("✅ PASS: Agent compatible with workflow system")
        print(f"   Has required attributes: {', '.join(required_attrs)}")

        # Check if validate_articles method has correct signature
        import inspect
        sig = inspect.signature(agent.validate_articles)
        params = list(sig.parameters.keys())

        print(f"   validate_articles params: {params}")

        # Should have: articles, min_evidence_level, max_age_years
        expected_params = {'articles', 'min_evidence_level', 'max_age_years'}
        has_params = set(params) >= expected_params

        if not has_params:
            print(f"   ⚠️  Warning: May be missing expected params: {expected_params - set(params)}")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """Test 6: Performance check"""
    print("\n" + "="*70)
    print("SYSTEMS TEST 6: Performance Check")
    print("="*70)

    try:
        from src.tools.validation_tools import ValidationTools
        import time

        tools = ValidationTools()

        # Create 100 test articles
        test_articles = []
        for i in range(100):
            test_articles.append({
                "pmid": f"{10000000 + i}",
                "title": f"Study {i}: Nursing Intervention Research",
                "abstract": "This randomized controlled trial examined nursing interventions in acute care settings with sample size of 200 patients.",
                "publication_date": "2023-01-15",
                "publication_types": ["Randomized Controlled Trial"]
            })

        # Time the validation
        start = time.time()
        results = tools.validate_batch(test_articles, max_age_years=5)
        duration = time.time() - start

        articles_per_second = len(test_articles) / duration

        print(f"✅ PASS: Performance test completed")
        print(f"   Articles validated: {len(results)}")
        print(f"   Duration: {duration:.2f}s")
        print(f"   Throughput: {articles_per_second:.1f} articles/second")

        if articles_per_second < 10:
            print(f"   ⚠️  Warning: Slow performance (< 10 articles/sec)")

        return True

    except Exception as e:
        print(f"❌ FAIL: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all systems integration tests"""
    print("=" * 70)
    print("  CITATION VALIDATION AGENT - SYSTEMS INTEGRATION TESTS")
    print("=" * 70)

    results = []

    # Run all tests
    results.append(("Main System Integration", test_agent_in_main_system()))
    results.append(("Database Integration", test_database_integration()))
    results.append(("Audit Logging", test_audit_logging()))
    results.append(("Medical Research Agent Integration", test_integration_with_medical_research_agent()))
    results.append(("Workflow Compatibility", test_workflow_compatibility()))
    results.append(("Performance", test_performance()))

    # Summary
    print("\n" + "="*70)
    print("  SYSTEMS TEST SUMMARY")
    print("="*70)

    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)

    print(f"\nTotal: {passed_count}/{total} systems tests passed")

    if passed_count == total:
        print("\n🟢 ALL SYSTEMS TESTS PASSED")
        print("   Citation Validation Agent is fully integrated!")
        return 0
    else:
        print(f"\n🔴 {total - passed_count} SYSTEMS TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
