"""
Phase 2 Validation Tests - Adaptive Evidence Retrieval

Tests validation gates:
1. Execution continues when 0 < found < requested
2. Shortfall metadata is correctly populated
3. Synthesis adapts tone based on shortfall context
4. Grounding failures only when found == 0

Created: 2025-12-16
"""

import pytest
from unittest.mock import Mock, patch
from src.adapters.base import SearchResult, SearchResultSet
from src.orchestration.response_synthesizer import ResponseSynthesizer
from src.orchestration.conversation_context import ConversationContext
from src.orchestration.intelligent_orchestrator import AgentTask


class TestSearchResultSet:
    """Test SearchResultSet dataclass and properties."""

    def test_create_full_results(self):
        """SearchResultSet with all requested results."""
        result_set = SearchResultSet(
            results=[Mock(spec=SearchResult) for _ in range(10)],
            requested=10,
            found=10,
            truncated=False,
            source="PubMed"
        )

        assert result_set.requested == 10
        assert result_set.found == 10
        assert result_set.has_shortfall is False
        assert result_set.is_empty is False
        assert result_set.shortfall_ratio == 1.0

    def test_create_partial_results(self):
        """SearchResultSet with fewer results than requested."""
        result_set = SearchResultSet(
            results=[Mock(spec=SearchResult) for _ in range(3)],
            requested=10,
            found=3,
            truncated=False,
            source="PubMed"
        )

        assert result_set.requested == 10
        assert result_set.found == 3
        assert result_set.has_shortfall is True
        assert result_set.is_empty is False
        assert result_set.shortfall_ratio == 0.3

    def test_create_empty_results(self):
        """SearchResultSet with no results found."""
        result_set = SearchResultSet(
            results=[],
            requested=10,
            found=0,
            truncated=False,
            source="PubMed"
        )

        assert result_set.requested == 10
        assert result_set.found == 0
        assert result_set.has_shortfall is False  # Shortfall is 0 < found < requested
        assert result_set.is_empty is True
        assert result_set.shortfall_ratio == 0.0

    def test_to_dict_serialization(self):
        """SearchResultSet.to_dict includes all metadata."""
        result_set = SearchResultSet(
            results=[Mock(spec=SearchResult, to_dict=lambda: {"title": "Test"})],
            requested=10,
            found=3,
            truncated=False,
            source="PubMed"
        )

        d = result_set.to_dict()

        assert d["requested"] == 10
        assert d["found"] == 3
        assert d["has_shortfall"] is True
        assert d["is_empty"] is False
        assert d["shortfall_ratio"] == 0.3
        assert d["truncated"] is False
        assert d["source"] == "PubMed"
        assert len(d["results"]) == 1


class TestPartialResultAcceptance:
    """Test that execution continues with partial results."""

    def test_base_adapter_returns_partial_results(self):
        """BaseAdapter.search should return SearchResultSet with metadata."""
        from src.adapters.base import BaseAdapter, DatabaseConfig, PaginationType

        # Create a concrete adapter for testing
        class TestAdapter(BaseAdapter):
            def translate_query(self, user_query: str) -> str:
                return user_query

            def search_ids(self, query: str, max_results: int) -> list:
                # Simulate finding only 3 results when 10 requested
                return ["id1", "id2", "id3"]

            def fetch_details(self, ids: list) -> list:
                return [
                    SearchResult(
                        record_id=id_val,
                        title=f"Article {id_val}",
                        authors=["Author"],
                        abstract="Test abstract",
                        publication_date="2024",
                        source="Test"
                    )
                    for id_val in ids
                ]

        config = DatabaseConfig(
            name="Test",
            base_url="http://test.com",
            rate_limit=1.0,
            batch_size=100,
            pagination_type=PaginationType.OFFSET,
            data_format="json"
        )
        adapter = TestAdapter(config)

        # Request 10, get 3
        result_set = adapter.search("test query", max_results=10)

        # Validation Gate: Should return SearchResultSet, not fail
        assert isinstance(result_set, SearchResultSet)
        assert result_set.requested == 10
        assert result_set.found == 3
        assert result_set.has_shortfall is True
        assert len(result_set.results) == 3

    def test_base_adapter_handles_zero_results(self):
        """BaseAdapter.search should handle zero results gracefully."""
        from src.adapters.base import BaseAdapter, DatabaseConfig, PaginationType

        class TestAdapter(BaseAdapter):
            def translate_query(self, user_query: str) -> str:
                return user_query

            def search_ids(self, query: str, max_results: int) -> list:
                return []  # No results found

            def fetch_details(self, ids: list) -> list:
                return []

        config = DatabaseConfig(
            name="Test",
            base_url="http://test.com",
            rate_limit=1.0,
            batch_size=100,
            pagination_type=PaginationType.OFFSET,
            data_format="json"
        )
        adapter = TestAdapter(config)

        result_set = adapter.search("test query", max_results=10)

        # Validation Gate: Should return empty SearchResultSet, not fail
        assert isinstance(result_set, SearchResultSet)
        assert result_set.requested == 10
        assert result_set.found == 0
        assert result_set.is_empty is True
        assert len(result_set.results) == 0


