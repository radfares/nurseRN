"""
Tests for database adapter pattern.

NOTE: These are unit tests with mocking.
Integration tests with real API calls are in tests/integration/.

Created: 2025-12-07 (Multi-Database Adapter - Phase 3)
"""
import pytest
from typing import List
from unittest.mock import Mock, patch, MagicMock

from src.adapters.base import (
    BaseAdapter,
    DatabaseConfig,
    SearchResult,
    PaginationType,
)


class MockAdapter(BaseAdapter):
    """Concrete implementation for testing"""
    
    def translate_query(self, user_query: str) -> str:
        return user_query.upper()
    
    def search_ids(self, query: str, max_results: int) -> List[str]:
        return [f"ID_{i}" for i in range(min(max_results, 5))]
    
    def fetch_details(self, ids: List[str]) -> List[SearchResult]:
        return [
            SearchResult(
                record_id=id,
                title=f"Paper {id}",
                authors=["Test Author"],
                abstract="Test abstract",
                publication_date="2025-01-01",
                source="MockDB",
                metadata={}
            )
            for id in ids
        ]


class TestSearchResult:
    """Test SearchResult dataclass"""
    
    def test_creation(self):
        """Verify SearchResult can be created"""
        result = SearchResult(
            record_id="12345",
            title="Test Paper",
            authors=["Author One", "Author Two"],
            abstract="This is an abstract",
            publication_date="2025-01-01",
            source="PubMed",
            metadata={"doi": "10.1234/test"}
        )
        
        assert result.record_id == "12345"
        assert result.source == "PubMed"
        assert len(result.authors) == 2
    
    def test_to_dict(self):
        """Verify to_dict serialization"""
        result = SearchResult(
            record_id="12345",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            publication_date="2025",
            source="Test",
            metadata={}
        )
        
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["record_id"] == "12345"
    
    def test_optional_fields(self):
        """Test optional fields default to None"""
        result = SearchResult(
            record_id="12345",
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            publication_date="2025",
            source="Test",
            metadata={}
        )
        
        assert result.full_text_url is None
        assert result.doi is None


class TestDatabaseConfig:
    """Test DatabaseConfig dataclass"""
    
    def test_creation(self):
        """Verify DatabaseConfig can be created"""
        config = DatabaseConfig(
            name="PubMed",
            base_url="https://example.com",
            rate_limit=3.0,
            batch_size=200,
            pagination_type=PaginationType.OFFSET,
            data_format="xml",
            thesaurus="mesh"
        )
        
        assert config.name == "PubMed"
        assert config.batch_size == 200
        assert config.pagination_type == PaginationType.OFFSET
    
    def test_optional_thesaurus(self):
        """Test thesaurus defaults to None"""
        config = DatabaseConfig(
            name="Test",
            base_url="",
            rate_limit=1.0,
            batch_size=10,
            pagination_type=PaginationType.PAGE,
            data_format="json"
        )
        
        assert config.thesaurus is None


