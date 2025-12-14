"""
Conversation Context - In-memory state for multi-turn conversations.

Tracks conversation history, artifacts, and project state for intelligent orchestration.

Created: 2025-12-11
"""

import sqlite3
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime


@dataclass
class ConversationContext:
    """
    Maintains state across conversation turns.

    Attributes:
        project_name: Current active project
        project_db_path: Path to project SQLite database
        current_phase: Project phase (planning, literature_review, data_collection, etc.)
        completed_tasks: Set of completed agent:action pairs
        artifacts: Dict of named artifacts (picot, articles, synthesis, etc.)
        conversation_history: List of (role, content) tuples
        messages: Alias for conversation_history (for compatibility)
        metadata: Arbitrary metadata storage
    """
    project_name: str = "default"
    project_db_path: str = ""
    current_phase: str = "planning"
    completed_tasks: Set[str] = field(default_factory=set)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @property
    def messages(self) -> List[Dict[str, str]]:
        """Alias for conversation_history for compatibility."""
        return self.conversation_history

    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()

    def add_artifact(self, name: str, value: Any) -> None:
        """Store a named artifact (e.g., picot, search_results)."""
        self.artifacts[name] = {
            "value": value,
            "created_at": datetime.now().isoformat()
        }
        self.updated_at = datetime.now()

    def get_artifact(self, name: str) -> Optional[Any]:
        """Retrieve an artifact by name."""
        artifact = self.artifacts.get(name)
        if artifact:
            return artifact.get("value")
        return None

    def mark_task_completed(self, agent: str, action: str) -> None:
        """Mark an agent:action pair as completed."""
        self.completed_tasks.add(f"{agent}:{action}")
        self.updated_at = datetime.now()

    def is_task_completed(self, agent: str, action: str) -> bool:
        """Check if a task was already completed."""
        return f"{agent}:{action}" in self.completed_tasks

    def set_phase(self, phase: str) -> None:
        """Update current project phase."""
        self.current_phase = phase
        self.updated_at = datetime.now()

    def get_recent_history(self, n: int = 10) -> List[Dict[str, str]]:
        """Get the last n messages from conversation history."""
        return self.conversation_history[-n:]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary."""
        return {
            "project_name": self.project_name,
            "current_phase": self.current_phase,
            "completed_tasks": list(self.completed_tasks),
            "artifacts": self.artifacts,
            "conversation_history": self.conversation_history,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationContext":
        """Deserialize context from dictionary."""
        ctx = cls(
            project_name=data.get("project_name", "default"),
            current_phase=data.get("current_phase", "planning"),
            completed_tasks=set(data.get("completed_tasks", [])),
            artifacts=data.get("artifacts", {}),
            conversation_history=data.get("conversation_history", []),
            metadata=data.get("metadata", {})
        )
        if "created_at" in data:
            ctx.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            ctx.updated_at = datetime.fromisoformat(data["updated_at"])
        return ctx

    def clear(self) -> None:
        """Reset context to initial state."""
        self.completed_tasks.clear()
        self.artifacts.clear()
        self.conversation_history.clear()
        self.metadata.clear()
        self.current_phase = "planning"
        self.updated_at = datetime.now()

    def save_to_db(self) -> None:
        """Persist conversation to project database."""
        if not self.project_db_path:
            return  # No database path set, skip persistence

        try:
            conn = sqlite3.connect(self.project_db_path)
            cursor = conn.cursor()

            # Save each new message to conversations table
            for msg in self.conversation_history:
                # Check if message already saved (has db_id)
                if "db_id" in msg:
                    continue

                cursor.execute("""
                    INSERT INTO conversations (
                        agent_name, user_query, agent_response,
                        importance_level, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    "orchestrator",
                    msg['content'] if msg['role'] == 'user' else "",
                    msg['content'] if msg['role'] == 'assistant' else "",
                    "normal",
                    msg.get('timestamp', datetime.now().isoformat())
                ))

                # Mark as saved
                msg['db_id'] = cursor.lastrowid

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Warning: Could not save conversation to database: {e}")

    def load_from_db(self) -> None:
        """Load recent conversation history from database."""
        if not self.project_db_path:
            return  # No database path set, skip loading

        try:
            conn = sqlite3.connect(self.project_db_path)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT user_query, agent_response, created_at, id
                FROM conversations
                WHERE agent_name = 'orchestrator'
                ORDER BY created_at DESC
                LIMIT 10
            """)

            rows = cursor.fetchall()
            conn.close()

            # Load in reverse order (oldest first)
            for row in reversed(rows):
                user_query, agent_response, timestamp, db_id = row
                if user_query:
                    self.conversation_history.append({
                        "role": "user",
                        "content": user_query,
                        "timestamp": timestamp,
                        "db_id": db_id
                    })
                if agent_response:
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": agent_response,
                        "timestamp": timestamp,
                        "db_id": db_id
                    })

        except Exception as e:
            # Table might not exist yet, that's okay
            pass


__all__ = ['ConversationContext']
