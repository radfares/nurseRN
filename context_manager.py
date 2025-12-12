"""
Context Manager for Workflow State

Provides SQLite-backed shared context storage for agent coordination.
This is Layer 3 (Context Management) in the orchestration architecture.

Part of Phase 1: Foundation
"""

import sqlite3
import json
from typing import Any, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import threading


class ContextManager:
    """
    Manages shared context across workflow executions.
    
    This enables stateless agents to share results via a persistent store.
    Uses SQLite for simplicity (suitable for single-node orchestration).
    """
    
    def __init__(self, db_path: str = "data/orchestration/workflow_context.db", default_ttl_seconds: int = 3600):
        """
        Initialize context manager with SQLite backend.
        
        Args:
            db_path: Path to SQLite database file
            default_ttl_seconds: Default time-to-live for context entries (1 hour)
        """
        self.db_path = db_path
        self.default_ttl = default_ttl_seconds
        self._lock = threading.RLock()  # Thread-safe operations
        
        # Ensure directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize schema
        self._initialize_schema()
    
    def _initialize_schema(self):
        """
        Create workflow_context table if not exists.
        
        Schema (idempotent):
        - workflow_id: Unique identifier for the workflow instance
        - agent_key: Which agent stored this result
        - context_key: Key for the stored value
        - context_value: JSON-serialized value
        - created_at: When this entry was created
        - expires_at: When this entry should be removed (TTL)
        """
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflow_context (
                    workflow_id TEXT NOT NULL,
                    agent_key TEXT NOT NULL,
                    context_key TEXT NOT NULL,
                    context_value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    PRIMARY KEY (workflow_id, agent_key, context_key)
                )
            """)
            
            # Index for expiration cleanup
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at 
                ON workflow_context(expires_at)
            """)
    
    def _get_connection(self) -> sqlite3.Connection:
        """
        Get SQLite connection with thread-safety.
        
        Returns:
            SQLite connection with row factory
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    
    def store_result(
        self,
        workflow_id: str,
        agent_key: str,
        context_key: str,
        value: Any,
        ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Store a result in the workflow context.
        
        Args:
            workflow_id: Unique workflow identifier
            agent_key: Agent that produced this result
            context_key: Key for this specific result
            value: Value to store (will be JSON-serialized)
            ttl_seconds: Time-to-live (defaults to class default)
        
        Raises:
            ValueError: If value cannot be JSON-serialized
        """
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl
        
        # Serialize value to JSON
        try:
            context_value = json.dumps(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Cannot JSON-serialize value: {e}")
        
        # Calculate expiration
        expires_at = datetime.now() + timedelta(seconds=ttl_seconds)
        
        # Store with thread safety
        with self._lock:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO workflow_context
                    (workflow_id, agent_key, context_key, context_value, expires_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (workflow_id, agent_key, context_key, context_value, expires_at))
                conn.commit()
    
    def get_result(
        self,
        workflow_id: str,
        agent_key: str,
        context_key: str
    ) -> Optional[Any]:
        """
        Retrieve a result from the workflow context.
        
        Args:
            workflow_id: Unique workflow identifier
            agent_key: Agent that produced the result
            context_key: Key for the specific result
        
        Returns:
            Deserialized value, or None if not found/expired
        """
        with self._lock:
            with self._get_connection() as conn:
                row = conn.execute("""
                    SELECT context_value, expires_at
                    FROM workflow_context
                    WHERE workflow_id = ? AND agent_key = ? AND context_key = ?
                """, (workflow_id, agent_key, context_key)).fetchone()
                
                if not row:
                    return None
                
                # Check expiration
                expires_at = datetime.fromisoformat(row["expires_at"])
                if datetime.now() > expires_at:
                    # Expired - return None
                    return None
                
                # Deserialize and return
                return json.loads(row["context_value"])
    
    def get_workflow_context(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get all non-expired context for a workflow.
        
        Args:
            workflow_id: Unique workflow identifier
        
        Returns:
            Dict mapping (agent_key, context_key) tuples to values
        """
        now = datetime.now()
        
        with self._lock:
            with self._get_connection() as conn:
                rows = conn.execute("""
                    SELECT agent_key, context_key, context_value, expires_at
                    FROM workflow_context
                    WHERE workflow_id = ?
                """, (workflow_id,)).fetchall()
                
                context = {}
                for row in rows:
                    # Check expiration in Python (datetime comparison)
                    expires_at = datetime.fromisoformat(row['expires_at'])
                    if now < expires_at:  # Not expired
                        key = f"{row['agent_key']}.{row['context_key']}"
                        context[key] = json.loads(row['context_value'])
                
                return context
    
    def clear_expired(self) -> int:
        """
        Remove expired context entries.
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    DELETE FROM workflow_context
                    WHERE expires_at <= CURRENT_TIMESTAMP
                """)
                conn.commit()
                return cursor.rowcount
    
    def clear_workflow(self, workflow_id: str) -> int:
        """
        Remove all context for a specific workflow.
        
        Args:
            workflow_id: Workflow to clear
        
        Returns:
            Number of entries removed
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    DELETE FROM workflow_context
                    WHERE workflow_id = ?
                """, (workflow_id,))
                conn.commit()
                return cursor.rowcount
