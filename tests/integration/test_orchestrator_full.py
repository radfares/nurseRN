"""
Comprehensive Orchestrator and Agent Diagnostic Test

Tests:
1. OpenAI API key is configured
2. Orchestrator uses LLM-based planning (not fallback)
3. All agents are accessible
4. Context awareness works correctly
5. Agents produce topic-relevant outputs

Run this to verify your system is working correctly.
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator
from src.orchestration.conversation_context import ConversationContext
from src.orchestration.agent_registry import AgentRegistry

def test_1_api_key():
    """Test 1: Check if OpenAI API key is configured"""
    print("\n" + "="*80)
    print("TEST 1: OpenAI API Key Configuration")
    print("="*80)
    
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ FAIL: OPENAI_API_KEY not set in environment")
        print("\nFix:")
        print("  1. Create/edit .env file")
        print("  2. Add: OPENAI_API_KEY=your-key-here")
        print("  3. Restart the application")
        return False
    
    if api_key.startswith("sk-"):
        print(f"✅ PASS: API key configured (starts with 'sk-', length: {len(api_key)})")
        return True
    else:
        print(f"⚠️  WARNING: API key doesn't start with 'sk-' (got: {api_key[:10]}...)")
        print("   This might be a custom endpoint or invalid key")
        return False


def test_2_orchestrator_init():
    """Test 2: Check if orchestrator initializes correctly"""
    print("\n" + "="*80)
    print("TEST 2: Orchestrator Initialization")
    print("="*80)
    
    try:
        orchestrator = IntelligentOrchestrator()
        print("✅ PASS: Orchestrator initialized")
        
        # Check if it has OpenAI client
        if hasattr(orchestrator, 'client') and orchestrator.client:
            print("✅ PASS: OpenAI client configured")
        else:
            print("❌ FAIL: No OpenAI client (using fallback mode)")
            return False, None
        
        # Check models
        print(f"   Planner model: {orchestrator.planner_model}")
        print(f"   Synthesis model: {orchestrator.synthesis_model}")
        
        return True, orchestrator
        
    except Exception as e:
        print(f"❌ FAIL: Orchestrator initialization failed: {e}")
        return False, None


def test_3_agent_registry():
    """Test 3: Check if all agents are accessible"""
    print("\n" + "="*80)
    print("TEST 3: Agent Registry")
    print("="*80)
    
    try:
        registry = AgentRegistry()
        print("✅ PASS: Agent registry initialized")
        
        # Test each agent
        agents_to_test = [
            "nursing_research",
            "medical_research",
            "academic_research",
            "research_writing",
            "project_timeline",
            "data_analysis",
            "citation_validation"
        ]
        
        all_passed = True
        for agent_name in agents_to_test:
            try:
                agent = registry.get_agent(agent_name)
                if agent:
                    print(f"✅ {agent_name}: Available")
                else:
                    print(f"❌ {agent_name}: Returned None")
                    all_passed = False
            except Exception as e:
                print(f"❌ {agent_name}: Error - {e}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ FAIL: Agent registry failed: {e}")
        return False


def test_4_llm_planning():
    """Test 4: Check if orchestrator uses LLM-based planning"""
    print("\n" + "="*80)
    print("TEST 4: LLM-Based Planning")
    print("="*80)
    
    try:
        orchestrator = IntelligentOrchestrator()
        context = ConversationContext(project_name="test_project")
        
        # Test query
        test_query = "Research fall prevention in elderly patients"
        print(f"\nTest query: \"{test_query}\"")
        
        # Create plan
        plan = orchestrator._create_execution_plan(test_query, context)
        
        if not plan:
            print("❌ FAIL: No plan created (0 tasks)")
            print("   This suggests fallback mode or planning failure")
            return False
        
        print(f"✅ PASS: Created plan with {len(plan)} tasks")
        
        # Verify plan structure
        for i, task in enumerate(plan, 1):
            print(f"\n   Task {i}:")
            print(f"     Agent: {task.agent_name}")
            print(f"     Action: {task.action}")
            print(f"     Params: {task.params}")
        
        # Check if params include topic
        has_topic = any("topic" in task.params or "query" in task.params for task in plan)
        if has_topic:
            print("\n✅ PASS: Tasks include topic/query parameters")
        else:
            print("\n⚠️  WARNING: Tasks don't include topic parameters")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: Planning failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_context_awareness():
    """Test 5: Check if orchestrator maintains conversation context"""
    print("\n" + "="*80)
    print("TEST 5: Context Awareness")
    print("="*80)
    
    try:
        orchestrator = IntelligentOrchestrator()
        context = ConversationContext(project_name="test_project")
        
        # Simulate conversation
        print("\nSimulating conversation:")
        print("  User: 'How does communication between nurses and aides help workflow?'")
        
        # Add message to context
        context.add_message("user", "How does communication between nurses and aides help workflow?")
        context.add_message("assistant", "Nurse-aide communication improves workflow by...")
        
        # Now test follow-up
        follow_up = "generate a picot question"
        print(f"  User: '{follow_up}'")
        
        # Create plan
        plan = orchestrator._create_execution_plan(follow_up, context)
        
        if not plan:
            print("❌ FAIL: No plan created for follow-up")
            return False
        
        print(f"\n✅ PASS: Created plan with {len(plan)} tasks")
        
        # Check if topic from context is used
        for task in plan:
            if "topic" in task.params:
                topic = task.params["topic"]
                print(f"\n   Topic extracted: \"{topic}\"")
                
                # Check if it mentions nurse/aide/communication
                keywords = ["nurse", "aide", "communication", "workflow"]
                has_context = any(keyword in topic.lower() for keyword in keywords)
                
                if has_context:
                    print("✅ PASS: Topic includes conversation context")
                    return True
                else:
                    print("❌ FAIL: Topic doesn't include conversation context")
                    print(f"   Expected keywords: {keywords}")
                    return False
        
        print("⚠️  WARNING: No topic parameter found in tasks")
        return False
        
    except Exception as e:
        print(f"❌ FAIL: Context awareness test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_6_end_to_end():
    """Test 6: End-to-end test with actual query"""
    print("\n" + "="*80)
    print("TEST 6: End-to-End Test")
    print("="*80)
    
    try:
        orchestrator = IntelligentOrchestrator()
        context = ConversationContext(project_name="test_project")
        
        # Test query
        test_query = "What are promising research topics in fall prevention?"
        print(f"\nTest query: \"{test_query}\"")
        
        # Process message
        print("\nProcessing... (this may take 30-60 seconds)")
        response, suggestions = orchestrator.process_user_message(test_query, context)
        
        print("\n✅ PASS: Query processed successfully")
        print(f"\nResponse length: {len(response)} characters")
        print(f"Suggestions: {len(suggestions)}")
        
        # Show first 500 chars of response
        print(f"\nResponse preview:")
        print("-" * 80)
        print(response[:500])
        if len(response) > 500:
            print("...")
        print("-" * 80)
        
        # Check response quality
        if len(response) < 100:
            print("\n⚠️  WARNING: Response is very short")
            return False
        
        if "fall prevention" in response.lower():
            print("\n✅ PASS: Response is relevant to query")
        else:
            print("\n⚠️  WARNING: Response may not be relevant to query")
        
        return True
        
    except Exception as e:
        print(f"❌ FAIL: End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("ORCHESTRATOR & AGENT DIAGNOSTIC TEST SUITE")
    print("="*80)
    print("\nThis will test:")
    print("  1. OpenAI API key configuration")
    print("  2. Orchestrator initialization")
    print("  3. Agent registry and availability")
    print("  4. LLM-based planning (not fallback)")
    print("  5. Context awareness")
    print("  6. End-to-end query processing")
    print("\n" + "="*80)
    
    results = {}
    
    # Test 1: API Key
    results["api_key"] = test_1_api_key()
    
    # Test 2: Orchestrator Init
    results["orchestrator_init"], orchestrator = test_2_orchestrator_init()
    
    # Test 3: Agent Registry
    results["agent_registry"] = test_3_agent_registry()
    
    # Test 4: LLM Planning
    results["llm_planning"] = test_4_llm_planning()
    
    # Test 5: Context Awareness
    results["context_awareness"] = test_5_context_awareness()
    
    # Test 6: End-to-End (skip if previous tests failed)
    if all([results["api_key"], results["orchestrator_init"], results["llm_planning"]]):
        results["end_to_end"] = test_6_end_to_end()
    else:
        print("\n" + "="*80)
        print("TEST 6: End-to-End Test")
        print("="*80)
        print("⏭️  SKIPPED: Previous tests failed")
        results["end_to_end"] = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*80)
    print(f"RESULT: {passed}/{total} tests passed")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your system is working correctly.")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED. See details above for fixes.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
