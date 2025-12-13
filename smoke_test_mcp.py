import sys
import os
import logging
from unittest.mock import MagicMock, ANY

# Add project root to path
sys.path.append(os.getcwd())

# Configure logging to see MCP debug messages
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("src.orchestration")
logger.setLevel(logging.DEBUG)

def safely_mock_dependencies():
    """Mock external dependencies to isolate orchestrators."""
    sys.modules['src.services.utils'] = MagicMock()
    sys.modules['src.services.api_tools'] = MagicMock()
    
safely_mock_dependencies()

from src.orchestration.orchestrator import WorkflowOrchestrator
from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator
from src.orchestration.mcp import MCPMessage
from dataclasses import dataclass

@dataclass
class MockRunOutput:
    content: str = "Mock Content"
    metadata: dict = None

class MockAgent:
    def __init__(self, name="MockAgent"):
        self.agent_name = name
        self.agent = MagicMock()
        self.calls = 0
    
    def run_with_grounding_check(self, query, **kwargs):
        self.calls += 1
        return {"content": f"Processed: {query}", "metadata": {"test": "data"}}

class ErrorAgent:
    def __init__(self, name="ErrorAgent"):
        self.agent_name = name
    
    def run_with_grounding_check(self, query, **kwargs):
        raise ValueError("Simulated Agent Failure")

def test_workflow_orchestrator():
    print("\n--- Testing WorkflowOrchestrator ---")
    mock_context = MagicMock()
    mock_registry = MagicMock()
    mock_synthesizer = MagicMock()
    
    orch = WorkflowOrchestrator(mock_context)
    agent = MockAgent("TestAgent")
    
    # Execute Success
    result = orch.execute_single_agent(agent, "Hello MCP", "workflow-123", extra_param="value")
    
    print(f"Result Success: {result.success}")
    print(f"Result Content: {result.content}")
    print(f"Result Metadata: {result.metadata}")
    
    assert result.success is True
    assert result.content == "Processed: Hello MCP"
    assert "mcp_task_id" in result.metadata
    assert agent.calls == 1, f"Expected 1 call, got {agent.calls}"
    print("✅ WorkflowOrchestrator (Success) passed")

    # Execute Error
    print("\n--- Testing WorkflowOrchestrator (Error Case) ---")
    error_agent = ErrorAgent()
    try:
        orch.execute_single_agent(error_agent, "Fail me", "workflow-123")
    except ValueError as e:
        print(f"Caught expected error: {e}")
        assert "Simulated Agent Failure" in str(e)
        print("✅ WorkflowOrchestrator (Error) passed")

def test_intelligent_orchestrator():
    print("\n--- Testing IntelligentOrchestrator ---")
    mock_context = MagicMock()
    mock_registry = MagicMock()
    
    # Mock specific methods to avoid full initialization
    orch = IntelligentOrchestrator(mock_context, mock_registry)
    orch._build_agent_query = MagicMock(return_value="Built Query")
    orch._extract_agent_output = MagicMock(return_value={"structured": "output"})
    
    agent = MockAgent("IntelligentAgent")
    
    # Execute
    result = orch._execute_agent_task(agent, "search", {"query": "term"}, mock_context)
    
    print(f"Result: {result}")
    assert result == {"structured": "output"}
    assert agent.calls == 1, f"Expected 1 call, got {agent.calls}"
    print("✅ IntelligentOrchestrator passed")

if __name__ == "__main__":
    try:
        test_workflow_orchestrator()
        test_intelligent_orchestrator()
        print("\n🎉 SMOKE TEST PASSED: MCP Envelope Verified")
    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
