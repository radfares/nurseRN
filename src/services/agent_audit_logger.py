"""
Agent Audit Logger - Complete Traceability for All Agent Actions

Every agent action is logged to an immutable audit trail.
No exceptions. No excuses. Complete accountability.

Created: 2025-11-30
Updated: 2025-12-02 - Added response hash logging for verification
"""

import json
import logging
import re
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Thread-safe logging
_log_lock = threading.Lock()

logger = logging.getLogger(__name__)

# Broad pattern to catch OpenAI-style keys and similar variants
_KEY_RE = re.compile(r"sk-[A-Za-z0-9_\-]{3,}\*{0,}[A-Za-z0-9]{0,}")

def _sanitize_entry(entry: dict) -> dict:
    """
    Remove or redact sensitive tokens from all string fields in a log entry.
    Replaces detected API key patterns with the literal "REDACTED_API_KEY".
    """
    if not isinstance(entry, dict):
        return entry
    for k, v in list(entry.items()):
        if isinstance(v, str):
            try:
                entry[k] = _KEY_RE.sub("REDACTED_API_KEY", v)
            except Exception:
                # If regex fails for any reason, fall back to removing the field
                entry[k] = "[REDACTED]"
        # If nested dicts appear, sanitize recursively
        elif isinstance(v, dict):
            entry[k] = _sanitize_entry(v)
        # If lists contain strings or dicts, sanitize each element
        elif isinstance(v, list):
            new_list = []
            for item in v:
                if isinstance(item, str):
                    try:
                        new_list.append(_KEY_RE.sub("REDACTED_API_KEY", item))
                    except Exception:
                        new_list.append("[REDACTED]")
                elif isinstance(item, dict):
                    new_list.append(_sanitize_entry(item))
                else:
                    new_list.append(item)
            entry[k] = new_list
    return entry


