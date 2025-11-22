"""
API Tools with Circuit Breaker Protection
Wrappers for agno tools with resilience mechanisms

Week 1 Refactoring - Focus Area 1: API Dependency Management
Created: 2025-11-22

This module provides safe wrappers for creating API tools that:
1. Handle missing API keys gracefully
2. Provide fallback behavior when APIs are unavailable
3. Log errors appropriately
"""

import logging
import os
from typing import Optional, Any

logger = logging.getLogger(__name__)


# ============================================================================
# Safe Tool Creation Functions
# ============================================================================

def create_exa_tools_safe(required: bool = False) -> Optional[Any]:
    """
    Safely create ExaTools with error handling.

    Args:
        required: If True, raises error when API key missing

    Returns:
        ExaTools instance or None if key missing and not required
    """
    try:
        from agno.tools.exa import ExaTools
    except ImportError:
        logger.error("agno.tools.exa not available")
        if required:
            raise
        return None

    api_key = os.getenv("EXA_API_KEY")

    if not api_key:
        msg = "EXA_API_KEY environment variable not set"
        logger.warning(msg)
        if required:
            raise ValueError(msg)
        return None

    try:
        return ExaTools(
            api_key=api_key,
            start_published_date="2020-01-01",
            type="neural",
        )
    except Exception as e:
        logger.error(f"Failed to create ExaTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_serp_tools_safe(required: bool = False) -> Optional[Any]:
    """
    Safely create SerpApiTools with error handling.

    Args:
        required: If True, raises error when API key missing

    Returns:
        SerpApiTools instance or None if key missing and not required
    """
    try:
        from agno.tools.serpapi import SerpApiTools
    except ImportError:
        logger.error("agno.tools.serpapi not available")
        if required:
            raise
        return None

    api_key = os.getenv("SERP_API_KEY")

    if not api_key:
        msg = "SERP_API_KEY environment variable not set"
        logger.warning(msg)
        if required:
            raise ValueError(msg)
        return None

    try:
        return SerpApiTools(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to create SerpApiTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_pubmed_tools_safe(required: bool = False) -> Optional[Any]:
    """
    Safely create PubmedTools with error handling.

    Args:
        required: If True, raises error on failure

    Returns:
        PubmedTools instance or None on failure
    """
    try:
        from agno.tools.pubmed import PubmedTools
    except ImportError:
        logger.error("agno.tools.pubmed not available")
        if required:
            raise
        return None

    try:
        return PubmedTools(
            email=os.getenv("PUBMED_EMAIL", "nursing.research@example.com"),
            max_results=10,
            results_expanded=True,
            enable_search_pubmed=True,
        )
    except Exception as e:
        logger.error(f"Failed to create PubmedTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_arxiv_tools_safe(required: bool = False) -> Optional[Any]:
    """
    Safely create ArxivTools with error handling.

    Args:
        required: If True, raises error on failure

    Returns:
        ArxivTools instance or None on failure
    """
    try:
        from agno.tools.arxiv import ArxivTools
    except ImportError:
        logger.error("agno.tools.arxiv not available")
        if required:
            raise
        return None

    try:
        return ArxivTools(enable_search_arxiv=True)
    except Exception as e:
        logger.error(f"Failed to create ArxivTools: {e}", exc_info=True)
        if required:
            raise
        return None


# ============================================================================
# Tool List Builder
# ============================================================================

def build_tools_list(*tools) -> list:
    """
    Build a list of tools, filtering out None values.

    Args:
        *tools: Tool instances (may include None)

    Returns:
        List of non-None tools
    """
    return [tool for tool in tools if tool is not None]


def validate_tools_list(tools: list, min_required: int = 1) -> bool:
    """
    Validate that we have minimum required tools.

    Args:
        tools: List of tools
        min_required: Minimum number of tools required

    Returns:
        True if validation passes

    Raises:
        ValueError: If insufficient tools available
    """
    if len(tools) < min_required:
        raise ValueError(
            f"Insufficient tools available: {len(tools)} (min required: {min_required})"
        )
    return True


# ============================================================================
# Status Reporting
# ============================================================================

def get_api_status() -> dict:
    """
    Check status of all API keys and services.

    Returns:
        Dict with API availability status
    """
    status = {
        "openai": {
            "key_set": bool(os.getenv("OPENAI_API_KEY")),
            "required": True,
        },
        "exa": {
            "key_set": bool(os.getenv("EXA_API_KEY")),
            "required": False,
        },
        "serp": {
            "key_set": bool(os.getenv("SERP_API_KEY")),
            "required": False,
        },
        "pubmed": {
            "email_set": bool(os.getenv("PUBMED_EMAIL")),
            "required": False,
            "note": "PubMed uses email, not API key"
        },
        "arxiv": {
            "key_set": True,  # Arxiv doesn't require key
            "required": False,
            "note": "Arxiv doesn't require authentication"
        },
    }
    return status


def print_api_status():
    """Print API availability status (for debugging)."""
    status = get_api_status()
    print("\n" + "=" * 60)
    print("API Configuration Status")
    print("=" * 60)

    for api_name, info in status.items():
        is_configured = info.get("key_set") or info.get("email_set", False)
        emoji = "✅" if is_configured else "❌"
        required_text = "REQUIRED" if info.get("required") else "optional"

        print(f"{emoji} {api_name.upper()}: {'configured' if is_configured else 'NOT configured'} ({required_text})")

        if "note" in info:
            print(f"   └─ {info['note']}")

    print("=" * 60 + "\n")


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    """Test API tools creation."""
    print("Testing API Tools Service\n")

    print_api_status()

    print("\nAttempting to create tools...")
    print("-" * 60)

    exa = create_exa_tools_safe()
    print(f"ExaTools: {'✅ created' if exa else '❌ failed (key missing?)'}")

    serp = create_serp_tools_safe()
    print(f"SerpApiTools: {'✅ created' if serp else '❌ failed (key missing?)'}")

    pubmed = create_pubmed_tools_safe()
    print(f"PubmedTools: {'✅ created' if pubmed else '❌ failed'}")

    arxiv = create_arxiv_tools_safe()
    print(f"ArxivTools: {'✅ created' if arxiv else '❌ failed'}")

    tools_list = build_tools_list(exa, serp, pubmed, arxiv)
    print(f"\n✅ Built tools list with {len(tools_list)} available tools")
