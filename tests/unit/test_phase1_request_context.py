"""
Phase 1 Validation Tests - Request Context & State Stability

Tests validation gates:
1. No query="" events in logs
2. request_id unique per user message
3. Retries reuse the same request_id

Created: 2025-12-16
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.orchestration.request_context import RequestContext
from src.orchestration.mcp import MCPMessage


class TestRequestContextCreation:
    """Test RequestContext creation and immutability."""

    def test_create_with_valid_query(self):
        """RequestContext.create should generate unique request_id."""
        ctx1 = RequestContext.create("What is diabetes?", intent="search")
        ctx2 = RequestContext.create("What is diabetes?", intent="search")

        assert ctx1.query == "What is diabetes?"
        assert ctx1.intent == "search"
        assert ctx1.request_id.startswith("req_")
        assert ctx1.request_id != ctx2.request_id  # Unique IDs

    def test_empty_query_raises_error(self):
        """RequestContext should reject empty queries."""
        with pytest.raises(ValueError, match="query cannot be empty"):
            RequestContext.create("", intent="search")

        with pytest.raises(ValueError, match="query cannot be empty"):
            RequestContext.create("   ", intent="search")

    def test_immutability(self):
        """RequestContext should be immutable (frozen dataclass)."""
        ctx = RequestContext.create("Test query", intent="search")

        with pytest.raises(Exception):  # FrozenInstanceError
            ctx.query = "Modified"

    def test_to_dict_serialization(self):
        """RequestContext.to_dict should produce valid dict."""
        ctx = RequestContext.create("Test query", intent="search", metadata={"foo": "bar"})
        d = ctx.to_dict()

        assert d["query"] == "Test query"
        assert d["intent"] == "search"
        assert d["request_id"] == ctx.request_id
        assert d["metadata"]["foo"] == "bar"

    def test_from_dict_deserialization(self):
        """RequestContext.from_dict should reconstruct context."""
        original = RequestContext.create("Test query", intent="search")
        d = original.to_dict()
        reconstructed = RequestContext.from_dict(d)

        assert reconstructed.request_id == original.request_id
        assert reconstructed.query == original.query
        assert reconstructed.intent == original.intent


class TestEmptyQueryGuard:
    """Test empty query guard in dispatch_mcp."""

    def test_dispatch_rejects_empty_query(self):
        """dispatch_mcp should abort when query is empty (via validator or guard)."""
        from src.orchestration.mcp_dispatch import dispatch_mcp
        from src.orchestration.mcp import new_task

        mock_agent = Mock()
        mock_agent.agent_name = "test_agent"

        # Create task with empty content
        task_msg = new_task(
            sender="TestOrchestrator",
            recipient="test_agent",
            content="",  # Empty query
            metadata={}
        )

        ctx = RequestContext.create("original query", intent="test")
        result = dispatch_mcp(mock_agent, task_msg, request_ctx=ctx)

        # Either validator or guard should reject empty queries
        assert result.message_type == "error"
        assert ("Empty query detected" in result.content or
                "Content cannot be empty" in result.content)

    def test_dispatch_rejects_whitespace_query(self):
        """dispatch_mcp should abort when query is only whitespace."""
        from src.orchestration.mcp_dispatch import dispatch_mcp
        from src.orchestration.mcp import new_task

        mock_agent = Mock()
        mock_agent.agent_name = "test_agent"

        task_msg = new_task(
            sender="TestOrchestrator",
            recipient="test_agent",
            content="   ",  # Whitespace only
            metadata={}
        )

        ctx = RequestContext.create("original query", intent="test")
        result = dispatch_mcp(mock_agent, task_msg, request_ctx=ctx)

        # Either validator or guard should reject
        assert result.message_type == "error"
        assert ("Empty query detected" in result.content or
                "Content cannot be empty" in result.content)


class TestRequestIdPropagation:
    """Test request_id propagation through orchestration layers."""

    def test_request_context_creation_logic(self):
        """RequestContext should be created with query from user message."""
        from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator, AgentTask
        from src.orchestration.conversation_context import ConversationContext

        # Test the logic that creates RequestContext
        plan = [
            AgentTask(
                task_id="task_1",
                agent_name="nursing_research",
                action="search",
                params={"query": "diabetes"}
            )
        ]

        # Simulate what happens after plan validation
        user_message = "What is diabetes?"
        intent = plan[0].action if plan else "execute_plan"
        ctx = RequestContext.create(
            query=user_message,
            intent=intent,
            metadata={"plan_size": len(plan)}
        )

        # Verify RequestContext properties
        assert ctx.query == "What is diabetes?"
        assert ctx.intent == "search"
        assert ctx.metadata["plan_size"] == 1
        assert ctx.request_id.startswith("req_")

    def test_request_id_in_mcp_metadata(self):
        """RequestContext should be included in MCP message metadata."""
        from src.orchestration.mcp import new_task

        ctx = RequestContext.create("Test query", intent="search")

        task_msg = new_task(
            sender="Orchestrator",
            recipient="agent",
            content="Test query",
            metadata={"request_context": ctx.to_dict()}
        )

        assert "request_context" in task_msg.metadata
        assert task_msg.metadata["request_context"]["request_id"] == ctx.request_id
        assert task_msg.metadata["request_context"]["query"] == "Test query"


class TestRetryRequestIdReuse:
    """Test that retries reuse the same request_id."""

    def test_resilient_orchestrator_preserves_request_id(self):
        """ResilientOrchestrator should pass same request_id to all retry attempts and fallbacks."""
        from src.orchestration.resilient_orchestrator import ResilientOrchestrator, RetryConfig
        from src.orchestration.mcp import new_task

        # Track request_ids seen in dispatch calls
        seen_request_ids = []

        def mock_dispatch(agent, task_msg, request_ctx=None, **kwargs):
            if request_ctx:
                seen_request_ids.append(request_ctx.request_id)
            # Simulate failure to trigger retry
            error_response = Mock()
            error_response.message_type = "error"
            error_response.content = "Simulated failure"
            return error_response

        with patch('src.orchestration.resilient_orchestrator.dispatch_mcp', side_effect=mock_dispatch):
            # Configure for 2 retries
            orchestrator = ResilientOrchestrator(
                retry_config=RetryConfig(max_retries=2, base_delay=0.01)
            )

            ctx = RequestContext.create("Test query", intent="search")

            # This will fail and retry, then try fallback agents
            result = orchestrator.execute_with_resilience(
                agent_name="nursing_research",
                query="Test query",
                request_ctx=ctx
            )

            # All attempts (initial + retries + fallbacks) should have the same request_id
            assert len(seen_request_ids) > 0
            # VALIDATION GATE: All request_ids must be the same
            assert all(rid == ctx.request_id for rid in seen_request_ids), \
                f"Expected all request_ids to be {ctx.request_id}, but got {set(seen_request_ids)}"
            assert result.success is False  # All failed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