class AuditLogger:
    """
    Audit logger for agent actions.

    Every agent must use this logger to record:
    - Queries received
    - Tool calls made
    - Tool results received
    - Validation checks performed
    - Responses generated
    - Errors encountered
    """

    def __init__(self, agent_key: str, agent_name: str):
        """
        Initialize audit logger for an agent.

        Args:
            agent_key: e.g., "medical_research"
            agent_name: e.g., "Medical Research Agent"
        """
        self.agent_key = agent_key
        self.agent_name = agent_name

        # Determine log file path
        audit_logs_dir = (
            Path(__file__).parent.parent.parent / ".claude" / "agent_audit_logs"
        )
        audit_logs_dir.mkdir(parents=True, exist_ok=True)

        # Log file: one per agent
        self.log_file = audit_logs_dir / f"{agent_key}_audit.jsonl"

        # Session tracking
        self.session_id = None
        self.project_name = None

        logger.info(f"AuditLogger initialized for {agent_name} → {self.log_file}")

    def _write_log_entry(self, entry: Dict[str, Any]) -> None:
        """
        Write a log entry to the audit file (thread-safe, append-only).

        Args:
            entry: Dictionary to log as JSON
        """
        # Add standard fields
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        entry["agent_name"] = self.agent_name
        entry["agent_key"] = self.agent_key

        if self.session_id:
            entry["session_id"] = self.session_id
        if self.project_name:
            entry["project_name"] = self.project_name

        # Sanitize entry to remove API keys and other sensitive tokens
        try:
            entry = _sanitize_entry(entry)
        except Exception:
            # If sanitization fails, avoid writing raw content
            entry = {"action_type": "log_sanitization_failed", "note": "Original entry redacted"}

        # Rotate log if needed
        self._rotate_log_if_needed()

        # Write to file (thread-safe, append-only)
        with _log_lock:
            try:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, default=str) + "\n")
            except Exception as e:
                logger.error(f"Failed to write audit log: {e}")

    def set_session(self, session_id: str, project_name: Optional[str] = None) -> None:
        """
        Set session context for all future log entries.

        Args:
            session_id: Unique identifier for this session
            project_name: Associated project name
        """
        self.session_id = session_id
        self.project_name = project_name

        # Log session start
        self._write_log_entry(
            {
                "action_type": "session_started",
                "session_id": session_id,
                "project_name": project_name,
            }
        )

    def log_query_received(
        self, query: str, project_name: Optional[str] = None
    ) -> None:
        """
        Log that agent received a query.

        Args:
            query: The user's query
            project_name: Associated project
        """
        if project_name:
            self.project_name = project_name

        self._write_log_entry(
            {
                "action_type": "query_received",
                "query": query,
                "query_length": len(query),
            }
        )

    def log_tool_call(
        self,
        tool_name: str,
        tool_method: str,
        tool_params: Dict[str, Any],
        circuit_breaker_status: Optional[str] = None,
    ) -> None:
        """
        Log that agent is calling a tool.

        Args:
            tool_name: e.g., "PubmedTools"
            tool_method: e.g., "search_pubmed"
            tool_params: Parameters passed to tool
            circuit_breaker_status: "closed", "open", "half-open"
        """
        self._write_log_entry(
            {
                "action_type": "tool_call",
                "tool_name": tool_name,
                "tool_method": tool_method,
                "tool_params": tool_params,
                "circuit_breaker_status": circuit_breaker_status or "unknown",
            }
        )

    def log_tool_result(
        self,
        tool_name: str,
        result: Any,
        error: Optional[Exception] = None,
        duration_ms: Optional[int] = None,
    ) -> None:
        """
        Log tool result received by agent.

        Args:
            tool_name: e.g., "PubmedTools"
            result: The result from the tool
            error: Exception if tool failed
            duration_ms: How long the call took
        """
        result_str = str(result)

        self._write_log_entry(
            {
                "action_type": "tool_result",
                "tool_name": tool_name,
                "result_type": "error" if error else "success",
                "result_length": len(result_str),
                "result_preview": result_str[:500],  # First 500 chars
                "error": str(error) if error else None,
                "duration_ms": duration_ms,
            }
        )

    def log_validation_check(
        self,
        check_type: str,  # "grounding", "sample_size", "path_traversal", etc.
        check_passed: bool,
        check_details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log validation check performed on agent output.

        Args:
            check_type: Type of validation performed
            check_passed: Whether validation passed
            check_details: Details of the validation
        """
        self._write_log_entry(
            {
                "action_type": "validation_check",
                "check_type": check_type,
                "check_passed": check_passed,
                "check_details": check_details or {},
            }
        )

    def log_grounding_check(
        self,
        pmids_cited: List[str],
        pmids_verified: List[str],
        hallucination_detected: bool,
    ) -> None:
        """
        Log grounding validation (PMID verification for citations).

        Args:
            pmids_cited: PMIDs mentioned in response
            pmids_verified: PMIDs confirmed from tool results
            hallucination_detected: Whether hallucination was found
        """
        unverified = set(pmids_cited) - set(pmids_verified)

        self._write_log_entry(
            {
                "action_type": "validation_check",
                "check_type": "grounding",
                "check_passed": not hallucination_detected,
                "check_details": {
                    "pmids_cited": pmids_cited,
                    "pmids_verified": pmids_verified,
                    "pmids_unverified": list(unverified),
                    "hallucination_detected": hallucination_detected,
                },
            }
        )

    def log_response_generated(
        self,
        response: str,
        response_type: str = "success",  # "success", "hallucination_detected", "error", "refusal"
        validation_passed: bool = True,
        duration_ms: Optional[int] = None,
    ) -> None:
        """
        Log agent response generated.

        Args:
            response: The response text
            response_type: Type of response
            validation_passed: Whether response passed all validation checks
            duration_ms: Total time for agent processing
        """
        import hashlib
        response_hash = hashlib.sha256(response.encode()).hexdigest()[:16]  # Short hash for verification

        self._write_log_entry(
            {
                "action_type": "response_generated",
                "response_length": len(response),
                "response_hash": response_hash,  # Hash instead of full preview
                "response_type": response_type,
                "validation_passed": validation_passed,
                "duration_ms": duration_ms,
            }
        )

    def log_decision(
        self, decision: str, rationale: str, alternatives: Optional[List[str]] = None
    ) -> None:
        """
        Log a decision made by the agent.

        Args:
            decision: What the agent decided
            rationale: Why it made that decision
            alternatives: Other options considered
        """
        self._write_log_entry(
            {
                "action_type": "decision",
                "decision": decision,
                "rationale": rationale,
                "alternatives": alternatives or [],
            }
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        stack_trace: Optional[str] = None,
        recovery_attempted: bool = False,
        recovery_status: Optional[str] = None,
    ) -> None:
        """
        Log an error encountered by the agent.

        Args:
            error_type: Exception class name
            error_message: Error message
            stack_trace: Full traceback
            recovery_attempted: Whether recovery was attempted
            recovery_status: "success" or "failed"
        """
        self._write_log_entry(
            {
                "action_type": "error",
                "error_type": error_type,
                "error_message": error_message,
                "error_stack_trace": stack_trace,
                "recovery_attempted": recovery_attempted,
                "recovery_status": recovery_status,
            }
        )

    def get_recent_entries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent audit log entries (for debugging).

        Args:
            limit: Number of recent entries to return

        Returns:
            List of recent log entries
        """
        entries = []

        if not self.log_file.exists():
            return entries

        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    entries.append(json.loads(line))
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")

        return entries

    def _rotate_log_if_needed(self) -> None:
        """
        Rotate log file if it exceeds size limit (10MB).
        """
        if self.log_file.exists() and self.log_file.stat().st_size > 10 * 1024 * 1024:  # 10MB
            rotated_file = self.log_file.with_name(
                f"{self.log_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            )
            self.log_file.rename(rotated_file)
            logger.info(f"Rotated audit log: {rotated_file}")

    def log_summary(self) -> None:
        """
        Log a summary of agent performance (call periodically).
        """
        entries = self.get_recent_entries(limit=100)

        if not entries:
            return

        # Count action types
        action_types = {}
        for entry in entries:
            action = entry.get("action_type", "unknown")
            action_types[action] = action_types.get(action, 0) + 1

        # Count validation results
        validation_passed = sum(
            1
            for e in entries
            if e.get("action_type") == "validation_check" and e.get("check_passed")
        )
        validation_failed = sum(
            1
            for e in entries
            if e.get("action_type") == "validation_check" and not e.get("check_passed")
        )

        # Count hallucinations
        hallucinations = sum(1 for e in entries if e.get("hallucination_detected"))

        self._write_log_entry(
            {
                "action_type": "summary",
                "action_types": action_types,
                "validation_passed": validation_passed,
                "validation_failed": validation_failed,
                "hallucinations_detected": hallucinations,
            }
        )


def get_audit_logger(agent_key: str, agent_name: str) -> AuditLogger:
    """Factory function to create audit logger for an agent."""
    return AuditLogger(agent_key, agent_name)


if __name__ == "__main__":
    # Test the audit logger
    logger = AuditLogger("test_agent", "Test Agent")
    logger.set_session("test_session_001", "test_project")

    logger.log_query_received("Find articles about CAUTI")
    logger.log_tool_call(
        "PubmedTools", "search_pubmed", {"query": "CAUTI", "max_results": 10}
    )
    logger.log_tool_result("PubmedTools", "[{'pmid': '12345678'}]")
    logger.log_grounding_check(
        pmids_cited=["12345678"],
        pmids_verified=["12345678"],
        hallucination_detected=False,
    )
    logger.log_response_generated(
        response="Found 1 article",
        response_type="success",
        validation_passed=True,
        duration_ms=2500,
    )

    print("✅ Audit log entries written to:", logger.log_file)
    print("\n📋 Recent entries:")
    for entry in logger.get_recent_entries(limit=5):
        print(json.dumps(entry, indent=2))
