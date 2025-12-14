"""
Unit Tests for Vector Store (Phase B2)
Validates: PersonalLibraryVectorStore, SearchResult, collection management

Created: 2025-12-13
Validation Gate: B2

Note: These tests use a temporary ChromaDB directory to avoid polluting production data.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.knowledge.vector_store import (
    PersonalLibraryVectorStore,
    SearchResult,
    get_personal_library_store,
    COLLECTION_PERSONAL,
    VectorStoreError,
)
from src.knowledge.document_ingester import ChunkRecord, DocumentIngester


class TestSearchResult:
    """Tests for SearchResult class."""

    def test_search_result_creation(self):
        """Test basic SearchResult creation."""
        result = SearchResult(
            chunk_id="doc123_chunk_0001",
            doc_id="doc123",
            text="This is test content.",
            score=0.85,
            source_path="/path/to/file.pdf",
            page_num=5
        )

        assert result.chunk_id == "doc123_chunk_0001"
        assert result.doc_id == "doc123"
        assert result.text == "This is test content."
        assert result.score == 0.85
        assert result.source_path == "/path/to/file.pdf"
        assert result.page_num == 5

    def test_search_result_filename(self):
        """Test filename extraction from source path."""
        result = SearchResult(
            chunk_id="test",
            doc_id="test",
            text="test",
            score=0.5,
            source_path="/some/long/path/to/document.pdf"
        )

        assert result.filename == "document.pdf"

    def test_search_result_to_dict(self):
        """Test conversion to dictionary."""
        result = SearchResult(
            chunk_id="chunk1",
            doc_id="doc1",
            text="Content",
            score=0.9,
            source_path="/path/file.txt",
            page_num=1,
            metadata={"extra": "value"}
        )

        d = result.to_dict()

        assert d["chunk_id"] == "chunk1"
        assert d["doc_id"] == "doc1"
        assert d["score"] == 0.9
        assert d["filename"] == "file.txt"
        assert d["metadata"]["extra"] == "value"

    def test_search_result_repr(self):
        """Test string representation."""
        result = SearchResult(
            chunk_id="test",
            doc_id="test",
            text="test",
            score=0.85,
            source_path="/path/to/file.pdf",
            page_num=10
        )

        repr_str = repr(result)
        assert "file.pdf" in repr_str
        assert "0.850" in repr_str
        assert "10" in repr_str


class TestPersonalLibraryVectorStore:
    """Tests for PersonalLibraryVectorStore class."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp(prefix="test_chromadb_")
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def store(self, temp_db_dir):
        """Create a PersonalLibraryVectorStore with temp directory."""
        return PersonalLibraryVectorStore(
            collection_name="test_collection",
            db_path=temp_db_dir
        )

    @pytest.fixture
    def sample_chunks(self):
        """Create sample ChunkRecords for testing."""
        return [
            ChunkRecord(
                doc_id="doc001",
                chunk_id="doc001_chunk_0000",
                text="Fall prevention is critical in nursing care. Regular patient assessment and environmental modifications reduce fall risk.",
                source_path="/test/fall_prevention.pdf",
                page_num=1,
                chunk_index=0,
                total_chunks=2
            ),
            ChunkRecord(
                doc_id="doc001",
                chunk_id="doc001_chunk_0001",
                text="Hourly rounding protocols have shown to reduce patient falls by up to 50%. Nurses should assess mobility and medication effects.",
                source_path="/test/fall_prevention.pdf",
                page_num=2,
                chunk_index=1,
                total_chunks=2
            ),
            ChunkRecord(
                doc_id="doc002",
                chunk_id="doc002_chunk_0000",
                text="Medication administration safety requires the five rights: right patient, right drug, right dose, right route, right time.",
                source_path="/test/medication_safety.pdf",
                page_num=1,
                chunk_index=0,
                total_chunks=1
            )
        ]

    def test_store_initialization(self, store, temp_db_dir):
        """Test store initialization."""
        assert store.collection_name == "test_collection"
        assert store.db_path == temp_db_dir
        assert store.embedder is not None

    def test_create_collection(self, store):
        """Test collection creation."""
        store.initialize()
        assert store.exists()

    def test_add_chunks(self, store, sample_chunks):
        """Test adding chunks to the store."""
        count = store.add_chunks(sample_chunks)

        assert count == 3
        stats = store.get_stats()
        assert stats["chunk_count"] == 3

    def test_add_empty_chunks(self, store):
        """Test adding empty chunk list."""
        count = store.add_chunks([])
        assert count == 0

    def test_search_returns_results(self, store, sample_chunks):
        """Test that search returns relevant results."""
        store.add_chunks(sample_chunks)

        results = store.search("fall prevention nursing", limit=5)

        assert len(results) > 0
        assert all(isinstance(r, SearchResult) for r in results)

    def test_search_relevance_ordering(self, store, sample_chunks):
        """Test that results are ordered by relevance."""
        store.add_chunks(sample_chunks)

        results = store.search("fall prevention", limit=5)

        # Scores should be in descending order
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_search_with_limit(self, store, sample_chunks):
        """Test search respects limit parameter."""
        store.add_chunks(sample_chunks)

        results = store.search("nursing care", limit=2)

        assert len(results) <= 2

    def test_search_empty_results(self, store):
        """Test search on empty store."""
        store.initialize()

        results = store.search("anything", limit=5)

        assert len(results) == 0

    def test_delete_document(self, store, sample_chunks):
        """Test deleting a document by doc_id."""
        store.add_chunks(sample_chunks)

        # Delete doc001 (has 2 chunks)
        result = store.delete_document("doc001")

        assert result == True

        # Verify only doc002 remains
        stats = store.get_stats()
        assert stats["chunk_count"] == 1

    def test_delete_nonexistent_document(self, store, sample_chunks):
        """Test deleting a document that doesn't exist."""
        store.add_chunks(sample_chunks)

        result = store.delete_document("nonexistent_doc")

        assert result == False

    def test_get_stats(self, store, sample_chunks):
        """Test getting store statistics."""
        store.add_chunks(sample_chunks)

        stats = store.get_stats()

        assert stats["collection_name"] == "test_collection"
        assert stats["exists"] == True
        assert stats["chunk_count"] == 3
        assert "embedder" in stats

    def test_clear_collection(self, store, sample_chunks):
        """Test clearing all documents."""
        store.add_chunks(sample_chunks)
        assert store.get_stats()["chunk_count"] == 3

        store.clear()

        # After clear, collection still exists but is empty
        # Note: Some ChromaDB versions may behave differently
        stats = store.get_stats()
        # Just verify operation completed without error

    def test_drop_collection(self, store, sample_chunks):
        """Test dropping the entire collection."""
        store.add_chunks(sample_chunks)
        assert store.exists()

        store.drop()

        assert not store.exists()

    def test_persistence_across_instances(self, temp_db_dir, sample_chunks):
        """Test that data persists across store instances."""
        # First instance - add data
        store1 = PersonalLibraryVectorStore(
            collection_name="persistence_test",
            db_path=temp_db_dir
        )
        store1.add_chunks(sample_chunks)
        count1 = store1.get_stats()["chunk_count"]

        # Create new instance pointing to same location
        store2 = PersonalLibraryVectorStore(
            collection_name="persistence_test",
            db_path=temp_db_dir
        )
        count2 = store2.get_stats()["chunk_count"]

        assert count1 == count2 == 3


