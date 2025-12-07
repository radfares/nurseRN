"""
PubMed adapter - wraps existing PubmedTools from agno.

DESIGN DECISIONS:
- Uses raw PubmedTools (not create_pubmed_tools_safe) to avoid double circuit breaker wrapping
- Rate limiting is handled by PubmedTools internally (0.34s delay)
- Caching is handled globally by requests_cache

Created: 2025-12-07 (Multi-Database Adapter - Phase 2)
"""
import os
import re
import logging
from typing import List, Optional

from src.adapters.base import (
    BaseAdapter,
    DatabaseConfig,
    SearchResult,
    PaginationType,
)

# Import raw PubmedTools, not the safe wrapper
from agno.tools.pubmed import PubmedTools

logger = logging.getLogger(__name__)


class PubMedAdapter(BaseAdapter):
    """
    Adapter for PubMed/MEDLINE database.
    
    Wraps the existing PubmedTools class to provide
    standardized SearchResult interface.
    """
    
    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize PubMed adapter.
        
        Args:
            email: Your email (NCBI requirement). Falls back to env var.
            api_key: Optional API key (increases rate limit to 10 req/s)
        """
        email = email or os.getenv("PUBMED_EMAIL", "nursing.research@example.com")
        
        config = DatabaseConfig(
            name="PubMed",
            base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
            rate_limit=10.0 if api_key else 3.0,
            batch_size=200,  # Max PMIDs per EFetch call
            pagination_type=PaginationType.OFFSET,
            data_format="xml",
            thesaurus="mesh"
        )
        
        super().__init__(config)
        
        # Use raw PubmedTools (rate limiting built-in)
        self._pubmed_tools = PubmedTools(
            email=email,
            max_results=None,  # We control this per-query
            results_expanded=True,
        )
        self.email = email
        self.api_key = api_key
        
        logger.info(f"✅ PubMedAdapter initialized (email: {email[:20]}...)")
    
    def translate_query(self, user_query: str) -> str:
        """
        Map keywords to MeSH terms (basic implementation).
        
        TODO: Implement proper MeSH lookup via NCBI API.
        """
        # For now, return query as-is
        # Future: Use ESearch with field=[MeSH Terms]
        return user_query
    
    def search_ids(self, query: str, max_results: int) -> List[str]:
        """
        Get PMIDs matching the query.
        
        Uses existing PubmedTools.fetch_pubmed_ids method.
        """
        try:
            pmids = self._pubmed_tools.fetch_pubmed_ids(
                query=query,
                max_results=max_results,
                email=self.email
            )
            logger.info(f"🔍 Found {len(pmids)} PMIDs for query: {query[:50]}...")
            return pmids
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
    
    def fetch_details(self, pmids: List[str]) -> List[SearchResult]:
        """
        Fetch full details for list of PMIDs.
        
        Converts PubmedTools output to standardized SearchResult format.
        """
        if not pmids:
            return []
        
        try:
            # Fetch XML from PubMed
            xml_root = self._pubmed_tools.fetch_details(pmids)
            
            # Parse XML into article dictionaries
            articles = self._pubmed_tools.parse_details(xml_root)
            
            # Convert to standardized SearchResult format
            results = []
            for article in articles:
                # Extract PMID from URL safely
                pubmed_url = article.get("PubMed_URL", "")
                pmid = self._extract_pmid(pubmed_url)
                
                result = SearchResult(
                    record_id=pmid,
                    title=article.get("Title", ""),
                    authors=[article.get("First_Author", "")],  # TODO: Get all authors
                    abstract=article.get("Summary", ""),
                    publication_date=article.get("Published", ""),
                    source="PubMed",
                    doi=article.get("DOI"),
                    full_text_url=article.get("Full_Text_URL"),
                    metadata={
                        "journal": article.get("Journal"),
                        "publication_type": article.get("Publication_Type"),
                        "keywords": article.get("Keywords"),
                        "mesh_terms": article.get("MeSH_Terms"),
                        "pubmed_url": pubmed_url,
                    },
                )
                results.append(result)
            
            logger.info(f"📄 Fetched details for {len(results)} articles")
            return results
            
        except Exception as e:
            logger.error(f"Error fetching PubMed details: {e}")
            return []
    
    def _extract_pmid(self, pubmed_url: str) -> str:
        """
        Safely extract PMID from PubMed URL.
        
        Handles both:
        - https://pubmed.ncbi.nlm.nih.gov/12345/
        - https://pubmed.ncbi.nlm.nih.gov/12345
        """
        if not pubmed_url:
            return ""
        
        # Use regex to extract numeric PMID
        match = re.search(r'/(\d+)/?$', pubmed_url)
        return match.group(1) if match else ""
