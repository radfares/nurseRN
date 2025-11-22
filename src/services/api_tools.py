"""
API Tools with Circuit Breaker Protection
Wrappers for agno tools with resilience mechanisms

Week 1 Refactoring - Focus Area 1: API Dependency Management
Created: 2025-11-22

This module provides safe wrappers for creating API tools that:
1. Handle missing API keys gracefully
2. Provide fallback behavior when APIs are unavailable
3. Log errors appropriately
4. Wrap actual API calls with circuit breakers
5. Cache API responses (24hr TTL)
"""

import logging
import os
from typing import Optional, Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)

# Import circuit breakers
try:
    from .circuit_breaker import (
        EXA_BREAKER,
        SERP_BREAKER,
        PUBMED_BREAKER,
        ARXIV_BREAKER,
        call_with_breaker
    )
except ImportError:
    logger.warning("Circuit breaker module not available")
    EXA_BREAKER = None
    SERP_BREAKER = None
    PUBMED_BREAKER = None
    ARXIV_BREAKER = None
    def call_with_breaker(breaker, func, fallback_message, *args, **kwargs):
        return func(*args, **kwargs)

# Setup HTTP caching for API responses (24hr TTL)
try:
    import requests_cache
    # Create a cached session with 24hr expiration
    requests_cache.install_cache(
        cache_name='api_cache',
        backend='sqlite',
        expire_after=86400,  # 24 hours in seconds
        allowable_codes=[200, 203],
        allowable_methods=['GET', 'POST'],
        match_headers=False,
        ignored_parameters=None,
    )
    logger.info("✅ HTTP caching enabled (24hr TTL)")
    CACHING_ENABLED = True
except ImportError:
    logger.warning("requests-cache not installed. API caching disabled. Run: pip install requests-cache")
    CACHING_ENABLED = False
except Exception as e:
    logger.error(f"Failed to setup API caching: {e}")
    CACHING_ENABLED = False


# ============================================================================
# Tool Wrapper Classes with Circuit Breaker Protection
# ============================================================================

class CircuitProtectedToolWrapper:
    """
    Base wrapper class that adds circuit breaker protection to tool method calls.

    This wraps any tool object and intercepts method calls to add:
    1. Circuit breaker protection
    2. Error handling with fallback responses
    3. Logging
    """

    def __init__(self, tool, breaker, tool_name: str):
        """
        Initialize wrapper.

        Args:
            tool: The tool instance to wrap
            breaker: Circuit breaker instance
            tool_name: Name for logging
        """
        self._tool = tool
        self._breaker = breaker
        self._tool_name = tool_name

    def __getattr__(self, name):
        """
        Intercept attribute access to wrap methods with circuit breaker.
        """
        # Get the original attribute from the wrapped tool
        attr = getattr(self._tool, name)

        # If it's a method, wrap it with circuit breaker
        if callable(attr):
            @wraps(attr)
            def circuit_protected_method(*args, **kwargs):
                logger.debug(f"Calling {self._tool_name}.{name} with circuit breaker protection")
                return call_with_breaker(
                    self._breaker,
                    attr,
                    f"{self._tool_name} temporarily unavailable. Please try again later.",
                    *args,
                    **kwargs
                )
            return circuit_protected_method

        # If it's not a method, return it as-is
        return attr


# ============================================================================
# Safe Tool Creation Functions
# ============================================================================

def create_exa_tools_safe(required: bool = False) -> Optional[Any]:
    """
    Safely create ExaTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error when API key missing

    Returns:
        Circuit-protected ExaTools instance or None if key missing and not required
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
        # Create the base tool
        exa_tool = ExaTools(
            api_key=api_key,
            start_published_date="2020-01-01",
            type="neural",
        )
        # Wrap with circuit breaker protection
        wrapped_tool = CircuitProtectedToolWrapper(exa_tool, EXA_BREAKER, "Exa API")
        logger.info("✅ Created Exa tool with circuit breaker protection")
        return wrapped_tool
    except Exception as e:
        logger.error(f"Failed to create ExaTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_serp_tools_safe(required: bool = False) -> Optional[Any]:
    """
    Safely create SerpApiTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error when API key missing

    Returns:
        Circuit-protected SerpApiTools instance or None if key missing and not required
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
        # Create the base tool
        serp_tool = SerpApiTools(api_key=api_key)
        # Wrap with circuit breaker protection
        wrapped_tool = CircuitProtectedToolWrapper(serp_tool, SERP_BREAKER, "SerpAPI")
        logger.info("✅ Created SerpAPI tool with circuit breaker protection")
        return wrapped_tool
    except Exception as e:
        logger.error(f"Failed to create SerpApiTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_pubmed_tools_safe(required: bool = False) -> Optional[Any]:
    """
    Safely create PubmedTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error on failure

    Returns:
        Circuit-protected PubmedTools instance or None on failure
    """
    try:
        from agno.tools.pubmed import PubmedTools
    except ImportError:
        logger.error("agno.tools.pubmed not available")
        if required:
            raise
        return None

    try:
        # Create the base tool
        pubmed_tool = PubmedTools(
            email=os.getenv("PUBMED_EMAIL", "nursing.research@example.com"),
            max_results=10,
            results_expanded=True,
            enable_search_pubmed=True,
        )
        # Wrap with circuit breaker protection
        wrapped_tool = CircuitProtectedToolWrapper(pubmed_tool, PUBMED_BREAKER, "PubMed API")
        logger.info("✅ Created PubMed tool with circuit breaker protection")
        return wrapped_tool
    except Exception as e:
        logger.error(f"Failed to create PubmedTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_arxiv_tools_safe(required: bool = False) -> Optional[Any]:
    """
    Safely create ArxivTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error on failure

    Returns:
        Circuit-protected ArxivTools instance or None on failure
    """
    try:
        from agno.tools.arxiv import ArxivTools
    except ImportError:
        logger.error("agno.tools.arxiv not available")
        if required:
            raise
        return None

    try:
        # Create the base tool
        arxiv_tool = ArxivTools(enable_search_arxiv=True)
        # Wrap with circuit breaker protection
        wrapped_tool = CircuitProtectedToolWrapper(arxiv_tool, ARXIV_BREAKER, "Arxiv API")
        logger.info("✅ Created Arxiv tool with circuit breaker protection")
        return wrapped_tool
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
