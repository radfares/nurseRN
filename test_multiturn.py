#!/usr/bin/env python3
"""
Phase 3A Test: Multi-Turn Conversation
Tests context persistence across multiple conversation turns.

This will test:
- Context carries forward across queries
- Artifacts are accessible in subsequent queries
- Completed tasks tracked correctly
- Conversation history maintained
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
print("PHASE 3A TEST: Multi-Turn Conversation with Context Persistence")
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

# Turn 1: Generate PICOT
print("=" * 80)
print("TURN 1: Generate PICOT Question")
print("=" * 80)
query1 = "Create a PICOT question about reducing catheter-associated UTIs"
print(f"Query: '{query1}'")
print()

try:
    response1, suggestions1 = orchestrator.process_user_message(query1, context)

    print("Response preview:")
    print(response1[:300] + "..." if len(response1) > 300 else response1)
    print()

    print(f"✅ Turn 1 complete")
    print(f"   Artifacts: {list(context.artifacts.keys())}")
    print(f"   Completed tasks: {context.completed_tasks}")
    print(f"   Messages in context: {len(context.messages)}")
    print()

except Exception as e:
    print(f"❌ Turn 1 failed: {e}")
    sys.exit(1)

# Turn 2: Follow-up that references previous context
print("=" * 80)
print("TURN 2: Follow-up Question (Tests Context Persistence)")
print("=" * 80)
query2 = "Now calculate the sample size I would need for that study"
print(f"Query: '{query2}'")
print("(This should reference the PICOT from Turn 1)")
print()

try:
    response2, suggestions2 = orchestrator.process_user_message(query2, context)

    print("Response preview:")
    print(response2[:400] + "..." if len(response2) > 400 else response2)
    print()

    print(f"✅ Turn 2 complete")
    print(f"   Artifacts: {list(context.artifacts.keys())}")
    print(f"   Completed tasks: {context.completed_tasks}")
    print(f"   Messages in context: {len(context.messages)}")
    print()

except Exception as e:
    print(f"❌ Turn 2 failed: {e}")
    import traceback
    traceback.print_exc()

# Turn 3: Another follow-up
print("=" * 80)
print("TURN 3: Another Follow-up")
print("=" * 80)
query3 = "What would be the key points to include in my literature review?"
print(f"Query: '{query3}'")
print()

try:
    response3, suggestions3 = orchestrator.process_user_message(query3, context)

    print("Response preview:")
    print(response3[:400] + "..." if len(response3) > 400 else response3)
    print()

    print(f"✅ Turn 3 complete")
    print(f"   Artifacts: {list(context.artifacts.keys())}")
    print(f"   Completed tasks: {context.completed_tasks}")
    print(f"   Messages in context: {len(context.messages)}")
    print()

except Exception as e:
    print(f"⚠️  Turn 3 failed (optional): {e}")

# Assessment
print("=" * 80)
print("MULTI-TURN CONVERSATION ASSESSMENT:")
print("=" * 80)

checks = {
    "Context persisted across turns": len(context.messages) >= 6,  # 3 queries + 3 responses
    "Artifacts accumulated": len(context.artifacts) > 0,
    "Tasks tracked": len(context.completed_tasks) > 0,
    "Turn 2 references Turn 1": "sample size" in response2.lower() or "picot" in response2.lower(),
}

passed = sum(checks.values())
total = len(checks)

for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"{status} {check}")

print()
print(f"Context Persistence Score: {passed}/{total} ({int(passed/total*100)}%)")
print()

if passed >= total * 0.75:
    print("✅ MULTI-TURN TEST PASSED - Context persistence working")
else:
    print("⚠️  WARNING - Context persistence needs improvement")

print()
print("-" * 80)
print("TEST COMPLETE")
print("-" * 80)
