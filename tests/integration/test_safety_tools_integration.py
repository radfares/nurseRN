"""
Test SafetyTools Integration with NursingResearchAgent
------------------------------------------------------
Verifies that SafetyTools is properly integrated into the agent.
"""

import sys
import os

# Ensure we can import from project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, project_root)

# Add agno to path
agno_path = os.path.join(project_root, 'libs', 'agno')
if agno_path not in sys.path:
    sys.path.insert(0, agno_path)


def test_safety_tools_in_agent():
    """Test that SafetyTools is loaded in NursingResearchAgent"""
    from agents.nursing_research_agent import NursingResearchAgent

    agent_instance = NursingResearchAgent()

    # ASSERTION 1: Verify _tool_status exists
    assert hasattr(agent_instance, '_tool_status'), \
        "Agent should have _tool_status attribute for tracking tool availability"

    # ASSERTION 2: Verify safety tool is registered
    assert 'safety' in agent_instance._tool_status, \
        "SafetyTools should be registered in agent's _tool_status"

    # ASSERTION 3: Verify safety tool is available (not None)
    safety_available = agent_instance._tool_status.get('safety', False)
    assert safety_available, \
        "SafetyTools should be available (not False/None) in agent"


def test_safety_tools_direct():
    """Test SafetyTools directly (not through agent)"""
    from src.services.safety_tools import SafetyTools

    tools = SafetyTools()

    # ASSERTION 1: Verify SafetyTools instantiates
    assert tools is not None, "SafetyTools should instantiate successfully"

    # ASSERTION 2: Verify verify_access method exists and returns boolean
    assert hasattr(tools, 'verify_access'), \
        "SafetyTools should have verify_access() method"

    access_result = tools.verify_access()
    assert isinstance(access_result, bool), \
        "verify_access() should return boolean"

    # ASSERTION 3: Verify get_device_recalls method exists
    assert hasattr(tools, 'get_device_recalls'), \
        "SafetyTools should have get_device_recalls() method"

    # ASSERTION 4: Test device recall query returns data
    result = tools.get_device_recalls("catheter", limit=1)
    assert result is not None, \
        "get_device_recalls() should return data (not None)"

    assert isinstance(result, str), \
        "get_device_recalls() should return string data"

    assert len(result) > 0, \
        "get_device_recalls() should return non-empty result"


def test_safety_tools_creation():
    """Test safe creation function"""
    from src.services.api_tools import create_safety_tools_safe

    # ASSERTION 1: Function should exist
    assert create_safety_tools_safe is not None, \
        "create_safety_tools_safe function should exist"

    # ASSERTION 2: Function should return SafetyTools instance (or None if unavailable)
    tool = create_safety_tools_safe(required=False)

    # Tool can be None if OpenFDA is unavailable, but should be a valid type
    assert tool is None or hasattr(tool, 'verify_access'), \
        "create_safety_tools_safe() should return SafetyTools instance or None"

    # ASSERTION 3: If tool exists, it should have required methods
    if tool is not None:
        assert hasattr(tool, 'get_device_recalls'), \
            "SafetyTools should have get_device_recalls method"
        assert hasattr(tool, 'get_drug_adverse_events'), \
            "SafetyTools should have get_drug_adverse_events method"
