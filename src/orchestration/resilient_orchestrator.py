"""
Resilient Orchestrator
Provides retry logic, fallback agents, and graceful degradation for agent execution.

Created: 2025-12-14
Features:
- Exponential backoff retry (1s, 2s, 4s, 8s...)
- Predefined fallback agent map
- Capability-based fallback matching
- Graceful degradation with partial results
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.orchestration.mcp import MCPMessage, new_task
from src.orchestration.mcp_dispatch import dispatch_mcp
from src.orchestration.mcp_validator import MCPMessageValidator

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 30.0  # seconds
    exponential_base: float = 2.0

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt using exponential backoff."""
        delay = self.base_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


# Predefined fallback map: agent -> list of fallback agents in priority order
FALLBACK_MAP: Dict[str, List[str]] = {
    "document_synthesis": ["nursing_research", "academic_research"],
    "medical_research": ["nursing_research", "academic_research"],
    "nursing_research": ["medical_research", "academic_research"],
    "academic_research": ["nursing_research", "research_writing"],
    "data_analysis": ["academic_research", "nursing_research"],
    "research_writing": ["academic_research", "nursing_research"],
    "project_timeline": ["nursing_research", "research_writing"],
    "citation_validation": ["medical_research", "academic_research"],
}

# Agent capabilities for capability-based fallback matching
AGENT_CAPABILITIES: Dict[str, List[str]] = {
    "nursing_research": ["search", "literature", "clinical", "pubmed", "research"],
    "medical_research": ["search", "literature", "synthesis", "pubmed", "clinical"],
    "document_synthesis": ["synthesis", "comparison", "themes", "analysis"],
    "academic_research": ["search", "literature", "arxiv", "scholarly", "academic"],
    "data_analysis": ["statistics", "analysis", "visualization", "data"],
    "research_writing": ["writing", "apa", "formatting", "documentation"],
    "project_timeline": ["planning", "timeline", "gantt", "scheduling"],
    "citation_validation": ["validation", "retraction", "quality", "citations"],
}


# =============================================================================
# RESULT DATA STRUCTURES
# =============================================================================

@dataclass
class ExecutionResult:
    """Result of resilient agent execution."""
    success: bool
    content: Optional[str] = None
    agent_used: str = ""
    original_agent: str = ""
    fallback_used: bool = False
    retries_attempted: int = 0
    total_attempts: int = 0
    partial_results: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    execution_time_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "content": self.content,
            "agent_used": self.agent_used,
            "original_agent": self.original_agent,
            "fallback_used": self.fallback_used,
            "retries_attempted": self.retries_attempted,
            "total_attempts": self.total_attempts,
            "partial_results": self.partial_results,
            "errors": self.errors,
            "execution_time_ms": self.execution_time_ms,
            "metadata": self.metadata,
        }


# =============================================================================
# RESILIENT ORCHESTRATOR
# =============================================================================

