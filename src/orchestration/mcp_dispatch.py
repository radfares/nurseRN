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

from typing import Any, Union, Tuple
from .mcp import MCPMessage
# Adjusted import to use relative path within src/orchestration
from .safe_accessors import safe_get_content, safe_get_metadata

def dispatch_mcp(
    agent: Any, 
    task_msg: MCPMessage, 
    *, 
    return_raw: bool = False, 
    **agent_kwargs: Any
) -> Union[MCPMessage, Tuple[MCPMessage, Any]]:
    # Very light validation
    required = ["protocol_version", "message_type", "sender", "recipient", "task_id", "content"]
    for f in required:
        if getattr(task_msg, f, None) in (None, ""):
            error_msg = MCPMessage(
                protocol_version="1.0",
                message_type="error",
                sender="MCPDispatch",
                recipient=task_msg.sender,
                task_id=getattr(task_msg, "task_id", "unknown"),
                content=f"Invalid MCP message: missing {f}",
                metadata={"error_type": "validation"},
                timestamp_ms=task_msg.timestamp_ms,
            )
            return (error_msg, None) if return_raw else error_msg

    if task_msg.message_type != "task":
        import time
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

    # ✅ Adapter: keep your existing “string prompt” contract
    import time
    start_time = time.time()
    
    # ✅ Adapter: keep your existing “string prompt” contract
    query = task_msg.content
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
        error_msg = MCPMessage(
            protocol_version="1.0",
            message_type="error",
            sender="MCPDispatch",
            recipient=task_msg.sender,
            task_id=task_msg.task_id,
            content=str(e),
            metadata={
                "error_type": type(e).__name__,
                "latency_ms": latency_ms,
                "request_metadata": task_msg.metadata
            },
            timestamp_ms=int(time.time() * 1000),
        )
        return (error_msg, None) if return_raw else error_msg

    latency_ms = int((time.time() - start_time) * 1000)

    # You already have safe accessors—use them here
    result_msg = MCPMessage(
        protocol_version="1.0",
        message_type="result",
        sender=getattr(agent, "agent_name", getattr(agent, "name", "Agent")),
        recipient=task_msg.sender,
        task_id=task_msg.task_id,
        content=safe_get_content(raw),
        metadata={
            "agent_metadata": safe_get_metadata(raw),
            "request_metadata": task_msg.metadata,
            "latency_ms": latency_ms,
        },
        timestamp_ms=int(time.time() * 1000),
    )

    return (result_msg, raw) if return_raw else result_msg
