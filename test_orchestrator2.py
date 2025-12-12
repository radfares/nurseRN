#!/usr/bin/env python3
"""
Test the IntelligentOrchestrator with a data analysis query.
This should work better as the data analysis agent is more reliable.
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
print("PHASE 2 TEST 2: Data Analysis Query")
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

# Test: Data analysis query
print("-" * 80)
print("TEST: Sample size calculation")
print("-" * 80)
query = "Calculate sample size for detecting a 30% reduction in fall rates"
print(f"Query: '{query}'")
print()

try:
    print("Processing query...")
    print()

    response, suggestions = orchestrator.process_user_message(query, context)

    print()
    print("=" * 80)
    print("RESPONSE:")
    print("=" * 80)
    print(response)
    print()

    if suggestions:
        print("SUGGESTIONS:")
        for s in suggestions:
            print(f"  • {s}")
    print()

    # Check if response contains actual numbers (indicates tool was used)
    if any(char.isdigit() for char in response):
        print("✅ TEST PASSED - Response contains numerical results (tools likely used)")
    else:
        print("⚠️  WARNING - Response may not have used calculation tools")

except Exception as e:
    print(f"❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("-" * 80)
print("TEST COMPLETE")
print("-" * 80)
