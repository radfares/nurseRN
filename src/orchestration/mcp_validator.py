"""
MCP Message Validator

Validates MCP messages against versioned JSON schemas.
Provides content sanitization and semantic validation.

Part of Phase: MCP Message Validation
Created: 2025-12-13
"""

import re
import time
import unicodedata
import logging
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional, Union

import jsonschema
from jsonschema import Draft7Validator, ValidationError

from .mcp import MCPMessage
from .mcp_schemas import (
    MCP_SCHEMAS,
    SUPPORTED_VERSIONS,
    DEFAULT_VERSION,
    MAX_CONTENT_LENGTH
)

logger = logging.getLogger(__name__)

# Severity levels (matching project pattern from clinical_checks.py)
SEVERITY_LEVELS = ["error", "warning", "info"]

# Timestamp validation: reject if more than 30 days old or in the future
MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000  # 30 days in ms
MAX_FUTURE_MS = 5 * 60 * 1000  # 5 minutes tolerance for clock skew


@dataclass
class MCPValidationIssue:
    """
    Represents a single validation issue.

    Attributes:
        severity: One of 'error', 'warning', 'info'
        field: The field that failed validation
        message: Human-readable description of the issue
        suggestion: Actionable recommendation to fix
    """
    severity: str
    field: str
    message: str
    suggestion: str

    def __post_init__(self):
        """Validate severity level."""
        if self.severity not in SEVERITY_LEVELS:
            raise ValueError(
                f"Invalid severity '{self.severity}'. "
                f"Must be one of {SEVERITY_LEVELS}"
            )

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for serialization."""
        return {
            "severity": self.severity,
            "field": self.field,
            "message": self.message,
            "suggestion": self.suggestion
        }


@dataclass
class MCPValidationResult:
    """
    Result of validating an MCP message.

    Attributes:
        valid: True if validation passed (no errors)
        issues: List of MCPValidationIssue objects
        sanitized_message: Cleaned message if valid, None otherwise
    """
    valid: bool
    issues: List[MCPValidationIssue] = field(default_factory=list)
    sanitized_message: Optional[MCPMessage] = None

    def has_errors(self) -> bool:
        """Check if result contains any errors."""
        return any(issue.severity == "error" for issue in self.issues)

    def has_warnings(self) -> bool:
        """Check if result contains any warnings."""
        return any(issue.severity == "warning" for issue in self.issues)

    def error_summary(self) -> str:
        """Get summary of all error messages."""
        errors = [i.message for i in self.issues if i.severity == "error"]
        return "; ".join(errors) if errors else ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "valid": self.valid,
            "issues": [i.to_dict() for i in self.issues],
            "sanitized_message": asdict(self.sanitized_message) if self.sanitized_message else None
        }


class MCPMessageValidator:
    """
    Validates MCP messages against versioned JSON schemas.

    Features:
    - JSON schema validation per protocol version
    - Content length enforcement (50KB max)
    - Content sanitization (control chars, unicode normalization)
    - Timestamp range validation
    - Version compatibility checks

    Usage:
        validator = MCPMessageValidator()
        result = validator.validate(message)
        if result.valid:
            use(result.sanitized_message)
        else:
            handle_errors(result.issues)
    """

    def __init__(self, default_version: str = DEFAULT_VERSION):
        """
        Initialize validator.

        Args:
            default_version: Default protocol version if not specified in message
        """
        self.default_version = default_version
        self.schemas = MCP_SCHEMAS
        self._validators: Dict[str, Draft7Validator] = {}

    def validate(self, message: Union[MCPMessage, Dict[str, Any]]) -> MCPValidationResult:
        """
        Validate an MCP message against appropriate schema.

        Args:
            message: MCPMessage instance or dict representation

        Returns:
            MCPValidationResult with validation status, issues, and sanitized message
        """
        issues: List[MCPValidationIssue] = []

        # Convert to dict for schema validation
        if isinstance(message, MCPMessage):
            msg_dict = asdict(message)
        elif isinstance(message, dict):
            msg_dict = message.copy()
        else:
            return MCPValidationResult(
                valid=False,
                issues=[MCPValidationIssue(
                    severity="error",
                    field="message",
                    message=f"Invalid message type: {type(message).__name__}",
                    suggestion="Provide MCPMessage instance or dict"
                )]
            )

        # Get protocol version
        version = msg_dict.get("protocol_version", self.default_version)

        # Check version compatibility
        version_issues = self._validate_version(version)
        issues.extend(version_issues)

        # Use default schema if version unknown
        schema_version = version if version in self.schemas else self.default_version

        # JSON schema validation
        schema_issues = self._validate_schema(msg_dict, schema_version)
        issues.extend(schema_issues)

        # Content validation and sanitization
        content = msg_dict.get("content", "")
        content_issues, sanitized_content = self._validate_and_sanitize_content(content)
        issues.extend(content_issues)

        # Timestamp validation
        timestamp_ms = msg_dict.get("timestamp_ms", 0)
        timestamp_issues = self._validate_timestamp(timestamp_ms)
        issues.extend(timestamp_issues)

        # Determine validity (no errors)
        valid = not any(i.severity == "error" for i in issues)

        # Create sanitized message if valid
        sanitized_message = None
        if valid:
            sanitized_dict = msg_dict.copy()
            sanitized_dict["content"] = sanitized_content
            try:
                sanitized_message = MCPMessage(
                    protocol_version=sanitized_dict["protocol_version"],
                    message_type=sanitized_dict["message_type"],
                    sender=sanitized_dict["sender"],
                    recipient=sanitized_dict["recipient"],
                    task_id=sanitized_dict["task_id"],
                    content=sanitized_dict["content"],
                    metadata=sanitized_dict.get("metadata", {}),
                    timestamp_ms=sanitized_dict["timestamp_ms"]
                )
            except Exception as e:
                logger.warning(f"Failed to create sanitized message: {e}")
                sanitized_message = message if isinstance(message, MCPMessage) else None

        return MCPValidationResult(
            valid=valid,
            issues=issues,
            sanitized_message=sanitized_message
        )

    def _validate_version(self, version: str) -> List[MCPValidationIssue]:
        """Validate protocol version compatibility."""
        issues = []

        if not version:
            issues.append(MCPValidationIssue(
                severity="error",
                field="protocol_version",
                message="Missing protocol version",
                suggestion=f"Set protocol_version to '{self.default_version}'"
            ))
        elif version not in SUPPORTED_VERSIONS:
            issues.append(MCPValidationIssue(
                severity="warning",
                field="protocol_version",
                message=f"Unknown protocol version '{version}'",
                suggestion=f"Supported versions: {', '.join(SUPPORTED_VERSIONS)}"
            ))

        return issues

    def _validate_schema(self, msg_dict: Dict[str, Any], version: str) -> List[MCPValidationIssue]:
        """Validate message against JSON schema for given version."""
        issues = []

        validator = self._get_validator(version)
        if validator is None:
            issues.append(MCPValidationIssue(
                severity="error",
                field="protocol_version",
                message=f"No schema found for version '{version}'",
                suggestion=f"Use supported version: {', '.join(SUPPORTED_VERSIONS)}"
            ))
            return issues

        # Collect all schema validation errors
        for error in validator.iter_errors(msg_dict):
            # Extract field name from error path
            field = ".".join(str(p) for p in error.absolute_path) or "root"

            # Create user-friendly message
            if error.validator == "required":
                missing = list(error.validator_value)
                for f in missing:
                    if f not in msg_dict:
                        issues.append(MCPValidationIssue(
                            severity="error",
                            field=f,
                            message=f"Missing required field: {f}",
                            suggestion=f"Add '{f}' to message"
                        ))
            elif error.validator == "enum":
                issues.append(MCPValidationIssue(
                    severity="error",
                    field=field,
                    message=f"Invalid value for {field}: '{error.instance}'",
                    suggestion=f"Must be one of: {', '.join(error.validator_value)}"
                ))
            elif error.validator == "pattern":
                issues.append(MCPValidationIssue(
                    severity="error",
                    field=field,
                    message=f"Invalid format for {field}: '{error.instance}'",
                    suggestion=f"Must match pattern: {error.validator_value}"
                ))
            elif error.validator == "maxLength":
                issues.append(MCPValidationIssue(
                    severity="error",
                    field=field,
                    message=f"Field {field} exceeds maximum length ({error.validator_value})",
                    suggestion=f"Reduce {field} to {error.validator_value} characters or less"
                ))
            elif error.validator == "minLength":
                issues.append(MCPValidationIssue(
                    severity="error",
                    field=field,
                    message=f"Field {field} is empty or too short",
                    suggestion=f"Provide a non-empty value for {field}"
                ))
            elif error.validator == "type":
                issues.append(MCPValidationIssue(
                    severity="error",
                    field=field,
                    message=f"Invalid type for {field}: expected {error.validator_value}, got {type(error.instance).__name__}",
                    suggestion=f"Ensure {field} is of type {error.validator_value}"
                ))
            elif error.validator == "additionalProperties":
                issues.append(MCPValidationIssue(
                    severity="warning",
                    field=field,
                    message=f"Unknown field in message: {field}",
                    suggestion="Remove unknown fields or update to newer protocol version"
                ))
            else:
                # Generic error
                issues.append(MCPValidationIssue(
                    severity="error",
                    field=field,
                    message=str(error.message),
                    suggestion="Check message format against schema"
                ))

        return issues

    def _validate_and_sanitize_content(self, content: str) -> tuple[List[MCPValidationIssue], str]:
        """
        Validate content field and return sanitized version.

        Returns:
            Tuple of (issues list, sanitized content string)
        """
        issues = []
        sanitized = content

        # Check if content is string
        if not isinstance(content, str):
            issues.append(MCPValidationIssue(
                severity="error",
                field="content",
                message=f"Content must be string, got {type(content).__name__}",
                suggestion="Convert content to string"
            ))
            return issues, str(content) if content else ""

        # Check length (in bytes for accurate limit)
        content_bytes = len(content.encode("utf-8"))
        if content_bytes > MAX_CONTENT_LENGTH:
            issues.append(MCPValidationIssue(
                severity="error",
                field="content",
                message=f"Content exceeds maximum size ({content_bytes} bytes > {MAX_CONTENT_LENGTH} bytes)",
                suggestion=f"Reduce content to under {MAX_CONTENT_LENGTH} bytes (50KB)"
            ))

        # Check for empty content
        if not content or not content.strip():
            issues.append(MCPValidationIssue(
                severity="error",
                field="content",
                message="Content cannot be empty",
                suggestion="Provide a non-empty content string"
            ))
            return issues, content

        # Sanitize content
        sanitized = self._sanitize_content(content)

        # Warn if content was modified
        if sanitized != content:
            issues.append(MCPValidationIssue(
                severity="info",
                field="content",
                message="Content was sanitized (control characters removed)",
                suggestion="Use sanitized_message from validation result"
            ))

        return issues, sanitized

    def _sanitize_content(self, content: str) -> str:
        """
        Sanitize content by removing control characters and normalizing unicode.

        Preserves:
        - Newlines (\\n)
        - Tabs (\\t)
        - Carriage returns (\\r)

        Removes:
        - NULL bytes
        - Other control characters (0x00-0x1F except \\t, \\n, \\r)
        - Unicode control characters
        """
        if not content:
            return content

        # Normalize unicode (NFC form)
        content = unicodedata.normalize("NFC", content)

        # Remove control characters except \t, \n, \r
        # Control chars are 0x00-0x1F and 0x7F-0x9F
        def is_allowed(char: str) -> bool:
            if char in "\t\n\r":
                return True
            code = ord(char)
            # Allow printable characters and extended unicode
            return code >= 0x20 and code != 0x7F and not (0x80 <= code <= 0x9F)

        sanitized = "".join(c for c in content if is_allowed(c))

        return sanitized

    def _validate_timestamp(self, timestamp_ms: int) -> List[MCPValidationIssue]:
        """Validate timestamp is within acceptable range."""
        issues = []

        if not isinstance(timestamp_ms, int):
            issues.append(MCPValidationIssue(
                severity="error",
                field="timestamp_ms",
                message=f"Timestamp must be integer, got {type(timestamp_ms).__name__}",
                suggestion="Provide Unix timestamp in milliseconds as integer"
            ))
            return issues

        if timestamp_ms < 0:
            issues.append(MCPValidationIssue(
                severity="error",
                field="timestamp_ms",
                message="Timestamp cannot be negative",
                suggestion="Provide positive Unix timestamp in milliseconds"
            ))
            return issues

        current_ms = int(time.time() * 1000)

        # Check if too far in the future
        if timestamp_ms > current_ms + MAX_FUTURE_MS:
            issues.append(MCPValidationIssue(
                severity="warning",
                field="timestamp_ms",
                message="Timestamp is in the future (possible clock skew)",
                suggestion="Check system clock synchronization"
            ))

        # Check if too old
        if timestamp_ms < current_ms - MAX_AGE_MS:
            issues.append(MCPValidationIssue(
                severity="warning",
                field="timestamp_ms",
                message="Timestamp is more than 30 days old",
                suggestion="Use current timestamp for new messages"
            ))

        return issues

    def _get_validator(self, version: str) -> Optional[Draft7Validator]:
        """Get or create cached JSON schema validator for version."""
        if version not in self._validators:
            schema = self.schemas.get(version)
            if schema:
                self._validators[version] = Draft7Validator(schema)
        return self._validators.get(version)

    def get_supported_versions(self) -> List[str]:
        """Return list of supported protocol versions."""
        return SUPPORTED_VERSIONS.copy()

    def is_version_supported(self, version: str) -> bool:
        """Check if a protocol version is supported."""
        return version in SUPPORTED_VERSIONS
