"""
Test script to debug OpenAI 400 "Invalid schema for function" errors.
This will print all tool schemas before sending to OpenAI to identify the problematic tool.

Usage:
    DEBUG_TOOL_SCHEMAS=true python test_tool_schema_debug.py
"""

import os
import sys

# Enable tool schema debugging
os.environ["DEBUG_TOOL_SCHEMAS"] = "true"

# Add project paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs', 'agno'))

from agents.research_writing_agent import ResearchWritingAgent

def test_research_writing_agent_tools():
    """
    Test Research Writing Agent which has:
    - create_reference_list (uses List[CitationInput])
    - extract_url_content (uses format: str parameter)
    - think (from ReasoningTools)
    """
    print("\n" + "="*80)
    print("Testing Research Writing Agent - Tool Schema Debug")
    print("="*80 + "\n")

    try:
        # Create agent
        agent = ResearchWritingAgent()

        print(f"✅ Agent created successfully")
        print(f"   Tools registered: {len(agent.functions) if hasattr(agent, 'functions') else 'N/A'}")

        # Try a simple query that will trigger tool schema validation
        print("\n📝 Running test query...")
        # BaseAgent uses print_response method, not run
        response = agent.print_response(
            "Please help me format a reference list for a research paper.",
            stream=False
        )

        print("\n✅ Test completed successfully!")
        print(f"Response preview: {str(response)[:200]}...")

    except Exception as e:
        print(f"\n❌ ERROR OCCURRED:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")

        # Check if this is an OpenAI 400 error
        if "400" in str(e) or "Invalid schema" in str(e):
            print("\n🔍 FOUND THE BLOCKER!")
            print("   This is an OpenAI 400 schema validation error.")
            print("   Check the tool schema output above to identify the problematic tool.")

        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

        return False

    return True

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PHASE 1: OpenAI 400 Schema Blocker Debug")
    print("="*80)
    print("\nThis test will:")
    print("1. Create Research Writing Agent with problematic tools")
    print("2. Print all tool schemas before sending to OpenAI")
    print("3. Identify which tool index causes the 400 error")
    print("\nLook for:")
    print("- Missing 'required': [...]")
    print("- 'required' not listing all keys")
    print("- Disallowed keywords like 'propertyNames'")
    print("- Missing required fields\n")

    success = test_research_writing_agent_tools()

    sys.exit(0 if success else 1)
