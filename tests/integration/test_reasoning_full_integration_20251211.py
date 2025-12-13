"""
Full Integration Test: ReasoningTools in Production Workflow
Created: 2025-12-11
Tests that ReasoningTools work correctly in the actual production workflow.

This test verifies:
1. Agents can be imported and initialized
2. ReasoningTools are accessible in agent.tools
3. Agents can process queries (with reasoning if appropriate)
4. Integration with run_nursing_project.py works
5. No import errors or broken links
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Test 1: Verify all agents can be imported"""
    print("Test 1: Import all agents...")
    try:
        from agents.nursing_research_agent import NursingResearchAgent
        from agents.medical_research_agent import MedicalResearchAgent
        from agents.academic_research_agent import AcademicResearchAgent
        from agents.research_writing_agent import ResearchWritingAgent
        from agents.nursing_project_timeline_agent import ProjectTimelineAgent
        from agents.data_analysis_agent import DataAnalysisAgent
        print("  ✓ All agent imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_reasoning_tools_present():
    """Test 2: Verify ReasoningTools are in agent tools"""
    print("\nTest 2: Check ReasoningTools presence in each agent...")
    
    from agents.nursing_research_agent import NursingResearchAgent
    from agents.medical_research_agent import MedicalResearchAgent
    from agents.academic_research_agent import AcademicResearchAgent
    from agents.research_writing_agent import ResearchWritingAgent
    from agents.nursing_project_timeline_agent import ProjectTimelineAgent
    from agents.data_analysis_agent import DataAnalysisAgent
    
    agents = [
        ("NursingResearchAgent", NursingResearchAgent()),
        ("MedicalResearchAgent", MedicalResearchAgent()),
        ("AcademicResearchAgent", AcademicResearchAgent()),
        ("ResearchWritingAgent", ResearchWritingAgent()),
        ("ProjectTimelineAgent", ProjectTimelineAgent()),
        ("DataAnalysisAgent", DataAnalysisAgent()),
    ]
    
    results = []
    for name, agent_instance in agents:
        # Check if tools list contains reasoning
        has_reasoning = False
        tool_names = []
        
        for tool in agent_instance.tools:
            tool_type = str(type(tool))
            tool_names.append(tool_type)
            if 'reasoning' in tool_type.lower():
                has_reasoning = True
        
        if has_reasoning:
            print(f"  ✓ {name}: ReasoningTools found")
            results.append(True)
        else:
            print(f"  ✗ {name}: ReasoningTools NOT found")
            print(f"    Available tools: {tool_names}")
            results.append(False)
    
    return all(results)


def test_agent_tool_access():
    """Test 3: Verify agents can access their tools programmatically"""
    print("\nTest 3: Verify tool accessibility...")
    
    from agents.nursing_research_agent import NursingResearchAgent
    
    try:
        agent = NursingResearchAgent()
        
        # Check that tools attribute exists and is iterable
        if hasattr(agent, 'tools') and agent.tools:
            print(f"  ✓ Agent has {len(agent.tools)} tools")
            
            # Try to access individual tools
            for i, tool in enumerate(agent.tools):
                tool_name = type(tool).__name__
                print(f"    - Tool {i+1}: {tool_name}")
            
            return True
        else:
            print("  ✗ Agent has no tools or tools attribute missing")
            return False
            
    except Exception as e:
        print(f"  ✗ Tool access failed: {e}")
        return False


def test_agent_creation_via_agent_config():
    """Test 4: Verify agents work with agent_config imports"""
    print("\nTest 4: Test agent_config integration...")
    
    try:
        from agent_config import get_db_path
        
        # Test that config works
        db_path = get_db_path("nursing_research")
        if "nursing_research_agent.db" in db_path:
            print(f"  ✓ agent_config working: {db_path}")
            return True
        else:
            print(f"  ✗ Unexpected db_path: {db_path}")
            return False
            
    except Exception as e:
        print(f"  ✗ agent_config test failed: {e}")
        return False


def test_main_entry_point():
    """Test 5: Verify run_nursing_project.py can import agents"""
    print("\nTest 5: Check main entry point compatibility...")
    
    try:
        # Try to import the main script components
        import run_nursing_project
        
        print("  ✓ run_nursing_project.py imports successfully")
        
        # Check if it has the expected functions
        if hasattr(run_nursing_project, 'main') or hasattr(run_nursing_project, 'run'):
            print("  ✓ Main function found")
        else:
            print("  ⚠ No main/run function found (might be script-only)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Main entry point test failed: {e}")
        import traceback
        print(f"    {traceback.format_exc()}")
        return False


def test_agent_query_execution():
    """Test 6: Verify an agent can execute a simple query"""
    print("\nTest 6: Test actual agent query execution...")
    
    # Only run if API key is available
    if not os.getenv("OPENAI_API_KEY"):
        print("  ⚠ SKIPPED: No OPENAI_API_KEY available")
        return True
    
    try:
        from agents.research_writing_agent import ResearchWritingAgent
        
        agent = ResearchWritingAgent()
        
        # Try a simple query that doesn't require external tools
        print("  Running test query...")
        response = agent.agent.run(
            "What are the key components of a PICOT question? Give a brief answer.",
            stream=False
        )
        
        if response and response.content:
            response_text = response.content[:100]
            print(f"  ✓ Query executed successfully")
            print(f"    Response preview: {response_text}...")
            return True
        else:
            print("  ✗ Query returned no response")
            return False
            
    except Exception as e:
        print(f"  ✗ Query execution failed: {e}")
        import traceback
        print(f"    {traceback.format_exc()}")
        return False


def run_full_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("FULL INTEGRATION TEST: ReasoningTools in Production")
    print("="*60 + "\n")
    
    tests = [
        ("Import Test", test_imports),
        ("ReasoningTools Presence", test_reasoning_tools_present),
        ("Tool Access", test_agent_tool_access),
        ("Agent Config", test_agent_creation_via_agent_config),
        ("Main Entry Point", test_main_entry_point),
        ("Query Execution", test_agent_query_execution),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    total = len(results)
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ FULL INTEGRATION SUCCESSFUL!")
        print("ReasoningTools are properly integrated into production workflow.")
        print("="*60 + "\n")
        return True
    else:
        print(f"\n⚠️ {total - passed} TEST(S) FAILED")
        print("Review issues above before deploying.")
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    success = run_full_integration_tests()
    sys.exit(0 if success else 1)
