#!/usr/bin/env python3
"""
Quick smoke test for conversational interface.
Tests that all imports work and orchestrator can be instantiated.
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

print("🔍 Testing conversational interface startup...")
print()

# Test 1: Imports
print("Test 1: Verifying imports...")
try:
    from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator
    from src.orchestration.conversation_context import ConversationContext
    from project_manager import get_project_manager
    print("  ✅ All imports successful")
except Exception as e:
    print(f"  ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Orchestrator instantiation
print()
print("Test 2: Creating IntelligentOrchestrator...")
try:
    orchestrator = IntelligentOrchestrator()
    print("  ✅ Orchestrator created successfully")
except Exception as e:
    print(f"  ❌ Orchestrator creation failed: {e}")
    sys.exit(1)

# Test 3: Context creation
print()
print("Test 3: Creating ConversationContext...")
try:
    # Get a test project or use default
    pm = get_project_manager()
    active = pm.get_active_project()
    if not active:
        active = "test_project"

    db_path = pm.get_project_db_path() if active != "test_project" else ""

    context = ConversationContext(
        project_name=active,
        project_db_path=db_path
    )
    print(f"  ✅ Context created for project: {active}")
except Exception as e:
    print(f"  ❌ Context creation failed: {e}")
    sys.exit(1)

# Test 4: Message handling
print()
print("Test 4: Testing message handling...")
try:
    context.add_message("user", "Test message")
    context.add_message("assistant", "Test response")
    assert len(context.messages) == 2, "Message count incorrect"
    print(f"  ✅ Messages handled correctly ({len(context.messages)} messages)")
except Exception as e:
    print(f"  ❌ Message handling failed: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("✅ ALL TESTS PASSED")
print("=" * 60)
print()
print("The conversational interface is ready to use!")
print("Run: python run_nursing_project.py")
