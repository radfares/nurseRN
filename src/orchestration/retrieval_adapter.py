"""
Retrieval Adapter
Formats retrieved RAG items for LLM consumption.

Created: 2025-12-15
Phase: 2
"""

import logging
from typing import List, Optional

from src.services.rag_pipeline import RetrievedItem

logger = logging.getLogger(__name__)

class RetrievalAdapter:
    """
    Adapter to convert Retrieval Results into prompt-friendly context.
    """

    @staticmethod
    def format_for_llm(
        items: List[RetrievedItem],
        include_scores: bool = False,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Format items into a single context string.
        
        Args:
            items: List of RetrievedItem objects.
            include_scores: Whether to include relevance score in text.
            max_tokens: Approximate token limit (character count heuristic for now).
            
        Returns:
            Formatted string:
            
            [Source: PubMed | ID: 12345]
            The content of the article...
            
            [Source: Local Store | ID: file.pdf]
            The content of the chunk...
        """
        if not items:
            return "No relevant context found."

        sections = []
        current_chars = 0
        MAX_CHARS = (max_tokens * 4) if max_tokens else 100000

        for item in items:
            header_parts = [f"Source: {item.source}"]
            if item.citation_id:
                header_parts.append(f"ID: {item.citation_id}")
            if include_scores:
                header_parts.append(f"Score: {item.score:.2f}")
            
            header = f"[{' | '.join(header_parts)}]"
            entry = f"{header}\n{item.content}\n"
            
            if current_chars + len(entry) > MAX_CHARS:
                logger.info(f"Context truncated at {current_chars} chars")
                break
                
            sections.append(entry)
            current_chars += len(entry)

        return "\n".join(sections)

    @staticmethod
    def extract_citations(items: List[RetrievedItem]) -> List[str]:
        """
        Get a list of citation strings for the 'References' section.
        """
        citations = []
        seen = set()
        
        for item in items:
            cit_id = item.citation_id
            if cit_id and cit_id not in seen:
                # Basic formatting, could be enhanced with full metadata
                title = item.metadata.get("title", "Untitled")
                cit_str = f"{cit_id}: {title}"
                citations.append(cit_str)
                seen.add(cit_id)
        
        return citations
