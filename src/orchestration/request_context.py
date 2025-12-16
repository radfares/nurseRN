"""
Request Context - Immutable state for a single request lifecycle.

Tracks the canonical query, intent, and metadata throughout retries and fallbacks.
Ensures state stability across orchestration layers.

Created: 2025-12-16
Phase 1: Input & State Stability
"""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from datetime import datetime


@dataclass(frozen=True)
class RequestContext:
    """
    Immutable context for a single request execution.

    Created after intent classification and plan validation.
    Passed through all retries, fallbacks, and MCP dispatch calls.

    Attributes:
        request_id: Unique identifier for this request (UUID)
        query: The canonical user query (must not be empty)
        intent: Classified intent (e.g., "generate_picot", "search_literature")
        metadata: Additional context (user_id, session_id, etc.)
        created_at: Timestamp of request creation
    """
    request_id: str
    query: str
    intent: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate required fields."""
        if not self.query or not self.query.strip():
            raise ValueError("RequestContext.query cannot be empty")
        if not self.request_id:
            raise ValueError("RequestContext.request_id cannot be empty")

    @classmethod
    def create(
        cls,
        query: str,
        intent: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> "RequestContext":
        """
        Factory method to create a new RequestContext with auto-generated ID.

        Args:
            query: The user's canonical query
            intent: The classified intent
            metadata: Optional metadata dictionary

        Returns:
            Immutable RequestContext instance

        Raises:
            ValueError: If query is empty
        """
        return cls(
            request_id=f"req_{uuid.uuid4().hex[:12]}",
            query=query.strip(),
            intent=intent,
            metadata=metadata or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for logging and MCP metadata."""
        return {
            "request_id": self.request_id,
            "query": self.query,
            "intent": self.intent,
            "metadata": self.metadata,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RequestContext":
        """Deserialize from dictionary."""
        return cls(
            request_id=data["request_id"],
            query=data["query"],
            intent=data.get("intent", "unknown"),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", datetime.now().isoformat())
        )


__all__ = ['RequestContext']
