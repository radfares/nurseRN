"""
Unit Tests for Notion Document Agent

Tests core functionality, methods, and interfaces in isolation.

Created: 2025-12-20
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from agents.notion_document_agent import NotionDocumentAgent


class TestNotionAgentInitialization:
    """Test agent initialization and setup."""
    
    def test_agent_inherits_from_base_agent(self):
        """Test that NotionDocumentAgent properly inherits BaseAgent."""
        from agents.base_agent import BaseAgent
        
        agent = NotionDocumentAgent()
        assert isinstance(agent, BaseAgent)
    
    def test_agent_has_required_attributes(self):
        """Test that agent has all required attributes."""
        agent = NotionDocumentAgent()
        
        assert agent.agent_name == "Notion Document Agent"
        assert agent.agent_key == "notion_documents"
        assert hasattr(agent, 'logger')
        assert hasattr(agent, 'audit_logger')
        assert hasattr(agent, 'tools')
    
    def test_placeholder_agent_created(self):
        """Test that placeholder agent is created during init."""
        agent = NotionDocumentAgent()
        
        assert agent.agent is not None
        assert hasattr(agent.agent, 'name')


class TestNotionAgentMethods:
    """Test public methods and interfaces."""
    
    def test_create_agent_returns_placeholder(self):
        """Test that _create_agent returns valid Agent."""
        agent = NotionDocumentAgent()
        placeholder = agent._create_agent()
        
        assert placeholder is not None
        assert hasattr(placeholder, 'name')
        assert "Placeholder" in placeholder.name
    
    def test_show_usage_examples_displays_info(self, capsys):
        """Test that show_usage_examples prints helpful information."""
        agent = NotionDocumentAgent()
        agent.show_usage_examples()
        
        captured = capsys.readouterr()
        assert "Notion Document Agent" in captured.out
        assert "Search" in captured.out or "search" in captured.out
        assert "example" in captured.out.lower()
    
    def test_run_with_grounding_check_exists(self):
        """Test that run_with_grounding_check method exists."""
        agent = NotionDocumentAgent()
        
        assert hasattr(agent, 'run_with_grounding_check')
        assert callable(agent.run_with_grounding_check)
    
    def test_run_with_error_handling_exists(self):
        """Test that inherited run_with_error_handling exists."""
        agent = NotionDocumentAgent()
        
        assert hasattr(agent, 'run_with_error_handling')
        assert callable(agent.run_with_error_handling)


class TestNotionAgentAsyncMethods:
    """Test async method signatures and contracts."""
    
    def test_run_async_is_async(self):
        """Test that _run_async is an async method."""
        import inspect
        
        agent = NotionDocumentAgent()
        assert inspect.iscoroutinefunction(agent._run_async)
    
    def test_run_async_accepts_stream_parameter(self):
        """Test that _run_async accepts stream parameter."""
        import inspect
        
        agent = NotionDocumentAgent()
        sig = inspect.signature(agent._run_async)
        
        assert 'query' in sig.parameters
        assert 'stream' in sig.parameters
        assert sig.parameters['stream'].default is False


class TestNotionAgentErrorMessages:
    """Test error message content and formatting."""
    
    def test_missing_api_key_error_message_is_clear(self):
        """Test that missing API key error message is user-friendly."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
            try:
                agent.run_with_grounding_check("test")
                assert False, "Should have raised RuntimeError"
            except RuntimeError as e:
                error_msg = str(e)
                assert "NOTION_API_KEY" in error_msg
                assert "environment variable" in error_msg.lower()
    
    def test_missing_npx_error_message_is_helpful(self):
        """Test that missing npx error includes installation hint."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": "test_key"}, clear=False):
            with patch("shutil.which", return_value=None):
                try:
                    agent.run_with_grounding_check("test")
                    assert False, "Should have raised RuntimeError"
                except RuntimeError as e:
                    error_msg = str(e)
                    assert "npx" in error_msg.lower()
                    assert "Node.js" in error_msg or "npm" in error_msg


class TestNotionAgentMCPContract:
    """Test MCP protocol contract compliance."""
    
    @pytest.mark.asyncio
    async def test_run_async_with_invalid_token_raises_error(self):
        """Test that invalid token raises proper error."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
            with pytest.raises(RuntimeError):
                await agent._run_async("test", stream=False)
    
    def test_sync_wrapper_calls_asyncio_run(self):
        """Test that run_with_grounding_check properly wraps async."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
            with patch('asyncio.run') as mock_run:
                mock_run.side_effect = RuntimeError("Missing Notion API key")
                
                with pytest.raises(RuntimeError):
                    agent.run_with_grounding_check("test")
                
                assert mock_run.called


class TestNotionAgentLogging:
    """Test logging behavior."""
    
    def test_logger_logs_errors(self):
        """Test that logger captures errors."""
        agent = NotionDocumentAgent()
        
        with patch.object(agent.logger, 'error') as mock_error:
            with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
                try:
                    agent.run_with_grounding_check("test")
                except RuntimeError:
                    pass
                
                # Logger should have been called
                assert mock_error.called


class TestNotionAgentPrintResponse:
    """Test print_response method behavior."""
    
    def test_print_response_with_error_shows_friendly_message(self, capsys):
        """Test that print_response shows user-friendly error."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
            agent.print_response("test query", stream=False)
            
            captured = capsys.readouterr()
            assert "❌" in captured.out
            assert len(captured.out) > 0
    
    def test_print_response_does_not_expose_stack_traces(self, capsys):
        """Test that print_response doesn't leak stack traces to user."""
        agent = NotionDocumentAgent()
        
        with patch.dict(os.environ, {"NOTION_API_KEY": ""}, clear=False):
            agent.print_response("test query", stream=False)
            
            captured = capsys.readouterr()
            # Should not contain Python stack trace elements
            assert "Traceback" not in captured.out
            assert "File \"" not in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
