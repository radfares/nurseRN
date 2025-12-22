"""
Personal Library Tools for Agent Integration
Agent-callable toolkit for searching the personal document library.

Created: 2025-12-13
Phase: B3

Tracer IDs: TRACE-B3-001 through TRACE-B3-006
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

from agno.tools import Toolkit

from src.knowledge.vector_store import (
    PersonalLibraryVectorStore,
    SearchResult,
    COLLECTION_PERSONAL,
)

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_DB_PATH = "data/chroma_db"
DEFAULT_MAX_RESULTS = 20
DEFAULT_MIN_SCORE = 0.1


def _load_default_settings() -> Tuple[str, int, float]:
    """Load default settings from knowledge config with safe fallbacks."""
    try:
        from src.knowledge.config import get_config

        cfg = get_config()
        return (
            cfg.db_path,
            int(cfg.personal_library.max_results),
            float(cfg.personal_library.min_score),
        )
    except Exception:
        return DEFAULT_DB_PATH, DEFAULT_MAX_RESULTS, DEFAULT_MIN_SCORE


class PersonalLibraryTools(Toolkit):
    """
    Toolkit for searching personal document library.

    Provides agent-callable tools for semantic search over user's
    personal documents (PDFs, notes, articles, presentations).

    Use Cases:
    - Search for information in personal notes and documents
    - Find relevant content from uploaded research papers
    - Retrieve saved guidelines and protocols
    - Access class notes and project documents

    Example Agent Usage:
        When user says "check my notes about fall prevention",
        the agent calls search_personal_library("fall prevention")
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        collection_name: str = COLLECTION_PERSONAL,
        max_results: Optional[int] = None,
        min_score: Optional[float] = None,
        enable_search: bool = True,
        **kwargs,
    ):
        """
        Initialize Personal Library Tools.

        Args:
            db_path: Path to ChromaDB storage (default from knowledge config)
            collection_name: Name of the vector collection
            max_results: Default maximum results to return (configurable)
            min_score: Minimum relevance score threshold (0-1, configurable)
            enable_search: Whether to enable the search tool
        """
        if db_path is None or max_results is None or min_score is None:
            cfg_db_path, cfg_max_results, cfg_min_score = _load_default_settings()
            if db_path is None:
                db_path = cfg_db_path
            if max_results is None:
                max_results = cfg_max_results
            if min_score is None:
                min_score = cfg_min_score

        self.db_path = db_path
        self.collection_name = collection_name
        self.max_results = max(1, int(max_results))
        self.min_score = float(min_score)

        # Initialize vector store (lazy - only connects when needed)
        self._store: Optional[PersonalLibraryVectorStore] = None

        # Build tools list
        tools: List[Any] = []
        if enable_search:
            tools.append(self.search_personal_library)
            tools.append(self.list_library_documents)  # Phase 3: Inventory tool

        # Initialize parent Toolkit
        super().__init__(
            name="personal_library",
            tools=tools,
            instructions=self._get_instructions(),
            add_instructions=True,
            **kwargs,
        )

        logger.info(
            f"PersonalLibraryTools initialized: db_path={db_path}, "
            f"collection={collection_name}, max_results={self.max_results}"
        )

    def _trace(self, trace_id: str, **kwargs) -> None:
        """Log a trace point for debugging."""
        msg = f"[{trace_id}] " + " | ".join(f"{k}={v}" for k, v in kwargs.items())
        logger.debug(msg)

    def _get_instructions(self) -> str:
        """Get instructions for the agent about using this toolkit."""
        return """
PERSONAL LIBRARY TOOLS:

DOCUMENT INVENTORY (list_library_documents):
- Use when user asks "what documents do I have", "show my files",
  "list my uploads", "what's in my library", "how many files"
- Returns complete list of all uploaded documents with metadata
- Does NOT perform semantic search

SEMANTIC SEARCH (search_personal_library):
- Use when user asks "find information about X", "search for Y topic",
  "what do I have on Z", "check my notes about..."
- Performs relevance-ranked search for specific content
- Returns text excerpts with source attribution

Personal library may contain:
  * Unpublished work and drafts
  * Class notes and lecture materials
  * Project documents and reports
  * Saved articles and PDFs
  * Guidelines and protocols

- Always cite source path and page number from results
- Tool priority: PubMed/External sources first, then personal library as supplement
"""

    @property
    def store(self) -> PersonalLibraryVectorStore:
        """Get or initialize the vector store."""
        if self._store is None:
            self._store = PersonalLibraryVectorStore(
                collection_name=self.collection_name,
                db_path=self.db_path,
            )
        return self._store

    def _format_result(self, result: SearchResult, index: int) -> str:
        """Format a single search result for display."""
        # Build source reference
        source_ref = result.filename
        if result.page_num is not None:
            source_ref += f", p.{result.page_num}"

        # Truncate text if too long
        text = result.text
        if len(text) > 500:
            text = text[:497] + "..."

        return f"{index}. [{source_ref}] (Score: {result.score:.2f})\n   \"{text}\""

    def _format_results(self, results: List[SearchResult], query: str) -> str:
        """Format search results for agent consumption."""
        if not results:
            return f"No relevant documents found in your personal library for: \"{query}\"\n\nTip: You may need to add documents using the ingestion CLI."

        # Filter by minimum score
        filtered = [r for r in results if r.score >= self.min_score]

        if not filtered:
            return f"No sufficiently relevant documents found for: \"{query}\" (all results below relevance threshold)"

        # Build output
        lines = [f"Found {len(filtered)} relevant sections from your personal library:\n"]

        for i, result in enumerate(filtered, 1):
            lines.append(self._format_result(result, i))
            lines.append("")  # Blank line between results

        return "\n".join(lines)

    def search_personal_library(
        self,
        query: str,
        n_results: Optional[int] = None,
    ) -> str:
        """
        Search your personal document library for relevant information.

        Use this tool to find content from your uploaded documents, notes,
        PDFs, presentations, and other personal files.

        Args:
            query: The search query describing what you're looking for.
                   Be specific for better results.
                   Example: "fall prevention protocols" or "medication safety guidelines"
            n_results: Maximum number of results to return (default: configured max_results).
                      Use fewer for focused answers, more for comprehensive research.

        Returns:
            Formatted search results with source attribution, page numbers,
            and relevance scores. Each result includes a text excerpt.

        Example:
            search_personal_library("hourly rounding protocols", n_results=3)

        Tips:
            - Use specific clinical terms for medical content
            - Include topic keywords relevant to your documents
            - Results are ranked by semantic similarity
        """
        # Validate query
        if not query or not isinstance(query, str):
            return json.dumps({
                "error": "invalid_query",
                "message": "Query must be a non-empty string"
            })

        query = query.strip()
        if not query:
            return json.dumps({
                "error": "empty_query",
                "message": "Query cannot be empty"
            })

        # Set result limit
        limit = n_results if n_results is not None else self.max_results
        limit = min(max(1, int(limit)), self.max_results)

        self._trace("TRACE-B3-001", query=query[:50], n_results=limit)

        try:
            # Check if store has any documents
            stats = self.store.get_stats()
            if stats.get("chunk_count", 0) == 0:
                self._trace("TRACE-B3-004", query=query[:50])
                return "Your personal library is empty. Use the ingestion CLI to add documents:\n  python scripts/ingest_documents.py add /path/to/document.pdf"

            # Perform search
            import time
            start_time = time.time()

            results = self.store.search(query=query, limit=limit)

            duration_ms = int((time.time() - start_time) * 1000)
            self._trace("TRACE-B3-002", duration_ms=duration_ms)

            # Format results
            formatted = self._format_results(results, query)
            self._trace("TRACE-B3-003", count=len(results))

            return formatted

        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self._trace("TRACE-B3-006", error_type=type(e).__name__, error_message=str(e))

            return json.dumps({
                "error": "search_failed",
                "message": error_msg
            })

    def list_library_documents(self) -> str:
        """
        List all documents in your personal library.

        Use this tool to see what files you have uploaded to your personal library.
        This provides an inventory of all documents without performing semantic search.

        Returns:
            Formatted list of all documents with filenames, chunk counts,
            and ingestion timestamps.

        Example:
            list_library_documents()

        Use Cases:
            - "What documents do I have in my library?"
            - "Show me all my uploaded files"
            - "List all documents I've added"
            - "How many files are in my library?"
        """
        try:
            # Get all documents using full collection scan (Phase 3 Fix)
            docs = self.store.list_documents()

            if not docs:
                return "Your personal library is empty. Use the ingestion CLI to add documents:\n  python scripts/ingest_documents.py add /path/to/document.pdf"

            # Sort by ingestion date (newest first)
            docs.sort(key=lambda d: d.get("ingested_at", ""), reverse=True)

            # Build formatted output
            lines = [f"Found {len(docs)} documents in your personal library:\n"]

            for i, doc in enumerate(docs, 1):
                filename = doc.get("filename", "Unknown")
                chunks = doc.get("chunk_count", 0)
                ingested = doc.get("ingested_at", "Unknown")
                is_active = doc.get("is_active", True)

                status = "" if is_active else " [INACTIVE]"
                lines.append(f"{i}. {filename} ({chunks} chunks){status}")
                lines.append(f"   Ingested: {ingested}")
                lines.append("")  # Blank line

            return "\n".join(lines)

        except Exception as e:
            error_msg = f"Failed to list documents: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return json.dumps({
                "error": "list_failed",
                "message": error_msg
            })

    def get_library_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the personal library.

        Returns:
            Dictionary with library statistics including document count,
            chunk count, and storage information.
        """
        try:
            stats = self.store.get_stats()
            docs = self.store.list_documents()

            return {
                "collection_name": stats.get("collection_name", "unknown"),
                "total_chunks": stats.get("chunk_count", 0),
                "total_documents": len(docs),
                "documents": [
                    {
                        "filename": d.get("filename", "unknown"),
                        "chunks": d.get("chunk_count", 0),
                        "ingested_at": d.get("ingested_at", "unknown")
                    }
                    for d in docs
                ]
            }
        except Exception as e:
            logger.error(f"Error getting library stats: {e}")
            return {"error": str(e)}


def create_personal_library_tools(
    db_path: Optional[str] = None,
    collection_name: str = COLLECTION_PERSONAL,
    max_results: Optional[int] = None,
) -> PersonalLibraryTools:
    """
    Factory function to create PersonalLibraryTools instance.

    Args:
        db_path: Path to ChromaDB storage
        collection_name: Name of the vector collection
        max_results: Default maximum results to return (configurable)

    Returns:
        Configured PersonalLibraryTools instance
    """
    return PersonalLibraryTools(
        db_path=db_path,
        collection_name=collection_name,
        max_results=max_results,
    )


def create_personal_library_tools_safe(
    db_path: Optional[str] = None,
    collection_name: str = COLLECTION_PERSONAL,
    max_results: Optional[int] = None,
) -> Optional[PersonalLibraryTools]:
    """
    Safe factory function that returns None on initialization failure.

    Use this when adding to agent tools list to gracefully handle
    cases where the library is not available.

    Args:
        db_path: Path to ChromaDB storage
        collection_name: Name of the vector collection
        max_results: Default maximum results to return (configurable)

    Returns:
        PersonalLibraryTools instance or None if initialization fails
    """
    try:
        return PersonalLibraryTools(
            db_path=db_path,
            collection_name=collection_name,
            max_results=max_results,
        )
    except Exception as e:
        logger.warning(f"Failed to initialize PersonalLibraryTools: {e}")
        return None
