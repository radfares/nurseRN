"""
Database Adapters Package

Provides standardized interface for searching multiple databases.

Available Adapters:
- PubMedAdapter: PubMed/MEDLINE database access

Created: 2025-12-07 (Multi-Database Adapter - Phase 1)
"""
from .base import (
    BaseAdapter,
    DatabaseConfig,
    SearchResult,
    PaginationType,
)
from .pubmed_adapter import PubMedAdapter

__all__ = [
    "BaseAdapter",
    "DatabaseConfig",
    "SearchResult",
    "PaginationType",
    "PubMedAdapter",
]
