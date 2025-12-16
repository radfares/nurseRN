"""
Phase 3 Validation Tests - Synthesis & Generation Guards

Tests validation gates:
1. No synthesis with articles=None or empty results
2. One response_generated per request_id
3. synthesis_completed flag prevents re-entry
4. _extract_agent_output never returns None

Created: 2025-12-16
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.orchestration.response_synthesizer import ResponseSynthesizer
from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator, AgentTask
from src.orchestration.conversation_context import ConversationContext
from src.orchestration.request_context import RequestContext


class TestPreSynthesisGuards:
    """Test guards that prevent synthesis with invalid inputs."""

    def setup_method(self):
        """Reset synthesis tracking before each test."""
        ResponseSynthesizer.reset_synthesis_tracking()

    def test_synthesis_aborts_on_empty_results(self):
        """Synthesis should abort when results dict is empty."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]

        # Empty results
        response = synthesizer.synthesize(
            user_message="test query",
            plan=plan,
            results={},
            context=context,
            request_id="req_test123"
        )

        assert "no agent tasks were executed" in response.lower()

    def test_synthesis_aborts_on_all_failed_results(self):
        """Synthesis should abort when all results failed."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]

        # All results failed
        results = {
            "task_1": {"success": False, "error": "Test error", "agent": "test_agent", "action": "search"},
        }

        response = synthesizer.synthesize(
            user_message="test query",
            plan=plan,
            results=results,
            context=context,
            request_id="req_test456"
        )

        assert "all agent tasks failed" in response.lower() or "encountered errors" in response.lower()

    def test_synthesis_aborts_on_none_output(self):
        """Synthesis should abort when results contain None output."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]

        # Result with None output
        results = {
            "task_1": {"success": True, "output": None, "agent": "test_agent", "action": "search"},
        }

        response = synthesizer.synthesize(
            user_message="test query",
            plan=plan,
            results=results,
            context=context,
            request_id="req_test789"
        )

        assert "all agent tasks failed" in response.lower() or "no output produced" in response.lower()

    def test_synthesis_aborts_on_empty_dict_output(self):
        """Synthesis should abort when results contain empty dict output."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]

        # Result with empty dict output
        results = {
            "task_1": {"success": True, "output": {}, "agent": "test_agent", "action": "search"},
        }

        response = synthesizer.synthesize(
            user_message="test query",
            plan=plan,
            results=results,
            context=context,
            request_id="req_testabc"
        )

        assert "all agent tasks failed" in response.lower() or "no output produced" in response.lower()

    def test_synthesis_proceeds_with_valid_output(self):
        """Synthesis should proceed when at least one result has valid output."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]

        # Result with valid output
        results = {
            "task_1": {"success": True, "output": {"text": "Valid result"}, "agent": "test_agent", "action": "search"},
        }

        response = synthesizer.synthesize(
            user_message="test query",
            plan=plan,
            results=results,
            context=context,
            request_id="req_testdef"
        )

        # Should use fallback synthesis (since client=None)
        assert "here's what i found" in response.lower() or "valid result" in response.lower()


