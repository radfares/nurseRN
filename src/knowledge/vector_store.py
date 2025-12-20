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

# RAG-specific collections (Phase 1 - Foundation Enhancement)
COLLECTION_CLINICAL = "clinical_knowledge"     # Clinical facts, guidelines
COLLECTION_PROCEDURAL = "procedural_knowledge" # Protocols, workflows
COLLECTION_RESEARCH = "research_cache"         # Research findings cache


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
        if embedder is not None:
            self.embedder = embedder
        else:
            # Default to the configured embedder so query-time embeddings match ingestion-time embeddings.
            try:
                from src.knowledge.config import get_config

                cfg = get_config()
                dims = cfg.embedder.dimensions if cfg.embedder.dimensions != 1536 else None
                self.embedder = OpenAIEmbedder(id=cfg.embedder.model, dimensions=dims)
            except Exception:
                self.embedder = OpenAIEmbedder(id="text-embedding-3-small")

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
        filters: Optional[Dict[str, Any]] = None,
        include_inactive: bool = False
    ) -> List[SearchResult]:
        """
        Search the vector store for relevant chunks.

        Args:
            query: Search query text
            limit: Maximum number of results to return
            filters: Optional metadata filters (e.g., {"source_type": "personal"})
            include_inactive: If False (default), only return is_active=true chunks

        Returns:
            List of SearchResult objects, sorted by relevance (highest first)
        """
        self.initialize()

        self._trace("TRACE-B2-003", query=query[:50], limit=limit)

        # Apply is_active filter by default (R6 requirement)
        effective_filters = dict(filters) if filters else {}
        if not include_inactive:
            # Only return active chunks by default
            if "is_active" not in effective_filters:
                effective_filters["is_active"] = True

        try:
            # Perform search
            docs = self.db.search(query=query, limit=limit, filters=effective_filters if effective_filters else None)

            # Convert to SearchResults
            results: List[SearchResult] = []
            for doc in docs:
                meta = doc.meta_data or {}

                # Extract distance/score - ChromaDB returns distances, convert to similarity
                distance_raw = meta.get("distances", 1.0)
                # Convert L2 distance to similarity score (0-1, higher is better).
                # Chroma/agno may report 0.0 for identical vectors; that should map to score=1.0.
                try:
                    distance = float(distance_raw)
                except Exception:
                    distance = 1.0
                if distance < 0:
                    distance = 0.0
                score = 1.0 / (1.0 + distance)

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


# =============================================================================
# RAG-Enhanced Vector Stores (Phase 1 - Foundation Enhancement)
# =============================================================================

class ClinicalKnowledgeStore(PersonalLibraryVectorStore):
    """
    Vector store for clinical knowledge (facts, guidelines, evidence).

    Optimized for storing and retrieving clinical facts that require
    high accuracy and source attribution.

    Example:
        store = ClinicalKnowledgeStore()
        store.add_chunks(clinical_chunks)
        results = store.search("diabetes treatment guidelines", limit=5)
    """

    def __init__(self, db_path: str = "data/chroma_db", embedder: Optional[OpenAIEmbedder] = None):
        """
        Initialize clinical knowledge store.

        Args:
            db_path: Path to ChromaDB storage
            embedder: Optional custom embedder
        """
        super().__init__(
            collection_name=COLLECTION_CLINICAL,
            db_path=db_path,
            embedder=embedder
        )
        logger.info("ClinicalKnowledgeStore initialized")


class ProceduralKnowledgeStore(PersonalLibraryVectorStore):
    """
    Vector store for procedural knowledge (protocols, workflows, procedures).

    Optimized for storing step-by-step procedures and clinical protocols
    that clinicians need to follow.

    Example:
        store = ProceduralKnowledgeStore()
        store.add_chunks(protocol_chunks)
        results = store.search("IV insertion procedure", limit=5)
    """

    def __init__(self, db_path: str = "data/chroma_db", embedder: Optional[OpenAIEmbedder] = None):
        """
        Initialize procedural knowledge store.

        Args:
            db_path: Path to ChromaDB storage
            embedder: Optional custom embedder
        """
        super().__init__(
            collection_name=COLLECTION_PROCEDURAL,
            db_path=db_path,
            embedder=embedder
        )
        logger.info("ProceduralKnowledgeStore initialized")


