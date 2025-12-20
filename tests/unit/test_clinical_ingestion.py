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
from src.knowledge.ingestion_service import IngestionResult as ServiceIngestionResult


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
    @patch("src.knowledge.clinical_ingestion.ClinicalDocumentIngestion._get_service")
    def test_ingest_text_success(self, mock_get_service):
        mock_service = Mock()
        mock_service.ingest_text.return_value = ServiceIngestionResult(
            success=True,
            doc_key="inline_123",
            ingestion_run_id="ing_x",
            chunk_count=1,
            store_type="clinical",
            doc_type="clinical",
            committed=True,
        )
        mock_get_service.return_value = mock_service

        ingestion = ClinicalDocumentIngestion()
        result = ingestion.ingest_text(text="Test content", doc_type="clinical")

        assert isinstance(result, IngestionResult)
        assert result.success is True
        assert result.chunk_count == 1

    @patch("src.knowledge.clinical_ingestion.ClinicalDocumentIngestion._get_service")
    def test_ingest_text_empty(self, mock_get_service):
        mock_service = Mock()
        mock_service.ingest_text.return_value = ServiceIngestionResult(
            success=False,
            error_message="Empty text provided",
        )
        mock_get_service.return_value = mock_service

        ingestion = ClinicalDocumentIngestion()
        result = ingestion.ingest_text(text="   ")
        assert result.success is False

    @patch("src.knowledge.clinical_ingestion.ClinicalDocumentIngestion._get_service")
    def test_ingest_text_uses_default_doc_type(self, mock_get_service):
        mock_service = Mock()
        mock_service.ingest_text.return_value = ServiceIngestionResult(
            success=True,
            doc_key="inline_abc",
            ingestion_run_id="ing_x",
            chunk_count=1,
            store_type="procedural",
            doc_type="procedural",
            committed=True,
        )
        mock_get_service.return_value = mock_service

        ingestion = ClinicalDocumentIngestion(default_doc_type="procedural")
        result = ingestion.ingest_text(text="Test text")  # No doc_type specified

        assert result.doc_type == "procedural"

    @patch("src.knowledge.clinical_ingestion.ClinicalDocumentIngestion._get_service")
    def test_ingest_text_with_chunker_params(self, mock_get_service):
        mock_service = Mock()
        mock_service.ingest_text.return_value = ServiceIngestionResult(
            success=True,
            doc_key="inline_abc",
            ingestion_run_id="ing_x",
            chunk_count=1,
            store_type="research",
            doc_type="research",
            committed=True,
        )
        mock_get_service.return_value = mock_service

        ingestion = ClinicalDocumentIngestion()
        ingestion.ingest_text(
            text="Test text",
            doc_type="research",
            chunker_params={"token_limit": 200}
        )
        assert mock_service.ingest_text.called


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
    @patch("src.knowledge.clinical_ingestion.ClinicalDocumentIngestion._get_service")
    def test_clinical_routes_to_clinical_store(self, mock_get_service):
        mock_service = Mock()
        mock_service.ingest_text.return_value = ServiceIngestionResult(
            success=True,
            doc_key="inline_abc",
            ingestion_run_id="ing_x",
            chunk_count=1,
            store_type="clinical",
            doc_type="clinical",
            committed=True,
        )
        mock_get_service.return_value = mock_service

        ingestion = ClinicalDocumentIngestion(db_path="test_db")
        ingestion.ingest_text(text="Test", doc_type="clinical")
        called_kwargs = mock_service.ingest_text.call_args.kwargs
        assert called_kwargs["store_type"] == "clinical"

    @patch("src.knowledge.clinical_ingestion.ClinicalDocumentIngestion._get_service")
    def test_procedural_routes_to_procedural_store(self, mock_get_service):
        mock_service = Mock()
        mock_service.ingest_text.return_value = ServiceIngestionResult(
            success=True,
            doc_key="inline_abc",
            ingestion_run_id="ing_x",
            chunk_count=1,
            store_type="procedural",
            doc_type="procedural",
            committed=True,
        )
        mock_get_service.return_value = mock_service

        ingestion = ClinicalDocumentIngestion(db_path="test_db")
        ingestion.ingest_text(text="Test", doc_type="procedural")
        called_kwargs = mock_service.ingest_text.call_args.kwargs
        assert called_kwargs["store_type"] == "procedural"

    @patch("src.knowledge.clinical_ingestion.ClinicalDocumentIngestion._get_service")
    def test_research_routes_to_research_store(self, mock_get_service):
        mock_service = Mock()
        mock_service.ingest_text.return_value = ServiceIngestionResult(
            success=True,
            doc_key="inline_abc",
            ingestion_run_id="ing_x",
            chunk_count=1,
            store_type="research",
            doc_type="research",
            committed=True,
        )
        mock_get_service.return_value = mock_service

        ingestion = ClinicalDocumentIngestion(db_path="test_db")
        ingestion.ingest_text(text="Test", doc_type="research")
        called_kwargs = mock_service.ingest_text.call_args.kwargs
        assert called_kwargs["store_type"] == "research"