class ResilientOrchestrator:
    """
    Orchestrator with retry logic, fallback agents, and graceful degradation.

    Features:
    - Exponential backoff retry (configurable)
    - Predefined fallback agent map
    - Capability-based fallback as last resort
    - Partial results on graceful degradation
    - Full audit trail of attempts

    Example:
        orchestrator = ResilientOrchestrator()
        result = orchestrator.execute_with_resilience(
            agent_name="medical_research",
            query="Find articles about fall prevention"
        )
        if result.success:
            print(result.content)
        else:
            print(f"Failed after {result.total_attempts} attempts")
            print(f"Errors: {result.errors}")
    """

    def __init__(
        self,
        retry_config: Optional[RetryConfig] = None,
        fallback_map: Optional[Dict[str, List[str]]] = None,
        agent_capabilities: Optional[Dict[str, List[str]]] = None,
        enable_partial_results: bool = True,
        validate_messages: bool = True,
    ):
        """
        Initialize resilient orchestrator.

        Args:
            retry_config: Configuration for retry behavior
            fallback_map: Map of agent -> fallback agents
            agent_capabilities: Map of agent -> capabilities for matching
            enable_partial_results: If True, collect partial results on failure
            validate_messages: If True, validate MCP messages before dispatch
        """
        self.retry_config = retry_config or RetryConfig()
        self.fallback_map = fallback_map or FALLBACK_MAP
        self.agent_capabilities = agent_capabilities or AGENT_CAPABILITIES
        self.enable_partial_results = enable_partial_results
        self.validate_messages = validate_messages

        # Initialize validator
        self.validator = MCPMessageValidator() if validate_messages else None

        # Lazy-load agent registry
        self._registry = None

        logger.info(
            f"ResilientOrchestrator initialized: "
            f"max_retries={self.retry_config.max_retries}, "
            f"fallback_agents={len(self.fallback_map)}"
        )

    @property
    def registry(self):
        """Lazy-load agent registry."""
        if self._registry is None:
            try:
                from src.orchestration.agent_registry import AgentRegistry
                self._registry = AgentRegistry()
            except ImportError:
                logger.warning("AgentRegistry not available")
                self._registry = None
        return self._registry

    def execute_with_resilience(
        self,
        agent_name: str,
        query: str,
        metadata: Optional[Dict[str, Any]] = None,
        required_capabilities: Optional[List[str]] = None,
    ) -> ExecutionResult:
        """
        Execute agent with retry and fallback logic.

        Flow:
        1. Try primary agent with retries (exponential backoff)
        2. If primary fails, try predefined fallback agents
        3. If predefined fallbacks fail, try capability-matched agents
        4. Return partial results if all fail (graceful degradation)

        Args:
            agent_name: Primary agent to execute
            query: Query to send to agent
            metadata: Optional metadata for MCP message
            required_capabilities: Capabilities needed for fallback matching

        Returns:
            ExecutionResult with success status, content, and audit trail
        """
        start_time = time.time()
        result = ExecutionResult(
            success=False,
            original_agent=agent_name,
            agent_used=agent_name,
        )

        # Build list of agents to try: primary + fallbacks
        agents_to_try = self._get_agents_to_try(agent_name, required_capabilities)
        tried_agents: List[str] = []

        for agent in agents_to_try:
            if agent in tried_agents:
                continue
            tried_agents.append(agent)

            is_fallback = agent != agent_name
            if is_fallback:
                logger.info(f"Trying fallback agent: {agent}")

            # Try agent with retries
            success, content, error = self._execute_with_retries(
                agent_name=agent,
                query=query,
                metadata=metadata,
                result=result,
            )

            if success:
                result.success = True
                result.content = content
                result.agent_used = agent
                result.fallback_used = is_fallback
                break
            else:
                result.errors.append(f"{agent}: {error}")
                if self.enable_partial_results and content:
                    result.partial_results.append({
                        "agent": agent,
                        "content": content,
                        "error": error,
                    })

        result.total_attempts = len(tried_agents)
        result.execution_time_ms = int((time.time() - start_time) * 1000)
        result.metadata["agents_tried"] = tried_agents

        if result.success:
            logger.info(
                f"Execution succeeded: agent={result.agent_used}, "
                f"fallback={result.fallback_used}, "
                f"retries={result.retries_attempted}"
            )
        else:
            logger.warning(
                f"Execution failed after {result.total_attempts} agents: "
                f"errors={result.errors}"
            )

        return result

    def _get_agents_to_try(
        self,
        primary_agent: str,
        required_capabilities: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Build ordered list of agents to try.

        Order:
        1. Primary agent
        2. Predefined fallbacks from map
        3. Capability-matched agents (if capabilities provided)
        """
        agents = [primary_agent]

        # Add predefined fallbacks
        if primary_agent in self.fallback_map:
            for fallback in self.fallback_map[primary_agent]:
                if fallback not in agents:
                    agents.append(fallback)

        # Add capability-matched agents
        if required_capabilities:
            capable_agents = self._find_capable_agents(
                capabilities=required_capabilities,
                exclude=agents,
            )
            agents.extend(capable_agents)

        return agents

    def _find_capable_agents(
        self,
        capabilities: List[str],
        exclude: List[str],
    ) -> List[str]:
        """Find agents with matching capabilities, sorted by match score."""
        scored_agents = []

        for agent, agent_caps in self.agent_capabilities.items():
            if agent in exclude:
                continue

            # Count matching capabilities
            matches = sum(1 for cap in capabilities if cap in agent_caps)
            if matches > 0:
                scored_agents.append((agent, matches))

        # Sort by match score (descending)
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return [agent for agent, _ in scored_agents]

    def _execute_with_retries(
        self,
        agent_name: str,
        query: str,
        metadata: Optional[Dict[str, Any]],
        result: ExecutionResult,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Execute agent with exponential backoff retries.

        Returns:
            Tuple of (success, content, error_message)
        """
        last_error = None

        for attempt in range(self.retry_config.max_retries + 1):
            if attempt > 0:
                delay = self.retry_config.get_delay(attempt - 1)
                logger.info(f"Retry {attempt}/{self.retry_config.max_retries} for {agent_name} after {delay}s")
                time.sleep(delay)
                result.retries_attempted += 1

            try:
                success, content, error = self._attempt_execution(
                    agent_name=agent_name,
                    query=query,
                    metadata=metadata,
                )

                if success:
                    return True, content, None
                else:
                    last_error = error
                    logger.warning(f"Attempt {attempt + 1} failed for {agent_name}: {error}")

            except Exception as e:
                last_error = str(e)
                logger.error(f"Exception on attempt {attempt + 1} for {agent_name}: {e}")

        return False, None, last_error

    def _attempt_execution(
        self,
        agent_name: str,
        query: str,
        metadata: Optional[Dict[str, Any]],
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Single execution attempt via MCP dispatch.

        Returns:
            Tuple of (success, content, error_message)
        """
        try:
            # Create MCP message
            mcp_message = new_task(
                sender="ResilientOrchestrator",
                recipient=agent_name,
                content=query,
                metadata=metadata or {},
            )

            # Validate message if enabled
            if self.validator:
                validation = self.validator.validate(mcp_message)
                if not validation.valid:
                    error_msg = validation.error_summary()
                    return False, None, f"Validation failed: {error_msg}"
                # Use sanitized message
                if validation.sanitized_message:
                    mcp_message = validation.sanitized_message

            # Dispatch to agent
            response = dispatch_mcp(mcp_message)

            # Check response
            if response.message_type == "error":
                return False, response.content, f"Agent error: {response.content}"

            if response.message_type == "result":
                return True, response.content, None

            return False, None, f"Unexpected message type: {response.message_type}"

        except Exception as e:
            logger.exception(f"Execution error for {agent_name}")
            return False, None, str(e)

    def get_fallback_agents(self, agent_name: str) -> List[str]:
        """Get list of fallback agents for a given agent."""
        return self.fallback_map.get(agent_name, []).copy()

    def get_agent_capabilities(self, agent_name: str) -> List[str]:
        """Get capabilities for a given agent."""
        return self.agent_capabilities.get(agent_name, []).copy()


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_default_orchestrator: Optional[ResilientOrchestrator] = None


def get_resilient_orchestrator() -> ResilientOrchestrator:
    """Get or create default ResilientOrchestrator instance."""
    global _default_orchestrator
    if _default_orchestrator is None:
        _default_orchestrator = ResilientOrchestrator()
    return _default_orchestrator


def execute_with_resilience(
    agent_name: str,
    query: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> ExecutionResult:
    """
    Convenience function to execute with resilience using default orchestrator.

    Args:
        agent_name: Agent to execute
        query: Query to send
        metadata: Optional metadata

    Returns:
        ExecutionResult
    """
    orchestrator = get_resilient_orchestrator()
    return orchestrator.execute_with_resilience(
        agent_name=agent_name,
        query=query,
        metadata=metadata,
    )
