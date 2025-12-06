"""
Base Workflow Template

Abstract base class for workflow templates.
Part of Phase 3: Workflow Templates
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import time

from src.orchestration.orchestrator import WorkflowOrchestrator, AgentResult
from src.orchestration.context_manager import ContextManager


@dataclass
class WorkflowResult:
    """Standardized result from a workflow execution"""
    workflow_name: str
    success: bool
    outputs: Dict[str, Any]
    execution_time: float
    steps_completed: int
    error: Optional[str] = None
    
    def summary(self) -> str:
        """Generate a human-readable summary"""
        if self.success:
            return (
                f"✅ {self.workflow_name} completed in {self.execution_time:.2f}s\n"
                f"   Steps: {self.steps_completed}\n"
                f"   Outputs: {', '.join(self.outputs.keys())}"
            )
        else:
            return (
                f"❌ {self.workflow_name} failed after {self.execution_time:.2f}s\n"
                f"   Error: {self.error}"
            )


class WorkflowTemplate(ABC):
    """
    Abstract base class for workflow templates.
    
    All concrete workflows (ResearchWorkflow, ParallelSearchWorkflow, etc.)
    should inherit from this class.
    """
    
    def __init__(
        self,
        orchestrator: WorkflowOrchestrator,
        context_manager: ContextManager,
        workflow_id: Optional[str] = None
    ):
        """
        Initialize workflow template.
        
        Args:
            orchestrator: WorkflowOrchestrator instance for agent execution
            context_manager: ContextManager for state persistence
            workflow_id: Optional workflow ID (auto-generated if not provided)
        """
        self.orchestrator = orchestrator
        self.context = context_manager
        self.workflow_id = workflow_id or f"{self.name}_{int(time.time())}"
        self._execution_start = None
        self._steps_completed = 0
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Workflow name (e.g., 'research_workflow')"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this workflow does"""
        pass
    
    @abstractmethod
    def validate_inputs(self, **kwargs) -> bool:
        """
        Validate input parameters before execution.
        
        Returns:
            True if inputs are valid, raises ValueError otherwise
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> WorkflowResult:
        """
        Execute the workflow with given inputs.
        
        Returns:
            WorkflowResult object with outputs and metadata
        """
        pass
    
    def _start_execution(self):
        """Mark the start of workflow execution"""
        self._execution_start = time.time()
        self._steps_completed = 0
    
    def _end_execution(self, outputs: Dict[str, Any], error: Optional[str] = None) -> WorkflowResult:
        """
        Mark the end of workflow execution and create result.
        
        Args:
            outputs: Dictionary of workflow outputs
            error: Optional error message if workflow failed
            
        Returns:
            WorkflowResult object
        """
        execution_time = time.time() - self._execution_start if self._execution_start else 0
        
        return WorkflowResult(
            workflow_name=self.name,
            success=(error is None),
            outputs=outputs,
            execution_time=execution_time,
            steps_completed=self._steps_completed,
            error=error
        )
    
    def _increment_step(self):
        """Increment the step counter"""
        self._steps_completed += 1
    
    def get_context(self) -> Dict[str, Any]:
        """Retrieve all context for this workflow"""
        return self.context.get_workflow_context(self.workflow_id)
    
    def clear_context(self):
        """Clear all context for this workflow"""
        self.context.clear_workflow(self.workflow_id)
