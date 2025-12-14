"""
Personal Library Vector Store for Knowledge Library
Wraps agno ChromaDb with project-specific collections and convenience methods.

Created: 2025-12-13
Phase: B2

Tracer IDs: TRACE-B2-001 through TRACE-B2-006
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agno.vectordb.chroma.chromadb import ChromaDb
from agno.knowledge.document.base import Document
from agno.knowledge.embedder.openai import OpenAIEmbedder

from src.knowledge.document_ingester import ChunkRecord

logger = logging.getLogger(__name__)


# Collection names (designed for Phase C expansion)
COLLECTION_PERSONAL = "personal_docs"
COLLECTION_PUBMED_CACHE = "pubmed_cache"      # Phase C
COLLECTION_ARXIV_CACHE = "arxiv_cache"        # Phase C
COLLECTION_COMBINED = "combined_index"        # Phase C


class VectorStoreError(Exception):
    """Base exception for vector store errors."""
    pass


class CollectionNotFoundError(VectorStoreError):
    """Raised when collection does not exist."""
    pass


class DocumentNotFoundError(VectorStoreError):
    """Raised when document is not found."""
    pass


class SearchResult:
    """
    Search result with relevance score and metadata.

    Attributes:
        chunk_id: Unique chunk identifier
        doc_id: Parent document identifier
        text: The chunk text content
        score: Relevance score (0-1, higher is better)
        source_path: Original file path
        page_num: Page number if applicable
        metadata: Full metadata dictionary
    """

    def __init__(
        self,
        chunk_id: str,
        doc_id: str,
        text: str,
        score: float,
        source_path: str,
        page_num: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.chunk_id = chunk_id
        self.doc_id = doc_id
        self.text = text
        self.score = score
        self.source_path = source_path
        self.page_num = page_num
        self.metadata = metadata or {}

    @property
    def filename(self) -> str:
        """Extract filename from source path."""
        return Path(self.source_path).name if self.source_path else ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "chunk_id": self.chunk_id,
            "doc_id": self.doc_id,
            "text": self.text,
            "score": self.score,
            "source_path": self.source_path,
            "page_num": self.page_num,
            "filename": self.filename,
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        return f"SearchResult(filename={self.filename}, score={self.score:.3f}, page={self.page_num})"


class PersonalLibraryVectorStore:
    """
    Vector store for personal document library.

    Wraps agno ChromaDb with:
    - Project-specific collection management
    - ChunkRecord integration
    - Convenience search methods
    - Tracer points for debugging

    Example:
        store = PersonalLibraryVectorStore()
        store.add_chunks(chunks)  # From DocumentIngester
        results = store.search("fall prevention protocols", limit=5)
        for r in results:
            print(f"{r.filename} (p.{r.page_num}): {r.score:.2f}")
    """

    def __init__(
        self,
        collection_name: str = COLLECTION_PERSONAL,
        db_path: str = "data/chroma_db",
        embedder: Optional[OpenAIEmbedder] = None,
    ):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the ChromaDB collection
            db_path: Path to persistent ChromaDB storage
            embedder: Optional custom embedder (defaults to OpenAI text-embedding-3-small)
        """
        self.collection_name = collection_name
        self.db_path = db_path

        # Ensure db path exists
        Path(db_path).mkdir(parents=True, exist_ok=True)

        # Initialize embedder
        self.embedder = embedder or OpenAIEmbedder(id="text-embedding-3-small")

        # Initialize ChromaDb
        self._db: Optional[ChromaDb] = None
        self._initialized = False

        logger.info(f"PersonalLibraryVectorStore configured: collection={collection_name}, path={db_path}")

    def _trace(self, trace_id: str, **kwargs) -> None:
        """Log a trace point for debugging."""
        msg = f"[{trace_id}] " + " | ".join(f"{k}={v}" for k, v in kwargs.items())
        logger.debug(msg)

    @property
    def db(self) -> ChromaDb:
        """Get or initialize the ChromaDb instance."""
        if self._db is None:
            self._db = ChromaDb(
                collection=self.collection_name,
                path=self.db_path,
                persistent_client=True,
                embedder=self.embedder
            )
            self._trace("TRACE-B2-001", collection_name=self.collection_name, path=self.db_path)
        return self._db

    def initialize(self) -> None:
        """Initialize the collection (create if not exists)."""
        if not self._initialized:
            self.db.create()
            self._initialized = True
            self._trace("TRACE-B2-001", collection_name=self.collection_name, path=self.db_path)
            logger.info(f"Collection '{self.collection_name}' initialized")

    def add_chunks(self, chunks: List[ChunkRecord]) -> int:
        """
        Add chunk records to the vector store.

        Args:
            chunks: List of ChunkRecord objects from DocumentIngester

        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0

        self.initialize()

        # Convert ChunkRecords to Documents
        documents = [chunk.to_document() for chunk in chunks]

        # Generate content hash from first chunk's doc_id
        content_hash = chunks[0].doc_id

        # Calculate total tokens (approximate)
        total_chars = sum(len(chunk.text) for chunk in chunks)

        # Insert documents
        try:
            self.db.upsert(content_hash=content_hash, documents=documents)
            self._trace(
                "TRACE-B2-002",
                count=len(documents),
                total_chars=total_chars,
                doc_id=content_hash
            )
            logger.info(f"Added {len(documents)} chunks ({total_chars} chars) to collection")
            return len(documents)
        except Exception as e:
            logger.error(f"Failed to add chunks: {e}")
            raise VectorStoreError(f"Failed to add chunks: {e}")

    def add_documents(self, documents: List[Document], content_hash: str) -> int:
        """
        Add raw Document objects to the vector store.

        Args:
            documents: List of agno Document objects
            content_hash: Unique hash for this batch

        Returns:
            Number of documents added
        """
        if not documents:
            return 0

        self.initialize()

        try:
            self.db.upsert(content_hash=content_hash, documents=documents)
            self._trace("TRACE-B2-002", count=len(documents), content_hash=content_hash)
            return len(documents)
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise VectorStoreError(f"Failed to add documents: {e}")

    def search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search the vector store for relevant chunks.

        Args:
            query: Search query text
            limit: Maximum number of results to return
            filters: Optional metadata filters (e.g., {"source_type": "personal"})

        Returns:
            List of SearchResult objects, sorted by relevance (highest first)
        """
        self.initialize()

        self._trace("TRACE-B2-003", query=query[:50], limit=limit)

        try:
            # Perform search
            docs = self.db.search(query=query, limit=limit, filters=filters)

            # Convert to SearchResults
            results: List[SearchResult] = []
            for doc in docs:
                meta = doc.meta_data or {}

                # Extract distance/score - ChromaDB returns distances, convert to similarity
                distance = meta.get("distances", 1.0)
                # Convert L2 distance to similarity score (0-1)
                score = 1.0 / (1.0 + distance) if distance else 0.0

                result = SearchResult(
                    chunk_id=doc.id or meta.get("chunk_id", ""),
                    doc_id=doc.content_id or meta.get("doc_id", ""),
                    text=doc.content,
                    score=score,
                    source_path=meta.get("source_path", ""),
                    page_num=meta.get("page_num"),
                    metadata=meta
                )
                results.append(result)

            # Sort by score (highest first)
            results.sort(key=lambda r: r.score, reverse=True)

            top_score = results[0].score if results else 0.0
            self._trace("TRACE-B2-004", count=len(results), top_score=f"{top_score:.3f}")

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise VectorStoreError(f"Search failed: {e}")

    def delete_document(self, doc_id: str) -> bool:
        """
        Delete all chunks for a document by doc_id.

        Args:
            doc_id: Document ID (content_id from ChunkRecord)

        Returns:
            True if document was deleted, False if not found
        """
        self.initialize()

        try:
            # Use content_id deletion
            result = self.db.delete_by_content_id(doc_id)
            self._trace("TRACE-B2-005", doc_id=doc_id, deleted=result)

            if result:
                logger.info(f"Deleted document: {doc_id}")
            else:
                logger.info(f"Document not found for deletion: {doc_id}")

            return result
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            raise VectorStoreError(f"Delete failed: {e}")

    def delete_by_source_path(self, source_path: str) -> bool:
        """
        Delete all chunks from a specific source file.

        Args:
            source_path: Original file path

        Returns:
            True if chunks were deleted, False if not found
        """
        self.initialize()

        try:
            result = self.db.delete_by_metadata({"source_path": source_path})
            self._trace("TRACE-B2-005", source_path=source_path, deleted=result)
            return result
        except Exception as e:
            logger.error(f"Delete by source path failed: {e}")
            raise VectorStoreError(f"Delete by source path failed: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.

        Returns:
            Dictionary with collection statistics
        """
        self.initialize()

        try:
            count = self.db.get_count()
            exists = self.db.exists()

            stats = {
                "collection_name": self.collection_name,
                "db_path": self.db_path,
                "exists": exists,
                "chunk_count": count,
                "embedder": self.embedder.id if self.embedder else "none"
            }

            self._trace("TRACE-B2-006", doc_count="N/A", chunk_count=count)
            return stats
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                "collection_name": self.collection_name,
                "db_path": self.db_path,
                "error": str(e)
            }

    def list_documents(self) -> List[Dict[str, Any]]:
        """
        List all unique documents in the store.

        Returns:
            List of document info dictionaries
        """
        self.initialize()

        # Search with empty-ish query to get all documents
        # This is a workaround since ChromaDB doesn't have a direct "list all" method
        try:
            # Get a large number of results
            docs = self.db.search(query="document", limit=1000)

            # Group by doc_id
            doc_map: Dict[str, Dict[str, Any]] = {}
            for doc in docs:
                meta = doc.meta_data or {}
                doc_id = doc.content_id or meta.get("doc_id", "unknown")

                if doc_id not in doc_map:
                    doc_map[doc_id] = {
                        "doc_id": doc_id,
                        "source_path": meta.get("source_path", ""),
                        "filename": Path(meta.get("source_path", "")).name,
                        "chunk_count": 0,
                        "total_chunks": meta.get("total_chunks", 0),
                        "ingested_at": meta.get("ingested_at", ""),
                        "file_hash": meta.get("file_hash", "")
                    }
                doc_map[doc_id]["chunk_count"] += 1

            return list(doc_map.values())
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []

    def get_chunks_by_doc_id(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve ALL chunks for a specific document ID.

        Used for full document retrieval in synthesis operations.

        Args:
            doc_id: The document ID to retrieve chunks for

        Returns:
            List of chunk dictionaries with text and metadata
        """
        self.initialize()

        try:
            # Search with high limit to get all chunks
            # Use doc_id as query since it's in the metadata
            all_docs = self.db.search(query=doc_id, limit=500)

            # Filter to only chunks matching this doc_id
            matching_chunks = []
            for doc in all_docs:
                meta = doc.meta_data or {}
                if meta.get("doc_id") == doc_id or doc.content_id == doc_id:
                    matching_chunks.append({
                        "chunk_id": meta.get("chunk_id", doc.id),
                        "doc_id": doc_id,
                        "text": doc.content,
                        "source_path": meta.get("source_path", ""),
                        "page_num": meta.get("page_num"),
                        "chunk_index": meta.get("chunk_index", 0),
                        "total_chunks": meta.get("total_chunks", 0),
                        "char_count": meta.get("char_count", len(doc.content)),
                    })

            logger.info(f"Retrieved {len(matching_chunks)} chunks for doc_id: {doc_id}")
            return matching_chunks

        except Exception as e:
            logger.error(f"Failed to get chunks for doc_id {doc_id}: {e}")
            return []

    def clear(self) -> bool:
        """
        Clear all documents from the collection.

        Returns:
            True if cleared successfully
        """
        self.initialize()

        try:
            result = self.db.delete()
            logger.info(f"Collection '{self.collection_name}' cleared")
            return result
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise VectorStoreError(f"Failed to clear collection: {e}")

    def drop(self) -> None:
        """Drop the entire collection."""
        try:
            self.db.drop()
            self._initialized = False
            logger.info(f"Collection '{self.collection_name}' dropped")
        except Exception as e:
            logger.error(f"Failed to drop collection: {e}")
            raise VectorStoreError(f"Failed to drop collection: {e}")

    def exists(self) -> bool:
        """Check if the collection exists."""
        return self.db.exists()


def get_personal_library_store(
    collection_name: str = COLLECTION_PERSONAL,
    db_path: str = "data/chroma_db"
) -> PersonalLibraryVectorStore:
    """
    Factory function to get a configured PersonalLibraryVectorStore.

    Args:
        collection_name: Name of the collection
        db_path: Path to ChromaDB storage

    Returns:
        Configured PersonalLibraryVectorStore instance
    """
    return PersonalLibraryVectorStore(
        collection_name=collection_name,
        db_path=db_path
    )
