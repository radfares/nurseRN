"""
Test SafetyTools Integration with NursingResearchAgent
------------------------------------------------------
Verifies that SafetyTools is properly integrated into the agent.
"""

import sys
import os

# Ensure we can import from project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Add agno to path
agno_path = os.path.join(project_root, 'libs', 'agno')
if agno_path not in sys.path:
    sys.path.insert(0, agno_path)


def test_safety_tools_in_agent():
    """Test that SafetyTools is loaded in NursingResearchAgent"""
    print("\n🧪 TEST 1: SafetyTools Integration Check")
    try:
        from agents.nursing_research_agent import NursingResearchAgent

        agent_instance = NursingResearchAgent()

        # Check if safety tool is in the status
        if hasattr(agent_instance, '_tool_status'):
            safety_available = agent_instance._tool_status.get('safety', False)
            if safety_available:
                print("   ✅ SUCCESS: SafetyTools is registered in agent")
                return True
            else:
                print("   ❌ FAILED: SafetyTools not in agent status")
                return False
        else:
            print("   ❌ FAILED: Agent missing _tool_status attribute")
            return False

    except Exception as e:
        print(f"   ❌ FAILED: Error loading agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_safety_tools_direct():
    """Test SafetyTools directly (not through agent)"""
    print("\n🧪 TEST 2: SafetyTools Direct API Test")
    try:
        from src.services.safety_tools import SafetyTools

        tools = SafetyTools()

        # Test connectivity
        if tools.verify_access():
            print("   ✅ SUCCESS: OpenFDA API is accessible")

            # Try a real query
            print("   Testing device recall query...")
            result = tools.get_device_recalls("catheter", limit=1)

            if result and len(result) > 50:
                print(f"   ✅ SUCCESS: Got device recall data ({len(result)} chars)")
                # Show snippet
                snippet = result[:150] + "..." if len(result) > 150 else result
                print(f"   📄 Sample: {snippet}")
                return True
            else:
                print(f"   ⚠️ WARNING: Short or empty result: {result}")
                return False
        else:
            print("   ❌ FAILED: OpenFDA API not accessible")
            return False

    except Exception as e:
        print(f"   ❌ FAILED: Error testing SafetyTools: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_safety_tools_creation():
    """Test safe creation function"""
    print("\n🧪 TEST 3: Safe Tool Creation Function")
    try:
        from src.services.api_tools import create_safety_tools_safe

        tool = create_safety_tools_safe(required=False)

        if tool:
            print("   ✅ SUCCESS: create_safety_tools_safe() returned tool")
            return True
        else:
            print("   ❌ FAILED: create_safety_tools_safe() returned None")
            return False

    except Exception as e:
        print(f"   ❌ FAILED: Error in safe creation: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("   SAFETY TOOLS INTEGRATION TEST")
    print("=" * 70)
    print("\nVerifying SafetyTools is properly integrated into NursingResearchAgent\n")

    # Run tests
    test1_pass = test_safety_tools_in_agent()
    test2_pass = test_safety_tools_direct()
    test3_pass = test_safety_tools_creation()

    # Summary
    print("\n" + "=" * 70)
    print("   TEST SUMMARY")
    print("=" * 70)

    print(f"\nTest 1 - Agent Integration:     {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"Test 2 - Direct API Test:       {'✅ PASS' if test2_pass else '❌ FAIL'}")
    print(f"Test 3 - Safe Creation:         {'✅ PASS' if test3_pass else '❌ FAIL'}")

    all_passed = test1_pass and test2_pass and test3_pass

    if all_passed:
        print("\n🟢 ALL TESTS PASSED: SafetyTools is fully integrated!")
        print("   ✓ Agent has SafetyTools registered")
        print("   ✓ OpenFDA API is accessible")
        print("   ✓ Safe creation pattern works")
        print("\n   The NursingResearchAgent can now check FDA device recalls")
        print("   and drug adverse events using SafetyTools.\n")
        sys.exit(0)
    else:
        print("\n🔴 SOME TESTS FAILED: Check errors above")
        print("   Review the integration and ensure:")
        print("   - src/services/safety_tools.py exists")
        print("   - SafetyTools is imported in nursing_research_agent.py")
        print("   - OpenFDA API is accessible from your network\n")
        sys.exit(1)
