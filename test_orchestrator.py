#!/usr/bin/env python3
"""
Test the IntelligentOrchestrator with a simple query.
This will test planning, execution, and synthesis.

NOTE: This makes real OpenAI API calls and will cost ~$0.05-0.10
"""

import sys
from pathlib import Path

# Setup path
_project_root = Path(__file__).parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))

from dotenv import load_dotenv
load_dotenv(override=True)

from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator
from src.orchestration.conversation_context import ConversationContext
from project_manager import get_project_manager

print("=" * 80)
print("PHASE 2 TEST: IntelligentOrchestrator Query Processing")
print("=" * 80)
print()

# Setup
print("Setting up test environment...")
pm = get_project_manager()
active = pm.get_active_project() or "test_project"
db_path = pm.get_project_db_path() if pm.get_active_project() else ""

context = ConversationContext(
    project_name=active,
    project_db_path=db_path
)

orchestrator = IntelligentOrchestrator()

print(f"✅ Project: {active}")
print(f"✅ Orchestrator ready")
print()

# Test 1: Simple query that should route to timeline agent
print("-" * 80)
print("TEST 1: Simple timeline query")
print("-" * 80)
query = "What's my next deadline?"
print(f"Query: '{query}'")
print()

try:
    print("Processing query...")
    response, suggestions = orchestrator.process_user_message(query, context)

    print()
    print("RESPONSE:")
    print(response)
    print()

    if suggestions:
        print("SUGGESTIONS:")
        for s in suggestions:
            print(f"  • {s}")
    print()

    print("✅ TEST 1 PASSED - Orchestrator processed query successfully")
    print()

except Exception as e:
    print(f"❌ TEST 1 FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("-" * 80)
print("TEST COMPLETE")
print("-" * 80)
print()
print("Next: Run full integration test with 'Research fall prevention' query")
print("      (This will cost more as it uses multiple agents)")
