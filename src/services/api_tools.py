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

import functools
import inspect
import logging
import os
import threading
from typing import Any, Callable, Dict, List, Optional

import pybreaker

CircuitBreakerError = getattr(pybreaker, "CircuitBreakerError", Exception)

logger = logging.getLogger(__name__)


class CircuitProtectedToolWrapper:
    """
    Lightweight wrapper that preserves the tool interface while keeping a reference
    to the circuit breaker for logging/inspection. Minimal by design so tests can
    patch it without altering tool behavior.
    """
    def __init__(self, tool: Any, breaker: Optional[Any], api_name: str = "API"):
        self._tool = tool
        self._breaker = breaker
        self._api_name = api_name

    def __getattr__(self, name: str) -> Any:
        return getattr(self._tool, name)

    def __repr__(self) -> str:
        return f"CircuitProtectedToolWrapper(api={self._api_name!r}, tool={self._tool!r})"

try:
    from agno.tools.exa import ExaTools
    from agno.tools.duckduckgo import DuckDuckGoTools
    from agno.tools.serpapi import SerpApiTools
    from agno.tools.tavily import TavilyTools
    from agno.tools.pubmed import PubmedTools
    from agno.tools.arxiv import ArxivTools
    from agno.tools.clinicaltrials import ClinicalTrialsTools
    from agno.tools.medrxiv import MedRxivTools
    from agno.tools.semantic_scholar import SemanticScholarTools
    from agno.tools.core import CoreTools
    from agno.tools.doaj import DoajTools
    from src.tools.milestone_tools import MilestoneTools
    from src.services.safety_tools import SafetyTools
except ImportError as e:
    logger.warning(f"Could not import one or more tool classes, type hints may be imprecise: {e}")
    ExaTools = DuckDuckGoTools = SerpApiTools = TavilyTools = PubmedTools = ArxivTools = ClinicalTrialsTools = MedRxivTools = SemanticScholarTools = CoreTools = DoajTools = MilestoneTools = SafetyTools = Any

# Import circuit breakers
try:
    from .circuit_breaker import (
        EXA_BREAKER,
        DUCKDUCKGO_BREAKER,
        TAVILY_BREAKER,
        SERP_BREAKER,
        PUBMED_BREAKER,
        ARXIV_BREAKER,
        CLINICALTRIALS_BREAKER,
        MEDRXIV_BREAKER,
        SEMANTIC_SCHOLAR_BREAKER,
        CORE_BREAKER,
        DOAJ_BREAKER,
    )
except ImportError:
    logger.warning("Circuit breaker module not available")
    EXA_BREAKER = None
    DUCKDUCKGO_BREAKER = None
    TAVILY_BREAKER = None
    SERP_BREAKER = None
    PUBMED_BREAKER = None
    ARXIV_BREAKER = None
    CLINICALTRIALS_BREAKER = None
    MEDRXIV_BREAKER = None
    SEMANTIC_SCHOLAR_BREAKER = None
    CORE_BREAKER = None
    DOAJ_BREAKER = None


# Feature gates and configuration defaults
def _env_flag(name: str, default: str = "false") -> bool:
    """Normalize boolean-like environment flags."""
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "on"}


ENABLE_EXA_FOR_CLINICAL = _env_flag("ENABLE_EXA_FOR_CLINICAL", "false")

try:
    PUBMED_RETMAX = int(os.getenv("PUBMED_RETMAX", "20"))
except ValueError:
    logger.warning("Invalid PUBMED_RETMAX value; falling back to 20")
    PUBMED_RETMAX = 20


