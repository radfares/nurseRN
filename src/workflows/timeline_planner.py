"""
Timeline Planner Workflow Template

Generates project timelines with milestones.
Part of Phase 3: Workflow Templates
"""

from typing import Any, Dict
from datetime import datetime, timedelta
from src.workflows.base import WorkflowTemplate, WorkflowResult
# MockAgent import removed - only needed for testing


class TimelinePlannerWorkflow(WorkflowTemplate):
    """
    Timeline Planner: Generate project timeline with milestones
    
    Creates a complete project timeline for capstone/DNP projects.
    """
    
    @property
    def name(self) -> str:
        return "timeline_planner"
    
    @property
    def description(self) -> str:
        return "Generate project timeline with milestones for capstone/DNP projects"
    
    def validate_inputs(self, **kwargs) -> bool:
        """Validate required inputs"""
        required = ["project_type", "start_date", "end_date"]
        for param in required:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        return True
    
    def execute(self, **kwargs) -> WorkflowResult:
        """
        Generate project timeline.
        
        Args:
            project_type: Type of project (e.g., "DNP Capstone")
            start_date: Project start date (str, YYYY-MM-DD)
            end_date: Project end date (str, YYYY-MM-DD)
            requirements: Optional list of requirements
        
        Returns:
            WorkflowResult with timeline and milestones
        """
        self._start_execution()
        outputs = {}
        
        try:
            self.validate_inputs(**kwargs)
            
            project_type = kwargs["project_type"]
            start_date = kwargs["start_date"]
            end_date = kwargs["end_date"]
            requirements = kwargs.get("requirements", [])
            
            # Step 1: Create timeline
            self._increment_step()
            timeline_agent = kwargs.get("timeline_agent")
            if timeline_agent is None:
                raise ValueError("Missing required agent: timeline_agent")
            
            timeline_result = self.orchestrator.execute_single_agent(
                agent=timeline_agent,
                query=f"GENERATE a standard academic research timeline for a {project_type} project starting {start_date} and ending {end_date}. Create monthly or quarterly phases with specific deliverables.",
                workflow_id=self.workflow_id
            )
            
            if not timeline_result.success:
                return self._end_execution(outputs, error=f"Timeline creation failed: {timeline_result.error}")
            
            outputs["timeline"] = timeline_result.content
            
            # Step 2: Generate milestones
            self._increment_step()
            milestone_agent = kwargs.get("milestone_agent")
            if milestone_agent is None:
                raise ValueError("Missing required agent: milestone_agent")
            
            milestone_result = self.orchestrator.execute_single_agent(
                agent=milestone_agent,
                query=f"GENERATE milestones for a {project_type} spanning {start_date} to {end_date}. Include: IRB submission, data collection, analysis, writing, and defense phases with due dates.",
                workflow_id=self.workflow_id
            )
            
            if not milestone_result.success:
                return self._end_execution(outputs, error=f"Milestone generation failed: {milestone_result.error}")
            
            outputs["milestones"] = milestone_result.content
            outputs["duration_days"] = (
                datetime.strptime(end_date, "%Y-%m-%d") - 
                datetime.strptime(start_date, "%Y-%m-%d")
            ).days
            
            return self._end_execution(outputs)
            
        except Exception as e:
            return self._end_execution(outputs, error=str(e))
