"""
Unit Tests for MCP Message Validator

Tests schema validation, content sanitization, and semantic checks.

Part of Phase: MCP Message Validation
Created: 2025-12-13
"""

import time
import pytest
from dataclasses import asdict

from src.orchestration.mcp import MCPMessage, new_task
from src.orchestration.mcp_validator import (
    MCPMessageValidator,
    MCPValidationResult,
    MCPValidationIssue,
    MAX_AGE_MS,
    MAX_FUTURE_MS
)
from src.orchestration.mcp_schemas import MAX_CONTENT_LENGTH, SUPPORTED_VERSIONS


@pytest.fixture
def validator():
    """Create a fresh validator instance for each test."""
    return MCPMessageValidator()


@pytest.fixture
def valid_task_message():
    """Create a valid task message."""
    return new_task(
        sender="user",
        recipient="NursingResearchAgent",
        content="What are the best practices for fall prevention?",
        metadata={"session_id": "test-123"}
    )


@pytest.fixture
def valid_result_message():
    """Create a valid result message."""
    return MCPMessage(
        protocol_version="1.0",
        message_type="result",
        sender="NursingResearchAgent",
        recipient="user",
        task_id="T-abc1234567",
        content="Here are the best practices for fall prevention...",
        metadata={"latency_ms": 150},
        timestamp_ms=int(time.time() * 1000)
    )


@pytest.fixture
def valid_error_message():
    """Create a valid error message."""
    return MCPMessage(
        protocol_version="1.0",
        message_type="error",
        sender="MCPDispatch",
        recipient="user",
        task_id="T-abc1234567",
        content="Agent execution failed: timeout",
        metadata={"error_type": "TimeoutError"},
        timestamp_ms=int(time.time() * 1000)
    )


class TestValidMessages:
    """Tests for valid MCP messages."""

    def test_valid_task_message(self, validator, valid_task_message):
        """Valid task message should pass validation."""
        result = validator.validate(valid_task_message)

        assert result.valid is True
        assert not result.has_errors()
        assert result.sanitized_message is not None
        assert result.sanitized_message.content == valid_task_message.content

    def test_valid_result_message(self, validator, valid_result_message):
        """Valid result message should pass validation."""
        result = validator.validate(valid_result_message)

        assert result.valid is True
        assert not result.has_errors()
        assert result.sanitized_message is not None

    def test_valid_error_message(self, validator, valid_error_message):
        """Valid error message should pass validation."""
        result = validator.validate(valid_error_message)

        assert result.valid is True
        assert not result.has_errors()
        assert result.sanitized_message is not None

    def test_valid_dict_message(self, validator):
        """Dictionary representation should also validate."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is True
        assert result.sanitized_message is not None


class TestMissingRequiredFields:
    """Tests for missing required fields."""

    @pytest.mark.parametrize("missing_field", [
        "protocol_version",
        "message_type",
        "sender",
        "recipient",
        "task_id",
        "content",
        "timestamp_ms"
    ])
    def test_missing_required_field(self, validator, missing_field):
        """Each missing required field should cause validation error."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }
        del msg_dict[missing_field]

        result = validator.validate(msg_dict)

        assert result.valid is False
        assert result.has_errors()
        error_fields = [i.field for i in result.issues if i.severity == "error"]
        assert missing_field in error_fields


class TestInvalidMessageType:
    """Tests for invalid message_type values."""

    def test_invalid_message_type(self, validator):
        """Invalid message_type should be rejected."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "invalid",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is False
        assert any(
            i.field == "message_type" and i.severity == "error"
            for i in result.issues
        )

    def test_empty_message_type(self, validator):
        """Empty message_type should be rejected."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is False


