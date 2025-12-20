"""
Clinical ingestion utilities for nurseRN RAG system (Phase 1)

Provides ClinicalDocumentIngestion and helper convenience functions
used during Phase 1 foundation enhancement.

This module provides a minimal, test-friendly API while delegating
all real ingestion to the production-safe KnowledgeIngestionService:
- two-phase commit (prevents zombie data)
- metadata schema enforcement (incl. is_active)
- embedding + chunk caches

IMPORTANT:
- External callers should prefer src/knowledge/ingestion_service.py directly.
- This wrapper exists for backwards compatibility and unit tests.

This module intentionally keeps a small API surface:
- IngestionResult dataclass
- ClinicalDocumentIngestion with:
  - ingest_text(text, doc_type=None, chunker_params=None, source_name=None)
  - ingest_file(path, doc_type=None, **kwargs)
  - ingest_folder(folder, **kwargs)

Created: 2025-12-15
Phase: 1 - Foundation Enhancement
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging
import os

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    success: bool
    doc_id: Optional[str] = None
    chunk_count: int = 0
    store_type: Optional[str] = None
    doc_type: Optional[str] = None
    error_message: Optional[str] = None


class ClinicalDocumentIngestion:
    """Orchestrates ingestion of clinical/procedural/research documents."""

    def __init__(self, db_path: str = "data/chroma_db", default_doc_type: str = "clinical"):
        self.db_path = db_path
        self.default_doc_type = default_doc_type

    @staticmethod
    def _map_doc_type_to_store(doc_type: str) -> str:
        return {
            "clinical": "clinical",
            "procedural": "procedural",
            "research": "research",
        }.get(doc_type, "personal")

    def _get_service(self):
        """Create an ingestion service pinned to this instance's db_path."""
        from src.knowledge.config import KnowledgeConfig
        from src.knowledge.ingestion_service import KnowledgeIngestionService

        cfg = KnowledgeConfig(db_path=self.db_path)
        return KnowledgeIngestionService(config=cfg)

    def ingest_text(self, text: str, doc_type: Optional[str] = None, chunker_params: Optional[Dict[str, Any]] = None, source_name: Optional[str] = None) -> IngestionResult:
        doc_type = doc_type or self.default_doc_type
        store_type = self._map_doc_type_to_store(doc_type)

        service = self._get_service()
        result = service.ingest_text(
            text=text,
            doc_type=doc_type,
            store_type=store_type,
            source_type=doc_type,
            source_name=source_name,
            auto_commit=True,
            extra_metadata=chunker_params or None,
        )
        return IngestionResult(
            success=bool(result.success),
            doc_id=result.doc_key,
            chunk_count=int(result.chunk_count or 0),
            store_type=result.store_type,
            doc_type=result.doc_type,
            error_message=result.error_message,
        )

    def ingest_file(self, path: str, doc_type: Optional[str] = None, **kwargs) -> IngestionResult:
        if not os.path.exists(path):
            return IngestionResult(success=False, error_message=f"File not found: {path}")

        doc_type = doc_type or self.default_doc_type
        store_type = self._map_doc_type_to_store(doc_type)

        service = self._get_service()
        result = service.ingest_file(
            file_path=str(path),
            doc_type=doc_type,
            store_type=store_type,
            source_type=doc_type,
            auto_commit=True,
        )
        return IngestionResult(
            success=bool(result.success),
            doc_id=result.doc_key,
            chunk_count=int(result.chunk_count or 0),
            store_type=result.store_type,
            doc_type=result.doc_type,
            error_message=result.error_message,
        )

    def ingest_folder(self, folder: str, doc_type: Optional[str] = None, **kwargs) -> List[IngestionResult]:
        results: List[IngestionResult] = []
        if not os.path.isdir(folder):
            return [IngestionResult(success=False, error_message=f"Not a folder: {folder}")]

        for fname in os.listdir(folder):
            path = os.path.join(folder, fname)
            if os.path.isfile(path):
                res = self.ingest_file(path, doc_type=doc_type, **kwargs)
                results.append(res)
        return results


# Convenience helpers

def ingest_clinical_text(text: str, source_name: Optional[str] = None, db_path: str = "data/chroma_db") -> IngestionResult:
    ingestion = ClinicalDocumentIngestion(db_path=db_path, default_doc_type="clinical")
    return ingestion.ingest_text(text=text, doc_type="clinical", source_name=source_name)


def ingest_procedural_text(text: str, source_name: Optional[str] = None, db_path: str = "data/chroma_db") -> IngestionResult:
    ingestion = ClinicalDocumentIngestion(db_path=db_path, default_doc_type="procedural")
    return ingestion.ingest_text(text=text, doc_type="procedural", source_name=source_name)


def ingest_research_text(text: str, source_name: Optional[str] = None, db_path: str = "data/chroma_db") -> IngestionResult:
    ingestion = ClinicalDocumentIngestion(db_path=db_path, default_doc_type="research")
    return ingestion.ingest_text(text=text, doc_type="research", source_name=source_name)