class TestSynthesisReentry:
    """Test that synthesis cannot be called multiple times for the same request_id."""

    def setup_method(self):
        """Reset synthesis tracking before each test."""
        ResponseSynthesizer.reset_synthesis_tracking()

    def test_duplicate_synthesis_prevented(self):
        """Duplicate synthesis attempts for same request_id should be blocked."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]
        results = {
            "task_1": {"success": True, "output": {"text": "Test result"}, "agent": "test_agent", "action": "search"},
        }

        request_id = "req_duplicate_test"

        # First synthesis should succeed
        response1 = synthesizer.synthesize(
            user_message="test query",
            plan=plan,
            results=results,
            context=context,
            request_id=request_id
        )

        assert "test result" in response1.lower() or "found" in response1.lower()

        # Second synthesis with same request_id should be blocked
        response2 = synthesizer.synthesize(
            user_message="test query",
            plan=plan,
            results=results,
            context=context,
            request_id=request_id
        )

        assert "already generated" in response2.lower()

    def test_different_request_ids_allowed(self):
        """Synthesis should proceed normally for different request_ids."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]
        results = {
            "task_1": {"success": True, "output": {"text": "Test result"}, "agent": "test_agent", "action": "search"},
        }

        # First request
        response1 = synthesizer.synthesize(
            user_message="test query 1",
            plan=plan,
            results=results,
            context=context,
            request_id="req_first"
        )

        # Second request with different ID
        response2 = synthesizer.synthesize(
            user_message="test query 2",
            plan=plan,
            results=results,
            context=context,
            request_id="req_second"
        )

        # Both should succeed and NOT be the "already generated" message
        assert "already generated" not in response1.lower()
        assert "already generated" not in response2.lower()

    def test_synthesis_without_request_id_always_allowed(self):
        """Synthesis without request_id should always proceed (backward compat)."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]
        results = {
            "task_1": {"success": True, "output": {"text": "Test result"}, "agent": "test_agent", "action": "search"},
        }

        # Call twice without request_id
        response1 = synthesizer.synthesize(
            user_message="test query",
            plan=plan,
            results=results,
            context=context
        )

        response2 = synthesizer.synthesize(
            user_message="test query",
            plan=plan,
            results=results,
            context=context
        )

        # Both should succeed (no tracking without request_id)
        assert "already generated" not in response1.lower()
        assert "already generated" not in response2.lower()


class TestExtractAgentOutputGuards:
    """Test that _extract_agent_output never returns None."""

    def test_extract_returns_dict_on_valid_json(self):
        """_extract_agent_output should return parsed dict for valid JSON."""
        orchestrator = IntelligentOrchestrator(client=None)

        response = '{"key": "value"}'
        output = orchestrator._extract_agent_output(response, "test_action")

        assert isinstance(output, dict)
        assert output.get("key") == "value"

    def test_extract_returns_dict_on_invalid_json(self):
        """_extract_agent_output should return dict with text on invalid JSON."""
        orchestrator = IntelligentOrchestrator(client=None)

        response = "Not JSON at all"
        output = orchestrator._extract_agent_output(response, "test_action")

        assert isinstance(output, dict)
        assert output is not None
        assert "text" in output or "error" in output

    def test_extract_handles_none_response(self):
        """_extract_agent_output should handle None input gracefully."""
        orchestrator = IntelligentOrchestrator(client=None)

        response = None
        output = orchestrator._extract_agent_output(response, "test_action")

        assert isinstance(output, dict)
        assert output is not None
        # Should contain fallback text or empty dict
        assert "text" in output or "error" in output or output == {}

    def test_extract_handles_empty_string(self):
        """_extract_agent_output should handle empty string input."""
        orchestrator = IntelligentOrchestrator(client=None)

        response = ""
        output = orchestrator._extract_agent_output(response, "test_action")

        assert isinstance(output, dict)
        assert output is not None

    def test_extract_handles_complex_object(self):
        """_extract_agent_output should handle complex response objects."""
        orchestrator = IntelligentOrchestrator(client=None)

        # Mock response object with content attribute
        mock_response = Mock()
        mock_response.content = '{"result": "success"}'
        # Ensure hasattr returns correct values
        del mock_response.model_dump
        del mock_response.dict

        output = orchestrator._extract_agent_output(mock_response, "test_action")

        assert isinstance(output, dict)
        assert output is not None
        assert output.get("result") == "success" or "text" in output


class TestOneResponsePerRequest:
    """Test that only one response is generated per request_id."""

    def setup_method(self):
        """Reset synthesis tracking before each test."""
        ResponseSynthesizer.reset_synthesis_tracking()

    @patch('src.orchestration.intelligent_orchestrator.OpenAI')
    def test_one_synthesis_per_request_id(self, mock_openai_class):
        """Verify only one synthesis occurs per request_id."""
        # Mock OpenAI client
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"tasks": [{"task_id": "task_1", "agent_name": "nursing_research", "action": "search", "params": {"query": "test"}}]}'
        mock_client.chat.completions.create.return_value = mock_response

        # Track synthesis calls
        synthesis_calls = []
        original_synthesize = ResponseSynthesizer.synthesize

        def tracked_synthesize(self, *args, **kwargs):
            synthesis_calls.append(kwargs.get('request_id'))
            return original_synthesize(self, *args, **kwargs)

        with patch.object(ResponseSynthesizer, 'synthesize', tracked_synthesize):
            with patch('src.orchestration.intelligent_orchestrator.dispatch_mcp') as mock_dispatch:
                mock_dispatch.return_value = Mock(message_type="result", content='{"text": "result"}')

                orchestrator = IntelligentOrchestrator(client=mock_client)
                context = ConversationContext()

                # Process one user message
                response, suggestions = orchestrator.process_user_message("test query", context)

                # Verify synthesis was called exactly once
                assert len(synthesis_calls) == 1
                assert synthesis_calls[0] is not None
                assert synthesis_calls[0].startswith("req_")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