class TestContentValidation:
    """Tests for content field validation."""

    def test_content_too_long(self, validator):
        """Content exceeding 50KB should be rejected."""
        # Create content just over the limit
        long_content = "x" * (MAX_CONTENT_LENGTH + 100)

        msg = MCPMessage(
            protocol_version="1.0",
            message_type="task",
            sender="user",
            recipient="Agent",
            task_id="T-0123456789",
            content=long_content,
            metadata={},
            timestamp_ms=int(time.time() * 1000)
        )

        result = validator.validate(msg)

        assert result.valid is False
        assert any(
            i.field == "content" and "exceeds" in i.message.lower()
            for i in result.issues
        )

    def test_empty_content(self, validator):
        """Empty content should be rejected."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is False
        assert any(i.field == "content" for i in result.issues)

    def test_whitespace_only_content(self, validator):
        """Whitespace-only content should be rejected."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "   \n\t   ",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is False

    def test_content_at_max_length(self, validator):
        """Content at exactly max length should pass."""
        max_content = "x" * MAX_CONTENT_LENGTH

        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": max_content,
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is True


class TestContentSanitization:
    """Tests for content sanitization."""

    def test_control_chars_removed(self, validator):
        """Control characters should be removed from content."""
        # Include NULL byte and other control chars
        dirty_content = "Hello\x00World\x01Test\x02Query"

        msg = MCPMessage(
            protocol_version="1.0",
            message_type="task",
            sender="user",
            recipient="Agent",
            task_id="T-0123456789",
            content=dirty_content,
            metadata={},
            timestamp_ms=int(time.time() * 1000)
        )

        result = validator.validate(msg)

        assert result.valid is True
        assert result.sanitized_message is not None
        # Control chars should be removed
        assert "\x00" not in result.sanitized_message.content
        assert "\x01" not in result.sanitized_message.content
        assert "\x02" not in result.sanitized_message.content
        # Actual content should remain
        assert "Hello" in result.sanitized_message.content
        assert "World" in result.sanitized_message.content

    def test_newlines_preserved(self, validator):
        """Newlines should be preserved in content."""
        content_with_newlines = "Line 1\nLine 2\nLine 3"

        msg = MCPMessage(
            protocol_version="1.0",
            message_type="task",
            sender="user",
            recipient="Agent",
            task_id="T-0123456789",
            content=content_with_newlines,
            metadata={},
            timestamp_ms=int(time.time() * 1000)
        )

        result = validator.validate(msg)

        assert result.valid is True
        assert result.sanitized_message.content == content_with_newlines

    def test_tabs_preserved(self, validator):
        """Tabs should be preserved in content."""
        content_with_tabs = "Column1\tColumn2\tColumn3"

        msg = MCPMessage(
            protocol_version="1.0",
            message_type="task",
            sender="user",
            recipient="Agent",
            task_id="T-0123456789",
            content=content_with_tabs,
            metadata={},
            timestamp_ms=int(time.time() * 1000)
        )

        result = validator.validate(msg)

        assert result.valid is True
        assert result.sanitized_message.content == content_with_tabs

    def test_sanitization_info_message(self, validator):
        """When content is sanitized, info issue should be added."""
        dirty_content = "Clean\x00Content"

        msg = MCPMessage(
            protocol_version="1.0",
            message_type="task",
            sender="user",
            recipient="Agent",
            task_id="T-0123456789",
            content=dirty_content,
            metadata={},
            timestamp_ms=int(time.time() * 1000)
        )

        result = validator.validate(msg)

        assert result.valid is True
        assert any(
            i.severity == "info" and "sanitized" in i.message.lower()
            for i in result.issues
        )


class TestTaskIdFormat:
    """Tests for task_id format validation."""

    def test_invalid_task_id_format(self, validator):
        """Invalid task_id format should be rejected."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "invalid-task-id",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is False
        assert any(i.field == "task_id" for i in result.issues)

    def test_task_id_wrong_prefix(self, validator):
        """Task ID with wrong prefix should be rejected."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "X-0123456789",  # Wrong prefix
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is False

    def test_task_id_wrong_length(self, validator):
        """Task ID with wrong hex length should be rejected."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-012345",  # Too short
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is False

    def test_valid_task_id(self, validator):
        """Valid task ID should pass."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-abcdef1234",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is True


