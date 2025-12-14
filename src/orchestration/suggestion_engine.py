"""
Suggestion Engine - Generates contextual next-step suggestions.

Provides intelligent suggestions based on conversation context,
completed tasks, and project phase.

Created: 2025-12-11
"""

import logging
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.orchestration.conversation_context import ConversationContext

logger = logging.getLogger(__name__)


# Phase-based suggestion templates
PHASE_SUGGESTIONS = {
    "planning": [
        "Define your research topic",
        "Generate a PICOT question",
        "Review project timeline",
        "Set project milestones"
    ],
    "literature_review": [
        "Search PubMed for articles",
        "Validate article quality",
        "Synthesize findings",
        "Export citations"
    ],
    "data_collection": [
        "Calculate sample size",
        "Select statistical tests",
        "Create data template",
        "Check upcoming deadlines"
    ],
    "analysis": [
        "Run statistical analysis",
        "Interpret results",
        "Create visualizations",
        "Compare to literature"
    ],
    "writing": [
        "Draft introduction",
        "Write methods section",
        "Summarize results",
        "Format citations"
    ],
    "review": [
        "Check project completion",
        "Review all milestones",
        "Prepare presentation",
        "Final edits"
    ]
}

# Task-based follow-up suggestions
TASK_FOLLOWUPS = {
    "writing:generate_picot": [
        "Search for related articles",
        "Refine the PICOT question",
        "Save PICOT to project"
    ],
    "medical_research:search_pubmed": [
        "Validate article quality",
        "Synthesize findings",
        "Search for more articles",
        "Save selected articles"
    ],
    "citation_validation:validate": [
        "Review evidence grades",
        "Exclude low-quality articles",
        "Synthesize high-quality findings"
    ],
    "data_analysis:calculate_sample_size": [
        "Review calculation assumptions",
        "Adjust parameters",
        "Document in methods section"
    ],
    "timeline:get_milestones": [
        "Update milestone status",
        "Add new milestone",
        "Check overdue tasks"
    ]
}


class SuggestionEngine:
    """
    Generates contextual suggestions for next steps.

    Uses conversation context to provide relevant, actionable
    suggestions that guide the user through their research workflow.
    """

    def __init__(self):
        """Initialize suggestion engine."""
        self.phase_suggestions = PHASE_SUGGESTIONS
        self.task_followups = TASK_FOLLOWUPS

    def generate_suggestions(
        self,
        context: "ConversationContext",
        max_suggestions: int = 4
    ) -> List[str]:
        """
        Generate contextual suggestions.

        Args:
            context: Current conversation context
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of suggestion strings
        """
        suggestions = []

        # 1. Check for task-specific follow-ups
        task_suggestions = self._get_task_followups(context)
        suggestions.extend(task_suggestions[:2])  # Max 2 task-specific

        # 2. Add phase-based suggestions
        phase_suggestions = self._get_phase_suggestions(context)
        remaining_slots = max_suggestions - len(suggestions)
        suggestions.extend(phase_suggestions[:remaining_slots])

        # 3. Add contextual suggestions based on artifacts
        if len(suggestions) < max_suggestions:
            artifact_suggestions = self._get_artifact_suggestions(context)
            remaining_slots = max_suggestions - len(suggestions)
            suggestions.extend(artifact_suggestions[:remaining_slots])

        # Deduplicate while preserving order
        seen = set()
        unique_suggestions = []
        for s in suggestions:
            if s not in seen:
                seen.add(s)
                unique_suggestions.append(s)

        return unique_suggestions[:max_suggestions]

    def _get_task_followups(self, context: "ConversationContext") -> List[str]:
        """Get follow-up suggestions based on completed tasks."""
        suggestions = []

        # Get most recent completed task
        completed = list(context.completed_tasks)
        if not completed:
            return suggestions

        # Check for follow-ups for recent tasks (last 3)
        for task in completed[-3:]:
            if task in self.task_followups:
                followups = self.task_followups[task]
                # Filter out already completed tasks
                for followup in followups:
                    if followup not in suggestions:
                        suggestions.append(followup)

        return suggestions

    def _get_phase_suggestions(self, context: "ConversationContext") -> List[str]:
        """Get suggestions based on current project phase."""
        phase = context.current_phase
        return self.phase_suggestions.get(phase, self.phase_suggestions["planning"])

    def _get_artifact_suggestions(self, context: "ConversationContext") -> List[str]:
        """Get suggestions based on available artifacts."""
        suggestions = []
        artifacts = context.artifacts

        # If we have PICOT but no search results
        if "generate_picot" in artifacts and "search_pubmed" not in artifacts:
            suggestions.append("Search PubMed with your PICOT question")

        # If we have search results but no validation
        if "search_pubmed" in artifacts and "validate" not in artifacts:
            suggestions.append("Validate the quality of found articles")

        # If we have validated articles but no synthesis
        if "validate" in artifacts and "synthesize" not in artifacts:
            suggestions.append("Synthesize your research findings")

        # If we have nothing, suggest starting
        if not artifacts:
            suggestions.append("Start by defining your research topic")

        return suggestions

    def get_help_suggestions(self) -> List[str]:
        """Get general help suggestions."""
        return [
            "Research a nursing topic",
            "Check project timeline",
            "Calculate sample size",
            "Get writing help",
            "Validate citations"
        ]


__all__ = ['SuggestionEngine']
