from dataclasses import dataclass, asdict
from typing import Any, Dict, Literal, Optional
import json, time, uuid

MessageType = Literal["task", "result", "error"]

@dataclass
class MCPMessage:
    protocol_version: str
    message_type: MessageType
    sender: str
    recipient: str
    task_id: str
    content: str
    metadata: Dict[str, Any]
    timestamp_ms: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPMessage":
        """
        Deserialize dict to MCPMessage.

        Args:
            data: Dictionary with MCP message fields

        Returns:
            MCPMessage instance

        Raises:
            KeyError: If required field is missing
            TypeError: If field type is incorrect
        """
        return cls(
            protocol_version=data["protocol_version"],
            message_type=data["message_type"],
            sender=data["sender"],
            recipient=data["recipient"],
            task_id=data["task_id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            timestamp_ms=data["timestamp_ms"]
        )

def new_task(sender: str, recipient: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> MCPMessage:
    return MCPMessage(
        protocol_version="1.0",
        message_type="task",
        sender=sender,
        recipient=recipient,
        task_id=f"T-{uuid.uuid4().hex[:10]}",
        content=content,
        metadata=metadata or {},
        timestamp_ms=int(time.time() * 1000),
    )

def to_json_line(msg: MCPMessage) -> str:
    # single-line JSON (good for STDIO/HTTP later)
    return json.dumps(asdict(msg), separators=(",", ":"))
