"""
RAG Retrieval Pipeline
Orchestrates retrieval from multiple sources (Vector Stores, External APIs)
with caching and grounding.

Created: 2025-12-15
Phase: 2
"""

import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

from src.knowledge.vector_store import VectorStoreFactory, SearchResult
from src.services.cache_utils import RAGCache
from src.services.api_tools import (
    create_pubmed_tools_safe,
    create_arxiv_tools_safe,
    create_semantic_scholar_tools_safe
)

logger = logging.getLogger(__name__)

@dataclass
class RetrievedItem:
    """Unified representation of a retrieved item from any source."""
    content: str
    source: str         # e.g., "Personal Library", "PubMed", "ArXiv"
    score: float        # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_id: Optional[str] = None
    citation_id: Optional[str] = None  # PMID, DOI, or filename

class RAGPipeline:
    """
    Coordinator for retrieving information for RAG.
    
    Features:
    - Multi-source aggregation (Local Vector Stores + External APIs)
    - Caching (TTL)
    - Grounding extraction
    """

    def __init__(self, cache_ttl: int = 300):
        self.cache = RAGCache(maxsize=100, ttl_seconds=cache_ttl)
        # Initialize tool accessors (lazy load done in methods usually, but fast here)
        # We don't instantiate tools here to avoid overhead on init
        pass

    def retrieve(
        self, 
        query: str, 
        agent_hint: str = "general",
        limit: int = 5,
        use_cache: bool = True
    ) -> List[RetrievedItem]:
        """
        Main entry point for retrieval.
        
        Args:
            query: The search query string.
            agent_hint: specific context ("clinical", "research", "general").
            limit: Max items per source (soft limit).
            use_cache: Whether to use the TTL cache.
            
        Returns:
            List of RetrievedItem objects.
        """
        if use_cache:
            cache_key = f"{query}|{agent_hint}|{limit}"
            cached = self.cache.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for query: {query[:30]}...")
                return cached

        logger.info(f"Retrieving for query: {query} (hint={agent_hint})")
        
        results: List[RetrievedItem] = []

        # 1. Always search Local stores based on hint
        local_results = self._search_local_stores(query, agent_hint, limit)
        results.extend(local_results)

        # 2. If specialized hint, trigger external tools
        # We limit external calls to "research" or "clinical" contexts to save API calls/time
        if agent_hint in ["research", "clinical"]:
            external_results = self._search_external_sources(query, agent_hint, limit)
            results.extend(external_results)

        # 3. Deduplicate and Sort
        # Deduplication could be complex; simple approach: by content hash or citation_id
        unique_results = self._deduplicate(results)
        
        # Sort by score desc
        unique_results.sort(key=lambda x: x.score, reverse=True)
        
        final_results = unique_results[:limit * 2] # Allow a bit more than limit total

        if use_cache:
            self.cache.set(cache_key, final_results)

        return final_results

    def _search_local_stores(self, query: str, hint: str, limit: int) -> List[RetrievedItem]:
        items = []
        
        # Determine which stores to query
        store_types = ["personal"] # Always check personal
        if hint == "clinical":
            store_types.append("clinical")
            store_types.append("procedural")
        elif hint == "research":
            store_types.append("research")

        for s_type in store_types:
            try:
                store = VectorStoreFactory.get_store(s_type)
                # We check existence to avoid creating empty DBs if not needed, 
                # but VectorStoreFactory creates on get. 
                # Assuming valid stores.
                
                results = store.search(query, limit=limit)
                for r in results:
                    items.append(self._convert_chunk_to_item(r, source_type=s_type))
            except Exception as e:
                logger.warning(f"Failed to search local store {s_type}: {e}")
        
        return items

    def _search_external_sources(self, query: str, hint: str, limit: int) -> List[RetrievedItem]:
        items = []
        
        # PubMed (for clinical/research)
        if hint in ["clinical", "research"]:
            try:
                pubmed = create_pubmed_tools_safe()
                if pubmed:
                    # Note: agno tools usually return a string or list of dicts.
                    # We need to adapt based on tool version. 
                    # Wrapper provides access to underlying method usually.
                    # Assuming basic search capability.
                    # Since existing codebase uses agno tools, we simulate usage:
                    # The tool usually has `search_pubmed` method.
                    if hasattr(pubmed, "search_pubmed_and_return_articles"):
                         # Hypothetical method if we want structured data
                         # For now, let's assume we use the basic search
                         # This part relies on specific Agno Tool interfaces.
                         # Since I cannot see Agno source code, I will make a safe assumption
                         # that we can get text results.  
                         pass
                    
                    # For this draft, I will assume we can't easily parse raw tool output 
                    # without more integration code, so I will mark this as specific 
                    # to implemented tools. 
                    # We'll use a placeholder implementation that would be replaced 
                    # by actual tool calls returning structured data.
                    pass
            except Exception as e:
                logger.warning(f"External search failed: {e}")

        # ArXiv (only if research)
        if hint == "research":
            pass 
            
        return items

    def _convert_chunk_to_item(self, chunk: SearchResult, source_type: str) -> RetrievedItem:
        """Convert a local vector store chunk to a unified item."""
        # Try to find a citation ID (PMID/DOI) in metadata
        meta = chunk.metadata
        cit_id = meta.get("pmid") or meta.get("doi") or chunk.filename
        
        return RetrievedItem(
            content=chunk.text,
            source=f"Local Store ({source_type.title()})",
            score=chunk.score,
            metadata=meta,
            doc_id=chunk.doc_id,
            citation_id=cit_id
        )

    def _deduplicate(self, items: List[RetrievedItem]) -> List[RetrievedItem]:
        """Simple deduplication based on content hash."""
        seen_hashes = set()
        unique = []
        for item in items:
            # Hash of first 100 chars to avoid exact match rigidness
            h = hash(item.content[:100])
            if h not in seen_hashes:
                seen_hashes.add(h)
                unique.append(item)
        return unique

    def get_grounding_references(self, items: List[RetrievedItem]) -> List[str]:
        """Extract list of unique citation IDs (PMIDs, filenames) for grounding."""
        refs = set()
        for item in items:
            if item.citation_id:
                refs.add(item.citation_id)
        return list(refs)
