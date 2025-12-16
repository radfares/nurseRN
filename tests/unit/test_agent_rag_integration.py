"""
Agent RAG Integration Tests - Phase 3
Tests that agents can correctly call RAGEnhancer and receive grounding metadata.

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
from src.services.rag_config import get_collections_for_agent


class TestAgentRAGIntegration(unittest.TestCase):
    """Integration tests for agent-RAG interactions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.enhancer = RAGEnhancer(cache_ttl=60)
    
    @patch('src.services.rag_enhancement.VectorStoreFactory')
    def test_nursing_research_agent_integration(self, mock_factory):
        """Test nursing research agent calling RAGEnhancer."""
        from src.knowledge.vector_store import SearchResult

        # Mock vector store
        mock_store = Mock()
        mock_factory.get_store.return_value = mock_store

        # Mock clinical knowledge results using actual SearchResult objects
        mock_store.search.return_value = [
            SearchResult(
                chunk_id="clinical_1",
                doc_id="doc_1",
                text="Fall prevention: Use bed alarms and non-slip footwear.",
                score=0.92,
                source_path="clinical_guidelines.pdf",
                page_num=15,
                metadata={"pmid": "11111111", "source_type": "clinical"}
            )
        ]
        
        # Simulate agent calling retrieval
        results = self.enhancer.retrieve(
            query="fall prevention interventions for elderly",
            agent_hint="nursing_research",
            k=5,
            use_cache=False
        )
        
        # Assertions
        self.assertGreater(len(results), 0)
        self.assertIsInstance(results[0], RetrievalResult)
        
        # Verify routing to correct collections
        collections_used = get_collections_for_agent("nursing_research")
        self.assertIn("clinical_knowledge", collections_used)
        self.assertIn("research_cache", collections_used)
        
        # Extract grounding
        grounding = self.enhancer.extract_grounding_metadata(results)
        self.assertIn("pmids", grounding)
    
    @patch('src.services.rag_enhancement.VectorStoreFactory')
    def test_medical_research_agent_integration(self, mock_factory):
        """Test medical research agent calling RAGEnhancer."""
        from src.knowledge.vector_store import SearchResult

        mock_store = Mock()
        mock_factory.get_store.return_value = mock_store

        # Mock research cache results using actual SearchResult objects
        mock_store.search.return_value = [
            SearchResult(
                chunk_id="research_1",
                doc_id="doc_2",
                text="RCT showed 30% reduction in catheter infections.",
                score=0.88,
                source_path="pubmed_cache.txt",
                page_num=None,
                metadata={"doi": "10.1234/example"}
            )
        ]
        
        results = self.enhancer.retrieve(
            query="catheter infection prevention",
            agent_hint="medical_research",
            k=3,
            use_cache=False
        )
        
        # Assertions
        self.assertGreater(len(results), 0)
        
        # Verify routing
        collections_used = get_collections_for_agent("medical_research")
        self.assertIn("research_cache", collections_used)
        self.assertIn("clinical_knowledge", collections_used)
        
        # Extract grounding - should have DOI from research cache
        grounding = self.enhancer.extract_grounding_metadata(results)
        self.assertIn("10.1234/example", grounding["dois"])
    
    @patch('src.services.rag_enhancement.VectorStoreFactory')
    def test_document_synthesis_agent_integration(self, mock_factory):
        """Test document synthesis agent calling RAGEnhancer."""
        from src.knowledge.vector_store import SearchResult

        mock_store = Mock()
        mock_factory.get_store.return_value = mock_store

        # Mock personal library results using actual SearchResult objects
        mock_store.search.return_value = [
            SearchResult(
                chunk_id="personal_1",
                doc_id="doc_3",
                text="My notes on fall prevention project.",
                score=0.75,
                source_path="/Users/nurse/documents/fall_prevention_notes.pdf",
                page_num=2,
                metadata={"source_type": "personal"}
            )
        ]
        
        results = self.enhancer.retrieve(
            query="fall prevention",
            agent_hint="document_synthesis",
            k=5,
            use_cache=False
        )
        
        # Assertions
        self.assertGreater(len(results), 0)
        
        # Verify routing prioritizes personal docs
        collections_used = get_collections_for_agent("document_synthesis")
        self.assertEqual(collections_used[0], "personal_docs")
        
        # Extract grounding - should have filename
        grounding = self.enhancer.extract_grounding_metadata(results)
        self.assertIn("filenames", grounding)
    
    @patch('src.services.rag_enhancement.VectorStoreFactory')
    def test_grounding_metadata_flow_to_agent(self, mock_factory):
        """Test complete flow: retrieve → extract grounding → agent uses it."""
        from src.knowledge.vector_store import SearchResult

        mock_store = Mock()
        mock_factory.get_store.return_value = mock_store

        # Mock mixed results using actual SearchResult objects
        mock_store.search.return_value = [
            SearchResult(
                chunk_id="c1",
                doc_id="d1",
                text="Clinical guideline content",
                score=0.9,
                source_path="guideline.pdf",
                page_num=10,
                metadata={"pmid": "33333333"}
            ),
            SearchResult(
                chunk_id="c2",
                doc_id="d2",
                text="Research paper content",
                score=0.85,
                source_path="paper.pdf",
                page_num=5,
                metadata={"doi": "10.9999/test"}
            )
        ]
        
        # Step 1: Agent retrieves
        results = self.enhancer.retrieve(
            query="test query",
            agent_hint="nursing_research",
            k=10,
            use_cache=False
        )
        
        # Step 2: Agent extracts grounding
        grounding = self.enhancer.extract_grounding_metadata(results)
        
        # Step 3: Verify agent can use grounding for citations
        self.assertEqual(len(grounding['pmids']), 1)
        self.assertEqual(len(grounding['dois']), 1)
        self.assertIn("33333333", grounding['pmids'])
        self.assertIn("10.9999/test", grounding['dois'])
        
        # Step 4: Verify all_citations combines everything
        self.assertEqual(len(grounding['all_citations']), 2)
    
    @patch('src.services.rag_enhancement.VectorStoreFactory')
    def test_agent_respects_collection_routing(self, mock_factory):
        """Test that different agents get routed to different collections."""
        mock_store = Mock()
        mock_factory.get_store.return_value = mock_store
        mock_store.search.return_value = []
        
        # Nursing research agent
        self.enhancer.retrieve(
            query="test",
            agent_hint="nursing_research",
            k=3,
            use_cache=False
        )
        nursing_calls = mock_factory.get_store.call_count
        mock_factory.reset_mock()
        
        # Medical research agent
        self.enhancer.retrieve(
            query="test",
            agent_hint="medical_research",
            k=3,
            use_cache=False
        )
        medical_calls = mock_factory.get_store.call_count
        mock_factory.reset_mock()
        
        # Document synthesis agent
        self.enhancer.retrieve(
            query="test",
            agent_hint="document_synthesis",
            k=3,
            use_cache=False
        )
        synthesis_calls = mock_factory.get_store.call_count
        
        # All should make calls (exact count depends on config)
        self.assertGreater(nursing_calls, 0)
        self.assertGreater(medical_calls, 0)
        self.assertGreater(synthesis_calls, 0)
    
    def test_ttl_override_per_query(self):
        """Test that agents can override TTL per query."""
        # First query with default TTL
        with patch('src.services.rag_enhancement.VectorStoreFactory') as mock_factory:
            mock_store = Mock()
            mock_factory.get_store.return_value = mock_store
            mock_store.search.return_value = []
            
            results1 = self.enhancer.retrieve(
                query="test",
                agent_hint="general",
                k=5,
                ttl=None,  # Use default
                use_cache=True
            )
            
            # Second query with custom TTL
            results2 = self.enhancer.retrieve(
                query="test2",
                agent_hint="general",
                k=5,
                ttl=600,  # Override to 10 minutes
                use_cache=True
            )
        
        # Both should complete without error
        self.assertIsNotNone(results1)
        self.assertIsNotNone(results2)


