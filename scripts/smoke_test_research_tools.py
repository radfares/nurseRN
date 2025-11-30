#!/usr/bin/env python3
"""
Smoke Test for Core Research Tools
Tests PubMed and ClinicalTrials.gov connectivity and search functionality.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Add agno to path
agno_path = os.path.join(os.path.dirname(__file__), '..', 'libs', 'agno')
sys.path.insert(0, agno_path)

import requests
from typing import Dict, Optional


class ResearchToolsSmokeTest:
    """Smoke test for PubMed and ClinicalTrials.gov APIs"""

    def __init__(self):
        self.results = {
            'pubmed': {'status': 'pending', 'count': 0, 'error': None},
            'clinicaltrials': {'status': 'pending', 'count': 0, 'error': None}
        }

    def test_pubmed(self, query: str = "catheter associated urinary tract infection", max_results: int = 5) -> bool:
        """
        Test PubMed API connectivity and search.

        Args:
            query: Search term
            max_results: Maximum results to retrieve

        Returns:
            True if test passed, False otherwise
        """
        print(f"\n🔍 Testing PubMed API...")
        print(f"   Query: '{query}'")

        try:
            # Step 1: Search for article IDs
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": max_results,
                "usehistory": "y"
            }

            response = requests.get(search_url, params=search_params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check for results
            result_count = int(data.get('esearchresult', {}).get('count', 0))
            id_list = data.get('esearchresult', {}).get('idlist', [])

            self.results['pubmed']['count'] = result_count

            if result_count > 0:
                print(f"   ✅ PubMed API accessible")
                print(f"   ✅ Found {result_count} total results")
                print(f"   ✅ Retrieved {len(id_list)} PMIDs: {', '.join(id_list[:3])}...")
                self.results['pubmed']['status'] = 'passed'
                return True
            else:
                print(f"   ⚠️  No results found for query")
                self.results['pubmed']['status'] = 'warning'
                return True  # API works, just no results

        except requests.exceptions.Timeout:
            error = "Request timeout (>10 seconds)"
            print(f"   ❌ {error}")
            self.results['pubmed']['status'] = 'failed'
            self.results['pubmed']['error'] = error
            return False

        except requests.exceptions.RequestException as e:
            error = f"Network error: {str(e)}"
            print(f"   ❌ {error}")
            self.results['pubmed']['status'] = 'failed'
            self.results['pubmed']['error'] = error
            return False

        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            print(f"   ❌ {error}")
            self.results['pubmed']['status'] = 'failed'
            self.results['pubmed']['error'] = error
            return False

    def test_clinicaltrials(self, query: str = "catheter infection prevention", max_results: int = 5) -> bool:
        """
        Test ClinicalTrials.gov API connectivity and search.

        Args:
            query: Search term
            max_results: Maximum results to retrieve

        Returns:
            True if test passed, False otherwise
        """
        print(f"\n🔍 Testing ClinicalTrials.gov API...")
        print(f"   Query: '{query}'")

        try:
            # ClinicalTrials.gov API v2
            url = "https://clinicaltrials.gov/api/v2/studies"
            params = {
                "query.term": query,
                "pageSize": max_results,
                "format": "json"
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Check for results
            total_count = data.get('totalCount', 0)
            studies = data.get('studies', [])

            self.results['clinicaltrials']['count'] = total_count

            if total_count > 0:
                print(f"   ✅ ClinicalTrials.gov API accessible")
                print(f"   ✅ Found {total_count} total studies")
                print(f"   ✅ Retrieved {len(studies)} study records")

                # Show first study as sample
                if studies:
                    first_study = studies[0].get('protocolSection', {})
                    id_module = first_study.get('identificationModule', {})
                    nct_id = id_module.get('nctId', 'N/A')
                    title = id_module.get('briefTitle', 'N/A')
                    print(f"   📄 Sample: {nct_id} - {title[:60]}...")

                self.results['clinicaltrials']['status'] = 'passed'
                return True
            else:
                print(f"   ⚠️  No results found for query")
                self.results['clinicaltrials']['status'] = 'warning'
                return True  # API works, just no results

        except requests.exceptions.Timeout:
            error = "Request timeout (>10 seconds)"
            print(f"   ❌ {error}")
            self.results['clinicaltrials']['status'] = 'failed'
            self.results['clinicaltrials']['error'] = error
            return False

        except requests.exceptions.RequestException as e:
            error = f"Network error: {str(e)}"
            print(f"   ❌ {error}")
            self.results['clinicaltrials']['status'] = 'failed'
            self.results['clinicaltrials']['error'] = error
            return False

        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            print(f"   ❌ {error}")
            self.results['clinicaltrials']['status'] = 'failed'
            self.results['clinicaltrials']['error'] = error
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 SMOKE TEST SUMMARY")
        print("="*60)

        all_passed = True

        for tool_name, result in self.results.items():
            status = result['status']
            count = result['count']
            error = result['error']

            # Status emoji
            if status == 'passed':
                emoji = "✅"
            elif status == 'warning':
                emoji = "⚠️ "
            elif status == 'failed':
                emoji = "❌"
                all_passed = False
            else:
                emoji = "⏳"

            print(f"\n{emoji} {tool_name.upper()}: {status.upper()}")
            print(f"   Results found: {count}")
            if error:
                print(f"   Error: {error}")

        print("\n" + "="*60)
        if all_passed:
            print("✅ ALL TESTS PASSED - Core research tools operational")
        else:
            print("❌ SOME TESTS FAILED - Check errors above")
        print("="*60)

        return all_passed


# --- SELF-TEST BLOCK ---
if __name__ == "__main__":
    print("="*60)
    print("🧪 CORE RESEARCH TOOLS SMOKE TEST")
    print("="*60)
    print("Testing: PubMed, ClinicalTrials.gov")
    print("Purpose: Verify APIs are accessible and returning results")

    tester = ResearchToolsSmokeTest()

    # Run tests
    pubmed_ok = tester.test_pubmed(
        query="catheter associated urinary tract infection AND nursing",
        max_results=5
    )

    clinicaltrials_ok = tester.test_clinicaltrials(
        query="catheter infection prevention",
        max_results=5
    )

    # Print summary
    all_ok = tester.print_summary()

    # Exit with appropriate code
    sys.exit(0 if all_ok else 1)
