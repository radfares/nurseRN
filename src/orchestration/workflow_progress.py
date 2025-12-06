"""
Workflow Progress Tracker

Provides real-time progress tracking for multi-step workflows.
Enables visibility into agent execution status during long-running operations.

Part of Orchestration Layer Enhancement
Created: 2025-12-05
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class ProgressState:
    """
    Immutable snapshot of workflow progress.
    
    Attributes:
        workflow_id: Unique identifier for the workflow
        workflow_name: Human-readable name
        total_steps: Total number of steps in workflow
        current_step: Currently executing step (0-indexed)
        current_description: Description of current activity
        start_time: Unix timestamp when workflow started
        partial_results: Results from completed steps
        is_cancelled: True if cancellation was requested
        is_complete: True if workflow finished (success or failure)
        error: Error message if workflow failed
    """
    workflow_id: str
    workflow_name: str = ""
    total_steps: int = 0
    current_step: int = 0
    current_description: str = ""
    start_time: float = 0.0
    partial_results: Dict[str, Any] = field(default_factory=dict)
    is_cancelled: bool = False
    is_complete: bool = False
    error: Optional[str] = None
    
    @property
    def elapsed_seconds(self) -> float:
        """Time elapsed since workflow started."""
        if self.start_time == 0.0:
            return 0.0
        return time.time() - self.start_time
    
    @property
    def progress_percent(self) -> float:
        """Progress as percentage (0.0 to 100.0)."""
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100.0


class WorkflowProgressTracker:
    """
    Thread-safe tracker for workflow progress.
    
    Provides methods to track, update, and query workflow state.
    Uses in-memory storage for performance (progress is ephemeral).
    
    Example:
        tracker = WorkflowProgressTracker()
        tracker.start_workflow("wf1", 3, "Research Workflow")
        tracker.update_step("wf1", 1, "Searching PubMed", {"articles": 5})
        status = tracker.get_status("wf1")
        print(f"Step {status.current_step}/{status.total_steps}")
    """
    
    def __init__(self):
        """Initialize the tracker with empty state storage."""
        self._states: Dict[str, ProgressState] = {}
        self._lock = threading.RLock()
    
    def start_workflow(
        self, 
        workflow_id: str, 
        total_steps: int, 
        name: str = ""
    ) -> None:
        """
        Begin tracking a new workflow.
        
        Args:
            workflow_id: Unique identifier for this workflow execution
            total_steps: Number of steps in the workflow
            name: Human-readable name for the workflow
        
        Raises:
            ValueError: If workflow_id already exists and is not complete
        """
        with self._lock:
            existing = self._states.get(workflow_id)
            if existing and not existing.is_complete:
                raise ValueError(f"Workflow {workflow_id} already in progress")
            
            self._states[workflow_id] = ProgressState(
                workflow_id=workflow_id,
                workflow_name=name,
                total_steps=total_steps,
                current_step=0,
                current_description="Starting workflow",
                start_time=time.time(),
                partial_results={},
                is_cancelled=False,
                is_complete=False,
                error=None
            )
    
    def update_step(
        self,
        workflow_id: str,
        step_num: int,
        description: str,
        partial_result: Any = None
    ) -> None:
        """
        Update the current step of a workflow.
        
        Args:
            workflow_id: Workflow to update
            step_num: New step number (1-indexed for display)
            description: Description of current activity
            partial_result: Optional result from this step
        
        Raises:
            KeyError: If workflow_id doesn't exist
            ValueError: If workflow is already complete
        """
        with self._lock:
            if workflow_id not in self._states:
                raise KeyError(f"Unknown workflow: {workflow_id}")
            
            state = self._states[workflow_id]
            if state.is_complete:
                raise ValueError(f"Workflow {workflow_id} is already complete")
            
            # Create new state (immutable pattern)
            new_results = dict(state.partial_results)
            if partial_result is not None:
                new_results[f"step_{step_num}"] = partial_result
            
            self._states[workflow_id] = ProgressState(
                workflow_id=workflow_id,
                workflow_name=state.workflow_name,
                total_steps=state.total_steps,
                current_step=step_num,
                current_description=description,
                start_time=state.start_time,
                partial_results=new_results,
                is_cancelled=state.is_cancelled,
                is_complete=False,
                error=None
            )
    
    def complete_workflow(
        self,
        workflow_id: str,
        final_result: Any = None
    ) -> None:
        """
        Mark a workflow as successfully completed.
        
        Args:
            workflow_id: Workflow to complete
            final_result: Optional final result to store
        
        Raises:
            KeyError: If workflow_id doesn't exist
        """
        with self._lock:
            if workflow_id not in self._states:
                raise KeyError(f"Unknown workflow: {workflow_id}")
            
            state = self._states[workflow_id]
            
            new_results = dict(state.partial_results)
            if final_result is not None:
                new_results["final"] = final_result
            
            self._states[workflow_id] = ProgressState(
                workflow_id=workflow_id,
                workflow_name=state.workflow_name,
                total_steps=state.total_steps,
                current_step=state.total_steps,  # Completed all steps
                current_description="Workflow complete",
                start_time=state.start_time,
                partial_results=new_results,
                is_cancelled=state.is_cancelled,
                is_complete=True,
                error=None
            )
    
    def fail_workflow(self, workflow_id: str, error: str) -> None:
        """
        Mark a workflow as failed.
        
        Args:
            workflow_id: Workflow that failed
            error: Error message describing the failure
        
        Raises:
            KeyError: If workflow_id doesn't exist
        """
        with self._lock:
            if workflow_id not in self._states:
                raise KeyError(f"Unknown workflow: {workflow_id}")
            
            state = self._states[workflow_id]
            
            self._states[workflow_id] = ProgressState(
                workflow_id=workflow_id,
                workflow_name=state.workflow_name,
                total_steps=state.total_steps,
                current_step=state.current_step,
                current_description=f"Failed: {error}",
                start_time=state.start_time,
                partial_results=state.partial_results,
                is_cancelled=state.is_cancelled,
                is_complete=True,
                error=error
            )
    
    def get_status(self, workflow_id: str) -> Optional[ProgressState]:
        """
        Get current status of a workflow.
        
        Args:
            workflow_id: Workflow to query
        
        Returns:
            ProgressState snapshot, or None if workflow doesn't exist
        """
        with self._lock:
            return self._states.get(workflow_id)
    
    def request_cancel(self, workflow_id: str) -> None:
        """
        Request cancellation of a workflow.
        
        The workflow should check is_cancelled() and stop gracefully.
        
        Args:
            workflow_id: Workflow to cancel
        
        Raises:
            KeyError: If workflow_id doesn't exist
        """
        with self._lock:
            if workflow_id not in self._states:
                raise KeyError(f"Unknown workflow: {workflow_id}")
            
            state = self._states[workflow_id]
            
            self._states[workflow_id] = ProgressState(
                workflow_id=workflow_id,
                workflow_name=state.workflow_name,
                total_steps=state.total_steps,
                current_step=state.current_step,
                current_description=state.current_description,
                start_time=state.start_time,
                partial_results=state.partial_results,
                is_cancelled=True,
                is_complete=state.is_complete,
                error=state.error
            )
    
    def is_cancelled(self, workflow_id: str) -> bool:
        """
        Check if a workflow has been cancelled.
        
        Args:
            workflow_id: Workflow to check
        
        Returns:
            True if cancellation was requested, False otherwise
        """
        with self._lock:
            state = self._states.get(workflow_id)
            if state is None:
                return False
            return state.is_cancelled
    
    def elapsed_time(self, workflow_id: str) -> float:
        """
        Get elapsed time for a workflow.
        
        Args:
            workflow_id: Workflow to query
        
        Returns:
            Elapsed time in seconds, or 0.0 if workflow doesn't exist
        """
        with self._lock:
            state = self._states.get(workflow_id)
            if state is None:
                return 0.0
            return state.elapsed_seconds
    
    def clear_completed(self) -> int:
        """
        Remove all completed workflows from memory.
        
        Returns:
            Number of workflows removed
        """
        with self._lock:
            to_remove = [
                wf_id for wf_id, state in self._states.items()
                if state.is_complete
            ]
            for wf_id in to_remove:
                del self._states[wf_id]
            return len(to_remove)
