"""
Cache Utilities for RAG Pipeline
Provides thread-safe TTL caching mechanisms using cachetools.

Created: 2025-12-15
Phase: 2
"""

import logging
from typing import Any, Optional, Callable, Dict, TypeVar
from functools import wraps
import threading
from datetime import datetime, timedelta

try:
    from cachetools import TTLCache
except ImportError:
    # Fallback if cachetools not installed (though strictly required by requirements.txt)
    TTLCache = None

logger = logging.getLogger(__name__)

T = TypeVar("T")

class RAGCache:
    """
    Thread-safe TTL cache wrapper for RAG operations.
    
    Usage:
        cache = RAGCache(maxsize=100, ttl_seconds=300)
        cache.set("key", value)
        val = cache.get("key")
    """
    
    def __init__(self, maxsize: int = 100, ttl_seconds: int = 300):
        if TTLCache is None:
            logger.warning("cachetools not installed, caching disabled")
            self._cache = {}
            self._ttl_seconds = 0
            self._enabled = False
        else:
            self._cache = TTLCache(maxsize=maxsize, ttl=ttl_seconds)
            self._ttl_seconds = ttl_seconds
            self._enabled = True
            
        self._lock = threading.RLock()
        self._stats = {"hits": 0, "misses": 0}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self._enabled:
            return None
            
        with self._lock:
            try:
                if key in self._cache:
                    self._stats["hits"] += 1
                    return self._cache[key]
                self._stats["misses"] += 1
            except KeyError:
                self._stats["misses"] += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        if not self._enabled:
            return

        with self._lock:
            self._cache[key] = value

    def clear(self) -> None:
        """Clear the cache."""
        with self._lock:
            if self._enabled and hasattr(self._cache, "clear"):
                self._cache.clear()
            self._stats = {"hits": 0, "misses": 0}

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._lock:
            return self._stats.copy()

def cached_rag_result(ttl_seconds: int = 300):
    """Decorator for caching function results."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Create a specific cache for this function
        cache = RAGCache(maxsize=100, ttl_seconds=ttl_seconds)
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Simple key generation (naive)
            # For complex objects, might need better hashing
            key = f"{args}-{sorted(kwargs.items())}"
            
            cached_val = cache.get(key)
            if cached_val is not None:
                return cached_val
                
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        return wrapper
    return decorator