def call_with_breaker(
    func: Callable[..., Any],
    *args: Any,
    breaker: Optional[Any] = None,
    fallback: Optional[Callable[[BaseException], Any]] = None,
    fallback_message: str = "Service temporarily unavailable",
    **kwargs: Any,
) -> Any:
    """
    Execute a function with circuit-breaker protection.

    - Uses breaker.call(...) when a breaker is provided so failures trip/open the circuit
    - When the breaker is open or the call raises, an optional fallback is invoked
    - Without a fallback, exceptions are re-raised for the caller to handle
    """

    def _execute() -> Any:
        return func(*args, **kwargs)

    if breaker is not None:
        try:
            return breaker.call(_execute)
        except Exception as exc:  # pybreaker raises CircuitBreakerError when open
            logger.warning(f"Circuit-protected call failed for {getattr(breaker, 'name', 'unknown')}: {exc}")
            if fallback is not None:
                try:
                    return fallback(exc)
                except Exception as fallback_exc:
                    logger.error(f"Fallback for circuit-protected call raised: {fallback_exc}", exc_info=True)
            if isinstance(exc, CircuitBreakerError) or fallback is not None:
                return {"error": "service_unavailable", "message": fallback_message}
            raise

    try:
        return _execute()
    except Exception as exc:
        logger.error(f"Call failed without circuit breaker: {exc}")
        if fallback is not None:
            try:
                return fallback(exc)
            except Exception as fallback_exc:
                logger.error(f"Fallback for non-protected call raised: {fallback_exc}", exc_info=True)
        return {"error": "api_error", "message": fallback_message}


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

def _get_exa_breaker() -> Optional[Any]:
    """Get the Exa API circuit breaker."""
    return EXA_BREAKER

def _get_serp_breaker() -> Optional[Any]:
    """Get the SerpAPI circuit breaker."""
    return SERP_BREAKER

def _get_tavily_breaker() -> Optional[Any]:
    """Get the Tavily API circuit breaker."""
    return TAVILY_BREAKER

def _get_duckduckgo_breaker() -> Optional[Any]:
    """Get the DuckDuckGo circuit breaker."""
    return DUCKDUCKGO_BREAKER

def _get_pubmed_breaker() -> Optional[Any]:
    """Get the PubMed API circuit breaker."""
    return PUBMED_BREAKER

def _get_arxiv_breaker() -> Optional[Any]:
    """Get the Arxiv API circuit breaker."""
    return ARXIV_BREAKER

def _get_clinicaltrials_breaker() -> Optional[Any]:
    """Get the ClinicalTrials.gov API circuit breaker."""
    return CLINICALTRIALS_BREAKER

def _get_medrxiv_breaker() -> Optional[Any]:
    """Get the MedRxiv/BioRxiv API circuit breaker."""
    return MEDRXIV_BREAKER

def _get_semantic_scholar_breaker() -> Optional[Any]:
    """Get the Semantic Scholar API circuit breaker."""
    return SEMANTIC_SCHOLAR_BREAKER

def _get_core_breaker() -> Optional[Any]:
    """Get the CORE API circuit breaker."""
    return CORE_BREAKER

def _get_doaj_breaker() -> Optional[Any]:
    """Get the DOAJ API circuit breaker."""
    return DOAJ_BREAKER

def _custom_getstate(self: object) -> Dict[str, Any]:
    """Custom pickle getstate to remove unpicklable locks/breakers."""
    # If the class had a getstate, call it
    if hasattr(self, "_orig_getstate"):
        state = self._orig_getstate()
    else:
        state = self.__dict__.copy()
        
    # Remove locks and breakers
    keys = list(state.keys())
    for k in keys:
        if k.startswith("_breaker_lock_") or k.startswith("_breaker_"):
            # Keep factory
            if k == "_breaker_factory":
                continue
            del state[k]
    return state

def _custom_setstate(self: object, state: Dict[str, Any]) -> None:
    """Custom pickle setstate to restore locks/breakers."""
    # If the class had a setstate, call it
    if hasattr(self, "_orig_setstate"):
        self._orig_setstate(state)
    else:
        self.__dict__.update(state)
        
    # Restore locks and breakers
    if hasattr(self, "_wrapped_methods") and hasattr(self, "_breaker_factory"):
        factory = self._breaker_factory
        for name in self._wrapped_methods:
            setattr(self, f"_breaker_lock_{name}", threading.Lock())
            # Re-create breaker using the factory
            if factory:
                setattr(self, f"_breaker_{name}", factory())

