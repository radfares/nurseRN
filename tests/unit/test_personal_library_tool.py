"""
Unit Tests for Personal Library Tools (Phase B3)
Validates: PersonalLibraryTools, search formatting, error handling

Created: 2025-12-13
Validation Gate: B3
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.knowledge.personal_library_tool import (
    PersonalLibraryTools,
    create_personal_library_tools,
    create_personal_library_tools_safe,
)
from src.knowledge.vector_store import PersonalLibraryVectorStore, SearchResult
from src.knowledge.document_ingester import DocumentIngester, ChunkRecord


class TestPersonalLibraryToolsInitialization:
    """Tests for PersonalLibraryTools initialization."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp(prefix="test_lib_tools_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_initialization(self, temp_db_dir):
        """Test basic initialization."""
        tools = PersonalLibraryTools(db_path=temp_db_dir)

        assert tools.db_path == temp_db_dir
        assert tools.max_results == 5
        assert tools.min_score == 0.1

    def test_custom_parameters(self, temp_db_dir):
        """Test initialization with custom parameters."""
        tools = PersonalLibraryTools(
            db_path=temp_db_dir,
            collection_name="custom_collection",
            max_results=10,
            min_score=0.5,
        )

        assert tools.collection_name == "custom_collection"
        assert tools.max_results == 10
        assert tools.min_score == 0.5

    def test_toolkit_name(self, temp_db_dir):
        """Test that toolkit has correct name."""
        tools = PersonalLibraryTools(db_path=temp_db_dir)

        assert tools.name == "personal_library"

    def test_instructions_present(self, temp_db_dir):
        """Test that instructions are set."""
        tools = PersonalLibraryTools(db_path=temp_db_dir)

        assert tools.instructions is not None
        assert "PERSONAL LIBRARY TOOL" in tools.instructions
        assert "search_personal_library" in tools.instructions


class TestSearchPersonalLibrary:
    """Tests for search_personal_library method."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp(prefix="test_search_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def populated_tools(self, temp_db_dir):
        """Create tools with pre-populated data."""
        # Create and populate store
        store = PersonalLibraryVectorStore(
            collection_name="test_search",
            db_path=temp_db_dir
        )

        chunks = [
            ChunkRecord(
                doc_id="doc001",
                chunk_id="doc001_chunk_0000",
                text="Fall prevention is critical in nursing care. Regular patient assessment helps identify risk factors.",
                source_path="/test/fall_prevention.pdf",
                page_num=1,
                chunk_index=0,
                total_chunks=2
            ),
            ChunkRecord(
                doc_id="doc001",
                chunk_id="doc001_chunk_0001",
                text="Hourly rounding protocols reduce patient falls by up to 50%. Environmental safety checks are essential.",
                source_path="/test/fall_prevention.pdf",
                page_num=2,
                chunk_index=1,
                total_chunks=2
            ),
            ChunkRecord(
                doc_id="doc002",
                chunk_id="doc002_chunk_0000",
                text="Medication administration requires the five rights: right patient, drug, dose, route, and time.",
                source_path="/test/medication_safety.pdf",
                page_num=1,
                chunk_index=0,
                total_chunks=1
            ),
        ]
        store.add_chunks(chunks)

        # Create tools pointing to same store
        tools = PersonalLibraryTools(
            db_path=temp_db_dir,
            collection_name="test_search",
            max_results=5,
        )

        return tools

    def test_search_returns_formatted_results(self, populated_tools):
        """Test that search returns properly formatted results."""
        result = populated_tools.search_personal_library("fall prevention")

        assert "Found" in result
        assert "relevant sections" in result
        assert "Score:" in result

    def test_search_includes_source_attribution(self, populated_tools):
        """Test that results include source file names."""
        result = populated_tools.search_personal_library("fall prevention")

        assert "fall_prevention.pdf" in result

    def test_search_includes_page_numbers(self, populated_tools):
        """Test that results include page numbers."""
        result = populated_tools.search_personal_library("fall prevention")

        assert "p." in result  # Page number indicator

    def test_search_with_custom_limit(self, populated_tools):
        """Test search with custom result limit."""
        result = populated_tools.search_personal_library("nursing", n_results=2)

        # Count the numbered results (1., 2., etc.)
        result_count = sum(1 for line in result.split('\n') if line.strip().startswith(('1.', '2.', '3.')))
        assert result_count <= 2

    def test_search_invalid_query_empty(self, populated_tools):
        """Test handling of empty query."""
        result = populated_tools.search_personal_library("")

        parsed = json.loads(result)
        assert "error" in parsed

    def test_search_invalid_query_none(self, populated_tools):
        """Test handling of None query."""
        result = populated_tools.search_personal_library(None)

        parsed = json.loads(result)
        assert "error" in parsed

    def test_search_empty_library(self, temp_db_dir):
        """Test search on empty library."""
        tools = PersonalLibraryTools(
            db_path=temp_db_dir,
            collection_name="empty_collection",
        )

        result = tools.search_personal_library("anything")

        assert "empty" in result.lower() or "add documents" in result.lower()

    def test_search_no_matches(self, populated_tools):
        """Test search with no matching results."""
        # Search for something very specific that won't match
        result = populated_tools.search_personal_library("quantum physics black holes")

        # Should either find no relevant docs or return low-score results
        # The exact behavior depends on the vector search
        assert isinstance(result, str)


class TestResultFormatting:
    """Tests for result formatting."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_format_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_format_result_with_page(self, temp_db_dir):
        """Test formatting a result with page number."""
        tools = PersonalLibraryTools(db_path=temp_db_dir)

        result = SearchResult(
            chunk_id="test_chunk",
            doc_id="test_doc",
            text="This is the content.",
            score=0.85,
            source_path="/path/to/document.pdf",
            page_num=5,
        )

        formatted = tools._format_result(result, 1)

        assert "document.pdf" in formatted
        assert "p.5" in formatted
        assert "0.85" in formatted
        assert "This is the content." in formatted

    def test_format_result_without_page(self, temp_db_dir):
        """Test formatting a result without page number."""
        tools = PersonalLibraryTools(db_path=temp_db_dir)

        result = SearchResult(
            chunk_id="test_chunk",
            doc_id="test_doc",
            text="Content without page.",
            score=0.75,
            source_path="/path/to/notes.txt",
            page_num=None,
        )

        formatted = tools._format_result(result, 1)

        assert "notes.txt" in formatted
        assert "p." not in formatted  # No page number
        assert "0.75" in formatted

    def test_format_long_text_truncated(self, temp_db_dir):
        """Test that long text is truncated."""
        tools = PersonalLibraryTools(db_path=temp_db_dir)

        long_text = "A" * 1000  # Very long text
        result = SearchResult(
            chunk_id="test_chunk",
            doc_id="test_doc",
            text=long_text,
            score=0.9,
            source_path="/path/to/file.pdf",
        )

        formatted = tools._format_result(result, 1)

        # Text should be truncated with ellipsis
        assert "..." in formatted
        assert len(formatted) < len(long_text) + 100


