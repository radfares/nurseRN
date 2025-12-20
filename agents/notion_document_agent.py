"""
Notion Document Agent - Specialized for managing Notion documents via MCP.
Allows reading, searching, and updating Notion pages.
"""

import asyncio
import json
import os
from textwrap import dedent
from typing import List, Optional, Any
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.openai import OpenAIChat

try:
    from agno.tools.mcp import MCPTools
    from mcp import StdioServerParameters
    MCP_AVAILABLE = True
except ImportError:  # Optional dependency (Notion agent only)
    MCPTools = None
    StdioServerParameters = None
    MCP_AVAILABLE = False

# Import BaseAgent for inheritance pattern
from agents.base_agent import BaseAgent


class NotionDocumentAgent(BaseAgent):
    """
    Notion Document Agent - Managed via MCP.
    """

    def __init__(self):
        # We don't initialize tools in __init__ because MCPTools requires an async context.
        # We also wait to initialize the Agent until run-time to avoid event loop mismatches.
        super().__init__(
            agent_name="Notion Document Agent",
            agent_key="notion_documents",
            tools=[]
        )

    def _create_agent(self) -> Agent:
        """
        Create a placeholder agent.
        The REAL agent is created per-run in _run_async to ensure loop safety.
        """
        return Agent(
            name="NotionDocsAgent_Placeholder",
            role="Placeholder",
            instructions="Placeholder"
        )

    def show_usage_examples(self):
        print("\n📝 Notion Document Agent Ready!")
        print("Specialized for managing your Notion workspace:")
        print("  ✓ Search for pages and databases")
        print("  ✓ Read page content")
        print("  ✓ Create or update pages")
        print("\nExample usage:")
        print("  • 'Search my Notion for nursing protocols'")
        print("  • 'Read the page titled Fall Prevention Plan'")
        print("  • 'Update the project status in Notion to Completed'")

    async def _run_async(self, query: str, stream: bool = False) -> Any:
        """Internal async runner to handle MCP lifecycle."""
        # Check for API key BEFORE loading .env to allow test mocking
        token = os.getenv("NOTION_API_KEY")
        if not token:
            # Try loading from .env as fallback
            load_dotenv(override=False)
            token = os.getenv("NOTION_API_KEY")
        
        if not token:
            error_msg = "❌ Missing Notion API key: set NOTION_API_KEY environment variable"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        # Pre-flight check: verify npx is available
        import shutil
        if not shutil.which("npx"):
            error_msg = "❌ npx not found in PATH. Please install Node.js and npm."
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        if not MCP_AVAILABLE or MCPTools is None or StdioServerParameters is None:
            error_msg = "❌ Optional dependency missing: install `mcp` to use Notion MCP tools."
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        command = "npx"
        args = ["-y", "@notionhq/notion-mcp-server"]
        env = {
            "OPENAPI_MCP_HEADERS": json.dumps(
                {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"}
            ),
            "PATH": os.environ.get("PATH", "")  # Safe access with fallback
        }
        server_params = StdioServerParameters(command=command, args=args, env=env)

        # Create the agent FRESH inside the loop to avoid AnyIO/Loop mismatch errors
        try:
            async with MCPTools(server_params=server_params) as mcp_tools:
                
                # Instantiate agent with tools
                run_agent = Agent(
                    name="NotionDocsAgent",
                    model=OpenAIChat(id="gpt-4o"),
                    tools=[mcp_tools],
                    description="Agent to query and modify Notion docs via MCP",
                    instructions=dedent("""
                        You have access to Notion documents through MCP tools.
                        - Use tools to read, search, or update pages.
                        - CRITICAL: Confirm with the user before making ANY modifications.
                        - Follow pookie's \"Authentic Voice Framework\" when drafting content.
                    """),
                    markdown=True,
                )
                
                if stream:
                    # For streaming, we yield or print directly (legacy behavior)
                    # But for Orchestrator, we need a return value.
                    # Orchestrator usually calls with stream=False.
                    await run_agent.arun(query, stream=True)
                    return None
                else:
                    response = await run_agent.arun(query)
                    return response
        except Exception as e:
            error_msg = f"MCP connection or execution failed: {type(e).__name__}: {str(e)}"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg) from e

    def run_with_grounding_check(self, query: str, **kwargs) -> Any:
        """
        Orchestrator-compatible execution method.
        Named 'run_with_grounding_check' to take precedence in dispatch_mcp.
        """
        coroutine = self._run_async(query, stream=False)
        try:
            return asyncio.run(coroutine)
        except Exception as e:
            try:
                coroutine.close()
            except Exception:
                pass
            raise RuntimeError(f"Notion Agent execution failed: {e}") from e

    def print_response(self, query: str, project_name: Optional[str] = None, stream: bool = False) -> None:
        """Override print_response to handle async MCP lifecycle."""
        try:
            # We use _run_async directly here. 
            # If stream=False, we print the result content.
            if stream:
                coroutine = self._run_async(query, stream=True)
                try:
                    asyncio.run(coroutine)
                except Exception:
                    try:
                        coroutine.close()
                    except Exception:
                        pass
                    raise
            else:
                coroutine = self._run_async(query, stream=False)
                try:
                    result = asyncio.run(coroutine)
                except Exception:
                    try:
                        coroutine.close()
                    except Exception:
                        pass
                    raise
                if result:
                    print(getattr(result, 'content', str(result)))
        except RuntimeError as e:
            # Our own raised errors - display cleanly
            print(f"❌ {e}")
            self.logger.error(f"Print response failed: {e}")
        except Exception as e:
            # Unexpected errors - show type and message
            if "unhandled errors in a TaskGroup" not in str(e):
                print(f"❌ Notion Agent error: {type(e).__name__}: {e}")
                self.logger.error(f"Unexpected error in print_response: {e}", exc_info=True)

# Create global instance
try:
    notion_document_agent = NotionDocumentAgent()
except Exception as _init_error:
    import logging
    logging.error(f"Failed to initialize NotionDocumentAgent: {_init_error}")
    notion_document_agent = None

if __name__ == "__main__":
    if notion_document_agent:
        notion_document_agent.run_with_error_handling()
