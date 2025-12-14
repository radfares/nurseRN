"""
Workflow Registry - Central catalog of all available workflows
Enables dynamic workflow discovery and loading without code changes.

Phase 1: Schema Unification
Date: 2025-12-09
"""

from typing import Dict, List, Type, Optional
from src.workflows.base import WorkflowTemplate
from src.workflows.parallel_search import ParallelSearchWorkflow
from src.workflows.research_workflow import ResearchWorkflow
from src.workflows.timeline_planner import TimelinePlannerWorkflow
from src.workflows.validated_research_workflow import ValidatedResearchWorkflow


# Central registry of all workflows
WORKFLOW_REGISTRY: Dict[str, Type[WorkflowTemplate]] = {
    "parallel_search": ParallelSearchWorkflow,
    "research": ResearchWorkflow,
    "timeline_planner": TimelinePlannerWorkflow,
    "validated_research": ValidatedResearchWorkflow,
}


def get_workflow(name: str) -> Optional[Type[WorkflowTemplate]]:
    """
    Get a workflow class by name.

    Args:
        name: Workflow identifier (e.g., 'validated_research')

    Returns:
        Workflow class if found, None otherwise

    Example:
        >>> workflow_class = get_workflow('validated_research')
        >>> if workflow_class:
        ...     workflow = workflow_class(agents)
        ...     result = workflow.execute()
    """
    return WORKFLOW_REGISTRY.get(name)


def list_workflows() -> List[Dict[str, str]]:
    """
    List all available workflows with metadata.

    Returns:
        List of workflow info dictionaries with keys: name, class_name, description

    Example:
        >>> workflows = list_workflows()
        >>> for wf in workflows:
        ...     print(f"{wf['name']}: {wf['description']}")
    """
    workflows = []
    for name, workflow_class in WORKFLOW_REGISTRY.items():
        workflows.append({
            "name": name,
            "class_name": workflow_class.__name__,
            "description": workflow_class.__doc__.strip().split('\n')[0] if workflow_class.__doc__ else "No description available"
        })
    return workflows


def register_workflow(name: str, workflow_class: Type[WorkflowTemplate]) -> None:
    """
    Register a new workflow dynamically (for plugins/extensions).

    Args:
        name: Unique workflow identifier
        workflow_class: Workflow class inheriting from WorkflowTemplate

    Raises:
        ValueError: If name already exists or class is invalid

    Example:
        >>> class MyCustomWorkflow(WorkflowTemplate):
        ...     pass
        >>> register_workflow('my_custom', MyCustomWorkflow)
    """
    if name in WORKFLOW_REGISTRY:
        raise ValueError(f"Workflow '{name}' already registered")

    if not issubclass(workflow_class, WorkflowTemplate):
        raise ValueError(f"{workflow_class.__name__} must inherit from WorkflowTemplate")

    WORKFLOW_REGISTRY[name] = workflow_class


def workflow_exists(name: str) -> bool:
    """
    Check if a workflow is registered.

    Args:
        name: Workflow identifier

    Returns:
        True if workflow exists, False otherwise
    """
    return name in WORKFLOW_REGISTRY
