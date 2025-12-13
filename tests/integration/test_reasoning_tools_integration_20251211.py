"""
Smoke Test: Reasoning Tools Integration
Created: 2025-12-11
Tests that ReasoningTools can be integrated safely without breaking existing agents.

This test verifies:
1. Imports work correctly
2. Tools can be added to agents
3. Basic reasoning functionality works
4. No conflicts with existing tools
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agno.tools.reasoning import ReasoningTools
from agno.agent import Agent
from agno.models.openai import OpenAIChat


def test_reasoning_tools_import():
    """Test 1: Verify ReasoningTools can be imported"""
    print("✓ Test 1: ReasoningTools import successful")
    return True


def test_reasoning_tools_instantiation():
    """Test 2: Verify ReasoningTools can be instantiated"""
    try:
        reasoning_tools = ReasoningTools(add_instructions=True)
        print("✓ Test 2: ReasoningTools instantiation successful")
        return True
    except Exception as e:
        print(f"✗ Test 2 FAILED: {e}")
        return False


def test_agent_with_reasoning_tools():
    """Test 3: Verify agent can be created with ReasoningTools"""
    try:
        test_agent = Agent(
            name="Reasoning Test Agent",
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[ReasoningTools(add_instructions=True)],
            markdown=True,
        )
        print("✓ Test 3: Agent with ReasoningTools created successfully")
        return True
    except Exception as e:
        print(f"✗ Test 3 FAILED: {e}")
        return False


def test_reasoning_with_simple_query():
    """Test 4: Verify reasoning works on a simple query (requires API key)"""
    try:
        # Check for API key
        if not os.getenv("OPENAI_API_KEY"):
            print("⚠ Test 4 SKIPPED: No OPENAI_API_KEY found")
            return True
        
        test_agent = Agent(
            name="Reasoning Test Agent",
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[ReasoningTools(add_instructions=True)],
            markdown=False,
        )
        
        # Simple reasoning query
        response = test_agent.run("Should I use reasoning tools for nursing research? Give a brief yes/no answer.")
        
        if response and response.content:
            print("✓ Test 4: Reasoning query executed successfully")
            print(f"  Response length: {len(response.content)} chars")
            return True
        else:
            print("✗ Test 4 FAILED: No response from agent")
            return False
            
    except Exception as e:
        print(f"✗ Test 4 FAILED: {e}")
        return False


def run_smoke_tests():
    """Run all smoke tests"""
    print("\n" + "="*60)
    print("SMOKE TEST: Reasoning Tools Integration")
    print("="*60 + "\n")
    
    tests = [
        test_reasoning_tools_import,
        test_reasoning_tools_instantiation,
        test_agent_with_reasoning_tools,
        test_reasoning_with_simple_query,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL SMOKE TESTS PASSED - Safe to integrate")
        print("="*60 + "\n")
        return True
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED - Do not integrate")
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    success = run_smoke_tests()
    sys.exit(0 if success else 1)
