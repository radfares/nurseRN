"""
Integration Tests for Notion Document Agent

Tests MCP lifecycle, error handling, and orchestrator integration.

Created: 2025-12-20
"""

import os
import sys
import pytest
import asyncio
from unittest.mock import patch, MagicMock
from typing import Any

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.notion_document_agent import MCP_AVAILABLE, NotionDocumentAgent
from src.orchestration.mcp import new_task
from src.orchestration.mcp_dispatch import dispatch_mcp


class TestNotionAgentErrorHandling:
    """Test error scenarios and exception handling."""
    
    def test_missing_api_key_raises_runtime_error(self):
        """Test that missing API key raises RuntimeError, not mock object."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
            with pytest.raises(RuntimeError) as exc_info:
                agent.run_with_grounding_check("test query")
            
            assert "Missing Notion API key" in str(exc_info.value)
    
    def test_missing_npx_raises_runtime_error(self):
        """Test that missing npx binary raises RuntimeError."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": "test_key"}, clear=False):
            with patch("shutil.which", return_value=None):
                with pytest.raises(RuntimeError) as exc_info:
                    agent.run_with_grounding_check("test query")
                
                assert "npx not found" in str(exc_info.value)
    
    def test_print_response_handles_runtime_error_gracefully(self, capsys):
        """Test that print_response displays errors cleanly."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
            agent.print_response("test query", stream=False)
            
            captured = capsys.readouterr()
            assert "❌" in captured.out
            assert "Missing Notion API key" in captured.out


class TestNotionAgentReturnTypes:
    """Test that agent returns consistent types for orchestrator."""
    
    @pytest.mark.skipif(
        (not os.getenv("NOTION_API_KEY")) or (not MCP_AVAILABLE),
        reason="Requires NOTION_API_KEY and optional `mcp` dependency for live testing"
    )
    def test_successful_execution_returns_run_output(self):
        """Test that successful execution returns RunOutput object."""
        agent = NotionDocumentAgent()
        result = agent.run_with_grounding_check("Search for test")
        
        # Verify it's a RunOutput with content attribute
        assert hasattr(result, 'content')
        assert hasattr(result, 'metadata')
        assert isinstance(result.content, str)
    
    def test_error_execution_raises_exception(self):
        """Test that errors raise exceptions, not return error objects."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
            with pytest.raises(RuntimeError):
                agent.run_with_grounding_check("test query")


class TestNotionAgentMCPIntegration:
    """Test integration with MCP dispatch system."""
    
    def test_dispatch_mcp_handles_notion_agent_error(self):
        """Test that dispatch_mcp properly wraps Notion agent errors."""
        agent = NotionDocumentAgent()
        task_msg = new_task(
            sender="test_orchestrator",
            recipient="notion_documents",
            content="test query",
            metadata={"test": "data"}
        )
        
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
            result_msg = dispatch_mcp(agent, task_msg)
            
            # Should return error MCPMessage, not crash
            assert result_msg.message_type == "error"
            assert "Missing Notion API key" in result_msg.content
            assert result_msg.metadata["error_type"] == "RuntimeError"
    
    @pytest.mark.skipif(
        (not os.getenv("NOTION_API_KEY")) or (not MCP_AVAILABLE),
        reason="Requires NOTION_API_KEY and optional `mcp` dependency for live testing"
    )
    def test_dispatch_mcp_returns_result_on_success(self):
        """Test that dispatch_mcp returns result MCPMessage on success."""
        agent = NotionDocumentAgent()
        task_msg = new_task(
            sender="test_orchestrator",
            recipient="notion_documents",
            content="Search Notion for test",
            metadata={"test": "data"}
        )
        
        result_msg = dispatch_mcp(agent, task_msg)
        
        # Should return result MCPMessage
        assert result_msg.message_type == "result"
        assert hasattr(result_msg, 'content')
        assert isinstance(result_msg.content, str)
        assert result_msg.task_id == task_msg.task_id


class TestNotionAgentAsyncLifecycle:
    """Test async execution and event loop handling."""
    
    @pytest.mark.asyncio
    async def test_run_async_with_missing_key(self):
        """Test async execution with missing API key."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
            with pytest.raises(RuntimeError) as exc_info:
                await agent._run_async("test query", stream=False)
            
            assert "Missing Notion API key" in str(exc_info.value)
    
    @pytest.mark.skipif(
        (not os.getenv("NOTION_API_KEY")) or (not MCP_AVAILABLE),
        reason="Requires NOTION_API_KEY and optional `mcp` dependency for live testing"
    )
    @pytest.mark.asyncio
    async def test_run_async_successful_execution(self):
        """Test async execution completes successfully."""
        agent = NotionDocumentAgent()
        result = await agent._run_async("Search for test", stream=False)
        
        assert hasattr(result, 'content')
        assert isinstance(result.content, str)


class TestNotionAgentEnvironmentValidation:
    """Test environment setup and validation."""
    
    def test_agent_initializes_with_logger(self):
        """Test that agent initializes with proper logging."""
        agent = NotionDocumentAgent()
        
        assert agent.logger is not None
        assert agent.agent_name == "Notion Document Agent"
        assert agent.agent_key == "notion_documents"
    
    def test_agent_has_audit_logger(self):
        """Test that agent has audit logging enabled."""
        agent = NotionDocumentAgent()
        
        assert agent.audit_logger is not None
        assert hasattr(agent.audit_logger, 'log_file')


class TestNotionAgentPathHandling:
    """Test PATH environment variable handling."""
    
    def test_path_fallback_when_missing(self):
        """Test that PATH has safe fallback when missing."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {"NOTION_API_KEY": "test_key"}):
                with patch("shutil.which", return_value=None):
                    with pytest.raises(RuntimeError) as exc_info:
                        agent.run_with_grounding_check("test")
                    
                    assert "npx not found" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