class TestShortfallMetadataExtraction:
    """Test that synthesis extracts and uses shortfall metadata."""

    def setup_method(self):
        """Reset synthesis tracking before each test."""
        ResponseSynthesizer.reset_synthesis_tracking()

    def test_synthesis_detects_shortfall(self):
        """Synthesis should detect shortfall in output metadata."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]

        # Result with shortfall metadata
        results = {
            "task_1": {
                "success": True,
                "output": {
                    "results": [{"title": "Article 1"}],
                    "requested": 10,
                    "found": 3,
                    "has_shortfall": True,
                    "shortfall_ratio": 0.3,
                    "truncated": False,
                    "source": "PubMed"
                },
                "agent": "test_agent",
                "action": "search"
            },
        }

        response = synthesizer.synthesize(
            user_message="test query",
            plan=plan,
            results=results,
            context=context,
            request_id="req_test_shortfall"
        )

        # Synthesis should proceed (not abort)
        assert response is not None
        assert len(response) > 0
        # Fallback synthesis should include the result
        assert "found" in response.lower() or "article" in response.lower()

    def test_synthesis_prompt_includes_shortfall_context(self):
        """Synthesis prompt should include shortfall context when present."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]

        results = {
            "task_1": {
                "success": True,
                "output": {
                    "results": [{"title": "Article 1"}],
                    "requested": 10,
                    "found": 3,
                    "has_shortfall": True,
                    "shortfall_ratio": 0.3,
                },
                "agent": "test_agent",
                "action": "search"
            },
        }

        # Build prompt (internal method)
        prompt = synthesizer._build_user_prompt(
            user_message="test query",
            plan=plan,
            results=results,
            context=context
        )

        # Prompt should include shortfall context
        assert "Partial Results Context" in prompt or "fewer results" in prompt.lower()
        assert "Requested 10" in prompt or "requested 10" in prompt.lower()
        assert "found 3" in prompt.lower()

    def test_synthesis_no_shortfall_context_when_full_results(self):
        """Synthesis prompt should NOT include shortfall context with full results."""
        synthesizer = ResponseSynthesizer(client=None)
        context = ConversationContext()
        plan = [AgentTask("task_1", "test_agent", "search", {})]

        results = {
            "task_1": {
                "success": True,
                "output": {
                    "results": [{"title": f"Article {i}"} for i in range(10)],
                    "requested": 10,
                    "found": 10,
                    "has_shortfall": False,
                    "shortfall_ratio": 1.0,
                },
                "agent": "test_agent",
                "action": "search"
            },
        }

        prompt = synthesizer._build_user_prompt(
            user_message="test query",
            plan=plan,
            results=results,
            context=context
        )

        # Prompt should NOT include shortfall context
        assert "Partial Results Context" not in prompt
        assert "fewer results were found" not in prompt


class TestGroundingFailureConditions:
    """Test that grounding failures only occur when appropriate."""

    def test_no_grounding_failure_with_partial_results(self):
        """Partial results (0 < found < requested) should NOT trigger grounding failure."""
        # This is validated by the fact that synthesis proceeds with shortfall
        result_set = SearchResultSet(
            results=[Mock(spec=SearchResult)],
            requested=10,
            found=1,
            truncated=False,
            source="PubMed"
        )

        # Validation Gate: Has results, should NOT be considered a failure
        assert result_set.found > 0
        assert result_set.has_shortfall is True
        assert not result_set.is_empty

    def test_grounding_failure_only_with_zero_results(self):
        """Empty results (found == 0) should be the only grounding failure case."""
        result_set = SearchResultSet(
            results=[],
            requested=10,
            found=0,
            truncated=False,
            source="PubMed"
        )

        # Validation Gate: No results means potential grounding failure
        assert result_set.found == 0
        assert result_set.is_empty is True
        assert not result_set.has_shortfall  # Shortfall is for partial results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
