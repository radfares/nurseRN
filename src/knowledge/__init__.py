"""
Personal Knowledge Library Module
Provides document ingestion, vector storage, and search capabilities for agents.

Created: 2025-12-13
Updated: 2025-12-16 (Production-Safe Refactor)

Phases:
- B1: Document Ingester
- B2: Vector Store
- B3: Personal Library Tools
- Production-Safe Refactor: Config-driven, caching, two-phase commit

Components:
- KnowledgeIngestionService: UNIFIED ingestion API (use this for all ingestion)
- PersonalLibraryVectorStore: ChromaDB wrapper for embeddings
- PersonalLibraryTools: Agent-callable search toolkit
- KnowledgeConfig: Configuration management
- KnowledgeCache: Chunk and embedding caching
- EmbedderFactory: Pluggable embedding providers

IMPORTANT: For ingestion, use KnowledgeIngestionService instead of
DocumentIngester or ClinicalDocumentIngestion directly.
"""

# Legacy exports (for backwards compatibility)
from src.knowledge.document_ingester import DocumentIngester, ChunkRecord
from src.knowledge.vector_store import (
    PersonalLibraryVectorStore,
    SearchResult,
    get_personal_library_store,
    VectorStoreFactory,
    COLLECTION_PERSONAL,
)
from src.knowledge.personal_library_tool import (
    PersonalLibraryTools,
    create_personal_library_tools,
    create_personal_library_tools_safe,
)

# New unified ingestion API (R1 requirement - use this instead of direct ingestion)
from src.knowledge.ingestion_service import (
    KnowledgeIngestionService,
    get_ingestion_service,
    ingest_file,
    ingest_text,
    ingest_folder,
    IngestionResult,
)

# Configuration (R2 requirement)
from src.knowledge.config import (
    KnowledgeConfig,
    get_config,
    load_config,
)

# Caching (R5 requirement)
from src.knowledge.cache import (
    KnowledgeCache,
    get_cache,
)

# Embedders (R3 requirement)
from src.knowledge.embedders import (
    EmbedderFactory,
    EmbedderSpec,
    get_embedder,
)

# Metadata (R6 requirement)
from src.knowledge.metadata import (
    ChunkMetadata,
    generate_doc_key,
    generate_chunk_id,
    generate_ingestion_run_id,
)

__all__ = [
    # Unified Ingestion API (preferred)
    "KnowledgeIngestionService",
    "get_ingestion_service",
    "ingest_file",
    "ingest_text",
    "ingest_folder",
    "IngestionResult",
    # Configuration
    "KnowledgeConfig",
    "get_config",
    "load_config",
    # Vector Stores
    "PersonalLibraryVectorStore",
    "VectorStoreFactory",
    "SearchResult",
    "get_personal_library_store",
    "COLLECTION_PERSONAL",
    # Caching
    "KnowledgeCache",
    "get_cache",
    # Embedders
    "EmbedderFactory",
    "EmbedderSpec",
    "get_embedder",
    # Metadata
    "ChunkMetadata",
    "generate_doc_key",
    "generate_chunk_id",
    "generate_ingestion_run_id",
    # Legacy (for backwards compatibility)
    "DocumentIngester",
    "ChunkRecord",
    "PersonalLibraryTools",
    "create_personal_library_tools",
    "create_personal_library_tools_safe",
]
