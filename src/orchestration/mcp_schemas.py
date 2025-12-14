"""
MCP Message JSON Schemas

Defines JSON schemas for each MCP protocol version.
Used by MCPMessageValidator for schema-based validation.

Part of Phase: MCP Message Validation
Created: 2025-12-13
"""

from typing import Dict, Any

# Maximum content length in bytes (50KB)
MAX_CONTENT_LENGTH = 51200

# JSON Schema definitions for each MCP protocol version
MCP_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "1.0": {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "MCP Message v1.0",
        "description": "Model Context Protocol message envelope",
        "type": "object",
        "required": [
            "protocol_version",
            "message_type",
            "sender",
            "recipient",
            "task_id",
            "content",
            "metadata",
            "timestamp_ms"
        ],
        "properties": {
            "protocol_version": {
                "type": "string",
                "pattern": r"^\d+\.\d+$",
                "description": "Protocol version (e.g., '1.0')"
            },
            "message_type": {
                "type": "string",
                "enum": ["task", "result", "error"],
                "description": "Type of message"
            },
            "sender": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128,
                "description": "Sender identifier (agent name or 'user')"
            },
            "recipient": {
                "type": "string",
                "minLength": 1,
                "maxLength": 128,
                "description": "Recipient identifier (agent name or 'user')"
            },
            "task_id": {
                "type": "string",
                "pattern": r"^T-[a-f0-9]{10}$",
                "description": "Unique task identifier (T-{10 hex chars})"
            },
            "content": {
                "type": "string",
                "minLength": 1,
                "maxLength": MAX_CONTENT_LENGTH,
                "description": "Message payload (query or response)"
            },
            "metadata": {
                "type": "object",
                "description": "Additional context (latency, error_type, etc.)"
            },
            "timestamp_ms": {
                "type": "integer",
                "minimum": 0,
                "description": "Unix timestamp in milliseconds"
            }
        },
        "additionalProperties": False
    }
}

# Supported protocol versions (in order of preference)
SUPPORTED_VERSIONS = list(MCP_SCHEMAS.keys())

# Default version for new messages
DEFAULT_VERSION = "1.0"
