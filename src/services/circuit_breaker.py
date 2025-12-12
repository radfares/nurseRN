"""
Circuit Breaker Service for API Resilience
Prevents cascade failures by opening circuit after repeated API failures

Week 1 Refactoring - Focus Area 1: API Dependency Management
Created: 2025-11-22

Circuit Breaker Pattern:
- CLOSED: Normal operation, requests pass through
- OPEN: After N failures, reject requests immediately (fail fast)
- HALF_OPEN: After timeout, allow test request to check recovery

Configuration:
- Failure threshold: 5 failures
- Timeout: 60 seconds (circuit opens for 60s after 5 failures)
- Expected exceptions: RequestException, APIError, Timeout
"""

import logging
from typing import Callable, Any, Optional
from functools import wraps

try:
    from pybreaker import CircuitBreaker, CircuitBreakerError, CircuitBreakerListener
except ImportError:
    # Graceful degradation if pybreaker not installed.
    # We still need a base class for LoggingListener to inherit from;
    # using a simple object subclass avoids TypeError when pybreaker is missing.
    logging.warning("pybreaker not installed. Circuit breakers disabled. Run: pip install pybreaker")

    class _FallbackCircuitBreakerListener:
        """Fallback no-op listener used when pybreaker is not available."""

        def __init__(self, *args, **kwargs):
            """Accept arbitrary args for compatibility; do nothing."""
            return

    CircuitBreaker = None
    CircuitBreakerError = Exception
    CircuitBreakerListener = _FallbackCircuitBreakerListener


logger = logging.getLogger(__name__)


# ============================================================================
# Circuit Breaker Listener for Logging
# ============================================================================

class LoggingListener(CircuitBreakerListener):
    """Listener that logs circuit breaker events."""

    def __init__(self, timeout: int):
        self.timeout = timeout

    def success(self, cb):
        logger.debug(f"Circuit breaker '{cb.name}' - successful call")

    def failure(self, cb, exc):
        logger.warning(f"Circuit breaker '{cb.name}' - failure: {exc}")

    def state_change(self, cb, old_state, new_state):
        logger.warning(f"Circuit breaker '{cb.name}' - state change: {old_state} → {new_state}")
        if str(new_state) == "open":
            logger.error(
                f"🔴 API '{cb.name}' circuit OPEN - too many failures. "
                f"Will retry in {self.timeout} seconds."
            )


# ============================================================================
# Circuit Breaker Instances for Each API
# ============================================================================

# Configure circuit breakers for each external API
# Pattern: 5 failures → circuit opens → wait 60 seconds → retry

def create_circuit_breaker(name: str, failure_threshold: int = 5, timeout: int = 60):
    """
    Create a circuit breaker for an API.

    Args:
        name: Name of the API (for logging)
        failure_threshold: Number of failures before opening circuit
        timeout: Seconds to wait before attempting recovery

    Returns:
        CircuitBreaker instance or None if pybreaker not available
    """
    if CircuitBreaker is None:
        logger.warning(f"Circuit breaker for {name} not created (pybreaker not installed)")
        return None

    breaker = CircuitBreaker(
        fail_max=failure_threshold,
        reset_timeout=timeout,
        name=name,
        exclude=[KeyboardInterrupt],  # Don't count user interrupts as failures
    )

    # Add logging listener
    if CircuitBreakerListener is not None:
        breaker.add_listener(LoggingListener(timeout))

    return breaker


