"""
Agent Registry - Centralized agent access pattern.

Provides a unified interface to get any agent by name.
All agents are accessed via factory functions for consistent behavior.

Created: 2025-12-11
"""

import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# Lazy import functions to avoid circular imports and defer initialization
def _get_nursing_research():
    from agents.nursing_research_agent import get_nursing_research_agent
    return get_nursing_research_agent()


def _get_medical_research():
    from agents.medical_research_agent import get_medical_research_agent
    return get_medical_research_agent()


def _get_academic_research():
    from agents.academic_research_agent import get_academic_research_agent
    return get_academic_research_agent()


def _get_research_writing():
    from agents.research_writing_agent import get_research_writing_agent
    return get_research_writing_agent()


def _get_project_timeline():
    from agents.nursing_project_timeline_agent import get_project_timeline_agent
    return get_project_timeline_agent()


def _get_data_analysis():
    from agents.data_analysis_agent import get_data_analysis_agent
    return get_data_analysis_agent()


def _get_citation_validation():
    from agents.citation_validation_agent import get_citation_validation_agent
    return get_citation_validation_agent()


# Registry mapping agent names to their factory functions
_AGENT_FACTORIES: Dict[str, Callable[[], Any]] = {
    'nursing_research': _get_nursing_research,
    'medical_research': _get_medical_research,
    'academic_research': _get_academic_research,
    'research_writing': _get_research_writing,
    'project_timeline': _get_project_timeline,
    'data_analysis': _get_data_analysis,
    'citation_validation': _get_citation_validation,
    # Aliases for flexibility
    'nursing': _get_nursing_research,
    'medical': _get_medical_research,
    'academic': _get_academic_research,
    'writing': _get_research_writing,
    'timeline': _get_project_timeline,
    'data': _get_data_analysis,
    'citation': _get_citation_validation,
}


class AgentRegistry:
    """
    Class-based registry for agent access.

    Provides caching and a consistent interface for the orchestrator.
    """

    def __init__(self):
        """Initialize registry with empty cache."""
        self._cache: Dict[str, Any] = {}
        self._factories = _AGENT_FACTORIES

    def get_agent(self, agent_name: str, cached: bool = True) -> Any:
        """
        Get an agent by name.

        Args:
            agent_name: Agent identifier (e.g., 'nursing_research' or 'nursing')
            cached: If True (default), reuse existing instance

        Returns:
            Agent wrapper instance (BaseAgent subclass)

        Raises:
            ValueError: If agent_name not recognized
            RuntimeError: If agent fails to initialize
        """
        # Normalize name
        normalized = agent_name.lower().strip()

        if normalized not in self._factories:
            available = ', '.join(sorted(set(
                k for k in self._factories.keys()
                if '_' in k  # Only show full names, not aliases
            )))
            raise ValueError(f"Unknown agent: '{agent_name}'. Available: {available}")

        if cached and normalized in self._cache:
            return self._cache[normalized]

        try:
            agent = self._factories[normalized]()
        except Exception as e:
            logger.error(f"Failed to initialize agent '{agent_name}': {e}")
            raise RuntimeError(f"Agent '{agent_name}' failed to initialize: {e}")

        if agent is None:
            raise RuntimeError(f"Agent '{agent_name}' returned None")

        if cached:
            self._cache[normalized] = agent

        return agent

    def list_agents(self) -> List[str]:
        """Return list of available agent names (full names only)."""
        return sorted(k for k in self._factories.keys() if '_' in k)

    def clear_cache(self) -> None:
        """Clear the agent cache."""
        self._cache.clear()

    def is_available(self, agent_name: str) -> bool:
        """Check if an agent name is valid."""
        return agent_name.lower().strip() in self._factories


# Module-level functions for backward compatibility
_default_registry = None


def _get_default_registry() -> AgentRegistry:
    """Get or create the default registry singleton."""
    global _default_registry
    if _default_registry is None:
        _default_registry = AgentRegistry()
    return _default_registry


def get_agent(agent_name: str, cached: bool = True) -> Any:
    """
    Get an agent by name (module-level function).

    Args:
        agent_name: One of the registered agent names:
            - nursing_research (or 'nursing')
            - medical_research (or 'medical')
            - academic_research (or 'academic')
            - research_writing (or 'writing')
            - project_timeline (or 'timeline')
            - data_analysis (or 'data')
            - citation_validation (or 'citation')
        cached: If True (default), reuse existing instance

    Returns:
        Agent wrapper instance (BaseAgent subclass)

    Raises:
        ValueError: If agent_name not in registry
    """
    return _get_default_registry().get_agent(agent_name, cached)


def list_agents() -> List[str]:
    """Return sorted list of all available agent names."""
    return _get_default_registry().list_agents()


def clear_cache() -> None:
    """Clear the agent cache. Useful for testing."""
    _get_default_registry().clear_cache()


# For backward compatibility
AGENT_REGISTRY = _AGENT_FACTORIES


__all__ = [
    'AgentRegistry',
    'get_agent',
    'list_agents',
    'clear_cache',
    'AGENT_REGISTRY'
]
