
import asyncio
import os
from dotenv import load_dotenv
from agents.notion_document_agent import notion_document_agent

load_dotenv(override=True)

def test_crash():
    print("🚀 Starting MCP crash test...")
    try:
        # Simulate exactly what the CLI does
        notion_document_agent.print_response("Search notion for anything nursing", stream=False)
        print("✅ Test finished without crash.")
    except Exception as e:
        print(f"❌ Caught unexpected exception: {e}")

if __name__ == "__main__":
    test_crash()
