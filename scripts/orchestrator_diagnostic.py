"""
Comprehensive Orchestrator and Agent Diagnostic Test

Runs a lightweight diagnostic of the orchestrator and agent registry.
Designed to work in both API-key and keyless (fallback) environments.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator
from src.orchestration.conversation_context import ConversationContext
from src.orchestration.agent_registry import AgentRegistry


def has_api_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def test_1_api_key() -> bool:
    """Check if OpenAI API key is configured."""
    print("\n" + "=" * 80)
    print("TEST 1: OpenAI API Key Configuration")
    print("=" * 80)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ℹ️  OPENAI_API_KEY not set – running in fallback (no-LLM) mode.")
        return True

    if api_key.startswith("sk-"):
        print(f"✅ PASS: API key configured (starts with 'sk-', length: {len(api_key)})")
    else:
        print(f"⚠️  WARNING: API key doesn't start with 'sk-' (got: {api_key[:10]}...)")
        print("   This might be a custom endpoint or invalid key")
    return True


def test_2_orchestrator_init() -> Tuple[bool, IntelligentOrchestrator | None]:
    """Check if orchestrator initializes correctly."""
    print("\n" + "=" * 80)
    print("TEST 2: Orchestrator Initialization")
    print("=" * 80)

    try:
        orch = IntelligentOrchestrator()
        print("✅ PASS: Orchestrator initialized")

        if hasattr(orch, "client") and orch.client:
            print("✅ PASS: OpenAI client configured")
        else:
            print("ℹ️  No OpenAI client detected – fallback planner will be used")

        print(f"   Planner model: {orch.planner_model}")
        print(f"   Synthesis model: {orch.synthesis_model}")
        return True, orch
    except Exception as e:
        print(f"❌ FAIL: Orchestrator initialization failed: {e}")
        return False, None


def test_3_agent_registry() -> bool:
    """Check if all agents are accessible in the registry."""
    print("\n" + "=" * 80)
    print("TEST 3: Agent Registry")
    print("=" * 80)

    registry = AgentRegistry()
    agents_to_test = [
        "nursing_research",
        "medical_research",
        "academic_research",
        "research_writing",
        "project_timeline",
        "data_analysis",
        "citation_validation",
    ]

    missing = [name for name in agents_to_test if not registry.is_available(name)]
    if missing:
        print(f"❌ FAIL: Missing agents in registry: {', '.join(missing)}")
        return False

    print("✅ PASS: All agents present in registry (lookup only; instantiation skipped)")
    return True


def test_4_llm_planning() -> bool:
    """Check if orchestrator can build a plan (LLM or fallback)."""
    print("\n" + "=" * 80)
    print("TEST 4: Planning")
    print("=" * 80)

    orch = IntelligentOrchestrator()
    context = ConversationContext(project_name="test_project")
    test_query = "Research fall prevention in elderly patients"
    plan = orch._create_execution_plan(test_query, context)

    if not plan:
        print("❌ FAIL: No plan created (0 tasks)")
        return False

    mode = "LLM" if orch.client else "Fallback"
    print(f"✅ PASS: Created plan with {len(plan)} tasks [{mode}]")
    for i, task in enumerate(plan, 1):
        print(f"   Task {i}: agent={task.agent_name}, action={task.action}, params={task.params}")

    has_topic = any("topic" in t.params or "query" in t.params for t in plan)
    if has_topic:
        print("✅ PASS: Tasks include topic/query parameters")
    else:
        print("⚠️  WARNING: Tasks missing topic/query parameters")
    return True


def test_5_context_awareness() -> bool:
    """Check if orchestrator uses recent conversation context."""
    print("\n" + "=" * 80)
    print("TEST 5: Context Awareness")
    print("=" * 80)

    orch = IntelligentOrchestrator()
    context = ConversationContext(project_name="test_project")
    context.add_message("user", "How does communication between nurses and aides help workflow?")
    context.add_message("assistant", "Nurse-aide communication improves workflow by...")

    follow_up = "generate a picot question"
    plan = orch._create_execution_plan(follow_up, context)

    if not plan:
        print("❌ FAIL: No plan created for follow-up")
        return False

    print(f"✅ PASS: Created plan with {len(plan)} tasks")
    for task in plan:
        if "topic" in task.params:
            topic = task.params["topic"]
            keywords = ["nurse", "aide", "communication", "workflow"]
            has_context = any(k in topic.lower() for k in keywords)
            if has_context:
                print(f"✅ PASS: Topic includes context → \"{topic}\"")
                return True
            print(f"⚠️  WARNING: Topic missing expected context → \"{topic}\"")
            return False

    print("⚠️  WARNING: No topic parameter found in tasks")
    return False


def test_6_end_to_end() -> bool:
    """End-to-end test (only runs when API key is present)."""
    print("\n" + "=" * 80)
    print("TEST 6: End-to-End Test")
    print("=" * 80)

    if not has_api_key():
        print("⏭️  SKIPPED: OPENAI_API_KEY not set (LLM required for this test)")
        return True  # Skip without failing

    orch = IntelligentOrchestrator()
    context = ConversationContext(project_name="test_project")
    test_query = "What are promising research topics in fall prevention?"

    print("\nProcessing... (this may take 30-60 seconds)")
    response, suggestions = orch.process_user_message(test_query, context)

    if not response:
        print("❌ FAIL: Empty response")
        return False

    print(f"✅ PASS: Response length {len(response)} characters, {len(suggestions)} suggestions")
    preview = response[:500]
    print("\nResponse preview:\n" + "-" * 80 + f"\n{preview}\n" + "-" * 80)

    if "fall prevention" in response.lower():
        print("✅ PASS: Response appears relevant")
    else:
        print("⚠️  WARNING: Response may not mention the topic explicitly")
    return True


def main() -> int:
    print("\n" + "=" * 80)
    print("ORCHESTRATOR & AGENT DIAGNOSTIC TEST SUITE")
    print("=" * 80)
    print("\nThis will test:")
    print("  1. OpenAI API key configuration (optional)")
    print("  2. Orchestrator initialization")
    print("  3. Agent registry presence")
    print("  4. Planning (LLM or fallback)")
    print("  5. Context awareness")
    print("  6. End-to-end query (only with API key)")
    print("\n" + "=" * 80)

    results: Dict[str, Any] = {}
    results["api_key"] = test_1_api_key()
    results["orchestrator_init"], _ = test_2_orchestrator_init()
    results["agent_registry"] = test_3_agent_registry()
    results["planning"] = test_4_llm_planning()
    results["context_awareness"] = test_5_context_awareness()
    results["end_to_end"] = test_6_end_to_end()

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    for name, ok in results.items():
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"{status}: {name}")

    print("\n" + "=" * 80)
    print(f"RESULT: {passed}/{total} tests passed")
    print("=" * 80)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. See details above for fixes.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
