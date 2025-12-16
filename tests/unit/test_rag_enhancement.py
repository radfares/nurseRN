"""
Unit Tests for RAG Enhancement Service
Tests collection routing, TTL caching, and grounding extraction.

Created: 2025-12-15
Phase: 3 - Agent RAG Integration
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.services.rag_enhancement import RAGEnhancer, RetrievalResult
from src.knowledge.vector_store import SearchResult


class TestRAGEnhancer(unittest.TestCase):
    """Test suite for RAGEnhancer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enhancer = RAGEnhancer(cache_ttl=60, db_path="data/test_db")
    
    def tearDown(self):
        """Clean up after tests."""
        self.enhancer.clear_cache()
    
    def test_initialization(self):
        """Test RAGEnhancer initialization."""
        self.assertIsNotNone(self.enhancer)
        self.assertIsNotNone(self.enhancer.cache)
        self.assertEqual(self.enhancer.db_path, "data/test_db")
    
    @patch('src.services.rag_enhancement.VectorStoreFactory')
    def test_retrieve_basic(self, mock_factory):
        """Test basic retrieval without cache."""
        # Mock vector store
        mock_store = Mock()
        mock_factory.get_store.return_value = mock_store
        
        # Mock search results
        mock_search_result = SearchResult(
            chunk_id="chunk_1",
            doc_id="doc_1",
            text="Fall prevention protocols for elderly patients",
            score=0.95,
            source_path="/path/to/doc.pdf",
            page_num=3,
            metadata={"pmid": "12345678"}
        )
        mock_store.search.return_value = [mock_search_result]
        
        # Perform retrieval
        results = self.enhancer.retrieve(
            query="fall prevention",
            agent_hint="nursing_research",
            k=5,
            use_cache=False
        )
        
        # Assertions
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "Fall prevention protocols for elderly patients")
        self.assertEqual(results[0].citation_id, "PMID:12345678")
        self.assertEqual(results[0].score, 0.95)
    
    @patch('src.services.rag_enhancement.VectorStoreFactory')
    def test_collection_routing_nursing_research(self, mock_factory):
        """Test collection routing for nursing research agent."""
        mock_store = Mock()
        mock_factory.get_store.return_value = mock_store
        mock_store.search.return_value = []
        
        # Perform retrieval
        self.enhancer.retrieve(
            query="test query",
            agent_hint="nursing_research",
            k=3,
            use_cache=False
        )
        
        # Check that correct collections were accessed
        # nursing_research should use: clinical_knowledge, research_cache, procedural_knowledge, personal_docs
        # get_store is called with positional arg: get_store("clinical", db_path="...")
        # So call[0] is args tuple, call[0][0] is the store_type
        call_args_list = [call[0][0] for call in mock_factory.get_store.call_args_list]

        # Should include clinical, research, procedural, personal
        self.assertIn("clinical", call_args_list)
        self.assertIn("research", call_args_list)
    
    @patch('src.services.rag_enhancement.VectorStoreFactory')
    def test_caching_behavior(self, mock_factory):
        """Test that caching works correctly with TTL."""
        mock_store = Mock()
        mock_factory.get_store.return_value = mock_store
        
        mock_result = SearchResult(
            chunk_id="c1",
            doc_id="d1",
            text="cached content",
            score=0.9,
            source_path="test.pdf",
            metadata={}
        )
        mock_store.search.return_value = [mock_result]
        
        # First call - should hit vector store
        results1 = self.enhancer.retrieve(
            query="test",
            agent_hint="general",
            k=3,
            use_cache=True
        )
        
        # Second call - should hit cache
        results2 = self.enhancer.retrieve(
            query="test",
            agent_hint="general",
            k=3,
            use_cache=True
        )
        
        # Verify results are identical
        self.assertEqual(len(results1), len(results2))
        self.assertEqual(results1[0].content, results2[0].content)
        
        # Verify cache stats
        stats = self.enhancer.get_cache_stats()
        self.assertEqual(stats['hits'], 1)
    
    def test_extract_grounding_metadata_pmids(self):
        """Test extraction of PMID grounding metadata."""
        results = [
            RetrievalResult(
                content="Text 1",
                source="clinical",
                score=0.9,
                citation_id="PMID:12345678"
            ),
            RetrievalResult(
                content="Text 2",
                source="research",
                score=0.8,
                citation_id="PMID:87654321"
            )
        ]
        
        metadata = self.enhancer.extract_grounding_metadata(results)
        
        self.assertEqual(set(metadata['pmids']), {"12345678", "87654321"})
        self.assertEqual(len(metadata['dois']), 0)
        self.assertEqual(len(metadata['all_citations']), 2)
    
    def test_extract_grounding_metadata_mixed(self):
        """Test extraction with mixed citation types."""
        results = [
            RetrievalResult(
                content="Text 1",
                source="research",
                score=0.9,
                citation_id="PMID:11111111"
            ),
            RetrievalResult(
                content="Text 2",
                source="research",
                score=0.8,
                citation_id="DOI:10.1234/example"
            ),
            RetrievalResult(
                content="Text 3",
                source="research",
                score=0.7,
                citation_id="arXiv:2024.12345"
            ),
            RetrievalResult(
                content="Text 4",
                source="personal",
                score=0.6,
                citation_id="my_notes.pdf"
            )
        ]
        
        metadata = self.enhancer.extract_grounding_metadata(results)
        
        self.assertEqual(len(metadata['pmids']), 1)
        self.assertEqual(len(metadata['dois']), 1)
        self.assertEqual(len(metadata['arxiv_ids']), 1)
        self.assertEqual(len(metadata['filenames']), 1)
        self.assertEqual(len(metadata['all_citations']), 4)
    
    def test_deduplication(self):
        """Test that duplicate results are removed."""
        duplicate_results = [
            RetrievalResult(
                content="Duplicate content here",
                source="source1",
                score=0.9
            ),
            RetrievalResult(
                content="Duplicate content here",
                source="source2",
                score=0.8
            ),
            RetrievalResult(
                content="Different content",
                source="source3",
                score=0.7
            )
        ]
        
        unique = self.enhancer._deduplicate(duplicate_results)
        
        # Should have 2 unique results (first duplicate kept, second removed)
        self.assertEqual(len(unique), 2)
    
    @patch('src.services.rag_enhancement.VectorStoreFactory')
    def test_retrieve_limits_results_to_k(self, mock_factory):
        """Test that retrieve returns exactly k results."""
        mock_store = Mock()
        mock_factory.get_store.return_value = mock_store
        
        # Return 10 results
        mock_results = [
            SearchResult(
                chunk_id=f"c{i}",
                doc_id=f"d{i}",
                text=f"content {i}",
                score=0.9 - (i * 0.05),
                source_path="test.pdf",
                metadata={}
            )
            for i in range(10)
        ]
        mock_store.search.return_value = mock_results
        
        # Request only 5
        results = self.enhancer.retrieve(
            query="test",
            agent_hint="general",
            k=5,
            use_cache=False
        )
        
        # Should return exactly 5
        self.assertEqual(len(results), 5)
        
        # Should be sorted by score (highest first)
        scores = [r.score for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_cache_clear(self):
        """Test cache clearing functionality."""
        # Add something to cache manually
        self.enhancer.cache.set("test_key", "test_value")
        
        # Verify it's cached
        self.assertIsNotNone(self.enhancer.cache.get("test_key"))
        
        # Clear cache
        self.enhancer.clear_cache()

        # Verify stats are reset (check BEFORE calling get() which would increment misses)
        stats = self.enhancer.get_cache_stats()
        self.assertEqual(stats['hits'], 0)
        self.assertEqual(stats['misses'], 0)

        # Verify it's cleared (this will increment misses counter, so check stats first)
        self.assertIsNone(self.enhancer.cache.get("test_key"))


class TestCitationExtraction(unittest.TestCase):
    """Test suite for citation ID extraction logic."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enhancer = RAGEnhancer()
    
    def test_extract_pmid_from_metadata(self):
        """Test PMID extraction."""
        metadata = {"pmid": "12345678", "title": "Test Article"}
        cit_id = self.enhancer._extract_citation_id(metadata)
        self.assertEqual(cit_id, "PMID:12345678")
    
    def test_extract_doi_from_metadata(self):
        """Test DOI extraction."""
        metadata = {"doi": "10.1234/example", "title": "Test"}
        cit_id = self.enhancer._extract_citation_id(metadata)
        self.assertEqual(cit_id, "DOI:10.1234/example")
    
    def test_extract_arxiv_from_metadata(self):
        """Test ArXiv ID extraction."""
        metadata = {"arxiv_id": "2024.12345", "title": "Test"}
        cit_id = self.enhancer._extract_citation_id(metadata)
        self.assertEqual(cit_id, "arXiv:2024.12345")
    
    def test_extract_filename_fallback(self):
        """Test filename extraction as fallback."""
        metadata = {"source_path": "/path/to/document.pdf"}
        cit_id = self.enhancer._extract_citation_id(metadata)
        self.assertEqual(cit_id, "document.pdf")
    
    def test_priority_pmid_over_doi(self):
        """Test that PMID takes priority over DOI."""
        metadata = {
            "pmid": "99999999",
            "doi": "10.1234/example"
        }
        cit_id = self.enhancer._extract_citation_id(metadata)
        self.assertEqual(cit_id, "PMID:99999999")


if __name__ == '__main__':
    unittest.main()