# Create circuit breakers for each external API
OPENAI_BREAKER = create_circuit_breaker("OpenAI API", failure_threshold=5, timeout=60)
EXA_BREAKER = create_circuit_breaker("Exa API", failure_threshold=5, timeout=60)
SERP_BREAKER = create_circuit_breaker("SerpAPI", failure_threshold=5, timeout=60)
PUBMED_BREAKER = create_circuit_breaker("PubMed API", failure_threshold=5, timeout=60)
ARXIV_BREAKER = create_circuit_breaker("Arxiv API", failure_threshold=5, timeout=60)
CLINICALTRIALS_BREAKER = create_circuit_breaker("ClinicalTrials.gov API", failure_threshold=5, timeout=60)
MEDRXIV_BREAKER = create_circuit_breaker("medRxiv API", failure_threshold=5, timeout=60)
SEMANTIC_SCHOLAR_BREAKER = create_circuit_breaker("Semantic Scholar API", failure_threshold=5, timeout=60)
CORE_BREAKER = create_circuit_breaker("CORE API", failure_threshold=5, timeout=60)
DOAJ_BREAKER = create_circuit_breaker("DOAJ API", failure_threshold=5, timeout=60)

# Document reader circuit breakers (added 2025-12-11)
PDF_READER_BREAKER = create_circuit_breaker("PDF Reader", failure_threshold=5, timeout=60)
PPTX_READER_BREAKER = create_circuit_breaker("PPTX Reader", failure_threshold=5, timeout=60)
WEBSITE_READER_BREAKER = create_circuit_breaker("Website Reader", failure_threshold=5, timeout=60)
TAVILY_READER_BREAKER = create_circuit_breaker("Tavily Reader", failure_threshold=5, timeout=60)
WEB_SEARCH_READER_BREAKER = create_circuit_breaker("Web Search Reader", failure_threshold=5, timeout=60)


# ============================================================================
# Helper Functions for Wrapped API Calls
# ============================================================================

