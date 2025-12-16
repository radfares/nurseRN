"""
MCP Dispatch - Centralized Agent Execution Gateway

# All agent execution must go through dispatch_mcp (avoid double runs)

This module is the ONLY sanctioned entry point for running agents.
Orchestrators (WorkflowOrchestrator, IntelligentOrchestrator) must NOT
call agent.run(), agent.agent.run(), or run_with_grounding_check() directly.

MCP Contract:
1. Wrap query in MCPMessage via new_task()
2. Call dispatch_mcp(agent, task_msg)
3. Receive MCPMessage with message_type="result" or "error"
4. Unwrap content/metadata from result envelope

This ensures:
- Single execution per request (no double runs)
- Consistent task_id tracing
- Uniform error handling
- Latency tracking
"""

import time
import logging
from typing import Any, Union, Tuple, Optional

from .mcp import MCPMessage
from .mcp_validator import MCPMessageValidator, MCPValidationResult
# Adjusted import to use relative path within src/orchestration
from .safe_accessors import safe_get_content, safe_get_metadata
from .request_context import RequestContext

logger = logging.getLogger(__name__)

# Singleton validator instance
_validator = MCPMessageValidator()

def _create_validation_error(
    task_msg: MCPMessage,
    validation_result: MCPValidationResult
) -> MCPMessage:
    """Create error MCPMessage from validation result."""
    return MCPMessage(
        protocol_version="1.0",
        message_type="error",
        sender="MCPDispatch",
        recipient=getattr(task_msg, "sender", "unknown"),
        task_id=getattr(task_msg, "task_id", "unknown"),
        content=f"Invalid MCP message: {validation_result.error_summary()}",
        metadata={
            "error_type": "validation",
            "validation_issues": [i.to_dict() for i in validation_result.issues]
        },
        timestamp_ms=int(time.time() * 1000),
    )


def dispatch_mcp(
    agent: Any,
    task_msg: MCPMessage,
    *,
    request_ctx: Optional[RequestContext] = None,
    return_raw: bool = False,
    **agent_kwargs: Any
) -> Union[MCPMessage, Tuple[MCPMessage, Any]]:
    """
    Central dispatch for agent execution via MCP protocol.

    Args:
        agent: Agent instance to execute
        task_msg: MCP task message
        request_ctx: Optional immutable request context for tracing
        return_raw: If True, return (MCPMessage, raw_response) tuple
        **agent_kwargs: Additional kwargs for agent execution

    Returns:
        MCPMessage (result or error), or tuple if return_raw=True
    """
    # Phase 1: Log request_id if available
    request_id = None
    if request_ctx:
        request_id = request_ctx.request_id
        logger.info(f"[{request_id}] Dispatching to agent via MCP")

    # Validate incoming message using MCPMessageValidator
    validation_result = _validator.validate(task_msg)

    if not validation_result.valid:
        logger.warning(
            f"MCP validation failed for task {getattr(task_msg, 'task_id', 'unknown')}: "
            f"{validation_result.error_summary()}"
        )
        error_msg = _create_validation_error(task_msg, validation_result)
        return (error_msg, None) if return_raw else error_msg

    # Use sanitized message if available
    if validation_result.sanitized_message:
        task_msg = validation_result.sanitized_message

    # Additional check: dispatch_mcp only handles task messages
    if task_msg.message_type != "task":
        error_msg = MCPMessage(
            protocol_version="1.0",
            message_type="error",
            sender="MCPDispatch",
            recipient=task_msg.sender,
            task_id=task_msg.task_id,
            content=f"dispatch_mcp expected message_type='task' but got '{task_msg.message_type}'",
            metadata={"error_type": "validation"},
            timestamp_ms=int(time.time() * 1000),
        )
        return (error_msg, None) if return_raw else error_msg

    # Phase 1: CRITICAL GUARD - Abort if query is empty
    query = task_msg.content
    if not query or not query.strip():
        error_msg = MCPMessage(
            protocol_version="1.0",
            message_type="error",
            sender="MCPDispatch",
            recipient=task_msg.sender,
            task_id=task_msg.task_id,
            content="Empty query detected - aborting dispatch to prevent invalid execution",
            metadata={
                "error_type": "empty_query",
                "request_id": request_id,
            },
            timestamp_ms=int(time.time() * 1000),
        )
        logger.error(
            f"[{request_id}] ABORT: Empty query detected in task {task_msg.task_id}. "
            "This indicates a state propagation bug in the orchestrator."
        )
        return (error_msg, None) if return_raw else error_msg

    # ✅ Adapter: keep your existing "string prompt" contract
    start_time = time.time()
    raw = None

    try:
        if hasattr(agent, "run_with_grounding_check"):
            # Primary method with grounding (BaseAgent subclasses)
            raw = agent.run_with_grounding_check(query, **agent_kwargs)
        elif hasattr(agent, "agent") and hasattr(agent.agent, "run"):
            # Wrapper object
            raw = agent.agent.run(query, **agent_kwargs)
        elif hasattr(agent, "run"):
            # Direct agent
            raw = agent.run(query, **agent_kwargs)
        else:
            raise ValueError(f"Agent {getattr(agent, 'agent_name', 'Unknown')} has no compatible run method")

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        error_metadata = {
            "error_type": type(e).__name__,
            "latency_ms": latency_ms,
            "request_metadata": task_msg.metadata
        }
        if request_id:
            error_metadata["request_id"] = request_id

        error_msg = MCPMessage(
            protocol_version="1.0",
            message_type="error",
            sender="MCPDispatch",
            recipient=task_msg.sender,
            task_id=task_msg.task_id,
            content=str(e),
            metadata=error_metadata,
            timestamp_ms=int(time.time() * 1000),
        )
        return (error_msg, None) if return_raw else error_msg

    latency_ms = int((time.time() - start_time) * 1000)

    # You already have safe accessors—use them here
    result_metadata = {
        "agent_metadata": safe_get_metadata(raw),
        "request_metadata": task_msg.metadata,
        "latency_ms": latency_ms,
    }
    if request_id:
        result_metadata["request_id"] = request_id

    result_msg = MCPMessage(
        protocol_version="1.0",
        message_type="result",
        sender=getattr(agent, "agent_name", getattr(agent, "name", "Agent")),
        recipient=task_msg.sender,
        task_id=task_msg.task_id,
        content=safe_get_content(raw),
        metadata=result_metadata,
        timestamp_ms=int(time.time() * 1000),
    )

    if request_id:
        logger.info(f"[{request_id}] Agent execution completed in {latency_ms}ms")

    return (result_msg, raw) if return_raw else result_msg
