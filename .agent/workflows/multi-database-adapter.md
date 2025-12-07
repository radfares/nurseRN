---
description: Step-by-step guide for implementing the Multi-Database Adapter system
---

# Multi-Database Adapter Implementation Guide

## For AI Agents: Step-by-Step Execution Plan

This document provides a **traceable, step-by-step guide** for implementing the Multi-Database Adapter system. Each step includes validation checkpoints.

---

## Pre-Implementation Checklist

Before starting, verify these conditions:

```bash
# Check 1: Confirm src/adapters doesn't exist
ls -la src/adapters 2>&1 | grep -q "No such file" && echo "✅ Ready" || echo "⚠️ Already exists"

# Check 2: Confirm requests_cache is installed
python -c "import requests_cache; print('✅ requests_cache available')"

# Check 3: Confirm circuit_breaker exists
ls src/services/circuit_breaker.py && echo "✅ Circuit breaker exists"
```

---

## Phase 1: Foundation Layer (Simplified)

### Step 1.1: Create Directory Structure
// turbo

```bash
mkdir -p src/adapters
touch src/adapters/__init__.py
```

**Validation:** `ls src/adapters/__init__.py` should succeed.

---

### Step 1.2: Create Base Types (`src/adapters/base.py`)

> **NOTE:** No rate limiter or cache manager - use existing infrastructure.

```python
# src/adapters/base.py
"""
Base adapter interface for all database adapters.
Provides standardized SearchResult format.

IMPORTANT: This module does NOT implement:
- Rate limiting (handled by individual tools or requests_cache)
- Caching (handled by requests_cache in api_tools.py)
- Circuit breakers (handled by src/services/circuit_breaker.py)
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
        """Convert user query to database-specific format."""
        pass
    
    @abstractmethod
    def search_ids(self, query: str, max_results: int) -> List[str]:
        """Get list of record IDs matching query."""
        pass
    
    @abstractmethod
    def fetch_details(self, ids: List[str]) -> List[SearchResult]:
        """Fetch full details for list of IDs."""
        pass
    
    def search(self, user_query: str, max_results: int = 100) -> List[SearchResult]:
        """Main search method - orchestrates the workflow."""
        translated = self.translate_query(user_query)
        ids = self.search_ids(translated, max_results)
        
        if not ids:
            return []
        
        results = []
        batch_size = self.config.batch_size
        
        for i in range(0, len(ids), batch_size):
            batch = ids[i:i + batch_size]
            batch_results = self.fetch_details(batch)
            results.extend(batch_results)
        
        return results
```

**Validation:**
```bash
python -c "from src.adapters.base import SearchResult, BaseAdapter; print('✅ Base types importable')"
```

---

### Step 1.3: Create `__init__.py` Exports

```python
# src/adapters/__init__.py
"""Database Adapters Package"""
from .base import (
    BaseAdapter,
    DatabaseConfig,
    SearchResult,
    PaginationType,
)

__all__ = ["BaseAdapter", "DatabaseConfig", "SearchResult", "PaginationType"]
```

**Validation:**
```bash
python -c "from src.adapters import SearchResult; print('✅ Package exports work')"
```

---

## Phase 2: PubMed Adapter

### Step 2.1: Create PubMed Adapter (`src/adapters/pubmed_adapter.py`)

> **IMPORTANT:** Uses raw `PubmedTools`, NOT `create_pubmed_tools_safe()` to avoid double-wrapping.

```python
# src/adapters/pubmed_adapter.py
"""
PubMed adapter - wraps existing PubmedTools from agno.

DESIGN DECISIONS:
- Uses raw PubmedTools (not create_pubmed_tools_safe) to avoid double circuit breaker wrapping
- Rate limiting is handled by PubmedTools internally (0.34s delay)
- Caching is handled globally by requests_cache
"""
import os
import re
from typing import List, Optional

from src.adapters.base import (
    BaseAdapter,
    DatabaseConfig,
    SearchResult,
    PaginationType,
)
from agno.tools.pubmed import PubmedTools


class PubMedAdapter(BaseAdapter):
    """Adapter for PubMed/MEDLINE database."""
    
    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        email = email or os.getenv("PUBMED_EMAIL", "nursing.research@example.com")
        
        config = DatabaseConfig(
            name="PubMed",
            base_url="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/",
            rate_limit=10.0 if api_key else 3.0,
            batch_size=200,
            pagination_type=PaginationType.OFFSET,
            data_format="xml",
            thesaurus="mesh"
        )
        
        super().__init__(config)
        
        self._pubmed_tools = PubmedTools(
            email=email,
            max_results=None,
            results_expanded=True,
        )
        self.email = email
        self.api_key = api_key
    
    def translate_query(self, user_query: str) -> str:
        """Map keywords to MeSH terms (basic implementation)."""
        return user_query
    
    def search_ids(self, query: str, max_results: int) -> List[str]:
        """Get PMIDs matching the query."""
        return self._pubmed_tools.fetch_pubmed_ids(
            query=query,
            max_results=max_results,
            email=self.email
        )
    
    def fetch_details(self, pmids: List[str]) -> List[SearchResult]:
        """Fetch full details for list of PMIDs."""
        if not pmids:
            return []
            
        xml_root = self._pubmed_tools.fetch_details(pmids)
        articles = self._pubmed_tools.parse_details(xml_root)
        
        results = []
        for article in articles:
            pubmed_url = article.get("PubMed_URL", "")
            pmid = self._extract_pmid(pubmed_url)
            
            result = SearchResult(
                record_id=pmid,
                title=article.get("Title", ""),
                authors=[article.get("First_Author", "")],
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
        
        return results
    
    def _extract_pmid(self, pubmed_url: str) -> str:
        """Safely extract PMID from PubMed URL."""
        if not pubmed_url:
            return ""
        match = re.search(r'/(\d+)/?$', pubmed_url)
        return match.group(1) if match else ""
```

**Validation:**
```bash
python -c "from src.adapters.pubmed_adapter import PubMedAdapter; print('✅ PubMed adapter importable')"
```

---

### Step 2.2: Update `__init__.py` with PubMed

Update `src/adapters/__init__.py` to include `PubMedAdapter`.

---

## Phase 3: Test File

### Step 3.1: Create Unit Tests (`tests/unit/test_adapters.py`)
// turbo

```bash
pytest tests/unit/test_adapters.py -v
```

---

## Verification Checklist
// turbo

```bash
# 1. Import checks
python -c "from src.adapters import SearchResult, PubMedAdapter; print('✅ All imports work')"

# 2. Run unit tests
pytest tests/unit/test_adapters.py -v

# 3. Quick integration test (optional, hits real API)
python -c "
from src.adapters import PubMedAdapter
adapter = PubMedAdapter()
results = adapter.search('nursing pain management', max_results=2)
print(f'✅ Found {len(results)} results')
"
```

---

## Rollback Plan

If implementation fails:

```bash
rm -rf src/adapters
```

---

## Traceability Matrix

| Step | File | Validation Command |
|------|------|-------------------|
| 1.1 | `src/adapters/__init__.py` | `ls src/adapters/__init__.py` |
| 1.2 | `src/adapters/base.py` | `python -c "from src.adapters.base import SearchResult"` |
| 2.1 | `src/adapters/pubmed_adapter.py` | `python -c "from src.adapters import PubMedAdapter"` |
| 3.1 | `tests/unit/test_adapters.py` | `pytest tests/unit/test_adapters.py -v` |
