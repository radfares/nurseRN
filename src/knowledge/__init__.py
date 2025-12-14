"""
Personal Knowledge Library Module
Provides document ingestion, vector storage, and search capabilities for agents.

Created: 2025-12-13
Phase B1: Document Ingester
Phase B2: Vector Store
Phase B3: Personal Library Tools

Components:
- DocumentIngester: Extract and chunk text from documents
- PersonalLibraryVectorStore: ChromaDB wrapper for embeddings
- PersonalLibraryTools: Agent-callable search toolkit
"""

from src.knowledge.document_ingester import DocumentIngester, ChunkRecord
from src.knowledge.vector_store import (
    PersonalLibraryVectorStore,
    SearchResult,
    get_personal_library_store,
    COLLECTION_PERSONAL,
)
from src.knowledge.personal_library_tool import (
    PersonalLibraryTools,
    create_personal_library_tools,
    create_personal_library_tools_safe,
)

__all__ = [
    "DocumentIngester",
    "ChunkRecord",
    "PersonalLibraryVectorStore",
    "SearchResult",
    "get_personal_library_store",
    "COLLECTION_PERSONAL",
    "PersonalLibraryTools",
    "create_personal_library_tools",
    "create_personal_library_tools_safe",
]
