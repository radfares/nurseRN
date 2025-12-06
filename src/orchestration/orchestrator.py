"""
Workflow Orchestrator

Executes agents and manages workflow lifecycle.
This is Layer 2 (Agent Orchestration) in the orchestration architecture.

Part of Phase 1: Foundation
"""

import concurrent.futures
import logging
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import time

from src.orchestration.context_manager import ContextManager
from src.orchestration.safe_accessors import safe_get_content, safe_get_messages, safe_get_metadata
from src.orchestration.log_sanitizer import sanitize_log_entry

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class AgentResult:
    """Standardized result from an agent execution"""
    agent_name: str
    success: bool
    content: Optional[str] = None
    metadata: Dict[str, Any] = None
    error: Optional[str] = None
    execution_time: float = 0.0

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class WorkflowOrchestrator:
    """
    Orchestrates agent execution for single and parallel workflows.
    
    Features:
    - Single agent execution
    - Parallel execution (ThreadPoolExecutor)
    - Result aggregation
    - Context management integration
    - Graceful failure handling
    """
    
    def __init__(self, context_manager: ContextManager):
        """
        Initialize orchestrator with context manager.
        
        Args:
            context_manager: Instance of ContextManager for state persistence
        """
        self.context_manager = context_manager
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    
    def execute_single_agent(
        self, 
        agent: Any, 
        query: str, 
        workflow_id: str,
        **kwargs
    ) -> AgentResult:
        """
        Execute a single agent synchronously.
        
        Args:
            agent: The agent instance to run
            query: User query
            workflow_id: ID of the current workflow
            **kwargs: Additional arguments for the agent
            
        Returns:
            AgentResult object
        """
        start_time = time.time()
        agent_name = getattr(agent, "name", "UnknownAgent")
        
        try:
            # Log start (sanitized)
            logger.info(sanitize_log_entry(f"Starting execution for agent {agent_name}"))
            
            # Execute agent using safe method hierarchy:
            # 1. run_with_grounding_check (preferred - includes validation)
            # 2. print_response (standard interface)
            # 3. agent.run (raw agno method - last resort)
            response = None
            content = None
            
            if hasattr(agent, 'run_with_grounding_check'):
                # Use grounding-checked method if available
                result = agent.run_with_grounding_check(query, **kwargs)
                content = result.get("content") if isinstance(result, dict) else str(result)
            elif hasattr(agent, 'agent') and hasattr(agent.agent, 'run'):
                # BaseAgent pattern: use inner agent.run but capture output
                response = agent.agent.run(query, **kwargs)
                content = safe_get_content(response)
            elif hasattr(agent, 'run'):
                # Direct run method (MockAgent or simple agents)
                response = agent.run(query, **kwargs)
                content = safe_get_content(response) if response else str(response)
            else:
                raise ValueError(f"Agent {agent_name} has no compatible run method")
            
            # Extract metadata safely
            metadata = safe_get_metadata(response) if response else {}
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Store result in context
            self.context_manager.store_result(
                workflow_id=workflow_id,
                agent_key=agent_name,
                context_key="last_result",
                value={
                    "content": content,
                    "metadata": metadata,
                    "timestamp": time.time()
                }
            )
            
            return AgentResult(
                agent_name=agent_name,
                success=True,
                content=content,
                metadata=metadata,
                execution_time=duration
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            logger.error(f"Agent {agent_name} failed: {error_msg}")
            
            return AgentResult(
                agent_name=agent_name,
                success=False,
                error=error_msg,
                execution_time=duration
            )

    def execute_parallel(
        self,
        agents: List[Any],
        query: str,
        workflow_id: str,
        timeout_seconds: int = 30
    ) -> Dict[str, AgentResult]:
        """
        Execute multiple agents in parallel.
        
        Args:
            agents: List of agent instances
            query: User query
            workflow_id: ID of the current workflow
            timeout_seconds: Max time to wait for all agents
            
        Returns:
            Dict mapping agent names to AgentResults
        """
        results = {}
        futures = {}
        
        # Submit all tasks
        for agent in agents:
            agent_name = getattr(agent, "name", "UnknownAgent")
            future = self._executor.submit(
                self.execute_single_agent,
                agent=agent,
                query=query,
                workflow_id=workflow_id
            )
            futures[future] = agent_name
            
        # Wait for completion or timeout
        done, not_done = concurrent.futures.wait(
            futures.keys(),
            timeout=timeout_seconds,
            return_when=concurrent.futures.ALL_COMPLETED
        )
        
        # Process completed tasks
        for future in done:
            agent_name = futures[future]
            try:
                result = future.result()
                results[agent_name] = result
            except Exception as e:
                # This should rarely happen as execute_single_agent catches exceptions
                logger.error(f"Critical failure in parallel execution for {agent_name}: {e}")
                results[agent_name] = AgentResult(
                    agent_name=agent_name,
                    success=False,
                    error=f"System error: {str(e)}"
                )
                
        # Handle timeouts
        for future in not_done:
            agent_name = futures[future]
            logger.warning(f"Agent {agent_name} timed out after {timeout_seconds}s")
            results[agent_name] = AgentResult(
                agent_name=agent_name,
                success=False,
                error="Execution timed out"
            )
            # We can't easily kill the thread, but we stop waiting for it
            
        return results

    def aggregate_results(self, results: Dict[str, AgentResult]) -> str:
        """
        Simple aggregation of multiple agent results.
        
        Args:
            results: Dict of agent results
            
        Returns:
            Combined string summary
        """
        summary_parts = []
        
        for agent_name, result in results.items():
            if result.success:
                summary_parts.append(f"--- {agent_name} ---\n{result.content}")
            else:
                summary_parts.append(f"--- {agent_name} ---\nFAILED: {result.error}")
                
        return "\n\n".join(summary_parts)
