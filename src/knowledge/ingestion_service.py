"""
Knowledge Ingestion Service - Single Unified Ingestion API
Implements two-phase commit for safe updates without zombie data.

Created: 2025-12-16
Phase: Production-Safe Refactor

This is the ONLY ingestion entrypoint that external callers should use.
Do not use DocumentIngester or ClinicalDocumentIngestion directly.

Two-Phase Commit Protocol:
1. STAGE: Insert new chunks with is_active=false
2. COMMIT: Flip staged chunks to active, deactivate old chunks
3. CLEANUP (optional): Delete inactive chunks later
"""

import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from agno.knowledge.document.base import Document

from src.knowledge.config import get_config, KnowledgeConfig, ChunkerConfig
from src.knowledge.metadata import (
    ChunkMetadata,
    generate_doc_key,
    generate_chunk_id,
    generate_ingestion_run_id,
    normalize_for_chroma,
    MetadataValidationError,
)
from src.knowledge.cache import get_cache, KnowledgeCache
from src.knowledge.embedders import (
    get_embedder,
    get_current_embedder_spec,
    EmbedderSpec,
    BaseEmbedder,
)
from src.knowledge.chunking_strategies import (
    ChunkingFactory,
    ChunkingStrategy,
    ChunkResult,
    TokenBasedChunker,
    SemanticChunker,
    SentenceChunker,
)
from src.knowledge.document_ingester import DocumentIngester

logger = logging.getLogger(__name__)


@dataclass
class IngestionResult:
    """Result of an ingestion operation."""
    success: bool
    doc_key: Optional[str] = None
    ingestion_run_id: Optional[str] = None
    chunk_count: int = 0
    store_type: Optional[str] = None
    doc_type: Optional[str] = None
    error_message: Optional[str] = None
    cache_hits: int = 0
    embedding_cache_hits: int = 0
    committed: bool = False


@dataclass
class StagedChunk:
    """A chunk staged for insertion."""
    chunk_id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IngestionError(Exception):
    """Base exception for ingestion errors."""
    pass


class CommitError(IngestionError):
    """Raised when commit phase fails."""
    pass


