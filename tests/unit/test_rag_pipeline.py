"""
Unit tests for RAG Pipeline.
"""

import pytest
from unittest.mock import MagicMock, patch
from src.services.rag_pipeline import RAGPipeline, RetrievedItem
from src.knowledge.vector_store import SearchResult

@pytest.fixture
def mock_store():
    store = MagicMock()
    # Mock search return
    store.search.return_value = [
        SearchResult(
            chunk_id="c1",
            doc_id="d1",
            text="Clinical text content",
            score=0.9,
            source_path="/path/guideline.pdf",
            metadata={"title": "Guideline"}
        )
    ]
    return store

@pytest.fixture
def rag_pipeline():
    return RAGPipeline(cache_ttl=60)

@patch("src.services.rag_pipeline.VectorStoreFactory")
def test_retrieve_local_only(mock_factory, rag_pipeline):
    """Test retrieving from local stores only."""
    # Setup mocks for different stores
    personal_store = MagicMock()
    personal_store.search.return_value = []  # Empty personal results
    
    clinical_store = MagicMock()
    clinical_store.search.return_value = [
        SearchResult(
            chunk_id="c1",
            doc_id="d1",
            text="Clinical text content",
            score=0.9,
            source_path="/path/guideline.pdf",
            metadata={"title": "Guideline"}
        )
    ]
    
    # Configure factory to return specific stores based on type
    def get_store_side_effect(store_type, **kwargs):
        if store_type == "personal":
            return personal_store
        return clinical_store
        
    mock_factory.get_store.side_effect = get_store_side_effect
    
    results = rag_pipeline.retrieve(query="test query", agent_hint="clinical", limit=2, use_cache=False)
    
    assert len(results) >= 1
    assert isinstance(results[0], RetrievedItem)
    assert results[0].content == "Clinical text content"
    assert "Clinical" in results[0].source

@patch("src.services.rag_pipeline.VectorStoreFactory")
def test_caching_behavior(mock_factory, rag_pipeline, mock_store):
    """Test that caching prevents repeated calls."""
    mock_factory.get_store.return_value = mock_store
    
    # First call
    rag_pipeline.retrieve("cache query", agent_hint="general")
    assert mock_store.search.called
    
    # Reset mock
    mock_store.search.reset_mock()
    
    # Second call (should hit cache)
    rag_pipeline.retrieve("cache query", agent_hint="general")
    mock_store.search.assert_not_called()

def test_deduplication(rag_pipeline):
    """Test deduplication logic."""
    item1 = RetrievedItem(content="ABC", source="s1", score=1.0)
    item2 = RetrievedItem(content="ABC", source="s2", score=0.9) # Duplicate content
    item3 = RetrievedItem(content="XYZ", source="s1", score=0.8)
    
    deduped = rag_pipeline._deduplicate([item1, item2, item3])
    
    assert len(deduped) == 2
    # Should keep first occurrence or handle effectively logic (current implementation keeps first)
    assert deduped[0].content == "ABC"
    assert deduped[1].content == "XYZ"
