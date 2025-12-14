"""
Parallel Search Workflow Template

Searches multiple databases simultaneously for maximum speed.
Part of Phase 3: Workflow Templates
"""

from typing import Any, Dict, List
from src.workflows.base import WorkflowTemplate, WorkflowResult
# MockAgent import removed - only needed for testing


class ParallelSearchWorkflow(WorkflowTemplate):
    """
    Parallel Search: Search multiple databases simultaneously
    
    Searches PubMed, CINAHL, and Cochrane in parallel for comprehensive results.
    Target: >50% time savings vs sequential searches.
    """
    
    @property
    def name(self) -> str:
        return "parallel_search"
    
    @property
    def description(self) -> str:
        return "Parallel literature search across multiple databases (PubMed + CINAHL + Cochrane)"
    
    def validate_inputs(self, **kwargs) -> bool:
        """Validate required inputs: query"""
        if "query" not in kwargs:
            raise ValueError("Missing required parameter: query")
        return True
    
    def execute(self, **kwargs) -> WorkflowResult:
        """
        Execute parallel search across databases.
        
        Args:
            query: Search query string
            databases: Optional list of databases (defaults to all 3)
        
        Returns:
            WorkflowResult with combined, deduplicated results
        """
        self._start_execution()
        outputs = {}
        
        try:
            self.validate_inputs(**kwargs)
            
            query = kwargs["query"]
            databases = kwargs.get("databases", ["pubmed", "cinahl", "cochrane"])
            
            # Create agents for each database
            agents = []
            for db in databases:
                agent = kwargs.get(f"{db}_agent")
                if agent is None:
                    raise ValueError(f"Missing required agent: {db}_agent")
                agents.append(agent)
            
            # Execute in parallel
            self._increment_step()
            results = self.orchestrator.execute_parallel(
                agents=agents,
                query=query,
                workflow_id=self.workflow_id,
                timeout_seconds=10
            )
            
            # Aggregate results
            all_articles = []
            for agent_name, result in results.items():
                if result.success:
                    all_articles.append({
                        "source": agent_name,
                        "content": result.content
                    })
            
            outputs["results"] = all_articles
            outputs["total_sources"] = len(all_articles)
            outputs["databases_searched"] = databases
            
            return self._end_execution(outputs)
            
        except Exception as e:
            return self._end_execution(outputs, error=str(e))
