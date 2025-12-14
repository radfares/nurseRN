"""
Personal Library Tools for Agent Integration
Agent-callable toolkit for searching the personal document library.

Created: 2025-12-13
Phase: B3

Tracer IDs: TRACE-B3-001 through TRACE-B3-006
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from agno.tools import Toolkit

from src.knowledge.vector_store import (
    PersonalLibraryVectorStore,
    SearchResult,
    COLLECTION_PERSONAL,
)

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_DB_PATH = "data/chroma_db"
DEFAULT_MAX_RESULTS = 5
DEFAULT_MIN_SCORE = 0.1


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
        db_path: str = DEFAULT_DB_PATH,
        collection_name: str = COLLECTION_PERSONAL,
        max_results: int = DEFAULT_MAX_RESULTS,
        min_score: float = DEFAULT_MIN_SCORE,
        enable_search: bool = True,
        **kwargs,
    ):
        """
        Initialize Personal Library Tools.

        Args:
            db_path: Path to ChromaDB storage (default: data/chroma_db)
            collection_name: Name of the vector collection
            max_results: Default maximum results to return
            min_score: Minimum relevance score threshold (0-1)
            enable_search: Whether to enable the search tool
        """
        self.db_path = db_path
        self.collection_name = collection_name
        self.max_results = max_results
        self.min_score = min_score

        # Initialize vector store (lazy - only connects when needed)
        self._store: Optional[PersonalLibraryVectorStore] = None

        # Build tools list
        tools: List[Any] = []
        if enable_search:
            tools.append(self.search_personal_library)

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
            f"collection={collection_name}, max_results={max_results}"
        )

    def _trace(self, trace_id: str, **kwargs) -> None:
        """Log a trace point for debugging."""
        msg = f"[{trace_id}] " + " | ".join(f"{k}={v}" for k, v in kwargs.items())
        logger.debug(msg)

    def _get_instructions(self) -> str:
        """Get instructions for the agent about using this toolkit."""
        return """
PERSONAL LIBRARY TOOL:
- Use search_personal_library() when user mentions "my notes",
  "my documents", "files I uploaded", "my files", or similar phrases
- Also use when external sources (PubMed, etc.) lack relevant results
- Personal library may contain:
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
            n_results: Maximum number of results to return (default: 5).
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
        limit = min(max(1, limit), 20)  # Clamp between 1 and 20

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
    db_path: str = DEFAULT_DB_PATH,
    collection_name: str = COLLECTION_PERSONAL,
    max_results: int = DEFAULT_MAX_RESULTS,
) -> PersonalLibraryTools:
    """
    Factory function to create PersonalLibraryTools instance.

    Args:
        db_path: Path to ChromaDB storage
        collection_name: Name of the vector collection
        max_results: Default maximum results to return

    Returns:
        Configured PersonalLibraryTools instance
    """
    return PersonalLibraryTools(
        db_path=db_path,
        collection_name=collection_name,
        max_results=max_results,
    )


def create_personal_library_tools_safe(
    db_path: str = DEFAULT_DB_PATH,
    collection_name: str = COLLECTION_PERSONAL,
    max_results: int = DEFAULT_MAX_RESULTS,
) -> Optional[PersonalLibraryTools]:
    """
    Safe factory function that returns None on initialization failure.

    Use this when adding to agent tools list to gracefully handle
    cases where the library is not available.

    Args:
        db_path: Path to ChromaDB storage
        collection_name: Name of the vector collection
        max_results: Default maximum results to return

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
