"""
Research Workflow Template

Automates the PICOT → Search → Writing research workflow.
Part of Phase 3: Workflow Templates
"""

from typing import Any, Dict
from src.workflows.base import WorkflowTemplate, WorkflowResult
# MockAgent import removed - only needed for testing


class ResearchWorkflow(WorkflowTemplate):
    """
    Research Workflow: PICOT → Search → Writing
    
    Automates a complete research workflow:
    1. PICOT Agent develops research question
    2. Search Agent finds relevant literature
    3. Writing Agent drafts abstract
    
    Target execution time: 3-5 minutes
    """
    
    @property
    def name(self) -> str:
        return "research_workflow"
    
    @property
    def description(self) -> str:
        return "Complete research workflow: PICOT development → Literature search → Abstract draft"
    
    def validate_inputs(self, **kwargs) -> bool:
        """
        Validate required inputs.
        
        Required:
            - topic: Research topic (str)
            - setting: Clinical setting (str)
            - intervention: Proposed intervention (str)
        """
        required = ["topic", "setting", "intervention"]
        for param in required:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        
        return True
    
    def execute(self, **kwargs) -> WorkflowResult:
        """
        Execute the research workflow.
        
        Args:
            topic: Research topic (e.g., "fall prevention")
            setting: Clinical setting (e.g., "acute care hospital")
            intervention: Proposed intervention (e.g., "multifactorial bundle")
        
        Returns:
            WorkflowResult with picot, articles, and draft outputs
        """
        self._start_execution()
        outputs = {}
        
        try:
            # Validate inputs
            self.validate_inputs(**kwargs)
            
            topic = kwargs["topic"]
            setting = kwargs["setting"]
            intervention = kwargs["intervention"]
            
            # Step 1: PICOT Development
            self._increment_step()
            picot_query = f"Develop a PICOT question for {topic} in {setting} using {intervention}"
            
            # For testing, use mock agent (in production, use real PICOT agent)
            picot_agent = kwargs.get("picot_agent") or MockAgent(
                name="PICOTAgent",
                response=f"P: Patients in {setting}, I: {intervention}, C: Standard care, O: {topic} reduction"
            )
            
            picot_result = self.orchestrator.execute_single_agent(
                agent=picot_agent,
                query=picot_query,
                workflow_id=self.workflow_id
            )
            
            if not picot_result.success:
                return self._end_execution(outputs, error=f"PICOT step failed: {picot_result.error}")
            
            outputs["picot"] = picot_result.content
            
            # Step 2: Literature Search
            self._increment_step()
            search_query = f"Find studies on {topic} with {intervention}"
            
            search_agent = kwargs.get("search_agent") or MockAgent(
                name="SearchAgent",
                response=f"Found 15 articles on {topic} interventions"
            )
            
            search_result = self.orchestrator.execute_single_agent(
                agent=search_agent,
                query=search_query,
                workflow_id=self.workflow_id
            )
            
            if not search_result.success:
                return self._end_execution(outputs, error=f"Search step failed: {search_result.error}")
            
            outputs["articles"] = search_result.content
            
            #Step 3: Writing Draft
            self._increment_step()
            writing_query = f"Draft an abstract based on the PICOT: {picot_result.content}"
            
            writing_agent = kwargs.get("writing_agent") or MockAgent(
                name="WritingAgent",
                response=f"Abstract: This study investigates {intervention} for {topic}..."
            )
            
            writing_result = self.orchestrator.execute_single_agent(
                agent=writing_agent,
                query=writing_query,
                workflow_id=self.workflow_id
            )
            
            if not writing_result.success:
                return self._end_execution(outputs, error=f"Writing step failed: {writing_result.error}")
            
            outputs["draft"] = writing_result.content
            
            # Success!
            return self._end_execution(outputs)
            
        except Exception as e:
            return self._end_execution(outputs, error=str(e))
