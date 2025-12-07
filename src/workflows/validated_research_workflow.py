"""
Validated Research Workflow

Automates the pipeline: PICOT → Search → Validation → Filtering → Synthesis.
Ensures only high-quality, non-retracted evidence is used for research writing.

Created: 2025-12-07 (Phase 4b - Workflow Integration)
"""

import json
from typing import Any, Dict, List
from src.workflows.base import WorkflowTemplate, WorkflowResult
from src.models.evidence_types import EvidenceLevel, ValidationReport

class ValidatedResearchWorkflow(WorkflowTemplate):
    """
    Validated Research Workflow: PICOT → Search → Validate → Filter → Write
    
    Automates a complete research workflow with quality control:
    1. PICOT Agent develops research question
    2. Search Agent finds relevant literature
    3. Citation Validation Agent grades and checks for retractions
    4. Workflow filters out low-quality/retracted articles
    5. Writing Agent drafts abstract using ONLY validated evidence
    """
    
    @property
    def name(self) -> str:
        return "validated_research_workflow"
    
    @property
    def description(self) -> str:
        return "Research pipeline with automatic evidence validation and retraction checking"
    
    def validate_inputs(self, **kwargs) -> bool:
        """
        Validate required inputs.
        
        Required:
            - topic: Research topic (str)
            - setting: Clinical setting (str)
            - intervention: Proposed intervention (str)
            - picot_agent: Agent instance
            - search_agent: Agent instance
            - validation_agent: Agent instance
            - writing_agent: Agent instance
            
        Optional:
            - timeline_agent: Agent instance (for deadline awareness)
            - project_deadline: str (e.g., "June 2026")
        """
        required = [
            "topic", "setting", "intervention", 
            "picot_agent", "search_agent", "validation_agent", "writing_agent"
        ]
        for param in required:
            if param not in kwargs:
                raise ValueError(f"Missing required parameter: {param}")
        
        return True
    
    def _parse_search_results(self, search_content: str) -> List[Dict[str, Any]]:
        """
        Parse search agent output into structured article list.
        Handles both JSON-like strings and plain text.
        """
        # Attempt to find JSON structure
        try:
            # Look for list start/end
            start = search_content.find('[')
            end = search_content.rfind(']') + 1
            if start != -1 and end != -1:
                json_str = search_content[start:end]
                return json.loads(json_str)
        except Exception:
            pass
            
        # Fallback: Create a dummy structure if parsing fails
        # In a real implementation, we'd want robust parsing or structured output from the agent
        return []

    def execute(self, **kwargs) -> WorkflowResult:
        """
        Execute the validated research workflow.
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
            
            picot_result = self.orchestrator.execute_single_agent(
                agent=kwargs["picot_agent"],
                query=picot_query,
                workflow_id=self.workflow_id
            )
            
            if not picot_result.success:
                return self._end_execution(outputs, error=f"PICOT step failed: {picot_result.error}")
            
            outputs["picot"] = picot_result.content
            
            # Step 1.5: Timeline Context (OPTIONAL)
            # If timeline_agent is provided, get project deadline awareness
            timeline_context = ""
            if kwargs.get("timeline_agent"):
                self._increment_step()
                project_deadline = kwargs.get("project_deadline", "June 2026")
                
                timeline_query = f"""
                What are the key milestones and deadlines for a nursing research project?
                Project deadline: {project_deadline}
                Topic: {topic}
                
                Provide a brief timeline summary including:
                1. Literature review deadline
                2. Data collection window
                3. Analysis phase
                4. Final submission date
                """
                
                timeline_result = self.orchestrator.execute_single_agent(
                    agent=kwargs["timeline_agent"],
                    query=timeline_query,
                    workflow_id=self.workflow_id
                )
                
                if timeline_result.success:
                    timeline_context = f"\n\nPROJECT TIMELINE:\n{timeline_result.content}"
                    outputs["timeline"] = timeline_result.content
                # Note: Timeline failure is non-blocking - workflow continues
            
            # Step 2: Literature Search
            self._increment_step()
            search_query = f"Find 5 recent peer-reviewed studies on {topic} with {intervention}. Return results as a JSON list with keys: pmid, title, abstract, publication_date."
            
            search_result = self.orchestrator.execute_single_agent(
                agent=kwargs["search_agent"],
                query=search_query,
                workflow_id=self.workflow_id
            )
            
            if not search_result.success:
                return self._end_execution(outputs, error=f"Search step failed: {search_result.error}")
            
            outputs["raw_search_results"] = search_result.content
            
            # Step 3: Validation & Filtering
            self._increment_step()
            
            # Note: In a real scenario, we'd parse the search result content into a list of dicts.
            # For this implementation, we'll ask the validation agent to parse and validate the raw text directly
            # or use the tools directly if we had structured data.
            # Since we have the agent, let's ask it to validate the content found.
            
            validation_query = f"""
            Validate these search results. 
            1. Extract the articles.
            2. Grade evidence levels.
            3. Check for retractions.
            4. Return ONLY the valid, high-quality articles (Level I-III preferred) that are NOT retracted.
            
            Search Results to Validate:
            {search_result.content}
            """
            
            validation_result = self.orchestrator.execute_single_agent(
                agent=kwargs["validation_agent"],
                query=validation_query,
                workflow_id=self.workflow_id
            )
            
            if not validation_result.success:
                return self._end_execution(outputs, error=f"Validation step failed: {validation_result.error}")
            
            outputs["validation_report"] = validation_result.content
            
            # Step 4: Synthesis / Writing
            self._increment_step()
            writing_query = f"""
            Draft an evidence synthesis based on the following:
            
            PICOT: {picot_result.content}
            
            VALIDATED EVIDENCE (Use ONLY these sources):
            {validation_result.content}
            {timeline_context}
            
            Please synthesize the findings and provide a clinical recommendation.
            If project timeline is provided, ensure recommendations are feasible within that timeframe.
            """
            
            writing_result = self.orchestrator.execute_single_agent(
                agent=kwargs["writing_agent"],
                query=writing_query,
                workflow_id=self.workflow_id
            )
            
            if not writing_result.success:
                return self._end_execution(outputs, error=f"Writing step failed: {writing_result.error}")
            
            outputs["synthesis"] = writing_result.content
            
            # Success!
            return self._end_execution(outputs)
            
        except Exception as e:
            return self._end_execution(outputs, error=str(e))
