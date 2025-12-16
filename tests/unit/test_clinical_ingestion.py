"""
Unit tests for clinical ingestion module (Phase 1 Task 1.3)

Created: 2025-12-15
"""

import pytest
from unittest.mock import Mock, patch

from src.knowledge.clinical_ingestion import (
    IngestionResult,
    ClinicalDocumentIngestion,
    ingest_clinical_text,
    ingest_procedural_text,
    ingest_research_text,
)
from src.knowledge.chunking_strategies import ChunkResult


class TestIngestionResult:
    def test_dataclass_fields(self):
        r = IngestionResult(success=True, doc_id="d1", chunk_count=2, store_type="clinical", doc_type="clinical")
        assert r.success is True
        assert r.doc_id == "d1"
        assert r.chunk_count == 2
        assert r.store_type == "clinical"


class TestDocTypeToStoreMapping:
    def test_default_doc_type(self):
        ingestion = ClinicalDocumentIngestion()
        assert ingestion.default_doc_type in ("clinical", "procedural", "research")


class TestClinicalDocumentIngestion:
    def test_instantiation(self):
        ingestion = ClinicalDocumentIngestion(db_path="data/test_db")
        assert ingestion.db_path == "data/test_db"


class TestIngestTextMethod:
    @patch('src.knowledge.clinical_ingestion.VectorStoreFactory')
    @patch('src.knowledge.clinical_ingestion.ChunkingFactory')
    def test_ingest_text_success(self, mock_chunking_factory, mock_store_factory):
        mock_chunker = Mock()
        mock_chunker.chunk.return_value = [ChunkResult(text="x", start_idx=0, end_idx=1, token_count=1, metadata={})]
        mock_chunking_factory.get_chunker.return_value = mock_chunker

        mock_store = Mock()
        mock_store.add_chunks.return_value = 1
        mock_store_factory.get_store.return_value = mock_store

        ingestion = ClinicalDocumentIngestion()
        result = ingestion.ingest_text(text="Test content", doc_type="clinical")

        assert isinstance(result, IngestionResult)
        assert result.success is True
        assert result.chunk_count >= 0

    @patch('src.knowledge.clinical_ingestion.VectorStoreFactory')
    @patch('src.knowledge.clinical_ingestion.ChunkingFactory')
    def test_ingest_text_empty(self, mock_chunking_factory, mock_store_factory):
        ingestion = ClinicalDocumentIngestion()
        result = ingestion.ingest_text(text="   ")
        assert result.success is False
        assert "Empty text" in result.error_message

    @patch('src.knowledge.clinical_ingestion.VectorStoreFactory')
    @patch('src.knowledge.clinical_ingestion.ChunkingFactory')
    def test_ingest_text_uses_default_doc_type(self, mock_chunking_factory, mock_store_factory):
        mock_chunker = Mock()
        mock_chunker.chunk.return_value = [ChunkResult(text="chunk", start_idx=0, end_idx=5, token_count=1, metadata={})]
        mock_chunking_factory.get_chunker.return_value = mock_chunker

        mock_store = Mock()
        mock_store.add_chunks.return_value = 1
        mock_store_factory.get_store.return_value = mock_store

        ingestion = ClinicalDocumentIngestion(default_doc_type="procedural")
        result = ingestion.ingest_text(text="Test text")  # No doc_type specified

        assert result.doc_type == "procedural"
        mock_chunking_factory.get_chunker.assert_called_with("procedural")

    @patch('src.knowledge.clinical_ingestion.VectorStoreFactory')
    @patch('src.knowledge.clinical_ingestion.ChunkingFactory')
    def test_ingest_text_with_chunker_params(self, mock_chunking_factory, mock_store_factory):
        mock_chunker = Mock()
        mock_chunker.chunk.return_value = [ChunkResult(text="chunk", start_idx=0, end_idx=5, token_count=1, metadata={})]
        mock_chunking_factory.get_chunker.return_value = mock_chunker

        mock_store = Mock()
        mock_store.add_chunks.return_value = 1
        mock_store_factory.get_store.return_value = mock_store

        ingestion = ClinicalDocumentIngestion()
        ingestion.ingest_text(
            text="Test text",
            doc_type="research",
            chunker_params={"token_limit": 200}
        )

        mock_chunking_factory.get_chunker.assert_called_with("research", token_limit=200)