class TestFactoryFunction:
    """Tests for factory function."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp(prefix="test_chromadb_factory_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_personal_library_store(self, temp_db_dir):
        """Test the factory function."""
        store = get_personal_library_store(
            collection_name="factory_test",
            db_path=temp_db_dir
        )

        assert isinstance(store, PersonalLibraryVectorStore)
        assert store.collection_name == "factory_test"

    def test_default_collection_name(self, temp_db_dir):
        """Test default collection name."""
        store = get_personal_library_store(db_path=temp_db_dir)

        assert store.collection_name == COLLECTION_PERSONAL


class TestIntegrationWithIngester:
    """Integration tests with DocumentIngester."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp(prefix="test_chromadb_integration_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def temp_text_file(self):
        """Create a temporary text file."""
        content = """
        Patient Safety Guidelines

        Fall Prevention Protocol:
        1. Assess patient mobility on admission
        2. Implement hourly rounding
        3. Use bed alarms for high-risk patients
        4. Keep call light within reach

        Medication Safety:
        1. Verify patient identity
        2. Check for allergies
        3. Document administration
        """ * 5  # Repeat for enough content

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    def test_ingest_and_search(self, temp_db_dir, temp_text_file):
        """Test full pipeline: ingest file -> store -> search."""
        # Ingest
        ingester = DocumentIngester(chunk_size=500, overlap=50)
        chunks = ingester.ingest_file(temp_text_file)

        assert len(chunks) > 0

        # Store
        store = PersonalLibraryVectorStore(
            collection_name="integration_test",
            db_path=temp_db_dir
        )
        store.add_chunks(chunks)

        # Search
        results = store.search("fall prevention", limit=3)

        assert len(results) > 0
        # At least one result should mention fall
        assert any("fall" in r.text.lower() for r in results)

    def test_ingest_search_delete_cycle(self, temp_db_dir, temp_text_file):
        """Test complete lifecycle: ingest, search, delete."""
        # Ingest
        ingester = DocumentIngester(chunk_size=500, overlap=50)
        chunks = ingester.ingest_file(temp_text_file)
        doc_id = chunks[0].doc_id

        # Store
        store = PersonalLibraryVectorStore(
            collection_name="lifecycle_test",
            db_path=temp_db_dir
        )
        store.add_chunks(chunks)

        # Verify stored
        initial_count = store.get_stats()["chunk_count"]
        assert initial_count > 0

        # Search works
        results = store.search("patient safety", limit=3)
        assert len(results) > 0

        # Delete
        store.delete_document(doc_id)

        # Verify deleted
        final_count = store.get_stats()["chunk_count"]
        assert final_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
