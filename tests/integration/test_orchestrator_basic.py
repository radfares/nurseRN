#!/usr/bin/env python3
"""
Test the IntelligentOrchestrator with a simple timeline query.
Tests planning, execution, and synthesis.

Created: 2025-12-11 (Session 007 Phase 2)
Moved to tests/integration: 2025-12-11
"""

import sys
from pathlib import Path

# Setup path
_project_root = Path(__file__).parent.parent.parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))

# Add project root to sys.path for src imports
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

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
print("Next: Run data analysis test with 'Research fall prevention' query")
