#!/usr/bin/env python3
"""
Test that Exa is properly integrated into the conversational workflow.
Verifies:
1. Nursing research agent has Exa enabled
2. Agent is accessible via orchestrator
3. No mock code in production path
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

print("=" * 80)
print("EXA INTEGRATION VERIFICATION")
print("=" * 80)
print()

# Test 1: Verify nursing research agent has Exa
print("TEST 1: Nursing Research Agent - Exa Tool Status")
print("-" * 80)
from agents.nursing_research_agent import get_nursing_research_agent

agent_wrapper = get_nursing_research_agent()
if agent_wrapper is None:
    print("❌ FAILED: Agent failed to initialize")
    sys.exit(1)

# Check tool status
exa_enabled = agent_wrapper._tool_status.get('exa', False)
print(f"Exa enabled: {exa_enabled}")

if exa_enabled:
    print("✅ PASS: Exa is enabled in nursing research agent")
else:
    print("❌ FAIL: Exa is not enabled")
    sys.exit(1)

# Count total tools
total_tools = len(agent_wrapper.tools)
print(f"Total tools loaded: {total_tools}")
print()

# Test 2: Verify agent accessible via registry
print("TEST 2: Agent Registry - Nursing Research Agent Access")
print("-" * 80)
from src.orchestration.agent_registry import AgentRegistry

registry = AgentRegistry()
try:
    registered_agent = registry.get_agent('nursing_research')
    print("✅ PASS: Agent accessible via registry")
    print(f"   Agent type: {type(registered_agent).__name__}")
except Exception as e:
    print(f"❌ FAIL: Could not access agent via registry: {e}")
    sys.exit(1)

print()

# Test 3: Verify orchestrator can use the agent
print("TEST 3: Intelligent Orchestrator - Agent Integration")
print("-" * 80)
from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator

try:
    orchestrator = IntelligentOrchestrator()

    # Verify agent is in registry
    available_agents = orchestrator.agent_registry.list_agents()
    print(f"Available agents: {', '.join(available_agents)}")

    if 'nursing_research' in available_agents:
        print("✅ PASS: Nursing research agent registered in orchestrator")
    else:
        print("❌ FAIL: Nursing research agent not found in orchestrator")
        sys.exit(1)

except Exception as e:
    print(f"❌ FAIL: Orchestrator initialization error: {e}")
    sys.exit(1)

print()

# Test 4: Verify no mock code in production path
print("TEST 4: Production Code Verification - No Mocks")
print("-" * 80)
import inspect

# Check if agent is a real instance, not a mock
agent_class_name = type(registered_agent).__name__
if 'Mock' in agent_class_name or 'mock' in agent_class_name.lower():
    print(f"❌ FAIL: Agent appears to be a mock: {agent_class_name}")
    sys.exit(1)
else:
    print(f"✅ PASS: Agent is real production code: {agent_class_name}")

# Check if it has real methods
if hasattr(registered_agent, 'agent') and hasattr(registered_agent.agent, 'run'):
    print("✅ PASS: Agent has real run() method")
else:
    print("❌ FAIL: Agent missing expected methods")
    sys.exit(1)

print()

# Summary
print("=" * 80)
print("INTEGRATION VERIFICATION SUMMARY")
print("=" * 80)
print()
print("✅ Exa is enabled in nursing research agent")
print("✅ Agent accessible via registry")
print("✅ Agent integrated in orchestrator")
print("✅ No mock code in production path")
print()
print("RESULT: All tests passed - Exa is properly integrated!")
print()
print("The conversational workflow can now use Exa for:")
print("  • Neural web search for broader healthcare context")
print("  • Recent developments and guidelines")
print("  • Organizational resources (Joint Commission, CDC, WHO)")
print("  • Complementary to PubMed and other healthcare databases")
print()