class TestConvenienceFunctions:
    @patch('src.knowledge.clinical_ingestion.ClinicalDocumentIngestion')
    def test_ingest_clinical_text(self, mock_class):
        mock_instance = Mock()
        mock_instance.ingest_text.return_value = IngestionResult(success=True, doc_id="123", chunk_count=1, store_type="clinical", doc_type="clinical")
        mock_class.return_value = mock_instance

        result = ingest_clinical_text("Test text", source_name="test")

        mock_class.assert_called_once_with(db_path="data/chroma_db", default_doc_type="clinical")
        mock_instance.ingest_text.assert_called_once()
        call_kwargs = mock_instance.ingest_text.call_args[1]
        assert call_kwargs["doc_type"] == "clinical"

    @patch('src.knowledge.clinical_ingestion.ClinicalDocumentIngestion')
    def test_ingest_procedural_text(self, mock_class):
        mock_instance = Mock()
        mock_instance.ingest_text.return_value = IngestionResult(success=True, doc_id="123", chunk_count=1, store_type="procedural", doc_type="procedural")
        mock_class.return_value = mock_instance

        result = ingest_procedural_text("Step 1. Step 2.", source_name="proc")

        call_kwargs = mock_instance.ingest_text.call_args[1]
        assert call_kwargs["doc_type"] == "procedural"

    @patch('src.knowledge.clinical_ingestion.ClinicalDocumentIngestion')
    def test_ingest_research_text(self, mock_class):
        mock_instance = Mock()
        mock_instance.ingest_text.return_value = IngestionResult(success=True, doc_id="123", chunk_count=1, store_type="research", doc_type="research")
        mock_class.return_value = mock_instance

        result = ingest_research_text("Abstract: ...", source_name="study")

        call_kwargs = mock_instance.ingest_text.call_args[1]
        assert call_kwargs["doc_type"] == "research"


class TestDocTypeRouting:
    @patch('src.knowledge.clinical_ingestion.VectorStoreFactory')
    @patch('src.knowledge.clinical_ingestion.ChunkingFactory')
    def test_clinical_routes_to_clinical_store(self, mock_chunking, mock_store_factory):
        mock_chunker = Mock()
        mock_chunker.chunk.return_value = [ChunkResult(text="x", start_idx=0, end_idx=1, token_count=1, metadata={})]
        mock_chunking.get_chunker.return_value = mock_chunker

        mock_store = Mock()
        mock_store.add_chunks.return_value = 1
        mock_store_factory.get_store.return_value = mock_store

        ingestion = ClinicalDocumentIngestion(db_path="test_db")
        ingestion.ingest_text(text="Test", doc_type="clinical")

        mock_store_factory.get_store.assert_called_with("clinical", db_path="test_db")

    @patch('src.knowledge.clinical_ingestion.VectorStoreFactory')
    @patch('src.knowledge.clinical_ingestion.ChunkingFactory')
    def test_procedural_routes_to_procedural_store(self, mock_chunking, mock_store_factory):
        mock_chunker = Mock()
        mock_chunker.chunk.return_value = [ChunkResult(text="x", start_idx=0, end_idx=1, token_count=1, metadata={})]
        mock_chunking.get_chunker.return_value = mock_chunker

        mock_store = Mock()
        mock_store.add_chunks.return_value = 1
        mock_store_factory.get_store.return_value = mock_store

        ingestion = ClinicalDocumentIngestion(db_path="test_db")
        ingestion.ingest_text(text="Test", doc_type="procedural")

        mock_store_factory.get_store.assert_called_with("procedural", db_path="test_db")

    @patch('src.knowledge.clinical_ingestion.VectorStoreFactory')
    @patch('src.knowledge.clinical_ingestion.ChunkingFactory')
    def test_research_routes_to_research_store(self, mock_chunking, mock_store_factory):
        mock_chunker = Mock()
        mock_chunker.chunk.return_value = [ChunkResult(text="x", start_idx=0, end_idx=1, token_count=1, metadata={})]
        mock_chunking.get_chunker.return_value = mock_chunker

        mock_store = Mock()
        mock_store.add_chunks.return_value = 1
        mock_store_factory.get_store.return_value = mock_store

        ingestion = ClinicalDocumentIngestion(db_path="test_db")
        ingestion.ingest_text(text="Test", doc_type="research")

        mock_store_factory.get_store.assert_called_with("research", db_path="test_db")