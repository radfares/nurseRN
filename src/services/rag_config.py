"""
RAG Configuration - Phase 3
Defines agent-to-collection routing configuration.

Created: 2025-12-15
Phase: 3 - Agent RAG Integration
"""

from typing import List, Dict

# Agent-to-Collection Mapping
# Each agent has a prioritized list of collections to search
RAG_AGENT_CONFIG: Dict[str, Dict[str, List[str]]] = {
    "nursing_research": {
        "primary": ["clinical_knowledge", "research_cache"],
        "secondary": ["procedural_knowledge", "personal_docs"]
    },
    "medical_research": {
        "primary": ["research_cache", "clinical_knowledge"],
        "secondary": ["personal_docs"]
    },
    "document_synthesis": {
        "primary": ["personal_docs", "research_cache"],
        "secondary": ["clinical_knowledge", "procedural_knowledge"]
    },
    "general": {
        "primary": ["personal_docs"],
        "secondary": ["clinical_knowledge", "procedural_knowledge", "research_cache"]
    }
}

# Default fallback configuration
DEFAULT_COLLECTIONS = ["personal_docs", "clinical_knowledge"]


def get_collections_for_agent(agent_hint: str, include_secondary: bool = True) -> List[str]:
    """
    Get the list of collections to search for a given agent.
    
    Args:
        agent_hint: Agent identifier (e.g., "nursing_research", "medical_research")
        include_secondary: Whether to include secondary collections (default True)
    
    Returns:
        List of collection names in priority order
    """
    config = RAG_AGENT_CONFIG.get(agent_hint)
    
    if not config:
        # Unknown agent, use general configuration
        config = RAG_AGENT_CONFIG["general"]
    
    collections = config["primary"].copy()
    
    if include_secondary:
        collections.extend(config["secondary"])
    
    return collections


def get_primary_collection_for_agent(agent_hint: str) -> str:
    """
    Get the primary (first) collection for an agent.
    
    Args:
        agent_hint: Agent identifier
    
    Returns:
        Primary collection name
    """
    collections = get_collections_for_agent(agent_hint, include_secondary=False)
    return collections[0] if collections else "personal_docs"


def register_agent_config(agent_name: str, primary: List[str], secondary: List[str]) -> None:
    """
    Register a custom agent configuration.
    
    Args:
        agent_name: Unique agent identifier
        primary: List of primary collections to search
        secondary: List of secondary collections to search
    """
    RAG_AGENT_CONFIG[agent_name] = {
        "primary": primary,
        "secondary": secondary
    }


def get_all_agent_names() -> List[str]:
    """Get list of all configured agent names."""
    return list(RAG_AGENT_CONFIG.keys())