def _make_bound_wrapper(method_name: str, orig_func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Create a wrapper function for a method.
    Defined at module level to aid pickling.
    """
    @functools.wraps(orig_func)
    def _wrapper(self: object, *args: Any, **kwargs: Any) -> Any:
        """
        Internal wrapper that applies per-instance locking and circuit breaking.
        """
        # Retrieve instance-specific lock and breaker
        lock = getattr(self, f"_breaker_lock_{method_name}")
        breaker = getattr(self, f"_breaker_{method_name}")
        
        with lock:
            orig_method = getattr(self, f"_orig_{method_name}")
            if hasattr(orig_method, "__get__"):
                bound_orig = orig_method.__get__(self, self.__class__)
            else:
                bound_orig = orig_method
                
            # Use unified breaker helper so caller gets a structured fallback instead of an exception
            return call_with_breaker(
                bound_orig,
                *args,
                breaker=breaker,
                fallback=lambda exc: {"error": "service_unavailable", "message": f"{method_name} unavailable"},
                fallback_message=f"{method_name} unavailable",
                **kwargs,
            )
            
    # Explicitly copy signature from unbound function
    try:
        _wrapper.__signature__ = inspect.signature(orig_func)
    except Exception:
        pass
        
    return _wrapper

def _unwrap_tool_method(tool: Any, method_name: str) -> None:
    """
    Unwrap a method on a tool instance.
    Defined at module level for pickling.
    """
    key = f"_orig_{method_name}"
    if hasattr(tool, key):
        setattr(tool, method_name, getattr(tool, key))
        delattr(tool, key)
        # Clean up breaker artifacts
        if hasattr(tool, f"_breaker_{method_name}"):
            delattr(tool, f"_breaker_{method_name}")
        if hasattr(tool, f"_breaker_lock_{method_name}"):
            delattr(tool, f"_breaker_lock_{method_name}")
        if hasattr(tool, "_wrapped_methods"):
            tool._wrapped_methods.discard(method_name)

def apply_in_place_wrapper(tool: Any, method_names: list, breaker_factory: Callable[[], Optional[pybreaker.CircuitBreaker]]) -> Any:
    """
    Replace methods on `tool` in-place with circuit-breaker-protected bound methods.
    
    Args:
        tool: The tool instance to modify
        method_names: List of method names to wrap
        breaker_factory: Function that returns a circuit breaker instance. 
                        MUST be a top-level function for pickling.
        
    Returns:
        The modified tool instance
    """
    if not hasattr(tool, "_wrapped_methods") or not isinstance(getattr(tool, "_wrapped_methods", None), set):
        tool._wrapped_methods = set()
        # Store factory for unpickling restoration
        tool._breaker_factory = breaker_factory
        
        # Patch the class to support pickling
        cls = tool.__class__
        # Only patch if we haven't already (check for our custom methods)
        if getattr(cls, "__getstate__", None) != _custom_getstate:
            if hasattr(cls, "__getstate__"):
                setattr(cls, "_orig_getstate", cls.__getstate__)
            cls.__getstate__ = _custom_getstate
            
            if hasattr(cls, "__setstate__"):
                setattr(cls, "_orig_setstate", cls.__setstate__)
            cls.__setstate__ = _custom_setstate
        
    for name in method_names:
        if name in tool._wrapped_methods:
            continue
            
        try:
            orig_bound = getattr(tool, name)
            # Get unbound function from class for correct signature
            orig_unbound = getattr(tool.__class__, name)
        except AttributeError:
            continue

        # Store original bound method
        setattr(tool, f"_orig_{name}", orig_bound)

        # Create per-instance breaker and lock
        breaker = breaker_factory()
        
        # If breaker is None (e.g. pybreaker not installed), skip wrapping
        if breaker is None:
            continue
            
        setattr(tool, f"_breaker_{name}", breaker)
        setattr(tool, f"_breaker_lock_{name}", threading.Lock())

        # Create wrapper using unbound function and bind to instance
        wrapped = _make_bound_wrapper(name, orig_unbound)
        # Bind the wrapper to the instance
        bound = wrapped.__get__(tool, tool.__class__)
        setattr(tool, name, bound)
        tool._wrapped_methods.add(name)

    # Attach unwrap method using partial for pickling support
    tool._unwrap_method = functools.partial(_unwrap_tool_method, tool)
    
    return tool


# ============================================================================
# Safe Tool Creation Functions
# ============================================================================

def create_exa_tools_safe(required: bool = False) -> Optional[ExaTools]:
    """
    Safely create ExaTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error when API key missing

    Returns:
        Circuit-protected ExaTools instance or None if key missing and not required
    """
    if not ENABLE_EXA_FOR_CLINICAL:
        logger.info("Exa creation skipped (ENABLE_EXA_FOR_CLINICAL=false)")
        if required:
            raise ValueError("Exa is disabled by ENABLE_EXA_FOR_CLINICAL flag")
        return None

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
        # We use a lambda to pass the breaker instance as a factory
        # This means all instances share the same breaker state (global rate limiting)
        apply_in_place_wrapper(
            exa_tool, 
            [m for m in dir(exa_tool) if not m.startswith("_") and callable(getattr(exa_tool, m))],
            _get_exa_breaker
        )
        logger.info("✅ Created Exa tool with circuit breaker protection")
        return exa_tool
    except Exception as e:
        logger.error(f"Failed to create ExaTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_duckduckgo_tools_safe(required: bool = False) -> Optional[DuckDuckGoTools]:
    """
    Safely create DuckDuckGoTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error on failure

    Returns:
        Circuit-protected DuckDuckGoTools instance or None on failure
    """
    try:
        from agno.tools.duckduckgo import DuckDuckGoTools
    except ImportError:
        logger.error("agno.tools.duckduckgo not available")
        if required:
            raise
        return None

    # Policy: news search disabled to keep usage focused on research/web articles
    enable_news = False
    backend = os.getenv("DUCKDUCKGO_BACKEND", "duckduckgo")
    modifier = os.getenv("DUCKDUCKGO_MODIFIER")

    fixed_max_results = os.getenv("DUCKDUCKGO_MAX_RESULTS")
    try:
        fixed_max_results_int = int(fixed_max_results) if fixed_max_results else None
    except ValueError:
        logger.warning("Invalid DUCKDUCKGO_MAX_RESULTS value; expected integer.")
        fixed_max_results_int = None

    try:
        ddg_tool = DuckDuckGoTools(
            enable_search=True,
            enable_news=enable_news,
            backend=backend,
            modifier=modifier or None,
            fixed_max_results=fixed_max_results_int,
        )
        apply_in_place_wrapper(
            ddg_tool,
            [m for m in dir(ddg_tool) if not m.startswith("_") and callable(getattr(ddg_tool, m))],
            _get_duckduckgo_breaker,
        )
        logger.info("✅ Created DuckDuckGo tool with circuit breaker protection")
        return ddg_tool
    except Exception as e:
        logger.error(f"Failed to create DuckDuckGoTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_tavily_tools_safe(required: bool = False) -> Optional[TavilyTools]:
    """
    Safely create TavilyTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error when API key missing

    Returns:
        Circuit-protected TavilyTools instance or None if key missing and not required
    """
    try:
        from agno.tools.tavily import TavilyTools
    except ImportError:
        logger.error("agno.tools.tavily not available")
        if required:
            raise
        return None

    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        msg = "TAVILY_API_KEY environment variable not set"
        logger.warning(msg)
        if required:
            raise ValueError(msg)
        return None

    search_depth = os.getenv("TAVILY_SEARCH_DEPTH", "basic")
    extract_depth = os.getenv("TAVILY_EXTRACT_DEPTH", "basic")
    include_answer_flag = os.getenv("TAVILY_INCLUDE_ANSWER", "true").strip().lower()
    include_answer = include_answer_flag not in {"0", "false", "off", "no", "disable", "disabled"}

    try:
        tavily_tool = TavilyTools(
            api_key=api_key,
            enable_search=True,
            enable_extract=True,
            search_depth=search_depth if search_depth in {"basic", "advanced"} else "basic",
            extract_depth=extract_depth if extract_depth in {"basic", "advanced"} else "basic",
            include_answer=include_answer,
            format="markdown",
            extract_format="markdown",
        )
        apply_in_place_wrapper(
            tavily_tool,
            [m for m in dir(tavily_tool) if not m.startswith("_") and callable(getattr(tavily_tool, m))],
            _get_tavily_breaker,
        )
        logger.info("✅ Created Tavily tool with circuit breaker protection")
        return tavily_tool
    except Exception as e:
        logger.error(f"Failed to create TavilyTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_serp_tools_safe(required: bool = False) -> Optional[SerpApiTools]:
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
        apply_in_place_wrapper(
            serp_tool,
            [m for m in dir(serp_tool) if not m.startswith("_") and callable(getattr(serp_tool, m))],
            _get_serp_breaker
        )
        logger.info("✅ Created SerpAPI tool with circuit breaker protection")
        return serp_tool
    except Exception as e:
        logger.error(f"Failed to create SerpApiTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_pubmed_tools_safe(required: bool = False) -> Optional[PubmedTools]:
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
            max_results=PUBMED_RETMAX,
            results_expanded=True,
            enable_search_pubmed=True,
        )
        # Wrap with circuit breaker protection
        apply_in_place_wrapper(
            pubmed_tool,
            [m for m in dir(pubmed_tool) if not m.startswith("_") and callable(getattr(pubmed_tool, m))],
            _get_pubmed_breaker
        )
        logger.info("✅ Created PubMed tool with circuit breaker protection")
        return pubmed_tool
    except Exception as e:
        logger.error(f"Failed to create PubmedTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_arxiv_tools_safe(required: bool = False) -> Optional[ArxivTools]:
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
        apply_in_place_wrapper(
            arxiv_tool,
            [m for m in dir(arxiv_tool) if not m.startswith("_") and callable(getattr(arxiv_tool, m))],
            _get_arxiv_breaker
        )
        logger.info("✅ Created Arxiv tool with circuit breaker protection")
        return arxiv_tool
    except Exception as e:
        logger.error(f"Failed to create ArxivTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_clinicaltrials_tools_safe(required: bool = False) -> Optional[ClinicalTrialsTools]:
    """
    Safely create ClinicalTrialsTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error on failure

    Returns:
        Circuit-protected ClinicalTrialsTools instance or None on failure
    """
    try:
        from agno.tools.clinicaltrials import ClinicalTrialsTools
    except ImportError:
        logger.error("agno.tools.clinicaltrials not available")
        if required:
            raise
        return None

    try:
        # Create the base tool (no API key required for ClinicalTrials.gov)
        clinicaltrials_tool = ClinicalTrialsTools(
            enable_search_clinicaltrials=True,
            max_results=10,
        )
        # Wrap with circuit breaker protection
        apply_in_place_wrapper(
            clinicaltrials_tool,
            [m for m in dir(clinicaltrials_tool) if not m.startswith("_") and callable(getattr(clinicaltrials_tool, m))],
            _get_clinicaltrials_breaker
        )
        logger.info("✅ Created ClinicalTrials.gov tool with circuit breaker protection")
        return CircuitProtectedToolWrapper(clinicaltrials_tool, CLINICALTRIALS_BREAKER, "ClinicalTrials.gov API")
    except Exception as e:
        logger.error(f"Failed to create ClinicalTrialsTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_medrxiv_tools_safe(required: bool = False) -> Optional[MedRxivTools]:
    """
    Safely create MedRxivTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error on failure

    Returns:
        Circuit-protected MedRxivTools instance or None on failure
    """
    try:
        from agno.tools.medrxiv import MedRxivTools
    except ImportError:
        logger.error("agno.tools.medrxiv not available")
        if required:
            raise
        return None

    try:
        # Create the base tool (no API key required for medRxiv/bioRxiv)
        medrxiv_tool = MedRxivTools(
            enable_search_medrxiv=True,
            enable_search_biorxiv=True,
            max_results=10,
        )
        # Wrap with circuit breaker protection
        apply_in_place_wrapper(
            medrxiv_tool,
            [m for m in dir(medrxiv_tool) if not m.startswith("_") and callable(getattr(medrxiv_tool, m))],
            _get_medrxiv_breaker
        )
        logger.info("✅ Created medRxiv tool with circuit breaker protection")
        return CircuitProtectedToolWrapper(medrxiv_tool, MEDRXIV_BREAKER, "medRxiv API")
    except Exception as e:
        logger.error(f"Failed to create MedRxivTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_semantic_scholar_tools_safe(required: bool = False) -> Optional[SemanticScholarTools]:
    """
    Safely create SemanticScholarTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error on failure

    Returns:
        Circuit-protected SemanticScholarTools instance or None on failure
    """
    try:
        from agno.tools.semantic_scholar import SemanticScholarTools
    except ImportError:
        logger.error("agno.tools.semantic_scholar not available")
        if required:
            raise
        return None

    try:
        # Create the base tool (API key optional but recommended for higher rate limits)
        semantic_scholar_tool = SemanticScholarTools(
            enable_search_semantic_scholar=True,
            max_results=10,
            api_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY"),
        )
        # Wrap with circuit breaker protection
        apply_in_place_wrapper(
            semantic_scholar_tool,
            [m for m in dir(semantic_scholar_tool) if not m.startswith("_") and callable(getattr(semantic_scholar_tool, m))],
            _get_semantic_scholar_breaker
        )
        logger.info("✅ Created Semantic Scholar tool with circuit breaker protection")
        return CircuitProtectedToolWrapper(semantic_scholar_tool, SEMANTIC_SCHOLAR_BREAKER, "Semantic Scholar API")
    except Exception as e:
        logger.error(f"Failed to create SemanticScholarTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_core_tools_safe(required: bool = False) -> Optional[CoreTools]:
    """
    Safely create CoreTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error on failure

    Returns:
        Circuit-protected CoreTools instance or None on failure
    """
    try:
        from agno.tools.core import CoreTools
    except ImportError:
        logger.error("agno.tools.core not available")
        if required:
            raise
        return None

    try:
        # Create the base tool (API key optional but recommended for higher rate limits)
        core_tool = CoreTools(
            enable_search_core=True,
            max_results=10,
            api_key=os.getenv("CORE_API_KEY"),
        )
        # Wrap with circuit breaker protection
        apply_in_place_wrapper(
            core_tool,
            [m for m in dir(core_tool) if not m.startswith("_") and callable(getattr(core_tool, m))],
            _get_core_breaker
        )
        logger.info("✅ Created CORE tool with circuit breaker protection")
        return CircuitProtectedToolWrapper(core_tool, CORE_BREAKER, "CORE API")
    except Exception as e:
        logger.error(f"Failed to create CoreTools: {e}", exc_info=True)
        if required:
            raise
        return None


def create_doaj_tools_safe(required: bool = False) -> Optional[DoajTools]:
    """
    Safely create DoajTools with circuit breaker protection and error handling.

    Args:
        required: If True, raises error on failure

    Returns:
        Circuit-protected DoajTools instance or None on failure
    """
    try:
        from agno.tools.doaj import DoajTools
    except ImportError:
        logger.error("agno.tools.doaj not available")
        if required:
            raise
        return None

    try:
        # Create the base tool (no API key required for DOAJ)
        doaj_tool = DoajTools(
            enable_search_doaj=True,
            max_results=10,
        )
        # Wrap with circuit breaker protection
        apply_in_place_wrapper(
            doaj_tool,
            [m for m in dir(doaj_tool) if not m.startswith("_") and callable(getattr(doaj_tool, m))],
            _get_doaj_breaker
        )
        logger.info("✅ Created DOAJ tool with circuit breaker protection")
        return CircuitProtectedToolWrapper(doaj_tool, DOAJ_BREAKER, "DOAJ API")
    except Exception as e:
        logger.error(f"Failed to create DoajTools: {e}", exc_info=True)
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
# Milestone Tools (Database Access)
# ============================================================================

def create_milestone_tools_safe(required: bool = False) -> Optional[MilestoneTools]:
    """
    Create MilestoneTools with safe fallback.

    MilestoneTools doesn't require API keys - it queries the local project database.

    Args:
        required: If True, raises error on failure. If False, returns None.

    Returns:
        MilestoneTools instance or None if creation fails
    """
    try:
        from src.tools.milestone_tools import MilestoneTools

        # No circuit breaker needed - local database operation
        tool = MilestoneTools()
        logger.info("✅ Created MilestoneTools for database queries")
        return tool

    except ImportError as e:
        msg = f"MilestoneTools not available: {e}"
        logger.warning(msg)
        if required:
            raise ImportError(msg)
        return None
    except Exception as e:
        msg = f"Failed to create MilestoneTools: {e}"
        logger.error(msg)
        if required:
            raise RuntimeError(msg)
        return None


# ============================================================================
# Safety Tools (OpenFDA API)
# ============================================================================

def create_safety_tools_safe(required: bool = False) -> Optional[SafetyTools]:
    """
    Create SafetyTools with safe fallback.

    SafetyTools doesn't require API keys - it queries the public OpenFDA API.
    Used for device recalls and drug adverse events.

    Args:
        required: If True, raises error on failure. If False, returns None.

    Returns:
        SafetyTools instance or None if creation fails
    """
    try:
        from src.services.safety_tools import SafetyTools

        # No circuit breaker needed - public API with built-in error handling
        tool = SafetyTools(
            enable_device_recalls=True,
            enable_drug_events=True
        )
        logger.info("✅ Created SafetyTools for OpenFDA queries")
        return tool

    except ImportError as e:
        msg = f"SafetyTools not available: {e}"
        logger.warning(msg)
        if required:
            raise ImportError(msg)
        return None
    except Exception as e:
        msg = f"Failed to create SafetyTools: {e}"
        logger.error(msg)
        if required:
            raise RuntimeError(msg)
        return None


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
        "duckduckgo": {
            "key_set": True,  # DuckDuckGo via ddgs is keyless
            "required": False,
            "note": f"DuckDuckGo backend: {os.getenv('DUCKDUCKGO_BACKEND', 'duckduckgo')}",
        },
        "tavily": {
            "key_set": bool(os.getenv("TAVILY_API_KEY")),
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
        "clinicaltrials": {
            "key_set": True,  # ClinicalTrials.gov doesn't require key
            "required": False,
            "note": "ClinicalTrials.gov is free and public"
        },
        "medrxiv": {
            "key_set": True,  # medRxiv/bioRxiv don't require key
            "required": False,
            "note": "medRxiv/bioRxiv are free and public"
        },
        "semantic_scholar": {
            "key_set": bool(os.getenv("SEMANTIC_SCHOLAR_API_KEY")),
            "required": False,
            "note": "API key optional but recommended for higher rate limits"
        },
        "core": {
            "key_set": bool(os.getenv("CORE_API_KEY")),
            "required": False,
            "note": "API key optional but recommended for higher rate limits"
        },
        "doaj": {
            "key_set": True,  # DOAJ doesn't require key
            "required": False,
            "note": "DOAJ is free and public"
        },
        "safety": {
            "key_set": True,  # OpenFDA doesn't require key
            "required": False,
            "note": "OpenFDA is free and public (device recalls, drug events)"
        },
    }
    return status


def print_api_status() -> None:
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

    tavily = create_tavily_tools_safe()
    print(f"TavilyTools: {'✅ created' if tavily else '❌ failed (key missing?)'}")

    duckduckgo = create_duckduckgo_tools_safe()
    print(f"DuckDuckGoTools: {'✅ created' if duckduckgo else '❌ failed (dependency missing?)'}")

    serp = create_serp_tools_safe()
    print(f"SerpApiTools: {'✅ created' if serp else '❌ failed (key missing?)'}")

    pubmed = create_pubmed_tools_safe()
    print(f"PubmedTools: {'✅ created' if pubmed else '❌ failed'}")

    arxiv = create_arxiv_tools_safe()
    print(f"ArxivTools: {'✅ created' if arxiv else '❌ failed'}")

    clinicaltrials = create_clinicaltrials_tools_safe()
    print(f"ClinicalTrialsTools: {'✅ created' if clinicaltrials else '❌ failed'}")

    medrxiv = create_medrxiv_tools_safe()
    print(f"MedRxivTools: {'✅ created' if medrxiv else '❌ failed'}")

    semantic_scholar = create_semantic_scholar_tools_safe()
    print(f"SemanticScholarTools: {'✅ created' if semantic_scholar else '❌ failed'}")

    core = create_core_tools_safe()
    print(f"CoreTools: {'✅ created' if core else '❌ failed'}")

    doaj = create_doaj_tools_safe()
    print(f"DoajTools: {'✅ created' if doaj else '❌ failed'}")

    tools_list = build_tools_list(exa, tavily, duckduckgo, serp, pubmed, arxiv, clinicaltrials, medrxiv, semantic_scholar, core, doaj)
    print(f"\n✅ Built tools list with {len(tools_list)} available tools")
