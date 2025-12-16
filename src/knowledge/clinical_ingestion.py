"""
Clinical ingestion utilities for nurseRN RAG system (Phase 1)

Provides ClinicalDocumentIngestion and helper convenience functions
used during Phase 1 foundation enhancement.

This module intentionally implements a minimal, test-friendly API:
- IngestionResult dataclass
- ClinicalDocumentIngestion with:
  - ingest_text(text, doc_type=None, chunker_params=None, source_name=None)
  - ingest_file(path, doc_type=None, **kwargs)  # uses DocumentIngester when available
  - ingest_folder(folder, **kwargs)

The code routes to ChunkingFactory.get_chunker(doc_type, **params)
and VectorStoreFactory.get_store(store_type, db_path=...)

Created: 2025-12-15
Phase: 1 - Foundation Enhancement
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import logging
import os

from src.knowledge.chunking_strategies import ChunkResult, ChunkingFactory
from src.knowledge.vector_store import VectorStoreFactory
from src.knowledge.document_ingester import DocumentIngester, ChunkRecord

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

    def _chunks_to_chunkrecords(self, chunks: List[ChunkResult], doc_id: str, source_name: Optional[str], source_type: str = "personal") -> List[ChunkRecord]:
        records: List[ChunkRecord] = []
        total_chunks = len(chunks)
        for i, c in enumerate(chunks):
            rec = ChunkRecord(
                doc_id=doc_id,
                chunk_id=f"{doc_id}_chunk_{i:04d}",
                text=c.text,
                source_path=source_name or "inline",
                source_type=source_type,
                chunk_index=i,
                total_chunks=total_chunks,
                char_count=len(c.text),
                metadata={**(c.metadata or {}), "token_count": c.token_count}
            )
            records.append(rec)
        return records

    def ingest_text(self, text: str, doc_type: Optional[str] = None, chunker_params: Optional[Dict[str, Any]] = None, source_name: Optional[str] = None) -> IngestionResult:
        if not text or not text.strip():
            return IngestionResult(success=False, error_message="Empty text provided")

        doc_type = doc_type or self.default_doc_type
        chunker_params = chunker_params or {}

        # obtain chunker
        chunker = ChunkingFactory.get_chunker(doc_type, **chunker_params)
        chunks = chunker.chunk(text)

        doc_id = source_name or f"doc_{os.urandom(4).hex()}"

        # route to appropriate store
        store_type = {
            "clinical": "clinical",
            "procedural": "procedural",
            "research": "research"
        }.get(doc_type, "personal")

        store = VectorStoreFactory.get_store(store_type, db_path=self.db_path)

        # convert chunks to ChunkRecord and add
        chunk_records = self._chunks_to_chunkrecords(chunks, doc_id=doc_id, source_name=source_name, source_type=doc_type)
        added = store.add_chunks(chunk_records)

        return IngestionResult(success=True, doc_id=doc_id, chunk_count=len(chunk_records), store_type=store_type, doc_type=doc_type)

    def ingest_file(self, path: str, doc_type: Optional[str] = None, **kwargs) -> IngestionResult:
        if not os.path.exists(path):
            return IngestionResult(success=False, error_message=f"File not found: {path}")

        # Use DocumentIngester to extract text/chunks if available
        di = DocumentIngester()
        chunks = di.ingest_file(path)
        if not chunks:
            return IngestionResult(success=False, error_message="No chunks produced from file")

        doc_id = os.path.basename(path)
        store_type = doc_type or self.default_doc_type
        store = VectorStoreFactory.get_store(store_type, db_path=self.db_path)

        # ChunkRecord objects assumed from DocumentIngester; if not, map
        if isinstance(chunks[0], ChunkRecord):
            records = chunks
        else:
            records = self._chunks_to_chunkrecords(chunks, doc_id=doc_id, source_name=path, source_type=store_type)

        added = store.add_chunks(records)
        return IngestionResult(success=True, doc_id=doc_id, chunk_count=len(records), store_type=store_type, doc_type=doc_type)

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
