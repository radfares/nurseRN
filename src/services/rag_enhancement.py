"""
RAG Enhancement Service - Phase 3
Provides high-level RAG retrieval interface for agents with:
- Collection routing based on agent context
- Cache-first retrieval with TTL
- Grounding metadata extraction (PMID, arXiv, DOI)
- Lightweight agent integration

Created: 2025-12-15
Phase: 3 - Agent RAG Integration
"""

import logging
import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path

from src.knowledge.vector_store import VectorStoreFactory, SearchResult
from src.services.cache_utils import RAGCache
from src.services.rag_config import RAG_AGENT_CONFIG, get_collections_for_agent

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """
    Unified representation of retrieved content with grounding metadata.
    
    Attributes:
        content: The text content retrieved
        source: Source identifier (e.g., "clinical_knowledge", "pubmed")
        score: Relevance score (0.0 to 1.0)
        metadata: Full metadata dictionary
        doc_id: Document identifier if available
        citation_id: Citation identifier (PMID, arXiv ID, DOI, filename)
        page_num: Page number if from PDF
        source_path: Original file path if from local document
    """
    content: str
    source: str
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_id: Optional[str] = None
    citation_id: Optional[str] = None
    page_num: Optional[int] = None
    source_path: Optional[str] = None


class RAGEnhancer:
    """
    Enhanced RAG retrieval service for agent integration.
    
    Features:
    - Agent-specific collection routing
    - Cache-first retrieval with configurable TTL
    - Grounding metadata extraction
    - Simple API for agent integration
    
    Usage:
        enhancer = RAGEnhancer(cache_ttl=300)
        results = enhancer.retrieve(
            query="fall prevention protocols",
            agent_hint="nursing_research",
            k=5
        )
        
        # Extract grounding references
        refs = enhancer.extract_grounding_metadata(results)
        pmids = refs['pmids']
        files = refs['filenames']
    """
    
    def __init__(self, cache_ttl: Optional[int] = None, db_path: str = "data/chroma_db", embedder: Optional[Any] = None):
        """
        Initialize RAG enhancer.

        Args:
            cache_ttl: Cache time-to-live in seconds (uses config if None)
            db_path: Path to ChromaDB storage
            embedder: Optional embedder override
        """
        # Load config for RAG settings (Phase 1 Fix)
        try:
            from src.knowledge.config import get_config
            config = get_config()
            self._default_k = config.rag.default_k
            self._max_k = config.rag.max_k
            self._score_threshold = config.rag.score_threshold
            if cache_ttl is None:
                cache_ttl = config.rag.cache_ttl_seconds
        except Exception as e:
            logger.warning(f"Failed to load RAG config, using defaults: {e}")
            self._default_k = 10
            self._max_k = 50
            self._score_threshold = 0.1
            if cache_ttl is None:
                cache_ttl = 300

        self.cache = RAGCache(maxsize=100, ttl_seconds=cache_ttl)
        self.db_path = db_path
        self._embedder = embedder
        logger.info(f"RAGEnhancer initialized (default_k={self._default_k}, max_k={self._max_k}, cache_ttl={cache_ttl}s, db_path={db_path})")
    
    def retrieve(
        self,
        query: str,
        agent_hint: str = "general",
        k: Optional[int] = None,
        ttl: Optional[int] = None,
        use_cache: bool = True
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant content from appropriate collections.

        Args:
            query: Search query string
            agent_hint: Agent context hint for collection routing
                       (e.g., "nursing_research", "medical_research", "document_synthesis")
            k: Number of results to return (uses config default if None)
            ttl: Optional TTL override for this query (seconds)
            use_cache: Whether to use cache (default True)

        Returns:
            List of RetrievalResult objects, sorted by relevance
        """
        # Apply default and enforce max_k (Phase 1 Fix)
        if k is None:
            k = self._default_k
        k = min(max(1, int(k)), self._max_k)
        # Check cache first
        if use_cache:
            cache_key = self._build_cache_key(query, agent_hint, k)
            cached = self.cache.get(cache_key)
            if cached is not None:
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return cached
        
        logger.info(f"Retrieving for query='{query[:50]}...', agent={agent_hint}, k={k}")
        
        # Get collections to search based on agent hint
        collections = get_collections_for_agent(agent_hint)
        logger.debug(f"Routing to collections: {collections}")
        
        # Search each collection
        all_results: List[RetrievalResult] = []
        for collection_name in collections:
            try:
                results = self._search_collection(collection_name, query, k)
                all_results.extend(results)
            except Exception as e:
                logger.warning(f"Failed to search collection '{collection_name}': {e}")
        
        # Deduplicate and sort by score
        unique_results = self._deduplicate(all_results)
        unique_results.sort(key=lambda r: r.score, reverse=True)
        
        # Limit to k results
        final_results = unique_results[:k]
        
        # Cache results
        if use_cache:
            cache_ttl = ttl if ttl is not None else self.cache._ttl_seconds
            if cache_ttl > 0:
                self.cache.set(cache_key, final_results)
        
        logger.info(f"Retrieved {len(final_results)} results (from {len(all_results)} total)")
        return final_results

    def get_grounded_context(
        self,
        query: str,
        *,
        agent_hint: str = "general",
        n_results: int = 3,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Retrieve context with the source bound into the text.

        This is designed for safe prompt injection into an agent:
        each excerpt begins with `[[SOURCE: ...]]` so the model cannot
        separate the text from its origin when citing.

        Returns:
            Dict with:
              - context: str (formatted blocks)
              - sources: List[str] (exact source labels used)
              - results: List[RetrievalResult] (raw retrieval objects)
        """
        limit = max(1, min(int(n_results), 10))
        results = self.retrieve(query=query, agent_hint=agent_hint, k=limit, use_cache=use_cache)

        blocks: List[str] = []
        sources: List[str] = []
        for r in results[:limit]:
            # Prefer real DB metadata; fall back to structured fields.
            raw_source_path = None
            if isinstance(r.metadata, dict):
                raw_source_path = r.metadata.get("source_path")

            source_path = raw_source_path or r.source_path or r.citation_id or "Unknown Source"
            page = r.page_num

            # Keep the label stable but not overly long.
            label = str(source_path)
            try:
                if "/" in label or "\\" in label:
                    label = str(Path(label).name) or label
            except Exception:
                pass

            if page is not None:
                label = f"{label}, p.{page}"

            sources.append(label)
            blocks.append(f"[[SOURCE: {label}]] {r.content}")

        return {
            "context": "\n\n".join(blocks).strip(),
            "sources": sources,
            "results": results,
        }
    
    def _search_collection(
        self,
        collection_name: str,
        query: str,
        limit: int
    ) -> List[RetrievalResult]:
        """Search a single collection and convert results."""
        # Map collection name to store type
        store_type_map = {
            "clinical_knowledge": "clinical",
            "procedural_knowledge": "procedural",
            "research_cache": "research",
            "personal_docs": "personal"
        }
        
        store_type = store_type_map.get(collection_name, "personal")
        
        try:
            store = VectorStoreFactory.get_store(store_type, db_path=self.db_path, embedder=self._embedder)
            search_results = store.search(query, limit=limit)
            
            # Convert to RetrievalResult objects
            return [
                self._convert_search_result(r, collection_name)
                for r in search_results
            ]
        except Exception as e:
            logger.error(f"Search failed for collection '{collection_name}': {e}")
            return []
    
    def _convert_search_result(
        self,
        result: SearchResult,
        collection_name: str
    ) -> RetrievalResult:
        """Convert SearchResult to RetrievalResult with grounding metadata."""
        # Extract citation ID from metadata
        citation_id = self._extract_citation_id(result.metadata)
        
        return RetrievalResult(
            content=result.text,
            source=collection_name,
            score=result.score,
            metadata=result.metadata,
            doc_id=result.doc_id,
            citation_id=citation_id,
            page_num=result.page_num,
            source_path=result.source_path
        )
    
    def _extract_citation_id(self, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Extract citation identifier from metadata.
        
        Priority order: PMID > DOI > ArXiv > Filename
        """
        # Check for PMID
        if "pmid" in metadata:
            return f"PMID:{metadata['pmid']}"
        
        # Check for DOI
        if "doi" in metadata:
            return f"DOI:{metadata['doi']}"
        
        # Check for ArXiv
        if "arxiv_id" in metadata:
            return f"arXiv:{metadata['arxiv_id']}"
        
        # Fall back to source_path filename
        if "source_path" in metadata:
            from pathlib import Path
            return Path(metadata["source_path"]).name
        
        return None
    
    def _deduplicate(self, results: List[RetrievalResult]) -> List[RetrievalResult]:
        """
        Deduplicate results based on content similarity.
        
        Uses first 100 chars of content as simple hash.
        """
        seen_hashes: Set[int] = set()
        unique: List[RetrievalResult] = []
        
        for result in results:
            content_hash = hash(result.content[:100])
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique.append(result)
        
        return unique
    
    def _build_cache_key(self, query: str, agent_hint: str, k: int) -> str:
        """Build cache key from query parameters."""
        return f"{query}|{agent_hint}|{k}"
    
    def extract_grounding_metadata(
        self,
        results: List[RetrievalResult]
    ) -> Dict[str, List[str]]:
        """
        Extract grounding metadata from retrieval results.
        
        Returns:
            Dictionary with:
                - 'pmids': List of PMIDs
                - 'dois': List of DOIs
                - 'arxiv_ids': List of ArXiv IDs
                - 'filenames': List of source filenames
                - 'all_citations': Combined list of all citation IDs
        """
        pmids: Set[str] = set()
        dois: Set[str] = set()
        arxiv_ids: Set[str] = set()
        filenames: Set[str] = set()
        
        for result in results:
            if not result.citation_id:
                continue
            
            cit_id = result.citation_id
            
            if cit_id.startswith("PMID:"):
                pmids.add(cit_id.replace("PMID:", ""))
            elif cit_id.startswith("DOI:"):
                dois.add(cit_id.replace("DOI:", ""))
            elif cit_id.startswith("arXiv:"):
                arxiv_ids.add(cit_id.replace("arXiv:", ""))
            else:
                # Assume it's a filename
                filenames.add(cit_id)
        
        # Combine all for convenience
        all_citations = list(pmids) + list(dois) + list(arxiv_ids) + list(filenames)
        
        return {
            'pmids': sorted(pmids),
            'dois': sorted(dois),
            'arxiv_ids': sorted(arxiv_ids),
            'filenames': sorted(filenames),
            'all_citations': all_citations
        }
    
    def clear_cache(self) -> None:
        """Clear the retrieval cache."""
        self.cache.clear()
        logger.info("RAG cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache hit/miss statistics."""
        return self.cache.get_stats()


# Convenience factory function
def get_rag_enhancer(cache_ttl: int = 300, db_path: str = "data/chroma_db") -> RAGEnhancer:
    """
    Factory function to create RAGEnhancer instance.
    
    Args:
        cache_ttl: Cache TTL in seconds
        db_path: Path to ChromaDB storage
    
    Returns:
        Configured RAGEnhancer instance
    """
    return RAGEnhancer(cache_ttl=cache_ttl, db_path=db_path)
