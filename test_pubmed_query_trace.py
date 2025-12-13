"""
Phase 2: Trace where PubMed query becomes None

This test will trigger a PubMed search through the orchestrator and trace
the query parameter at each step of the call chain.

Expected trace points:
1. Orchestrator creates plan with params
2. Orchestrator resolves dependencies
3. Orchestrator builds agent query
4. Agent receives natural language query
5. Agent calls search_pubmed tool
6. Tool receives query parameter

Usage:
    python test_pubmed_query_trace.py
"""

import os
import sys
import logging

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s - %(message)s'
)

# Add project paths
sys.path.insert(0, os.path.dirname(__file__))

from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator
from src.orchestration.conversation_context import ConversationContext

def test_pubmed_search_trace():
    """
    Test that triggers a PubMed search to trace query parameter flow.
    """
    print("\n" + "="*80)
    print("PHASE 2: Tracing PubMed Query Parameter Flow")
    print("="*80 + "\n")

    # Create orchestrator
    orchestrator = IntelligentOrchestrator()
    context = ConversationContext()

    # Test query that should trigger medical research with PubMed search
    test_message = "Find research articles about diabetes management in elderly patients"

    print(f"📝 User query: {test_message}\n")
    print("="*80)
    print("TRACE LOG (watch for 🔍 PHASE2 TRACE markers)")
    print("="*80 + "\n")

    try:
        response, suggestions = orchestrator.process_user_message(test_message, context)

        print("\n" + "="*80)
        print("✅ Test completed successfully")
        print("="*80)
        print(f"\nResponse preview: {response[:200]}...")
        print(f"\nSuggestions: {suggestions}")

    except ValueError as e:
        if "requires a non-empty string query" in str(e):
            print("\n" + "="*80)
            print("🔍 FOUND THE ISSUE!")
            print("="*80)
            print(f"\n❌ Error: {e}")
            print("\nThe query parameter became None somewhere in the chain.")
            print("Check the trace logs above to find where it happened.")
            return False
        else:
            print(f"\n❌ Unexpected ValueError: {e}")
            import traceback
            traceback.print_exc()
            return False

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PHASE 2: PubMed Query=None Root Cause Analysis")
    print("="*80)
    print("\nThis test will trace the query parameter through:")
    print("  1. Orchestrator plan creation (LLM output)")
    print("  2. Task params from parsed plan")
    print("  3. Resolved params after dependency resolution")
    print("  4. Natural language query built for agent")
    print("  5. Agent tool call with arguments")
    print("  6. PubMed tool entrypoint")
    print("\nLook for the 🔍 PHASE2 TRACE markers in the output.\n")

    success = test_pubmed_search_trace()

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    if success:
        print("✅ Test passed - query flow is correct")
    else:
        print("❌ Test failed - query=None detected")
        print("\nReview the trace logs above to find where query became None")
    print("="*80 + "\n")

    sys.exit(0 if success else 1)
