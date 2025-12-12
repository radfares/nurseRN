#!/usr/bin/env python3
"""
Phase 3A Test: Full Research Workflow
Tests multi-agent orchestration with a complex research query.

This will test:
- Multi-agent coordination (nursing research + medical research)
- Complex query decomposition
- Response synthesis across multiple sources
- Suggestion quality for research workflow

WARNING: This will cost ~$0.30-0.50 in API calls
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
print("PHASE 3A TEST: Full Research Workflow - Multi-Agent Orchestration")
print("=" * 80)
print()
print("⚠️  This test will make multiple API calls (estimated cost: $0.30-0.50)")
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

# Test: Complex research query that should trigger multiple agents
print("-" * 80)
print("TEST: Complex Research Query")
print("-" * 80)
query = "Help me develop a PICOT question for reducing patient falls in elderly hospitalized patients"
print(f"Query: '{query}'")
print()
print("Expected behavior:")
print("  - Should use nursing_research or writing agent")
print("  - Should develop a structured PICOT question")
print("  - Should provide relevant suggestions for next steps")
print()

try:
    print("Processing query... (this may take 10-20 seconds)")
    print()

    response, suggestions = orchestrator.process_user_message(query, context)

    print()
    print("=" * 80)
    print("RESPONSE:")
    print("=" * 80)
    print(response)
    print()

    if suggestions:
        print("=" * 80)
        print("SUGGESTIONS:")
        print("=" * 80)
        for i, s in enumerate(suggestions, 1):
            print(f"{i}. {s}")
    print()

    # Check response quality
    print("=" * 80)
    print("QUALITY ASSESSMENT:")
    print("=" * 80)

    quality_checks = {
        "Contains 'P' (Population)": any(word in response.lower() for word in ['population', 'elderly', 'patients', 'hospitalized']),
        "Contains 'I' (Intervention)": any(word in response.lower() for word in ['intervention', 'program', 'strategy', 'prevent']),
        "Contains 'C' (Comparison)": any(word in response.lower() for word in ['comparison', 'compared', 'standard', 'usual']),
        "Contains 'O' (Outcome)": any(word in response.lower() for word in ['outcome', 'falls', 'reduction', 'decrease']),
        "Contains 'T' (Time)": any(word in response.lower() for word in ['time', 'weeks', 'months', 'days', 'period']),
        "Response length adequate": len(response) > 200,
        "Suggestions provided": len(suggestions) > 0,
    }

    passed = sum(quality_checks.values())
    total = len(quality_checks)

    for check, result in quality_checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")

    print()
    print(f"Quality Score: {passed}/{total} ({int(passed/total*100)}%)")
    print()

    if passed >= total * 0.7:  # 70% threshold
        print("✅ TEST PASSED - Response quality is good")
    else:
        print("⚠️  WARNING - Response quality could be improved")

    # Check artifacts
    print()
    print("=" * 80)
    print("CONTEXT ARTIFACTS:")
    print("=" * 80)
    if context.artifacts:
        for name, artifact in context.artifacts.items():
            print(f"  • {name}: {type(artifact.get('value'))}")
    else:
        print("  (No artifacts stored)")

    print()
    print("=" * 80)
    print("COMPLETED TASKS:")
    print("=" * 80)
    if context.completed_tasks:
        for task in context.completed_tasks:
            print(f"  • {task}")
    else:
        print("  (No tasks marked complete)")

except Exception as e:
    print(f"❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("-" * 80)
print("TEST COMPLETE")
print("-" * 80)
print()
print("Next: Test multi-turn conversation to verify context persistence")
