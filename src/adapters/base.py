"""
Base adapter interface for all database adapters.
Provides standardized SearchResult format.

IMPORTANT: This module does NOT implement:
- Rate limiting (handled by individual tools or requests_cache)
- Caching (handled by requests_cache in api_tools.py)
- Circuit breakers (handled by src/services/circuit_breaker.py)

Created: 2025-12-07 (Multi-Database Adapter - Phase 1)
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class PaginationType(Enum):
    """How the database handles pagination"""
    OFFSET = "offset"      # RetStart/RetMax (PubMed)
    CURSOR = "cursor"      # Cursor-based (OpenAlex)
    PAGE = "page"          # Page numbers


@dataclass
class DatabaseConfig:
    """Configuration metadata for a database adapter"""
    name: str
    base_url: str
    rate_limit: float           # requests per second (informational)
    batch_size: int             # records per fetch
    pagination_type: PaginationType
    data_format: str            # "xml" or "json"
    thesaurus: Optional[str] = None  # "mesh", "emtree", "concepts"


@dataclass
class SearchResult:
    """
    Standardized result format - all adapters return this.

    This ensures consistent data structure regardless of source database.
    """
    record_id: str              # PMID, DOI, OpenAlex ID
    title: str
    authors: List[str]
    abstract: str
    publication_date: str
    source: str                 # Database name (e.g., "PubMed", "OpenAlex")
    metadata: Dict = field(default_factory=dict)  # Database-specific extras
    full_text_url: Optional[str] = None
    doi: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "record_id": self.record_id,
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "publication_date": self.publication_date,
            "source": self.source,
            "metadata": self.metadata,
            "full_text_url": self.full_text_url,
            "doi": self.doi,
        }


@dataclass
class SearchResultSet:
    """
    Container for search results with shortfall metadata (Phase 2).

    Provides transparency when fewer results are found than requested.
    """
    results: List[SearchResult]
    requested: int              # Number of results requested
    found: int                  # Number of results actually found
    truncated: bool = False     # Whether results were truncated by API
    source: str = "unknown"     # Database name

    @property
    def has_shortfall(self) -> bool:
        """Check if fewer results were found than requested."""
        return 0 < self.found < self.requested

    @property
    def is_empty(self) -> bool:
        """Check if no results were found."""
        return self.found == 0

    @property
    def shortfall_ratio(self) -> float:
        """Ratio of found/requested (0.0 to 1.0)."""
        if self.requested == 0:
            return 1.0
        return min(self.found / self.requested, 1.0)

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            "results": [r.to_dict() for r in self.results],
            "requested": self.requested,
            "found": self.found,
            "truncated": self.truncated,
            "source": self.source,
            "has_shortfall": self.has_shortfall,
            "is_empty": self.is_empty,
            "shortfall_ratio": self.shortfall_ratio,
        }


class BaseAdapter(ABC):
    """
    Abstract base class for database adapters.
    
    Subclasses must implement:
    - translate_query(): Convert user query to database format
    - search_ids(): Get record IDs matching query
    - fetch_details(): Get full records for IDs
    
    The search() method orchestrates the workflow.
    """
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
    
    @abstractmethod
    def translate_query(self, user_query: str) -> str:
        """
        Convert user query to database-specific format.
        
        Example: "heart attack" → "Myocardial Infarction[MeSH]"
        """
        pass
    
    @abstractmethod
    def search_ids(self, query: str, max_results: int) -> List[str]:
        """
        Get list of record IDs matching query.
        
        Returns: List of IDs (PMIDs, DOIs, etc.)
        """
        pass
    
    @abstractmethod
    def fetch_details(self, ids: List[str]) -> List[SearchResult]:
        """
        Fetch full details for list of IDs.
        
        Returns: List of SearchResult objects
        """
        pass
    
    def search(self, user_query: str, max_results: int = 100) -> SearchResultSet:
        """
        Main search method - orchestrates the workflow.

        1. Translate query to database format
        2. Get matching IDs
        3. Fetch details in batches

        Returns: SearchResultSet with results and metadata (Phase 2)
        """
        # Step 1: Translate query
        translated = self.translate_query(user_query)

        # Step 2: Get IDs
        ids = self.search_ids(translated, max_results)

        # Phase 2: Track requested vs found
        found_count = len(ids)

        if not ids:
            return SearchResultSet(
                results=[],
                requested=max_results,
                found=0,
                truncated=False,
                source=self.config.name
            )

        # Step 3: Fetch details in batches
        results = []
        batch_size = self.config.batch_size

        for i in range(0, len(ids), batch_size):
            batch = ids[i:i + batch_size]
            batch_results = self.fetch_details(batch)
            results.extend(batch_results)

        # Phase 2: Return results with shortfall metadata
        return SearchResultSet(
            results=results,
            requested=max_results,
            found=found_count,
            truncated=(found_count >= max_results),  # May have more results available
            source=self.config.name
        )