class KnowledgeIngestionService:
    """
    Unified ingestion service for the knowledge module.

    Features:
    - Single API for all ingestion (files, text, folders)
    - Two-phase commit for safe updates
    - Caching for chunks and embeddings
    - Metadata schema enforcement
    - Config-driven (no hardcoding)
    """

    def __init__(
        self,
        config: Optional[KnowledgeConfig] = None,
        cache: Optional[KnowledgeCache] = None,
        embedder: Optional[BaseEmbedder] = None,
    ):
        """
        Initialize the ingestion service.

        Args:
            config: Configuration (uses global config if None)
            cache: Cache instance (uses global cache if None)
            embedder: Embedder instance (creates from config if None)
        """
        self.config = config or get_config()
        self._cache = cache
        self._embedder = embedder
        self._embedder_spec: Optional[EmbedderSpec] = None

        # Document ingester for file extraction
        self._document_ingester = DocumentIngester(
            chunk_size=2000,  # Will be overridden per doc_type
            overlap=200,
        )

        # Collection references (lazy-loaded)
        self._collections: Dict[str, Any] = {}

        logger.info("KnowledgeIngestionService initialized")

    @property
    def cache(self) -> KnowledgeCache:
        """Get the cache instance."""
        if self._cache is None:
            if self.config.cache.enabled:
                self._cache = get_cache()
            else:
                # Create a disabled cache (still needed for interface)
                self._cache = get_cache()
        return self._cache

    @property
    def embedder(self) -> BaseEmbedder:
        """Get the embedder instance."""
        if self._embedder is None:
            self._embedder = get_embedder(use_cache=True)
        return self._embedder

    @property
    def embedder_spec(self) -> EmbedderSpec:
        """Get the embedder specification."""
        if self._embedder_spec is None:
            self._embedder_spec = get_current_embedder_spec()
        return self._embedder_spec

    def _get_collection(self, store_type: str):
        """Get or create a Chroma collection for the given store type."""
        if store_type in self._collections:
            return self._collections[store_type]

        from agno.vectordb.chroma.chromadb import ChromaDb
        from agno.knowledge.embedder.openai import OpenAIEmbedder

        store_config = self.config.get_store_config(store_type)

        # Create ChromaDb with OpenAI embedder matching our config
        embedder = OpenAIEmbedder(
            id=self.config.embedder.model,
            dimensions=self.config.embedder.dimensions if self.config.embedder.dimensions != 1536 else None
        )

        db = ChromaDb(
            collection=store_config.collection_name,
            path=self.config.db_path,
            persistent_client=True,
            embedder=embedder
        )
        db.create()

        self._collections[store_type] = db
        logger.info(f"Initialized collection: {store_config.collection_name} for store_type={store_type}")
        return db

    def _get_raw_collection(self, store_type: str):
        """Get the raw Chroma Collection object for low-level operations."""
        db = self._get_collection(store_type)
        if db._collection is None:
            db._collection = db.client.get_collection(name=db.collection_name)
        return db._collection

    def _get_chunker(self, doc_type: str) -> ChunkingStrategy:
        """Get the chunker for a document type."""
        chunker_config = self.config.get_chunker_config(doc_type)

        # Map strategy name to class
        strategy_map = {
            "token": TokenBasedChunker,
            "semantic": SemanticChunker,
            "sentence": SentenceChunker,
        }

        chunker_class = strategy_map.get(chunker_config.strategy, TokenBasedChunker)

        # Build kwargs based on chunker type
        kwargs: Dict[str, Any] = {}
        if chunker_config.strategy == "sentence":
            kwargs["sentences_per_chunk"] = chunker_config.sentences_per_chunk or 5
            kwargs["overlap_sentences"] = chunker_config.overlap_sentences or 1
        else:
            if hasattr(chunker_class, "__init__"):
                # Token or semantic chunker
                if chunker_config.strategy == "token":
                    kwargs["token_limit"] = chunker_config.chunk_size
                else:
                    kwargs["chunk_size"] = chunker_config.chunk_size
                kwargs["overlap"] = chunker_config.overlap

        return chunker_class(**kwargs)

    def _compute_file_hash(self, file_path: Path) -> str:
        """Compute MD5 hash of a file."""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    # =========================================================================
    # Main Ingestion Methods
    # =========================================================================

    def ingest_file(
        self,
        file_path: str,
        doc_type: Optional[str] = None,
        store_type: Optional[str] = None,
        source_type: str = "personal",
        auto_commit: bool = True,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> IngestionResult:
        """
        Ingest a file into the knowledge store.

        Args:
            file_path: Path to the file to ingest
            doc_type: Document type for chunking strategy (inferred if None)
            store_type: Target store type (uses doc_type mapping if None)
            source_type: Source type metadata
            auto_commit: Whether to commit immediately (default: True)
            extra_metadata: Additional metadata to include

        Returns:
            IngestionResult with details of the operation
        """
        path = Path(file_path)

        # Validate file
        if not path.exists():
            return IngestionResult(
                success=False,
                error_message=f"File not found: {file_path}"
            )

        if not path.is_file():
            return IngestionResult(
                success=False,
                error_message=f"Not a file: {file_path}"
            )

        # Infer doc_type if not provided
        if doc_type is None:
            doc_type = self._infer_doc_type(path)

        # Infer store_type from doc_type
        if store_type is None:
            store_type = self._map_doc_type_to_store(doc_type)

        # Generate stable doc_key and run ID
        doc_key = generate_doc_key(str(path))
        ingestion_run_id = generate_ingestion_run_id()
        file_hash = self._compute_file_hash(path)

        logger.info(f"Ingesting file: {path.name} (doc_type={doc_type}, store={store_type})")

        # Get chunker config hash
        chunker_config = self.config.get_chunker_config(doc_type)
        chunker_config_hash = chunker_config.get_config_hash()

        # Check chunk cache
        cached_chunks = None
        cache_hits = 0
        if self.config.cache.enabled and self.config.cache.chunk_cache_enabled:
            cached_chunks = self.cache.get_chunks(file_hash, chunker_config_hash)
            if cached_chunks:
                cache_hits = len(cached_chunks)
                logger.debug(f"Chunk cache hit: {cache_hits} chunks")

        # Extract and chunk if not cached
        if cached_chunks is None:
            try:
                text_content = self._extract_text(path)
                if not text_content or not text_content.strip():
                    return IngestionResult(
                        success=False,
                        error_message=f"No content extracted from {file_path}"
                    )

                # Chunk the content
                chunker = self._get_chunker(doc_type)
                chunk_results = chunker.chunk(text_content)

                # Convert to cacheable format
                cached_chunks = [
                    {
                        "text": cr.text,
                        "start_idx": cr.start_idx,
                        "end_idx": cr.end_idx,
                        "token_count": cr.token_count,
                        "metadata": cr.metadata,
                    }
                    for cr in chunk_results
                ]

                # Cache the chunks
                if self.config.cache.enabled and self.config.cache.chunk_cache_enabled:
                    self.cache.set_chunks(file_hash, chunker_config_hash, cached_chunks)

            except Exception as e:
                logger.error(f"Failed to extract/chunk file: {e}")
                return IngestionResult(
                    success=False,
                    error_message=f"Extraction failed: {e}"
                )

        if not cached_chunks:
            return IngestionResult(
                success=False,
                error_message="No chunks produced"
            )

        # Build staged chunks with metadata
        staged_chunks = self._prepare_staged_chunks(
            chunks=cached_chunks,
            doc_key=doc_key,
            ingestion_run_id=ingestion_run_id,
            file_hash=file_hash,
            doc_type=doc_type,
            store_type=store_type,
            source_type=source_type,
            source_path=str(path.absolute()),
            chunker_config_hash=chunker_config_hash,
            extra_metadata=extra_metadata,
        )

        # Compute embeddings (with caching)
        embedding_cache_hits = self._compute_embeddings(staged_chunks)

        # Stage the chunks
        try:
            self._stage_chunks(staged_chunks, store_type)
        except Exception as e:
            logger.error(f"Failed to stage chunks: {e}")
            return IngestionResult(
                success=False,
                error_message=f"Stage failed: {e}",
                doc_key=doc_key,
                ingestion_run_id=ingestion_run_id,
            )

        # Commit if requested
        committed = False
        if auto_commit:
            try:
                self._commit_ingestion(doc_key, ingestion_run_id, store_type)
                committed = True
            except CommitError as e:
                logger.error(f"Commit failed: {e}")
                return IngestionResult(
                    success=False,
                    error_message=f"Commit failed: {e}",
                    doc_key=doc_key,
                    ingestion_run_id=ingestion_run_id,
                    chunk_count=len(staged_chunks),
                )

        return IngestionResult(
            success=True,
            doc_key=doc_key,
            ingestion_run_id=ingestion_run_id,
            chunk_count=len(staged_chunks),
            store_type=store_type,
            doc_type=doc_type,
            cache_hits=cache_hits,
            embedding_cache_hits=embedding_cache_hits,
            committed=committed,
        )

    def ingest_text(
        self,
        text: str,
        doc_type: str = "default",
        store_type: Optional[str] = None,
        source_type: str = "inline",
        source_name: Optional[str] = None,
        auto_commit: bool = True,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> IngestionResult:
        """
        Ingest raw text into the knowledge store.

        Args:
            text: Text content to ingest
            doc_type: Document type for chunking strategy
            store_type: Target store type
            source_type: Source type metadata
            source_name: Optional name for the source
            auto_commit: Whether to commit immediately
            extra_metadata: Additional metadata

        Returns:
            IngestionResult with details of the operation
        """
        if not text or not text.strip():
            return IngestionResult(
                success=False,
                error_message="Empty text provided"
            )

        # Infer store_type from doc_type
        if store_type is None:
            store_type = self._map_doc_type_to_store(doc_type)

        # Generate identifiers
        text_hash = hashlib.md5(text.encode()).hexdigest()
        doc_key = source_name or f"inline_{text_hash[:12]}"
        ingestion_run_id = generate_ingestion_run_id()

        # Get chunker config
        chunker_config = self.config.get_chunker_config(doc_type)
        chunker_config_hash = chunker_config.get_config_hash()

        # Check chunk cache
        cached_chunks = None
        cache_hits = 0
        if self.config.cache.enabled and self.config.cache.chunk_cache_enabled:
            cached_chunks = self.cache.get_chunks(text_hash, chunker_config_hash)
            if cached_chunks:
                cache_hits = len(cached_chunks)

        # Chunk if not cached
        if cached_chunks is None:
            chunker = self._get_chunker(doc_type)
            chunk_results = chunker.chunk(text)

            cached_chunks = [
                {
                    "text": cr.text,
                    "start_idx": cr.start_idx,
                    "end_idx": cr.end_idx,
                    "token_count": cr.token_count,
                    "metadata": cr.metadata,
                }
                for cr in chunk_results
            ]

            if self.config.cache.enabled and self.config.cache.chunk_cache_enabled:
                self.cache.set_chunks(text_hash, chunker_config_hash, cached_chunks)

        if not cached_chunks:
            return IngestionResult(
                success=False,
                error_message="No chunks produced"
            )

        # Build staged chunks
        staged_chunks = self._prepare_staged_chunks(
            chunks=cached_chunks,
            doc_key=doc_key,
            ingestion_run_id=ingestion_run_id,
            file_hash=text_hash,
            doc_type=doc_type,
            store_type=store_type,
            source_type=source_type,
            source_path=source_name or "inline",
            chunker_config_hash=chunker_config_hash,
            extra_metadata=extra_metadata,
        )

        # Compute embeddings
        embedding_cache_hits = self._compute_embeddings(staged_chunks)

        # Stage the chunks
        try:
            self._stage_chunks(staged_chunks, store_type)
        except Exception as e:
            return IngestionResult(
                success=False,
                error_message=f"Stage failed: {e}",
                doc_key=doc_key,
                ingestion_run_id=ingestion_run_id,
            )

        # Commit if requested
        committed = False
        if auto_commit:
            try:
                self._commit_ingestion(doc_key, ingestion_run_id, store_type)
                committed = True
            except CommitError as e:
                return IngestionResult(
                    success=False,
                    error_message=f"Commit failed: {e}",
                    doc_key=doc_key,
                    ingestion_run_id=ingestion_run_id,
                    chunk_count=len(staged_chunks),
                )

        return IngestionResult(
            success=True,
            doc_key=doc_key,
            ingestion_run_id=ingestion_run_id,
            chunk_count=len(staged_chunks),
            store_type=store_type,
            doc_type=doc_type,
            cache_hits=cache_hits,
            embedding_cache_hits=embedding_cache_hits,
            committed=committed,
        )

    def ingest_folder(
        self,
        folder_path: str,
        doc_type: Optional[str] = None,
        store_type: Optional[str] = None,
        recursive: bool = True,
        auto_commit: bool = True,
    ) -> List[IngestionResult]:
        """
        Ingest all supported files from a folder.

        Args:
            folder_path: Path to the folder
            doc_type: Document type (inferred per file if None)
            store_type: Target store type
            recursive: Whether to process subdirectories
            auto_commit: Whether to commit each file immediately

        Returns:
            List of IngestionResult for each file
        """
        folder = Path(folder_path)

        if not folder.exists():
            return [IngestionResult(
                success=False,
                error_message=f"Folder not found: {folder_path}"
            )]

        if not folder.is_dir():
            return [IngestionResult(
                success=False,
                error_message=f"Not a directory: {folder_path}"
            )]

        # Find supported files
        supported_extensions = set(self.config.supported_extensions)
        if recursive:
            files = list(folder.rglob("*"))
        else:
            files = list(folder.glob("*"))

        supported_files = [
            f for f in files
            if f.is_file() and f.suffix.lower() in supported_extensions
        ]

        logger.info(f"Found {len(supported_files)} supported files in {folder}")

        results = []
        for file_path in supported_files:
            result = self.ingest_file(
                file_path=str(file_path),
                doc_type=doc_type,
                store_type=store_type,
                auto_commit=auto_commit,
            )
            results.append(result)

        return results

    # =========================================================================
    # Two-Phase Commit Implementation
    # =========================================================================

    def _prepare_staged_chunks(
        self,
        chunks: List[Dict[str, Any]],
        doc_key: str,
        ingestion_run_id: str,
        file_hash: str,
        doc_type: str,
        store_type: str,
        source_type: str,
        source_path: str,
        chunker_config_hash: str,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[StagedChunk]:
        """Prepare chunks for staging with full metadata."""
        staged = []
        total_chunks = len(chunks)
        embedder_spec_hash = self.embedder_spec.get_hash()

        for i, chunk_data in enumerate(chunks):
            chunk_id = generate_chunk_id(doc_key, ingestion_run_id, i)

            # Build metadata
            metadata = ChunkMetadata(
                doc_key=doc_key,
                ingestion_run_id=ingestion_run_id,
                chunk_id=chunk_id,
                store_type=store_type,
                doc_type=doc_type,
                source_type=source_type,
                source_path=source_path,
                file_hash=file_hash,
                embedder_spec_hash=embedder_spec_hash,
                chunker_config_hash=chunker_config_hash,
                is_active=False,  # Staged as inactive
                ingested_at=datetime.utcnow().isoformat(),
                chunk_index=i,
                total_chunks=total_chunks,
                char_count=len(chunk_data["text"]),
                token_count=chunk_data.get("token_count"),
                filename=Path(source_path).name if source_path != "inline" else None,
            )

            # Add extra metadata
            meta_dict = metadata.to_dict()
            meta_dict["doc_id"] = doc_key
            if extra_metadata:
                meta_dict.update(extra_metadata)

            staged.append(StagedChunk(
                chunk_id=chunk_id,
                text=chunk_data["text"],
                metadata=normalize_for_chroma(meta_dict),
            ))

        return staged

    def _compute_embeddings(self, staged_chunks: List[StagedChunk]) -> int:
        """Compute embeddings for staged chunks, using cache where possible."""
        texts = [sc.text for sc in staged_chunks]
        embedder_spec_hash = self.embedder_spec.get_hash()

        # Check cache for existing embeddings
        text_hashes = [self.cache.compute_text_hash(t) for t in texts]
        cached = {}
        if self.config.cache.enabled and self.config.cache.embedding_cache_enabled:
            cached = self.cache.get_embeddings_batch(text_hashes, embedder_spec_hash)

        cache_hits = len(cached)

        # Determine which texts need embedding
        uncached_indices = []
        uncached_texts = []
        for i, (text, text_hash) in enumerate(zip(texts, text_hashes)):
            if text_hash in cached:
                staged_chunks[i].embedding = cached[text_hash]
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)

        # Compute embeddings for uncached texts
        if uncached_texts:
            new_embeddings = self.embedder.embed_texts(uncached_texts)

            # Store results and cache
            new_cache_entries = {}
            for idx, embedding in zip(uncached_indices, new_embeddings):
                staged_chunks[idx].embedding = embedding
                new_cache_entries[text_hashes[idx]] = embedding

            if self.config.cache.enabled and self.config.cache.embedding_cache_enabled:
                self.cache.set_embeddings_batch(new_cache_entries, embedder_spec_hash)

        logger.debug(f"Embeddings: {cache_hits} cache hits, {len(uncached_texts)} computed")
        return cache_hits

    def _stage_chunks(self, staged_chunks: List[StagedChunk], store_type: str) -> None:
        """
        Stage chunks by inserting them with is_active=false.

        Uses Chroma's add with pre-computed embeddings to bypass wrapper's embedding.
        """
        collection = self._get_raw_collection(store_type)

        # Prepare batch data
        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for sc in staged_chunks:
            if sc.embedding is None:
                raise IngestionError(f"Chunk {sc.chunk_id} has no embedding")

            ids.append(sc.chunk_id)
            embeddings.append(sc.embedding)
            documents.append(sc.text.replace("\x00", "\ufffd"))  # Clean null bytes
            metadatas.append(sc.metadata)

        # Insert directly into Chroma collection
        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(f"Staged {len(staged_chunks)} chunks for store_type={store_type}")

    def _commit_ingestion(
        self,
        doc_key: str,
        ingestion_run_id: str,
        store_type: str
    ) -> None:
        """
        Commit the ingestion: activate new chunks, deactivate old ones.

        Two-phase commit:
        1. Find and deactivate old active chunks for this doc_key
        2. Activate the newly staged chunks
        """
        collection = self._get_raw_collection(store_type)

        try:
            # Step 1: Find old active chunks for this doc_key
            old_result = collection.get(
                where={"$and": [
                    {"doc_key": {"$eq": doc_key}},
                    {"is_active": {"$eq": True}},
                ]}
            )
            old_ids = old_result.get("ids", [])

            # Step 2: Find newly staged chunks
            new_result = collection.get(
                where={"ingestion_run_id": {"$eq": ingestion_run_id}}
            )
            new_ids = new_result.get("ids", [])

            if not new_ids:
                raise CommitError(f"No staged chunks found for ingestion_run_id={ingestion_run_id}")

            # Step 3: Deactivate old chunks
            if old_ids:
                collection.update(
                    ids=old_ids,
                    metadatas=[{"is_active": False} for _ in old_ids]
                )
                logger.debug(f"Deactivated {len(old_ids)} old chunks for doc_key={doc_key}")

            # Step 4: Activate new chunks
            collection.update(
                ids=new_ids,
                metadatas=[{"is_active": True} for _ in new_ids]
            )
            logger.info(f"Committed {len(new_ids)} chunks for doc_key={doc_key}")

        except Exception as e:
            raise CommitError(f"Failed to commit ingestion: {e}")

    def commit(self, doc_key: str, ingestion_run_id: str, store_type: str) -> bool:
        """
        Manually commit a staged ingestion.

        Use this when auto_commit=False was used during ingestion.
        """
        try:
            self._commit_ingestion(doc_key, ingestion_run_id, store_type)
            return True
        except CommitError as e:
            logger.error(f"Manual commit failed: {e}")
            return False

    def rollback(self, ingestion_run_id: str, store_type: str) -> bool:
        """
        Rollback a staged ingestion by deleting staged chunks.

        Use this to abort an uncommitted ingestion.
        """
        try:
            collection = self._get_raw_collection(store_type)

            # Find staged chunks
            result = collection.get(
                where={"ingestion_run_id": {"$eq": ingestion_run_id}}
            )
            ids = result.get("ids", [])

            if ids:
                collection.delete(ids=ids)
                logger.info(f"Rolled back {len(ids)} staged chunks for ingestion_run_id={ingestion_run_id}")

            return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False

    def cleanup_inactive(self, store_type: str, older_than_days: int = 7) -> int:
        """
        Delete inactive chunks older than specified days.

        This is the optional cleanup phase of two-phase commit.
        """
        from datetime import datetime, timedelta

        collection = self._get_raw_collection(store_type)
        cutoff = (datetime.utcnow() - timedelta(days=older_than_days)).isoformat()

        try:
            # Find old inactive chunks
            result = collection.get(
                where={"$and": [
                    {"is_active": {"$eq": False}},
                    {"ingested_at": {"$lt": cutoff}},
                ]}
            )
            ids = result.get("ids", [])

            if ids:
                collection.delete(ids=ids)
                logger.info(f"Cleaned up {len(ids)} inactive chunks from {store_type}")

            return len(ids)
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _extract_text(self, file_path: Path) -> str:
        """Extract text content from a file."""
        suffix = file_path.suffix.lower()

        # Use DocumentIngester for complex formats
        if suffix in (".pdf", ".docx", ".pptx"):
            try:
                chunks = self._document_ingester.ingest_file(str(file_path))
                return "\n\n".join(chunk.text for chunk in chunks)
            except Exception as e:
                logger.warning(f"DocumentIngester failed, trying fallback: {e}")

        # Simple text extraction for text-based files
        if suffix in (".txt", ".md", ".markdown"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read()

        # CSV/JSON - read as text
        if suffix in (".csv", ".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()

        raise IngestionError(f"Unsupported file format: {suffix}")

    def _infer_doc_type(self, file_path: Path) -> str:
        """Infer document type from file path."""
        # Could be enhanced with content analysis
        name = file_path.name.lower()

        if any(kw in name for kw in ["clinical", "medical", "patient", "diagnosis"]):
            return "clinical"
        if any(kw in name for kw in ["protocol", "procedure", "workflow", "step"]):
            return "procedural"
        if any(kw in name for kw in ["research", "study", "paper", "journal"]):
            return "research"

        return "default"

    def _map_doc_type_to_store(self, doc_type: str) -> str:
        """Map document type to store type."""
        mapping = {
            "clinical": "clinical",
            "procedural": "procedural",
            "research": "research",
            "default": "personal",
        }
        return mapping.get(doc_type, "personal")


# =========================================================================
# Module-level convenience functions
# =========================================================================

_service_instance: Optional[KnowledgeIngestionService] = None


def get_ingestion_service() -> KnowledgeIngestionService:
    """Get the singleton ingestion service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = KnowledgeIngestionService()
    return _service_instance


def reset_ingestion_service() -> None:
    """Reset the singleton service instance (for testing)."""
    global _service_instance
    _service_instance = None


def ingest_file(file_path: str, **kwargs) -> IngestionResult:
    """Convenience function to ingest a file."""
    return get_ingestion_service().ingest_file(file_path, **kwargs)


def ingest_text(text: str, **kwargs) -> IngestionResult:
    """Convenience function to ingest text."""
    return get_ingestion_service().ingest_text(text, **kwargs)


def ingest_folder(folder_path: str, **kwargs) -> List[IngestionResult]:
    """Convenience function to ingest a folder."""
    return get_ingestion_service().ingest_folder(folder_path, **kwargs)
