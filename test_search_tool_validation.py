"""
Test to verify that search tools properly validate query parameters.
This test ensures that all search tools raise ValueError when query=None.
"""

import sys
import os

# Add libs/agno to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs', 'agno'))

def test_pubmed_validation():
    """Test that PubMed tool validates query parameter."""
    from agno.tools.pubmed import PubmedTools

    pubmed = PubmedTools()

    # Test with None query
    try:
        result = pubmed.search_pubmed(query=None)
        print("❌ FAILED: PubMed should have raised ValueError for query=None")
        return False
    except ValueError as e:
        if "non-empty string query" in str(e):
            print("✅ PASSED: PubMed correctly validates query parameter")
            return True
        else:
            print(f"❌ FAILED: PubMed raised ValueError but with wrong message: {e}")
            return False
    except Exception as e:
        print(f"❌ FAILED: PubMed raised unexpected error: {e}")
        return False

def test_arxiv_validation():
    """Test that Arxiv tool validates query parameter."""
    from agno.tools.arxiv import ArxivTools

    arxiv = ArxivTools()

    # Test with None query
    try:
        result = arxiv.search_arxiv_and_return_articles(query=None)
        print("❌ FAILED: Arxiv should have raised ValueError for query=None")
        return False
    except ValueError as e:
        if "non-empty string query" in str(e):
            print("✅ PASSED: Arxiv correctly validates query parameter")
            return True
        else:
            print(f"❌ FAILED: Arxiv raised ValueError but with wrong message: {e}")
            return False
    except Exception as e:
        print(f"❌ FAILED: Arxiv raised unexpected error: {e}")
        return False

def test_clinicaltrials_validation():
    """Test that ClinicalTrials tool validates query parameter."""
    from agno.tools.clinicaltrials import ClinicalTrialsTools

    ct = ClinicalTrialsTools()

    # Test with None query
    try:
        result = ct.search_clinicaltrials(query=None)
        print("❌ FAILED: ClinicalTrials should have raised ValueError for query=None")
        return False
    except ValueError as e:
        if "non-empty string query" in str(e):
            print("✅ PASSED: ClinicalTrials correctly validates query parameter")
            return True
        else:
            print(f"❌ FAILED: ClinicalTrials raised ValueError but with wrong message: {e}")
            return False
    except Exception as e:
        print(f"❌ FAILED: ClinicalTrials raised unexpected error: {e}")
        return False

def test_empty_string_validation():
    """Test that tools reject empty strings as well."""
    from agno.tools.pubmed import PubmedTools

    pubmed = PubmedTools()

    # Test with empty string query
    try:
        result = pubmed.search_pubmed(query="")
        print("❌ FAILED: PubMed should have raised ValueError for empty query")
        return False
    except ValueError as e:
        if "non-empty string query" in str(e):
            print("✅ PASSED: PubMed correctly rejects empty string query")
            return True
        else:
            print(f"❌ FAILED: PubMed raised ValueError but with wrong message: {e}")
            return False
    except Exception as e:
        print(f"❌ FAILED: PubMed raised unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Search Tool Query Validation")
    print("="*60 + "\n")

    results = []

    print("Test 1: PubMed validation")
    results.append(test_pubmed_validation())

    print("\nTest 2: Arxiv validation")
    results.append(test_arxiv_validation())

    print("\nTest 3: ClinicalTrials validation")
    results.append(test_clinicaltrials_validation())

    print("\nTest 4: Empty string validation")
    results.append(test_empty_string_validation())

    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60 + "\n")

    sys.exit(0 if passed == total else 1)
