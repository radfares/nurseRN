"""
Unit tests for system hardening fixes.

Tests for:
1. PubMed rate limiting (P0)
2. Workflow agent injection validation (P1)
3. Timeline prompt engineering (P2)
"""

import time
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestPubMedRateLimiting:
    """Test PubMed rate limiting to prevent 429 errors"""

    @patch('agno.tools.pubmed.httpx.get')
    def test_pubmed_rate_limiting(self, mock_get):
        """Verify PubMed requests are throttled to 3/sec"""
        from agno.tools.pubmed import PubmedTools

        # Mock successful responses
        mock_response = Mock()
        mock_response.content = b'''<?xml version="1.0"?>
        <eSearchResult>
            <IdList>
                <Id>12345</Id>
            </IdList>
        </eSearchResult>'''
        mock_get.return_value = mock_response

        tool = PubmedTools(email="test@example.com")

        start = time.time()
        # Two searches = 4 HTTP calls minimum (2 esearch + 2 efetch)
        tool.search_pubmed("test1", max_results=1)
        tool.search_pubmed("test2", max_results=1)
        elapsed = time.time() - start

        # Should take at least 1.3s (4 calls * 0.34s delay)
        assert elapsed > 1.2, f"Rate limiting failed: {elapsed}s < 1.2s expected"

    @patch('agno.tools.pubmed.httpx.get')
    def test_pubmed_fetch_ids_has_delay(self, mock_get):
        """Verify fetch_pubmed_ids includes rate limiting delay"""
        from agno.tools.pubmed import PubmedTools

        mock_response = Mock()
        mock_response.content = b'''<?xml version="1.0"?>
        <eSearchResult><IdList><Id>12345</Id></IdList></eSearchResult>'''
        mock_get.return_value = mock_response

        tool = PubmedTools(email="test@example.com")

        start = time.time()
        tool.fetch_pubmed_ids("test query", max_results=1, email="test@example.com")
        elapsed = time.time() - start

        # Should have at least 0.34s delay
        assert elapsed >= 0.33, f"Delay too short: {elapsed}s < 0.33s"

    @patch('agno.tools.pubmed.httpx.get')
    def test_pubmed_fetch_details_has_delay(self, mock_get):
        """Verify fetch_details includes rate limiting delay"""
        from agno.tools.pubmed import PubmedTools

        mock_response = Mock()
        mock_response.content = b'''<?xml version="1.0"?>
        <PubmedArticleSet></PubmedArticleSet>'''
        mock_get.return_value = mock_response

        tool = PubmedTools(email="test@example.com")

        start = time.time()
        tool.fetch_details(["12345"])
        elapsed = time.time() - start

        # Should have at least 0.34s delay
        assert elapsed >= 0.33, f"Delay too short: {elapsed}s < 0.33s"


class TestWorkflowAgentInjection:
    """Test workflow agent injection validation (P1)"""

    def test_parallel_search_requires_agents(self):
        """Verify parallel search fails fast without injected agents"""
        from src.workflows.parallel_search import ParallelSearchWorkflow

        # Mock orchestrator and context
        mock_orchestrator = Mock()
        mock_context = Mock()

        wf = ParallelSearchWorkflow(mock_orchestrator, mock_context)

        # Should return error result if no agents provided
        result = wf.execute(query="test")
        assert not result.success
        assert "Missing required agent" in result.error

    def test_parallel_search_with_valid_agents(self):
        """Verify parallel search succeeds when agents are provided"""
        from src.workflows.parallel_search import ParallelSearchWorkflow
        from src.workflows.base import AgentResult

        # Mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.execute_parallel.return_value = {
            "PubMedAgent": AgentResult(
                agent_name="PubMedAgent",
                success=True,
                content="Found 10 articles"
            )
        }

        mock_context = Mock()

        # Create mock agents
        mock_pubmed_agent = Mock()
        mock_pubmed_agent.name = "PubMedAgent"

        wf = ParallelSearchWorkflow(mock_orchestrator, mock_context)

        # Should succeed with provided agents
        result = wf.execute(
            query="test",
            databases=["pubmed"],
            pubmed_agent=mock_pubmed_agent
        )

        assert result.success
        assert "results" in result.outputs

    def test_research_workflow_requires_all_agents(self):
        """Verify research workflow fails fast without all required agents"""
        from src.workflows.research_workflow import ResearchWorkflow

        mock_orchestrator = Mock()
        mock_context = Mock()

        wf = ResearchWorkflow(mock_orchestrator, mock_context)

        # Should return error result for missing picot_agent
        result = wf.execute(
            topic="fall prevention",
            setting="hospital",
            intervention="bundle"
        )
        assert not result.success
        assert "Missing required agent: picot_agent" in result.error

    def test_timeline_planner_requires_agents(self):
        """Verify timeline planner fails fast without required agents"""
        from src.workflows.timeline_planner import TimelinePlannerWorkflow

        mock_orchestrator = Mock()
        mock_context = Mock()

        wf = TimelinePlannerWorkflow(mock_orchestrator, mock_context)

        # Should return error result for missing timeline_agent
        result = wf.execute(
            project_type="DNP",
            start_date="2025-01-01",
            end_date="2025-12-31"
        )
        assert not result.success
        assert "Missing required agent: timeline_agent" in result.error


