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
    
    def search(self, user_query: str, max_results: int = 100) -> List[SearchResult]:
        """
        Main search method - orchestrates the workflow.
        
        1. Translate query to database format
        2. Get matching IDs
        3. Fetch details in batches
        
        Returns: List of SearchResult objects
        """
        # Step 1: Translate query
        translated = self.translate_query(user_query)
        
        # Step 2: Get IDs
        ids = self.search_ids(translated, max_results)
        
        if not ids:
            return []
        
        # Step 3: Fetch details in batches
        results = []
        batch_size = self.config.batch_size
        
        for i in range(0, len(ids), batch_size):
            batch = ids[i:i + batch_size]
            batch_results = self.fetch_details(batch)
            results.extend(batch_results)
        
        return results