class TestBaseAdapter:
    """Test base adapter functionality"""
    
    def test_search_workflow(self):
        """Verify search orchestrates correctly"""
        config = DatabaseConfig(
            name="MockDB",
            base_url="",
            rate_limit=10.0,
            batch_size=3,
            pagination_type=PaginationType.OFFSET,
            data_format="json",
            thesaurus=None
        )
        adapter = MockAdapter(config)
        
        results = adapter.search("test query", max_results=5)
        
        assert len(results) == 5
        assert all(isinstance(r, SearchResult) for r in results)
        assert results[0].source == "MockDB"
    
    def test_query_translation(self):
        """Verify query translation is called"""
        config = DatabaseConfig(
            name="MockDB",
            base_url="",
            rate_limit=10.0,
            batch_size=10,
            pagination_type=PaginationType.OFFSET,
            data_format="json",
            thesaurus=None
        )
        adapter = MockAdapter(config)
        
        # MockAdapter.translate_query uppercases
        translated = adapter.translate_query("heart attack")
        assert translated == "HEART ATTACK"
    
    def test_empty_results(self):
        """Verify empty results handled"""
        config = DatabaseConfig(
            name="MockDB",
            base_url="",
            rate_limit=10.0,
            batch_size=10,
            pagination_type=PaginationType.OFFSET,
            data_format="json",
            thesaurus=None
        )
        
        class EmptyAdapter(BaseAdapter):
            def translate_query(self, q): 
                return q
            def search_ids(self, q, m): 
                return []
            def fetch_details(self, ids): 
                return []
        
        adapter = EmptyAdapter(config)
        results = adapter.search("nothing", max_results=10)
        
        assert results == []
    
    def test_batched_fetch(self):
        """Verify batches are processed correctly"""
        config = DatabaseConfig(
            name="MockDB",
            base_url="",
            rate_limit=10.0,
            batch_size=2,  # Small batch size
            pagination_type=PaginationType.OFFSET,
            data_format="json",
            thesaurus=None
        )
        adapter = MockAdapter(config)
        
        # Should process 5 IDs in 3 batches (2+2+1)
        results = adapter.search("test query", max_results=5)
        
        assert len(results) == 5


class TestPubMedAdapter:
    """Test PubMed adapter (with mocking)"""
    
    @patch('src.adapters.pubmed_adapter.PubmedTools')
    def test_initialization(self, mock_pubmed):
        """Verify PubMedAdapter initializes correctly"""
        from src.adapters.pubmed_adapter import PubMedAdapter
        
        adapter = PubMedAdapter(email="test@example.com")
        
        assert adapter.config.name == "PubMed"
        assert adapter.config.batch_size == 200
        assert adapter.email == "test@example.com"
    
    def test_pmid_extraction(self):
        """Test PMID extraction from URLs"""
        from src.adapters.pubmed_adapter import PubMedAdapter
        
        with patch('src.adapters.pubmed_adapter.PubmedTools'):
            adapter = PubMedAdapter()
        
        # With trailing slash
        assert adapter._extract_pmid("https://pubmed.ncbi.nlm.nih.gov/12345/") == "12345"
        
        # Without trailing slash
        assert adapter._extract_pmid("https://pubmed.ncbi.nlm.nih.gov/12345") == "12345"
        
        # Empty
        assert adapter._extract_pmid("") == ""
        
        # Invalid
        assert adapter._extract_pmid("not-a-url") == ""
    
    @patch('src.adapters.pubmed_adapter.PubmedTools')
    def test_translate_query_passthrough(self, mock_pubmed):
        """Verify translate_query passes through query unchanged"""
        from src.adapters.pubmed_adapter import PubMedAdapter
        
        adapter = PubMedAdapter()
        
        result = adapter.translate_query("fall prevention nursing")
        assert result == "fall prevention nursing"
    
    @patch('src.adapters.pubmed_adapter.PubmedTools')
    def test_search_ids_calls_tools(self, mock_pubmed_class):
        """Verify search_ids delegates to PubmedTools"""
        from src.adapters.pubmed_adapter import PubMedAdapter
        
        # Setup mock
        mock_tools_instance = MagicMock()
        mock_tools_instance.fetch_pubmed_ids.return_value = ["123", "456", "789"]
        mock_pubmed_class.return_value = mock_tools_instance
        
        adapter = PubMedAdapter()
        result = adapter.search_ids("test query", max_results=10)
        
        assert result == ["123", "456", "789"]
        mock_tools_instance.fetch_pubmed_ids.assert_called_once()


class TestPaginationType:
    """Test PaginationType enum"""
    
    def test_values(self):
        """Verify pagination types exist"""
        assert PaginationType.OFFSET.value == "offset"
        assert PaginationType.CURSOR.value == "cursor"
        assert PaginationType.PAGE.value == "page"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