class ResearchCacheStore(PersonalLibraryVectorStore):
    """
    Vector store for caching research findings and literature.

    Used for caching search results from external sources (PubMed, etc.)
    to reduce API calls and improve response times.

    Example:
        store = ResearchCacheStore()
        store.add_chunks(pubmed_chunks)
        results = store.search("fall prevention nursing", limit=10)
    """

    def __init__(self, db_path: str = "data/chroma_db", embedder: Optional[OpenAIEmbedder] = None):
        """
        Initialize research cache store.

        Args:
            db_path: Path to ChromaDB storage
            embedder: Optional custom embedder
        """
        super().__init__(
            collection_name=COLLECTION_RESEARCH,
            db_path=db_path,
            embedder=embedder
        )
        logger.info("ResearchCacheStore initialized")


class VectorStoreFactory:
    """
    Factory for creating and managing multiple vector store instances.

    Now config-driven: reads store configurations from KnowledgeConfig.

    Provides singleton-like access to vector stores, ensuring only one
    instance per store type exists at a time.

    Example:
        # Get stores by type (uses config for db_path and collection names)
        clinical_store = VectorStoreFactory.get_store("clinical")
        procedural_store = VectorStoreFactory.get_store("procedural")

        # Get with custom path (overrides config)
        test_store = VectorStoreFactory.get_store("clinical", db_path="data/test_db")

        # Clear cached instances
        VectorStoreFactory.clear_instances()
    """

    _instances: Dict[str, PersonalLibraryVectorStore] = {}

    # Mapping of store types to their classes
    _store_classes = {
        "personal": PersonalLibraryVectorStore,
        "clinical": ClinicalKnowledgeStore,
        "procedural": ProceduralKnowledgeStore,
        "research": ResearchCacheStore,
    }

    @classmethod
    def _get_config(cls):
        """Get knowledge config, with lazy import to avoid circular dependencies."""
        try:
            from src.knowledge.config import get_config
            return get_config()
        except ImportError:
            return None

    @classmethod
    def get_store(
        cls,
        store_type: str,
        db_path: Optional[str] = None,
        force_new: bool = False,
        embedder: Optional[OpenAIEmbedder] = None,
    ) -> PersonalLibraryVectorStore:
        """
        Get or create a vector store instance.

        Args:
            store_type: Type of store ("personal", "clinical", "procedural", "research")
            db_path: Path to ChromaDB storage (uses config if None)
            force_new: If True, create new instance even if one exists

        Returns:
            Vector store instance of the appropriate type

        Raises:
            ValueError: If store_type is not recognized
        """
        # Get db_path from config if not provided
        if db_path is None:
            config = cls._get_config()
            if config:
                db_path = config.db_path
            else:
                db_path = "data/chroma_db"

        # Create unique key for this store configuration.
        # If an embedder override is provided (common in tests), include a stable-ish signature
        # to avoid returning a cached store with a different query-embedder.
        embedder_sig = ""
        if embedder is not None:
            embedder_id = getattr(embedder, "id", None) or type(embedder).__name__
            dims = getattr(embedder, "dimensions", None)
            embedder_sig = f":embedder={embedder_id}:{dims}"
        cache_key = f"{store_type}:{db_path}{embedder_sig}"

        # Return cached instance if available and not forcing new
        if not force_new and cache_key in cls._instances:
            logger.debug(f"Returning cached store: {cache_key}")
            return cls._instances[cache_key]

        # Get the store class - first check config, then fallback to hardcoded
        store_class = cls._store_classes.get(store_type)
        if store_class is None:
            valid_types = list(cls._store_classes.keys())
            raise ValueError(f"Unknown store type: {store_type}. Valid types: {valid_types}")

        # Get collection name from config if available
        config = cls._get_config()
        collection_name = None
        if config:
            store_config = config.get_store_config(store_type)
            collection_name = store_config.collection_name

        # Create new instance
        logger.info(f"Creating new {store_type} store at {db_path}")
        if collection_name and store_class == PersonalLibraryVectorStore:
            instance = store_class(collection_name=collection_name, db_path=db_path, embedder=embedder)
        else:
            instance = store_class(db_path=db_path, embedder=embedder)

        # Cache the instance
        cls._instances[cache_key] = instance

        return instance

    @classmethod
    def clear_instances(cls) -> None:
        """Clear all cached store instances."""
        cls._instances.clear()
        logger.info("VectorStoreFactory: All cached instances cleared")

    @classmethod
    def get_available_types(cls) -> List[str]:
        """Get list of available store types."""
        return list(cls._store_classes.keys())

    @classmethod
    def register_store_type(cls, type_name: str, store_class: type) -> None:
        """
        Register a custom store type.

        Args:
            type_name: Name for the store type
            store_class: Class that extends PersonalLibraryVectorStore
        """
        cls._store_classes[type_name] = store_class
        logger.info(f"Registered store type: {type_name} -> {store_class.__name__}")
