"""
Orchestration Module for Nursing Research Project
Handles workflow coordination and state management.
"""

from .workflow_context import WorkflowContext, WorkflowError

__all__ = ['WorkflowContext', 'WorkflowError']
