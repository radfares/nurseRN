"""
Unit tests for Retrieval Adapter.
"""

import pytest
from src.orchestration.retrieval_adapter import RetrievalAdapter
from src.services.rag_pipeline import RetrievedItem

def test_format_for_llm():
    items = [
        RetrievedItem(
            content="Text A",
            source="SourceA",
            score=0.9,
            citation_id="PMID123",
            metadata={"title": "Study A"}
        ),
        RetrievedItem(
            content="Text B",
            source="SourceB",
            score=0.8,
            citation_id="file.pdf"
        )
    ]
    
    formatted = RetrievalAdapter.format_for_llm(items)
    
    assert "[Source: SourceA | ID: PMID123]" in formatted
    assert "Text A" in formatted
    assert "[Source: SourceB | ID: file.pdf]" in formatted
    assert "Text B" in formatted

def test_format_empty():
    assert RetrievalAdapter.format_for_llm([]) == "No relevant context found."

def test_extract_citations():
    items = [
        RetrievedItem(
            content="A",
            source="S",
            score=1,
            citation_id="123",
            metadata={"title": "Title A"}
        ),
         RetrievedItem(
            content="B",
            source="S",
            score=1,
            citation_id="123", # Duplicate ID
            metadata={"title": "Title A"}
        )
    ]
    
    cits = RetrievalAdapter.extract_citations(items)
    assert len(cits) == 1
    assert "123: Title A" in cits[0]
