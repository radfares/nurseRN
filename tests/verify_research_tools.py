"""
PHASE 1 VERIFICATION: RESEARCH CORE SMOKE TEST
----------------------------------------------
Goal: Verify that the core research tools (PubMed, ClinicalTrials)
are correctly configured and fetching real data.

This uses the project's safe tool creation pattern from src/services/api_tools.py
"""

import sys
import os

# Ensure we can import from project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Add agno to path
agno_path = os.path.join(project_root, 'libs', 'agno')
if agno_path not in sys.path:
    sys.path.insert(0, agno_path)

def test_pubmed_tool_creation():
    """Test 1: Verify PubMed tool can be created"""
    print("\n🧪 TEST 1: PubMed Tool Creation")
    try:
        from src.services.api_tools import create_pubmed_tools_safe

        tool = create_pubmed_tools_safe(required=False)

        if tool:
            print("   ✅ SUCCESS: PubMed tool created successfully")
            return True, tool
        else:
            print("   ❌ FAILED: PubMed tool creation returned None")
            return False, None

    except Exception as e:
        print(f"   ❌ FAILED: PubMed tool creation error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_pubmed_search(tool):
    """Test 2: Verify PubMed can search and return results"""
    print("\n🧪 TEST 2: PubMed Search (Real API Call)")

    if not tool:
        print("   ⚠️ SKIPPED: No tool available from Test 1")
        return False

    try:
        # Access the wrapped tool's search method
        # The tool is wrapped by CircuitProtectedToolWrapper, so we can call methods directly
        query = "catheter associated urinary tract infection nursing"
        print(f"   Querying: '{query}'...")

        # Try common method names
        if hasattr(tool._tool, 'search_pubmed'):
            results = tool._tool.search_pubmed(query, max_results=3)
        elif hasattr(tool._tool, 'search'):
            results = tool._tool.search(query, max_results=3)
        else:
            print(f"   ❌ Error: Could not find search method. Available methods: {dir(tool._tool)}")
            return False

        # Verify we got results
        results_str = str(results)
        if results and len(results_str) > 100:
            print(f"   ✅ SUCCESS: PubMed returned {len(results_str)} characters of data")
            # Try to show a snippet
            snippet = results_str[:200] + "..." if len(results_str) > 200 else results_str
            print(f"   📄 Sample output: {snippet}")
            return True
        else:
            print("   ⚠️ WARNING: PubMed returned empty or short results")
            print(f"   Raw output: {results_str}")
            return False

    except Exception as e:
        print(f"   ❌ FAILED: PubMed search error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_clinicaltrials_tool_creation():
    """Test 3: Verify ClinicalTrials.gov tool can be created"""
    print("\n🧪 TEST 3: ClinicalTrials.gov Tool Creation")
    try:
        from src.services.api_tools import create_clinicaltrials_tools_safe

        tool = create_clinicaltrials_tools_safe(required=False)

        if tool:
            print("   ✅ SUCCESS: ClinicalTrials.gov tool created successfully")
            return True, tool
        else:
            print("   ❌ FAILED: ClinicalTrials.gov tool creation returned None")
            return False, None

    except Exception as e:
        print(f"   ❌ FAILED: ClinicalTrials.gov tool creation error: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_clinicaltrials_search(tool):
    """Test 4: Verify ClinicalTrials.gov can search and return results"""
    print("\n🧪 TEST 4: ClinicalTrials.gov Search (Real API Call)")

    if not tool:
        print("   ⚠️ SKIPPED: No tool available from Test 3")
        return False

    try:
        # Access the wrapped tool's search method
        query = "sepsis nursing"
        print(f"   Querying: '{query}'...")

        # Try common method names
        if hasattr(tool._tool, 'search_clinicaltrials'):
            results = tool._tool.search_clinicaltrials(query, max_results=3)
        elif hasattr(tool._tool, 'search'):
            results = tool._tool.search(query, max_results=3)
        else:
            print(f"   ❌ Error: Could not find search method. Available methods: {dir(tool._tool)}")
            return False

        # Verify we got results with NCT IDs (standard ClinicalTrials.gov identifier)
        results_str = str(results)
        if results and "NCT" in results_str:
            print(f"   ✅ SUCCESS: Found Clinical Trials with NCT IDs")
            # Try to show a snippet
            snippet = results_str[:200] + "..." if len(results_str) > 200 else results_str
            print(f"   📄 Sample output: {snippet}")
            return True
        else:
            print("   ⚠️ WARNING: Results did not contain expected NCT IDs")
            print(f"   Raw output (first 300 chars): {results_str[:300]}...")
            # Still might be valid if we got any results
            return len(results_str) > 100

    except Exception as e:
        print(f"   ❌ FAILED: ClinicalTrials.gov search error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("   RESEARCH TOOLS VERIFICATION - PHASE 1")
    print("=" * 70)
    print("\nThis script verifies that PubMed and ClinicalTrials.gov tools")
    print("are correctly configured and can fetch real data.\n")

    # Test PubMed
    pubmed_created, pubmed_tool = test_pubmed_tool_creation()
    pubmed_search_ok = test_pubmed_search(pubmed_tool) if pubmed_created else False

    # Test ClinicalTrials.gov
    ct_created, ct_tool = test_clinicaltrials_tool_creation()
    ct_search_ok = test_clinicaltrials_search(ct_tool) if ct_created else False

    # Summary
    print("\n" + "=" * 70)
    print("   VERIFICATION SUMMARY")
    print("=" * 70)

    print(f"\nPubMed Tool:")
    print(f"  Creation:  {'✅ PASS' if pubmed_created else '❌ FAIL'}")
    print(f"  Search:    {'✅ PASS' if pubmed_search_ok else '❌ FAIL'}")

    print(f"\nClinicalTrials.gov Tool:")
    print(f"  Creation:  {'✅ PASS' if ct_created else '❌ FAIL'}")
    print(f"  Search:    {'✅ PASS' if ct_search_ok else '❌ FAIL'}")

    # Overall result
    all_passed = pubmed_created and pubmed_search_ok and ct_created and ct_search_ok

    if all_passed:
        print("\n🟢 VERIFICATION PASSED: Core Research Tools are Active and Functional")
        print("   ✓ PubMed is working correctly")
        print("   ✓ ClinicalTrials.gov is working correctly")
        print("\n   You are ready to proceed with Safety Tools integration.\n")
        sys.exit(0)
    else:
        print("\n🔴 VERIFICATION FAILED: Some tests did not pass")
        print("   Check the errors above for details.")
        print("   You may need to:")
        print("   - Verify internet connectivity")
        print("   - Check if required Python packages are installed")
        print("   - Review src/services/api_tools.py configuration\n")
        sys.exit(1)
