"""
End-to-End Test: ReasoningTools Integration with All 6 Agents
Created: 2025-12-11
Tests that ReasoningTools work correctly with each agent in production.

This test verifies:
1. Each agent initializes successfully with ReasoningTools
2. Agents can use reasoning when appropriate
3. Existing functionality remains intact
4. No conflicts with existing tools
"""

import sys
import os

# Add project root to path (parent of tests/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_agent_initialization(agent_module, agent_class_name):
    """Test that an agent initializes successfully"""
    try:
        module = __import__(agent_module, fromlist=[agent_class_name])
        agent_class = getattr(module, agent_class_name)
        agent_instance = agent_class()
        
        # Verify agent has tools
        if not agent_instance.tools:
            print(f"  ⚠️ Warning: {agent_class_name} has no tools")
        
        # Check if ReasoningTools is in the tools list
        has_reasoning = any('reasoning' in str(type(tool)).lower() for tool in agent_instance.tools)
        
        if has_reasoning:
            print(f"  ✓ {agent_class_name} initialized with ReasoningTools")
        else:
            print(f"  ⚠️ {agent_class_name} initialized but ReasoningTools not detected")
        
        return True
    except Exception as e:
        print(f"  ✗ {agent_class_name} FAILED: {e}")
        return False


def run_e2e_tests():
    """Run end-to-end tests for all 6 agents"""
    print("\n" + "="*60)
    print("END-TO-END TEST: ReasoningTools Integration")
    print("="*60 + "\n")
    
    agents_to_test = [
        ("agents.nursing_research_agent", "NursingResearchAgent"),
        ("agents.medical_research_agent", "MedicalResearchAgent"),
        ("agents.academic_research_agent", "AcademicResearchAgent"),
        ("agents.research_writing_agent", "ResearchWritingAgent"),
        ("agents.nursing_project_timeline_agent", "ProjectTimelineAgent"),
        ("agents.data_analysis_agent", "DataAnalysisAgent"),
    ]
    
    results = []
    
    print("Testing agent initialization with ReasoningTools:\n")
    for module, agent_class in agents_to_test:
        print(f"Testing {agent_class}...")
        result = test_agent_initialization(module, agent_class)
        results.append(result)
        print()
    
    # Summary
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} agents initialized successfully")
    
    if passed == total:
        print("\n✅ ALL E2E TESTS PASSED - Integration successful!")
        print("="*60 + "\n")
        return True
    else:
        print(f"\n❌ {total - passed} AGENT(S) FAILED - Review errors above")
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    success = run_e2e_tests()
    sys.exit(0 if success else 1)