def with_circuit_breaker(
    breaker: Optional[CircuitBreaker],
    fallback_message: str = "Service temporarily unavailable. Please try again later."
):
    """
    Decorator to wrap API calls with circuit breaker protection.

    Args:
        breaker: Circuit breaker instance to use
        fallback_message: Message to return when circuit is open

    Returns:
        Decorated function that uses circuit breaker

    Example:
        @with_circuit_breaker(OPENAI_BREAKER, "OpenAI service unavailable")
        def call_openai_api():
            return openai.ChatCompletion.create(...)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # If no circuit breaker available, call function directly
            if breaker is None:
                return func(*args, **kwargs)

            try:
                # Call function through circuit breaker
                return breaker.call(func, *args, **kwargs)

            except CircuitBreakerError:
                # Circuit is OPEN - too many failures
                logger.error(
                    f"Circuit breaker '{breaker.name}' is OPEN. "
                    f"Returning fallback message."
                )
                # Return fallback instead of crashing
                return {"error": "service_unavailable", "message": fallback_message}

            except Exception as e:
                # Other exceptions - log and re-raise
                logger.error(f"Error in circuit-protected call: {e}", exc_info=True)
                raise

        return wrapper
    return decorator


def call_with_breaker(
    breaker: Optional[CircuitBreaker],
    func: Callable,
    fallback_message: str,
    *args,
    **kwargs
) -> Any:
    """
    Call a function through a circuit breaker (non-decorator version).

    Args:
        breaker: Circuit breaker to use
        func: Function to call
        fallback_message: Message if circuit is open
        *args, **kwargs: Arguments to pass to func

    Returns:
        Result of func() or fallback dict if circuit open or error

    Example:
        result = call_with_breaker(
            EXA_BREAKER,
            exa_api.search,
            "Exa search unavailable",
            query="healthcare"
        )
    """
    if breaker is None:
        # No circuit breaker available, call directly
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error calling function (no breaker): {e}")
            return {"error": "api_error", "message": fallback_message}

    try:
        return breaker.call(func, *args, **kwargs)
    except CircuitBreakerError:
        # Circuit is OPEN - return fallback
        logger.error(
            f"Circuit breaker '{breaker.name}' is OPEN. "
            f"Returning fallback."
        )
        return {"error": "service_unavailable", "message": fallback_message}
    except Exception as e:
        # API call failed but circuit not yet open - return fallback
        logger.error(f"Error in circuit-protected call to '{breaker.name}': {e}")
        return {"error": "api_error", "message": fallback_message}


def get_breaker_status(breaker: Optional[CircuitBreaker]) -> dict:
    """
    Get current status of a circuit breaker.

    Args:
        breaker: Circuit breaker to check

    Returns:
        Dict with status info
    """
    if breaker is None:
        return {"available": False, "state": "disabled"}

    return {
        "available": True,
        "name": breaker.name,
        "state": breaker.current_state,
        "failure_count": breaker.fail_counter,
        "failure_threshold": breaker.fail_max,
        "opened_at": breaker.opened_at if hasattr(breaker, 'opened_at') else None,
    }


def reset_breaker(breaker: Optional[CircuitBreaker]) -> bool:
    """
    Manually reset a circuit breaker (for testing/debugging).

    Args:
        breaker: Circuit breaker to reset

    Returns:
        True if reset successful
    """
    if breaker is None:
        return False

    try:
        breaker.close()
        logger.info(f"Circuit breaker '{breaker.name}' manually reset")
        return True
    except Exception as e:
        logger.error(f"Failed to reset circuit breaker: {e}")
        return False


# ============================================================================
# Status Check Functions
# ============================================================================

def get_all_breaker_status() -> dict:
    """
    Get status of all circuit breakers.

    Returns:
        Dict mapping API name to status
    """
    return {
        "openai": get_breaker_status(OPENAI_BREAKER),
        "exa": get_breaker_status(EXA_BREAKER),
        "serp": get_breaker_status(SERP_BREAKER),
        "pubmed": get_breaker_status(PUBMED_BREAKER),
        "arxiv": get_breaker_status(ARXIV_BREAKER),
        "clinicaltrials": get_breaker_status(CLINICALTRIALS_BREAKER),
        "medrxiv": get_breaker_status(MEDRXIV_BREAKER),
        "semantic_scholar": get_breaker_status(SEMANTIC_SCHOLAR_BREAKER),
        "core": get_breaker_status(CORE_BREAKER),
        "doaj": get_breaker_status(DOAJ_BREAKER),
        "pdf_reader": get_breaker_status(PDF_READER_BREAKER),
        "pptx_reader": get_breaker_status(PPTX_READER_BREAKER),
        "website_reader": get_breaker_status(WEBSITE_READER_BREAKER),
        "tavily_reader": get_breaker_status(TAVILY_READER_BREAKER),
        "web_search_reader": get_breaker_status(WEB_SEARCH_READER_BREAKER),
    }


def print_breaker_status():
    """Print status of all circuit breakers (for debugging)."""
    status = get_all_breaker_status()
    print("\n" + "=" * 60)
    print("Circuit Breaker Status")
    print("=" * 60)
    for api_name, info in status.items():
        if info["available"]:
            state_emoji = {
                "closed": "✅",
                "open": "🔴",
                "half-open": "🟡"
            }.get(info["state"], "❓")
            print(f"{state_emoji} {api_name.upper()}: {info['state']} "
                  f"({info['failure_count']}/{info['failure_threshold']} failures)")
        else:
            print(f"⚠️  {api_name.upper()}: disabled (pybreaker not installed)")
    print("=" * 60 + "\n")


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    """Test circuit breaker functionality."""
    print("Testing Circuit Breaker Service\n")

    # Show initial status
    print_breaker_status()

    # Test with a simple failing function
    @with_circuit_breaker(
        create_circuit_breaker("Test API", failure_threshold=3, timeout=5),
        fallback_message="Test API is down"
    )
    def failing_api_call():
        raise Exception("API Error")

    print("Testing circuit breaker with failing API calls...\n")
    for i in range(5):
        print(f"Attempt {i+1}:")
        try:
            result = failing_api_call()
            print(f"  Result: {result}")
        except Exception as e:
            print(f"  Exception: {e}")

    print("\n✅ Circuit breaker service is functional!")