class TestCollectionRoutingConfiguration(unittest.TestCase):
    """Test collection routing configuration."""
    
    def test_nursing_research_collections(self):
        """Test nursing research agent collection configuration."""
        collections = get_collections_for_agent("nursing_research")
        
        # Should include clinical and research as primary
        self.assertIn("clinical_knowledge", collections)
        self.assertIn("research_cache", collections)
    
    def test_medical_research_collections(self):
        """Test medical research agent collection configuration."""
        collections = get_collections_for_agent("medical_research")
        
        # Should prioritize research cache
        self.assertIn("research_cache", collections)
        self.assertIn("clinical_knowledge", collections)
    
    def test_document_synthesis_collections(self):
        """Test document synthesis agent collection configuration."""
        collections = get_collections_for_agent("document_synthesis")
        
        # Should prioritize personal docs
        self.assertIn("personal_docs", collections)
        self.assertIn("research_cache", collections)
    
    def test_unknown_agent_fallback(self):
        """Test that unknown agents get general configuration."""
        collections = get_collections_for_agent("unknown_agent_xyz")
        
        # Should fall back to general config
        self.assertIn("personal_docs", collections)
        self.assertIsInstance(collections, list)
        self.assertGreater(len(collections), 0)


if __name__ == '__main__':
    unittest.main()