class TestTimelinePromptEngineering:
    """Test timeline prompt engineering (P2)"""

    def test_timeline_prompt_includes_dates(self):
        """Verify timeline prompts include user-provided dates"""
        from src.workflows.timeline_planner import TimelinePlannerWorkflow
        from src.workflows.base import AgentResult

        # Mock orchestrator that captures queries
        captured_queries = []

        def mock_execute_single(agent, query, workflow_id):
            captured_queries.append(query)
            return AgentResult(
                agent_name="test",
                success=True,
                content="Timeline generated"
            )

        mock_orchestrator = Mock()
        mock_orchestrator.execute_single_agent = mock_execute_single

        mock_context = Mock()

        # Create mock agents
        mock_timeline_agent = Mock()
        mock_milestone_agent = Mock()

        wf = TimelinePlannerWorkflow(mock_orchestrator, mock_context)

        # Run workflow
        result = wf.execute(
            project_type="DNP",
            start_date="2025-01-01",
            end_date="2025-12-31",
            timeline_agent=mock_timeline_agent,
            milestone_agent=mock_milestone_agent
        )

        # Verify dates appear in prompts
        assert len(captured_queries) == 2
        assert "2025-01-01" in captured_queries[0]
        assert "2025-12-31" in captured_queries[0]
        assert "2025-01-01" in captured_queries[1]
        assert "2025-12-31" in captured_queries[1]

    def test_timeline_prompt_uses_command_style(self):
        """Verify timeline prompts use command-style (GENERATE) not query-style"""
        from src.workflows.timeline_planner import TimelinePlannerWorkflow
        from src.workflows.base import AgentResult

        captured_queries = []

        def mock_execute_single(agent, query, workflow_id):
            captured_queries.append(query)
            return AgentResult(
                agent_name="test",
                success=True,
                content="Result"
            )

        mock_orchestrator = Mock()
        mock_orchestrator.execute_single_agent = mock_execute_single
        mock_context = Mock()

        mock_timeline_agent = Mock()
        mock_milestone_agent = Mock()

        wf = TimelinePlannerWorkflow(mock_orchestrator, mock_context)

        result = wf.execute(
            project_type="DNP",
            start_date="2025-01-01",
            end_date="2025-12-31",
            timeline_agent=mock_timeline_agent,
            milestone_agent=mock_milestone_agent
        )

        # Verify command-style prompts
        assert "GENERATE" in captured_queries[0]
        assert "GENERATE" in captured_queries[1]

    def test_milestone_prompt_includes_phases(self):
        """Verify milestone prompt includes specific phases"""
        from src.workflows.timeline_planner import TimelinePlannerWorkflow
        from src.workflows.base import AgentResult

        captured_queries = []

        def mock_execute_single(agent, query, workflow_id):
            captured_queries.append(query)
            return AgentResult(
                agent_name="test",
                success=True,
                content="Milestones"
            )

        mock_orchestrator = Mock()
        mock_orchestrator.execute_single_agent = mock_execute_single
        mock_context = Mock()

        mock_timeline_agent = Mock()
        mock_milestone_agent = Mock()

        wf = TimelinePlannerWorkflow(mock_orchestrator, mock_context)

        result = wf.execute(
            project_type="DNP",
            start_date="2025-01-01",
            end_date="2025-12-31",
            timeline_agent=mock_timeline_agent,
            milestone_agent=mock_milestone_agent
        )

        # Verify milestone prompt includes required phases
        milestone_prompt = captured_queries[1]
        assert "IRB submission" in milestone_prompt
        assert "data collection" in milestone_prompt
        assert "analysis" in milestone_prompt
        assert "writing" in milestone_prompt
        assert "defense" in milestone_prompt
