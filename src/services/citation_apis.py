"""
External API Clients for Citation Validation

Provides:
- PubMed retraction checking via ESearch API
- CrossRef metadata validation (future)
- Scimago journal ranking (future)

Created: 2025-12-07 (Phase 5 - Citation Validation, Phase 3)
"""

import re
import time
import httpx
from typing import Dict, Optional, Any
from dataclasses import dataclass
import logging

from src.services.circuit_breaker import (
    PUBMED_BREAKER,
    call_with_breaker,
)

logger = logging.getLogger(__name__)


@dataclass
class RetractionStatus:
    """Result of retraction check"""
    is_retracted: bool
    retraction_type: Optional[str] = None  # "retraction", "correction", "concern"
    retraction_date: Optional[str] = None
    retraction_reason: Optional[str] = None
    source: str = "unknown"


class PubMedRetractionChecker:
    """
    Check PubMed for article retractions.
    
    Uses PubMed's ESearch API to check if a PMID has been flagged
    as retracted using the publication type filter.
    """
    
    ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    
    def __init__(self, email: str = "nursing-research@example.com"):
        """
        Initialize the retraction checker.
        
        Args:
            email: Email for PubMed API tracking (recommended by NCBI)
        """
        self.email = email
        self._last_request_time = 0
        self._min_delay = 0.34  # 3 requests per second max (NCBI guideline)
    
    def _rate_limit(self):
        """Enforce rate limiting to comply with NCBI guidelines."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._min_delay:
            time.sleep(self._min_delay - elapsed)
        self._last_request_time = time.time()
    
    def check_retraction(self, pmid: str) -> RetractionStatus:
        """
        Check if a PMID has been retracted.
        
        Searches PubMed for retraction notices linked to the given PMID.
        
        Args:
            pmid: PubMed ID to check
            
        Returns:
            RetractionStatus with retraction info
        """
        self._rate_limit()
        
        try:
            # Define the search function for circuit breaker
            def do_search():
                response = httpx.get(
                    self.ESEARCH_URL,
                    params={
                        "db": "pubmed",
                        "term": f"{pmid}[PMID] AND retracted publication[pt]",
                        "email": self.email,
                        "retmode": "json",
                        "retmax": 1
                    },
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
            
            # Call through circuit breaker for resilience
            result = call_with_breaker(
                PUBMED_BREAKER,
                do_search,
                "PubMed retraction check unavailable"
            )
            
            # Circuit breaker returned fallback string
            if isinstance(result, str):
                logger.warning(f"Circuit breaker fallback for PMID {pmid}: {result}")
                return RetractionStatus(
                    is_retracted=False,
                    retraction_reason="Unable to verify - API unavailable",
                    source="circuit_breaker_fallback"
                )
            
            # Parse JSON result
            count = int(result.get("esearchresult", {}).get("count", 0))
            
            if count > 0:
                logger.info(f"PMID {pmid} found in retraction database")
                return RetractionStatus(
                    is_retracted=True,
                    retraction_type="retraction",
                    retraction_reason="Found in PubMed retraction database",
                    source="pubmed"
                )
            
            return RetractionStatus(
                is_retracted=False,
                source="pubmed"
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error checking retraction for PMID {pmid}: {e}")
            return RetractionStatus(
                is_retracted=False,
                retraction_reason=f"HTTP error: {e.response.status_code}",
                source="error"
            )
        except Exception as e:
            logger.error(f"Error checking retraction for PMID {pmid}: {e}")
            return RetractionStatus(
                is_retracted=False,
                retraction_reason=f"Check failed: {str(e)}",
                source="error"
            )
    
    def check_batch(self, pmids: list[str]) -> Dict[str, RetractionStatus]:
        """
        Check multiple PMIDs for retractions.
        
        Args:
            pmids: List of PubMed IDs to check
            
        Returns:
            Dict mapping PMID to RetractionStatus
        """
        results = {}
        for pmid in pmids:
            results[pmid] = self.check_retraction(pmid)
        return results
