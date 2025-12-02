"""
Workflow Context for Guided Mode
Tracks state across multi-agent workflow.

Created: 2025-11-29 (Phase 1, Task 1)
Part of: TECHNICAL_ANALYSIS_AND_V1_ROADMAP.md implementation
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class WorkflowContext:
    """
    Shared state passed between agents in guided workflow.

    This class enforces the PICOT → Search → Calculate → Export workflow
    by tracking progress and validating state transitions.

    Attributes:
        project_name: Name of the active project
        picot_id: Database ID of current PICOT version
        picot_text: Full text of approved PICOT question
        search_query: Query used for literature search
        finding_ids: List of literature_finding IDs from database
        draft_id: Database ID of writing draft
        plan_id: Database ID of analysis plan
        sample_size: Calculated sample size
        statistical_method: Selected statistical test
        export_path: Path to exported PDF
        started_at: Timestamp when workflow began

    Example:
        >>> ctx = WorkflowContext(project_name="fall_prevention")
        >>> ctx.picot_text = "In elderly patients, does hourly rounding reduce falls?"
        >>> ctx.picot_id = 1
        >>> ctx.validate_for_search()  # Returns True
        >>> ctx.validate_for_export()  # Raises WorkflowError - missing prerequisites
    """

    project_name: str

    # Step 1: PICOT Development
    picot_text: Optional[str] = None
    picot_id: Optional[int] = None

    # Step 2: Literature Search
    search_query: Optional[str] = None
    finding_ids: List[int] = field(default_factory=list)

    # Step 3: Writing/Synthesis
    draft_id: Optional[int] = None

    # Step 4: Sample Size Calculation
    plan_id: Optional[int] = None
    sample_size: Optional[int] = None
    statistical_method: Optional[str] = None

    # Step 5: Export
    export_path: Optional[str] = None

    # Metadata
    started_at: datetime = field(default_factory=datetime.now)

    def validate_for_search(self) -> bool:
        """
        Ensure PICOT exists before searching literature.

        Returns:
            True if validation passes

        Raises:
            WorkflowError: If PICOT not created yet

        Example:
            >>> ctx = WorkflowContext(project_name="test")
            >>> ctx.validate_for_search()  # Raises WorkflowError
            >>> ctx.picot_text = "..."
            >>> ctx.validate_for_search()  # Returns True
        """
        if not self.picot_text:
            raise WorkflowError(
                "Cannot search - PICOT not created yet. "
                "Complete Step 1 (PICOT Development) first."
            )
        return True

    def validate_for_writing(self) -> bool:
        """
        Ensure literature findings exist before writing synthesis.

        Returns:
            True if validation passes

        Raises:
            WorkflowError: If no literature found

        Example:
            >>> ctx = WorkflowContext(project_name="test")
            >>> ctx.picot_text = "..."
            >>> ctx.validate_for_writing()  # Raises WorkflowError
            >>> ctx.finding_ids = [1, 2, 3]
            >>> ctx.validate_for_writing()  # Returns True
        """
        if not self.finding_ids:
            raise WorkflowError(
                "Cannot write - no literature found. "
                "Complete Step 2 (Literature Search) first."
            )
        return True

    def validate_for_calculation(self) -> bool:
        """
        Ensure PICOT and literature exist before sample size calculation.

        Returns:
            True if validation passes

        Raises:
            WorkflowError: If prerequisites missing
        """
        if not self.picot_text:
            raise WorkflowError(
                "Cannot calculate sample size - PICOT not created yet. "
                "Complete Step 1 first."
            )
        if not self.finding_ids:
            raise WorkflowError(
                "Cannot calculate sample size - no literature to support effect size. "
                "Complete Step 2 (Literature Search) first."
            )
        return True

    def validate_for_export(self) -> bool:
        """
        Ensure all prerequisites complete before export.

        Returns:
            True if validation passes

        Raises:
            WorkflowError: If any prerequisite missing

        Example:
            >>> ctx = WorkflowContext(project_name="test")
            >>> ctx.validate_for_export()  # Raises WorkflowError
            >>> # ... complete all steps ...
            >>> ctx.validate_for_export()  # Returns True
        """
        if not self.picot_text:
            raise WorkflowError("Cannot export - PICOT missing")
        if not self.finding_ids:
            raise WorkflowError("Cannot export - no literature findings")
        if not self.sample_size:
            raise WorkflowError("Cannot export - sample size not calculated")
        return True

    def get_progress(self) -> dict:
        """
        Get workflow completion status.

        Returns:
            Dictionary with step completion flags and percentage

        Example:
            >>> ctx = WorkflowContext(project_name="test")
            >>> progress = ctx.get_progress()
            >>> progress['percent_complete']
            0
            >>> ctx.picot_id = 1
            >>> progress = ctx.get_progress()
            >>> progress['percent_complete']
            20
        """
        steps_complete = [
            self.picot_id is not None,           # Step 1: PICOT
            len(self.finding_ids) > 0,            # Step 2: Search
            self.draft_id is not None,            # Step 3: Writing
            self.sample_size is not None,         # Step 4: Calculate
            self.export_path is not None          # Step 5: Export
        ]

        return {
            "step_1_picot": steps_complete[0],
            "step_2_search": steps_complete[1],
            "step_3_writing": steps_complete[2],
            "step_4_calculate": steps_complete[3],
            "step_5_export": steps_complete[4],
            "percent_complete": sum(steps_complete) * 20,  # 20% per step
            "steps_complete": sum(steps_complete),
            "total_steps": 5
        }

    def __str__(self) -> str:
        """String representation showing progress."""
        progress = self.get_progress()
        return (
            f"WorkflowContext(project='{self.project_name}', "
            f"progress={progress['percent_complete']}%, "
            f"steps={progress['steps_complete']}/{progress['total_steps']})"
        )


class WorkflowError(Exception):
    """
    Raised when workflow state is invalid for requested operation.

    Example:
        >>> ctx = WorkflowContext(project_name="test")
        >>> try:
        ...     ctx.validate_for_search()
        ... except WorkflowError as e:
        ...     print(e)
        Cannot search - PICOT not created yet. Complete Step 1 (PICOT Development) first.
    """
    pass