class TestTimestampValidation:
    """Tests for timestamp validation."""

    def test_timestamp_in_future(self, validator):
        """Future timestamp should generate warning."""
        future_ts = int(time.time() * 1000) + (10 * 60 * 1000)  # 10 minutes ahead

        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": future_ts
        }

        result = validator.validate(msg_dict)

        # Should still be valid (warning, not error)
        assert result.valid is True
        assert result.has_warnings()
        assert any(
            i.field == "timestamp_ms" and "future" in i.message.lower()
            for i in result.issues
        )

    def test_timestamp_too_old(self, validator):
        """Very old timestamp should generate warning."""
        old_ts = int(time.time() * 1000) - (45 * 24 * 60 * 60 * 1000)  # 45 days ago

        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": old_ts
        }

        result = validator.validate(msg_dict)

        # Should still be valid (warning, not error)
        assert result.valid is True
        assert result.has_warnings()
        assert any(
            i.field == "timestamp_ms" and "old" in i.message.lower()
            for i in result.issues
        )

    def test_negative_timestamp(self, validator):
        """Negative timestamp should be rejected."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": -1000
        }

        result = validator.validate(msg_dict)

        assert result.valid is False
        assert any(i.field == "timestamp_ms" for i in result.issues)


class TestVersionValidation:
    """Tests for protocol version validation."""

    def test_unknown_version_warning(self, validator):
        """Unknown version should generate warning but still validate."""
        msg_dict = {
            "protocol_version": "2.0",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        # Should validate using default schema
        assert result.valid is True
        assert result.has_warnings()
        assert any(
            i.field == "protocol_version" and "unknown" in i.message.lower()
            for i in result.issues
        )

    def test_version_registry_selection(self, validator):
        """Correct schema should be selected based on version."""
        # Currently only 1.0 is supported
        assert validator.is_version_supported("1.0")
        assert not validator.is_version_supported("2.0")
        assert validator.get_supported_versions() == SUPPORTED_VERSIONS

    def test_empty_version(self, validator):
        """Empty version should cause error."""
        msg_dict = {
            "protocol_version": "",
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.valid is False


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_invalid_input_type(self, validator):
        """Non-dict, non-MCPMessage input should be rejected."""
        result = validator.validate("not a message")

        assert result.valid is False
        assert any(
            "invalid message type" in i.message.lower()
            for i in result.issues
        )

    def test_none_input(self, validator):
        """None input should be rejected."""
        result = validator.validate(None)

        assert result.valid is False

    def test_validation_result_serialization(self, validator, valid_task_message):
        """ValidationResult should serialize to dict properly."""
        result = validator.validate(valid_task_message)

        result_dict = result.to_dict()

        assert "valid" in result_dict
        assert "issues" in result_dict
        assert "sanitized_message" in result_dict
        assert isinstance(result_dict["issues"], list)

    def test_validation_issue_serialization(self):
        """MCPValidationIssue should serialize properly."""
        issue = MCPValidationIssue(
            severity="error",
            field="content",
            message="Content too long",
            suggestion="Shorten content"
        )

        issue_dict = issue.to_dict()

        assert issue_dict["severity"] == "error"
        assert issue_dict["field"] == "content"

    def test_invalid_severity_raises(self):
        """Invalid severity should raise ValueError."""
        with pytest.raises(ValueError):
            MCPValidationIssue(
                severity="critical",  # Invalid
                field="content",
                message="Test",
                suggestion="Test"
            )


class TestValidationResultMethods:
    """Tests for MCPValidationResult methods."""

    def test_error_summary(self, validator):
        """error_summary should return concatenated error messages."""
        msg_dict = {
            "protocol_version": "1.0",
            "message_type": "invalid",
            "sender": "",
            "recipient": "Agent",
            "task_id": "bad-id",
            "content": "",
            "metadata": {},
            "timestamp_ms": -1
        }

        result = validator.validate(msg_dict)

        summary = result.error_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_has_errors_false_for_valid(self, validator, valid_task_message):
        """has_errors should return False for valid message."""
        result = validator.validate(valid_task_message)

        assert result.has_errors() is False

    def test_has_warnings_true_for_warnings(self, validator):
        """has_warnings should return True when warnings present."""
        msg_dict = {
            "protocol_version": "9.9",  # Unknown version = warning
            "message_type": "task",
            "sender": "user",
            "recipient": "Agent",
            "task_id": "T-0123456789",
            "content": "Test query",
            "metadata": {},
            "timestamp_ms": int(time.time() * 1000)
        }

        result = validator.validate(msg_dict)

        assert result.has_warnings() is True