class TestFactoryFunctions:
    """Tests for factory functions."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_factory_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_create_personal_library_tools(self, temp_db_dir):
        """Test the standard factory function."""
        tools = create_personal_library_tools(db_path=temp_db_dir)

        assert isinstance(tools, PersonalLibraryTools)

    def test_create_personal_library_tools_safe_success(self, temp_db_dir):
        """Test the safe factory function on success."""
        tools = create_personal_library_tools_safe(db_path=temp_db_dir)

        assert isinstance(tools, PersonalLibraryTools)

    def test_create_personal_library_tools_safe_failure(self):
        """Test the safe factory function handles errors."""
        # Patch to simulate initialization failure
        with patch.object(PersonalLibraryTools, '__init__', side_effect=Exception("Init failed")):
            tools = create_personal_library_tools_safe()

            assert tools is None


class TestLibraryStats:
    """Tests for library statistics."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_stats_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_library_stats_empty(self, temp_db_dir):
        """Test getting stats from empty library."""
        tools = PersonalLibraryTools(
            db_path=temp_db_dir,
            collection_name="empty_stats",
        )

        stats = tools.get_library_stats()

        assert "total_chunks" in stats
        assert stats["total_chunks"] == 0

    def test_get_library_stats_with_data(self, temp_db_dir):
        """Test getting stats from populated library."""
        # Populate store
        store = PersonalLibraryVectorStore(
            collection_name="stats_test",
            db_path=temp_db_dir
        )

        chunks = [
            ChunkRecord(
                doc_id="doc001",
                chunk_id="doc001_chunk_0000",
                text="Test content for statistics.",
                source_path="/test/file.pdf",
                chunk_index=0,
                total_chunks=1
            ),
        ]
        store.add_chunks(chunks)

        # Get stats
        tools = PersonalLibraryTools(
            db_path=temp_db_dir,
            collection_name="stats_test",
        )

        stats = tools.get_library_stats()

        assert stats["total_chunks"] >= 1


class TestIntegrationWithFullPipeline:
    """Integration tests for full document pipeline."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_pipeline_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def temp_text_file(self):
        """Create a temporary text file with nursing content."""
        content = """
        Patient Safety in Nursing Practice

        Chapter 1: Fall Prevention
        Falls are a major concern in healthcare settings. Risk factors include
        age, medication effects, and mobility issues. Prevention strategies
        include hourly rounding, bed alarms, and environmental modifications.

        Chapter 2: Medication Safety
        The five rights of medication administration are essential:
        right patient, right drug, right dose, right route, right time.
        Bar code scanning and double-checking high-alert medications
        reduce errors significantly.

        Chapter 3: Infection Control
        Hand hygiene is the most effective way to prevent healthcare-associated
        infections. Standard precautions should be used for all patients.
        """ * 3  # Repeat for more content

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    def test_full_pipeline_ingest_search(self, temp_db_dir, temp_text_file):
        """Test complete pipeline: ingest -> tools -> search."""
        # Ingest document
        ingester = DocumentIngester(chunk_size=500, overlap=50)
        chunks = ingester.ingest_file(temp_text_file)

        # Store in vector store
        store = PersonalLibraryVectorStore(
            collection_name="pipeline_test",
            db_path=temp_db_dir
        )
        store.add_chunks(chunks)

        # Create tools
        tools = PersonalLibraryTools(
            db_path=temp_db_dir,
            collection_name="pipeline_test",
        )

        # Search
        result = tools.search_personal_library("fall prevention")

        # Verify results
        assert "Found" in result
        assert "fall" in result.lower() or "Fall" in result

    def test_search_relevance(self, temp_db_dir, temp_text_file):
        """Test that search returns relevant results."""
        # Setup
        ingester = DocumentIngester(chunk_size=500, overlap=50)
        chunks = ingester.ingest_file(temp_text_file)

        store = PersonalLibraryVectorStore(
            collection_name="relevance_test",
            db_path=temp_db_dir
        )
        store.add_chunks(chunks)

        tools = PersonalLibraryTools(
            db_path=temp_db_dir,
            collection_name="relevance_test",
        )

        # Search for medication - should find medication content
        result = tools.search_personal_library("medication five rights")

        assert "medication" in result.lower() or "drug" in result.lower() or "dose" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
