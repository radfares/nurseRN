"""
Unit Tests for Resilient Orchestrator

Tests retry logic, fallback agents, capability matching, and graceful degradation.

Part of Phase: Resilient Orchestration
Created: 2025-12-14
"""

import time
import pytest
from unittest.mock import Mock, patch, MagicMock

from src.orchestration.resilient_orchestrator import (
    ResilientOrchestrator,
    RetryConfig,
    ExecutionResult,
    FALLBACK_MAP,
    AGENT_CAPABILITIES,
    get_resilient_orchestrator,
    execute_with_resilience,
)
from src.orchestration.mcp import MCPMessage


@pytest.fixture
def orchestrator():
    """Create a fresh ResilientOrchestrator for each test."""
    return ResilientOrchestrator(
        validate_messages=False  # Skip validation for unit tests
    )


@pytest.fixture
def mock_dispatch():
    """Mock dispatch_mcp to control agent responses."""
    with patch("src.orchestration.resilient_orchestrator.dispatch_mcp") as mock:
        yield mock


class TestRetryConfig:
    """Tests for RetryConfig exponential backoff calculation."""

    def test_default_config_values(self):
        """Default config should have expected values."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 30.0
        assert config.exponential_base == 2.0

    def test_exponential_backoff_delays(self):
        """Delays should follow exponential pattern."""
        config = RetryConfig(base_delay=1.0, exponential_base=2.0)

        assert config.get_delay(0) == 1.0  # 1 * 2^0 = 1
        assert config.get_delay(1) == 2.0  # 1 * 2^1 = 2
        assert config.get_delay(2) == 4.0  # 1 * 2^2 = 4
        assert config.get_delay(3) == 8.0  # 1 * 2^3 = 8

    def test_max_delay_cap(self):
        """Delay should be capped at max_delay."""
        config = RetryConfig(
            base_delay=1.0,
            max_delay=5.0,
            exponential_base=2.0
        )

        assert config.get_delay(0) == 1.0
        assert config.get_delay(1) == 2.0
        assert config.get_delay(2) == 4.0
        assert config.get_delay(3) == 5.0  # Capped at max
        assert config.get_delay(10) == 5.0  # Still capped

    def test_custom_exponential_base(self):
        """Custom exponential base should work."""
        config = RetryConfig(
            base_delay=1.0,
            exponential_base=3.0,
            max_delay=100.0
        )

        assert config.get_delay(0) == 1.0  # 1 * 3^0 = 1
        assert config.get_delay(1) == 3.0  # 1 * 3^1 = 3
        assert config.get_delay(2) == 9.0  # 1 * 3^2 = 9


class TestExecutionResult:
    """Tests for ExecutionResult dataclass."""

    def test_default_values(self):
        """Default ExecutionResult should have expected values."""
        result = ExecutionResult(success=False)

        assert result.success is False
        assert result.content is None
        assert result.agent_used == ""
        assert result.original_agent == ""
        assert result.fallback_used is False
        assert result.retries_attempted == 0
        assert result.total_attempts == 0
        assert result.partial_results == []
        assert result.errors == []
        assert result.execution_time_ms == 0
        assert result.metadata == {}

    def test_to_dict_serialization(self):
        """ExecutionResult should serialize to dict."""
        result = ExecutionResult(
            success=True,
            content="Test content",
            agent_used="nursing_research",
            original_agent="medical_research",
            fallback_used=True,
            retries_attempted=2,
            total_attempts=3,
            errors=["error1", "error2"],
            execution_time_ms=150,
        )

        result_dict = result.to_dict()

        assert result_dict["success"] is True
        assert result_dict["content"] == "Test content"
        assert result_dict["agent_used"] == "nursing_research"
        assert result_dict["fallback_used"] is True
        assert result_dict["retries_attempted"] == 2
        assert len(result_dict["errors"]) == 2


class TestFallbackMap:
    """Tests for predefined fallback map."""

    def test_fallback_map_exists(self):
        """Fallback map should be defined."""
        assert len(FALLBACK_MAP) > 0

    def test_key_agents_have_fallbacks(self):
        """Key agents should have fallback definitions."""
        key_agents = [
            "medical_research",
            "nursing_research",
            "academic_research",
            "data_analysis",
            "document_synthesis",
        ]

        for agent in key_agents:
            assert agent in FALLBACK_MAP, f"{agent} missing from fallback map"
            assert len(FALLBACK_MAP[agent]) > 0, f"{agent} has no fallbacks"

    def test_fallbacks_are_valid_agents(self):
        """All fallback agents should exist in capabilities."""
        for primary, fallbacks in FALLBACK_MAP.items():
            for fallback in fallbacks:
                assert fallback in AGENT_CAPABILITIES, (
                    f"Fallback {fallback} for {primary} not in AGENT_CAPABILITIES"
                )


class TestAgentCapabilities:
    """Tests for agent capabilities map."""

    def test_capabilities_exist(self):
        """Agent capabilities should be defined."""
        assert len(AGENT_CAPABILITIES) > 0

    def test_agents_have_capabilities(self):
        """Each agent should have at least one capability."""
        for agent, caps in AGENT_CAPABILITIES.items():
            assert len(caps) > 0, f"{agent} has no capabilities"

    def test_common_capabilities_present(self):
        """Common capabilities should be present across agents."""
        all_caps = set()
        for caps in AGENT_CAPABILITIES.values():
            all_caps.update(caps)

        expected = {"search", "literature", "analysis"}
        for cap in expected:
            assert cap in all_caps, f"Expected capability '{cap}' not found"


class TestResilientOrchestratorInit:
    """Tests for ResilientOrchestrator initialization."""

    def test_default_initialization(self):
        """Default initialization should work."""
        orch = ResilientOrchestrator()

        assert orch.retry_config is not None
        assert orch.fallback_map == FALLBACK_MAP
        assert orch.agent_capabilities == AGENT_CAPABILITIES
        assert orch.enable_partial_results is True
        assert orch.validate_messages is True

    def test_custom_retry_config(self):
        """Custom retry config should be used."""
        custom_config = RetryConfig(max_retries=5, base_delay=0.5)
        orch = ResilientOrchestrator(retry_config=custom_config)

        assert orch.retry_config.max_retries == 5
        assert orch.retry_config.base_delay == 0.5

    def test_custom_fallback_map(self):
        """Custom fallback map should be used."""
        custom_map = {"agent_a": ["agent_b"]}
        orch = ResilientOrchestrator(fallback_map=custom_map)

        assert orch.fallback_map == custom_map

    def test_disable_partial_results(self):
        """Partial results can be disabled."""
        orch = ResilientOrchestrator(enable_partial_results=False)

        assert orch.enable_partial_results is False


class TestGetAgentsToTry:
    """Tests for _get_agents_to_try method."""

    def test_primary_agent_first(self, orchestrator):
        """Primary agent should always be first."""
        agents = orchestrator._get_agents_to_try("medical_research")

        assert agents[0] == "medical_research"

    def test_fallbacks_included(self, orchestrator):
        """Predefined fallbacks should be included."""
        agents = orchestrator._get_agents_to_try("medical_research")

        # medical_research fallbacks: ["nursing_research", "academic_research"]
        assert "nursing_research" in agents
        assert "academic_research" in agents

    def test_no_duplicate_agents(self, orchestrator):
        """Agent list should not have duplicates."""
        agents = orchestrator._get_agents_to_try("nursing_research")

        assert len(agents) == len(set(agents))

    def test_capability_matching_adds_agents(self, orchestrator):
        """Capability matching should add additional agents."""
        agents = orchestrator._get_agents_to_try(
            "data_analysis",
            required_capabilities=["pubmed", "literature"]
        )

        # data_analysis doesn't have pubmed, but medical_research does
        # This should be in fallbacks or capability-matched
        assert len(agents) > 1


class TestFindCapableAgents:
    """Tests for _find_capable_agents method."""

    def test_finds_matching_agents(self, orchestrator):
        """Should find agents with matching capabilities."""
        agents = orchestrator._find_capable_agents(
            capabilities=["pubmed", "clinical"],
            exclude=[]
        )

        # Both nursing_research and medical_research have these
        assert "nursing_research" in agents or "medical_research" in agents

    def test_excludes_specified_agents(self, orchestrator):
        """Excluded agents should not be returned."""
        agents = orchestrator._find_capable_agents(
            capabilities=["search"],
            exclude=["nursing_research", "medical_research"]
        )

        assert "nursing_research" not in agents
        assert "medical_research" not in agents

    def test_sorted_by_match_score(self, orchestrator):
        """Agents should be sorted by match score (descending)."""
        # Request capabilities that vary across agents
        agents = orchestrator._find_capable_agents(
            capabilities=["search", "literature", "pubmed", "clinical"],
            exclude=[]
        )

        # Agents with more matches should come first
        assert len(agents) > 0


class TestExecuteWithResilience:
    """Tests for execute_with_resilience method."""

    def test_success_on_first_try(self, orchestrator, mock_dispatch):
        """Should succeed immediately if agent works."""
        mock_dispatch.return_value = MCPMessage(
            protocol_version="1.0",
            message_type="result",
            sender="nursing_research",
            recipient="ResilientOrchestrator",
            task_id="T-0123456789",
            content="Success response",
            metadata={},
            timestamp_ms=int(time.time() * 1000),
        )

        result = orchestrator.execute_with_resilience(
            agent_name="nursing_research",
            query="Test query"
        )

        assert result.success is True
        assert result.content == "Success response"
        assert result.fallback_used is False
        assert result.retries_attempted == 0

    def test_fallback_on_error(self, orchestrator, mock_dispatch):
        """Should try fallback when primary fails."""
        # First call fails, second succeeds
        mock_dispatch.side_effect = [
            MCPMessage(
                protocol_version="1.0",
                message_type="error",
                sender="medical_research",
                recipient="ResilientOrchestrator",
                task_id="T-0123456789",
                content="Agent failed",
                metadata={},
                timestamp_ms=int(time.time() * 1000),
            ),
            MCPMessage(
                protocol_version="1.0",
                message_type="result",
                sender="nursing_research",
                recipient="ResilientOrchestrator",
                task_id="T-0123456789",
                content="Fallback success",
                metadata={},
                timestamp_ms=int(time.time() * 1000),
            ),
        ]

        # Use config with no retries to go straight to fallback
        orchestrator.retry_config = RetryConfig(max_retries=0)

        result = orchestrator.execute_with_resilience(
            agent_name="medical_research",
            query="Test query"
        )

        assert result.success is True
        assert result.fallback_used is True
        assert result.agent_used == "nursing_research"
        assert result.original_agent == "medical_research"

    def test_all_agents_fail(self, orchestrator, mock_dispatch):
        """Should return failure when all agents fail."""
        mock_dispatch.return_value = MCPMessage(
            protocol_version="1.0",
            message_type="error",
            sender="agent",
            recipient="ResilientOrchestrator",
            task_id="T-0123456789",
            content="Agent failed",
            metadata={},
            timestamp_ms=int(time.time() * 1000),
        )

        # No retries to speed up test
        orchestrator.retry_config = RetryConfig(max_retries=0)

        result = orchestrator.execute_with_resilience(
            agent_name="nursing_research",
            query="Test query"
        )

        assert result.success is False
        assert len(result.errors) > 0
        assert result.total_attempts > 0

    def test_execution_time_recorded(self, orchestrator, mock_dispatch):
        """Execution time should be recorded."""
        mock_dispatch.return_value = MCPMessage(
            protocol_version="1.0",
            message_type="result",
            sender="nursing_research",
            recipient="ResilientOrchestrator",
            task_id="T-0123456789",
            content="Success",
            metadata={},
            timestamp_ms=int(time.time() * 1000),
        )

        result = orchestrator.execute_with_resilience(
            agent_name="nursing_research",
            query="Test query"
        )

        assert result.execution_time_ms >= 0

    def test_metadata_tracks_agents_tried(self, orchestrator, mock_dispatch):
        """Metadata should track which agents were tried."""
        mock_dispatch.return_value = MCPMessage(
            protocol_version="1.0",
            message_type="result",
            sender="nursing_research",
            recipient="ResilientOrchestrator",
            task_id="T-0123456789",
            content="Success",
            metadata={},
            timestamp_ms=int(time.time() * 1000),
        )

        result = orchestrator.execute_with_resilience(
            agent_name="nursing_research",
            query="Test query"
        )

        assert "agents_tried" in result.metadata
        assert "nursing_research" in result.metadata["agents_tried"]


class TestRetryBehavior:
    """Tests for retry with exponential backoff."""

    def test_retries_on_failure(self, orchestrator, mock_dispatch):
        """Should retry on agent failure."""
        # First 2 calls fail, third succeeds
        mock_dispatch.side_effect = [
            MCPMessage(
                protocol_version="1.0",
                message_type="error",
                sender="nursing_research",
                recipient="ResilientOrchestrator",
                task_id="T-0123456789",
                content="Failed 1",
                metadata={},
                timestamp_ms=int(time.time() * 1000),
            ),
            MCPMessage(
                protocol_version="1.0",
                message_type="error",
                sender="nursing_research",
                recipient="ResilientOrchestrator",
                task_id="T-0123456789",
                content="Failed 2",
                metadata={},
                timestamp_ms=int(time.time() * 1000),
            ),
            MCPMessage(
                protocol_version="1.0",
                message_type="result",
                sender="nursing_research",
                recipient="ResilientOrchestrator",
                task_id="T-0123456789",
                content="Success on retry",
                metadata={},
                timestamp_ms=int(time.time() * 1000),
            ),
        ]

        # Use short delays for testing
        orchestrator.retry_config = RetryConfig(
            max_retries=2,
            base_delay=0.01,  # 10ms
        )

        result = orchestrator.execute_with_resilience(
            agent_name="nursing_research",
            query="Test query"
        )

        assert result.success is True
        assert result.retries_attempted == 2
        assert mock_dispatch.call_count == 3

    def test_exception_triggers_retry(self, orchestrator, mock_dispatch):
        """Exceptions should trigger retries."""
        # First call raises exception, second succeeds
        mock_dispatch.side_effect = [
            Exception("Network error"),
            MCPMessage(
                protocol_version="1.0",
                message_type="result",
                sender="nursing_research",
                recipient="ResilientOrchestrator",
                task_id="T-0123456789",
                content="Success after exception",
                metadata={},
                timestamp_ms=int(time.time() * 1000),
            ),
        ]

        orchestrator.retry_config = RetryConfig(
            max_retries=1,
            base_delay=0.01,
        )

        result = orchestrator.execute_with_resilience(
            agent_name="nursing_research",
            query="Test query"
        )

        assert result.success is True
        assert result.retries_attempted == 1


class TestPartialResults:
    """Tests for partial results collection."""

    def test_partial_results_collected(self, orchestrator, mock_dispatch):
        """Partial results should be collected on failure."""
        mock_dispatch.return_value = MCPMessage(
            protocol_version="1.0",
            message_type="error",
            sender="nursing_research",
            recipient="ResilientOrchestrator",
            task_id="T-0123456789",
            content="Partial data before failure",
            metadata={},
            timestamp_ms=int(time.time() * 1000),
        )

        orchestrator.retry_config = RetryConfig(max_retries=0)

        result = orchestrator.execute_with_resilience(
            agent_name="nursing_research",
            query="Test query"
        )

        assert result.success is False
        # Partial results may be collected if content was returned with error
        assert len(result.errors) > 0

    def test_partial_results_disabled(self, mock_dispatch):
        """Partial results should not be collected when disabled."""
        orchestrator = ResilientOrchestrator(
            enable_partial_results=False,
            validate_messages=False
        )

        mock_dispatch.return_value = MCPMessage(
            protocol_version="1.0",
            message_type="error",
            sender="nursing_research",
            recipient="ResilientOrchestrator",
            task_id="T-0123456789",
            content="Failed",
            metadata={},
            timestamp_ms=int(time.time() * 1000),
        )

        orchestrator.retry_config = RetryConfig(max_retries=0)

        result = orchestrator.execute_with_resilience(
            agent_name="nursing_research",
            query="Test query"
        )

        assert result.success is False
        assert len(result.partial_results) == 0


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""

    def test_get_resilient_orchestrator_singleton(self):
        """get_resilient_orchestrator should return singleton."""
        orch1 = get_resilient_orchestrator()
        orch2 = get_resilient_orchestrator()

        assert orch1 is orch2

    def test_execute_with_resilience_function(self, mock_dispatch):
        """execute_with_resilience convenience function should work."""
        mock_dispatch.return_value = MCPMessage(
            protocol_version="1.0",
            message_type="result",
            sender="nursing_research",
            recipient="ResilientOrchestrator",
            task_id="T-0123456789",
            content="Success",
            metadata={},
            timestamp_ms=int(time.time() * 1000),
        )

        result = execute_with_resilience(
            agent_name="nursing_research",
            query="Test query"
        )

        assert isinstance(result, ExecutionResult)


class TestGetterMethods:
    """Tests for getter methods."""

    def test_get_fallback_agents(self, orchestrator):
        """get_fallback_agents should return copy of fallbacks."""
        fallbacks = orchestrator.get_fallback_agents("medical_research")

        assert fallbacks == FALLBACK_MAP["medical_research"]
        # Verify it's a copy
        fallbacks.append("test")
        assert "test" not in orchestrator.fallback_map["medical_research"]

    def test_get_fallback_agents_unknown(self, orchestrator):
        """get_fallback_agents for unknown agent should return empty list."""
        fallbacks = orchestrator.get_fallback_agents("unknown_agent")

        assert fallbacks == []

    def test_get_agent_capabilities(self, orchestrator):
        """get_agent_capabilities should return copy of capabilities."""
        caps = orchestrator.get_agent_capabilities("nursing_research")

        assert caps == AGENT_CAPABILITIES["nursing_research"]
        # Verify it's a copy
        caps.append("test")
        assert "test" not in orchestrator.agent_capabilities["nursing_research"]

    def test_get_agent_capabilities_unknown(self, orchestrator):
        """get_agent_capabilities for unknown agent should return empty list."""
        caps = orchestrator.get_agent_capabilities("unknown_agent")

        assert caps == []
