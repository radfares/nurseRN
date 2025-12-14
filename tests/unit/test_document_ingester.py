"""
Unit Tests for Document Ingester (Phase B1)
Validates: ChunkRecord, DocumentIngester, error handling

Created: 2025-12-13
Validation Gate: B1
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.knowledge.document_ingester import (
    DocumentIngester,
    ChunkRecord,
    FileNotFoundError,
    UnsupportedFormatError,
    ReadError,
    ingest_document
)


class TestChunkRecord:
    """Tests for ChunkRecord dataclass."""

    def test_chunk_record_creation(self):
        """Test basic ChunkRecord creation."""
        record = ChunkRecord(
            doc_id="doc123",
            chunk_id="doc123_chunk_0001",
            text="This is test content.",
            source_path="/path/to/file.pdf"
        )

        assert record.doc_id == "doc123"
        assert record.chunk_id == "doc123_chunk_0001"
        assert record.text == "This is test content."
        assert record.source_path == "/path/to/file.pdf"
        assert record.source_type == "personal"
        assert record.version == 1
        assert record.char_count == len("This is test content.")

    def test_chunk_record_timestamp(self):
        """Test that timestamp is auto-generated."""
        record = ChunkRecord(
            doc_id="doc123",
            chunk_id="doc123_chunk_0001",
            text="Test",
            source_path="/path/to/file.pdf"
        )

        assert record.ingested_at != ""
        assert "T" in record.ingested_at  # ISO format contains T

    def test_chunk_record_to_document(self):
        """Test conversion to agno Document."""
        record = ChunkRecord(
            doc_id="doc123",
            chunk_id="doc123_chunk_0001",
            text="Test content here",
            source_path="/path/to/file.pdf",
            page_num=5,
            chunk_index=0,
            total_chunks=10
        )

        doc = record.to_document()

        assert doc.id == "doc123_chunk_0001"
        assert doc.name == "file.pdf"
        assert doc.content == "Test content here"
        assert doc.content_id == "doc123"
        assert doc.meta_data["doc_id"] == "doc123"
        assert doc.meta_data["page_num"] == 5
        assert doc.meta_data["chunk_index"] == 0
        assert doc.meta_data["total_chunks"] == 10

    def test_chunk_record_to_dict(self):
        """Test conversion to dictionary."""
        record = ChunkRecord(
            doc_id="doc123",
            chunk_id="doc123_chunk_0001",
            text="Test",
            source_path="/path/to/file.pdf"
        )

        d = record.to_dict()

        assert d["doc_id"] == "doc123"
        assert d["chunk_id"] == "doc123_chunk_0001"
        assert d["text"] == "Test"
        assert d["source_path"] == "/path/to/file.pdf"


class TestDocumentIngester:
    """Tests for DocumentIngester class."""

    @pytest.fixture
    def ingester(self):
        """Create a DocumentIngester instance."""
        return DocumentIngester(chunk_size=500, overlap=50)

    @pytest.fixture
    def temp_text_file(self):
        """Create a temporary text file for testing."""
        content = "This is a test document. " * 100  # ~2500 chars
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def temp_md_file(self):
        """Create a temporary markdown file for testing."""
        content = """# Test Document

## Section 1
This is the first section with some content.
It contains multiple paragraphs.

## Section 2
This is the second section.
More content here for chunking tests.

## Section 3
Final section with additional text to ensure we have enough content for multiple chunks.
""" * 20  # Repeat to get enough content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_ingester_initialization(self, ingester):
        """Test DocumentIngester initialization."""
        assert ingester.chunk_size == 500
        assert ingester.overlap == 50
        assert ingester.source_type == "personal"
        assert ingester.chunker is not None

    def test_get_supported_formats(self, ingester):
        """Test supported formats list."""
        formats = ingester.get_supported_formats()

        assert ".pdf" in formats
        assert ".txt" in formats
        assert ".md" in formats
        assert ".pptx" in formats
        assert ".csv" in formats
        assert ".json" in formats

    def test_ingest_text_file(self, ingester, temp_text_file):
        """Test ingesting a text file."""
        chunks = ingester.ingest_file(temp_text_file)

        assert len(chunks) > 0
        assert all(isinstance(c, ChunkRecord) for c in chunks)
        assert all(c.source_type == "personal" for c in chunks)
        assert all(c.source_path == str(Path(temp_text_file).absolute()) for c in chunks)

        # Check chunk indices are sequential
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i
            assert chunk.total_chunks == len(chunks)

    def test_ingest_markdown_file(self, ingester, temp_md_file):
        """Test ingesting a markdown file."""
        chunks = ingester.ingest_file(temp_md_file)

        assert len(chunks) > 0
        assert all(c.metadata.get("file_extension") == ".md" for c in chunks)

    def test_chunk_size_bounds(self, ingester, temp_text_file):
        """Test that chunks respect size bounds (approximately)."""
        chunks = ingester.ingest_file(temp_text_file)

        # All chunks except possibly the last should be close to chunk_size
        for chunk in chunks[:-1]:
            # Allow some flexibility due to word boundary handling
            assert chunk.char_count <= ingester.chunk_size * 1.5

    def test_file_not_found(self, ingester):
        """Test error handling for non-existent file."""
        with pytest.raises(FileNotFoundError) as exc_info:
            ingester.ingest_file("/nonexistent/path/file.txt")

        assert "not found" in str(exc_info.value).lower()

    def test_unsupported_format(self, ingester):
        """Test error handling for unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            with pytest.raises(UnsupportedFormatError) as exc_info:
                ingester.ingest_file(temp_path)

            assert "unsupported" in str(exc_info.value).lower()
            assert ".xyz" in str(exc_info.value)
        finally:
            os.unlink(temp_path)

    def test_empty_file_handling(self, ingester):
        """Test handling of empty files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")  # Empty file
            temp_path = f.name

        try:
            with pytest.raises(ReadError) as exc_info:
                ingester.ingest_file(temp_path)

            assert "no content" in str(exc_info.value).lower()
        finally:
            os.unlink(temp_path)

    def test_metadata_completeness(self, ingester, temp_text_file):
        """Test that metadata is complete."""
        chunks = ingester.ingest_file(temp_text_file)

        for chunk in chunks:
            # Required fields
            assert chunk.doc_id != ""
            assert chunk.chunk_id != ""
            assert chunk.source_path != ""
            assert chunk.file_hash != ""
            assert chunk.ingested_at != ""

            # Metadata
            assert "filename" in chunk.metadata
            assert "file_extension" in chunk.metadata
            assert "file_size_bytes" in chunk.metadata

    def test_custom_source_type(self, ingester, temp_text_file):
        """Test custom source type override."""
        chunks = ingester.ingest_file(temp_text_file, source_type="custom_source")

        assert all(c.source_type == "custom_source" for c in chunks)

    def test_extra_metadata(self, ingester, temp_text_file):
        """Test extra metadata is included."""
        extra = {"project": "test_project", "author": "test_author"}
        chunks = ingester.ingest_file(temp_text_file, extra_metadata=extra)

        for chunk in chunks:
            assert chunk.metadata.get("project") == "test_project"
            assert chunk.metadata.get("author") == "test_author"

    def test_doc_id_consistency(self, ingester, temp_text_file):
        """Test that doc_id is consistent across chunks."""
        chunks = ingester.ingest_file(temp_text_file)

        doc_ids = {c.doc_id for c in chunks}
        assert len(doc_ids) == 1  # All chunks have same doc_id

    def test_chunk_id_uniqueness(self, ingester, temp_text_file):
        """Test that chunk_ids are unique."""
        chunks = ingester.ingest_file(temp_text_file)

        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))  # All unique


class TestDocumentIngesterFolder:
    """Tests for folder ingestion."""

    @pytest.fixture
    def temp_folder(self):
        """Create a temporary folder with test files."""
        import tempfile
        import shutil

        temp_dir = tempfile.mkdtemp()

        # Create test files
        with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
            f.write("Content for file 1. " * 50)

        with open(os.path.join(temp_dir, "file2.md"), "w") as f:
            f.write("# File 2\nContent for file 2. " * 50)

        with open(os.path.join(temp_dir, "ignored.xyz"), "w") as f:
            f.write("This should be ignored")

        # Create subfolder
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)
        with open(os.path.join(subdir, "file3.txt"), "w") as f:
            f.write("Content for file 3 in subdir. " * 50)

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_ingest_folder(self, temp_folder):
        """Test folder ingestion."""
        ingester = DocumentIngester(chunk_size=500, overlap=50)
        chunks, failures = ingester.ingest_folder(temp_folder)

        # Should have chunks from 3 supported files
        assert len(chunks) > 0
        assert len(failures) == 0

        # Check we got chunks from multiple files
        source_files = {c.metadata.get("filename") for c in chunks}
        assert len(source_files) >= 3

    def test_ingest_folder_non_recursive(self, temp_folder):
        """Test non-recursive folder ingestion."""
        ingester = DocumentIngester(chunk_size=500, overlap=50)
        chunks, failures = ingester.ingest_folder(temp_folder, recursive=False)

        # Should only get files from root, not subdir
        source_files = {c.metadata.get("filename") for c in chunks}
        assert "file3.txt" not in source_files

    def test_ingest_folder_not_found(self):
        """Test error for non-existent folder."""
        ingester = DocumentIngester()

        with pytest.raises(FileNotFoundError):
            ingester.ingest_folder("/nonexistent/folder")


class TestConvenienceFunction:
    """Tests for the convenience function."""

    def test_ingest_document_function(self):
        """Test the convenience ingest_document function."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for convenience function. " * 50)
            temp_path = f.name

        try:
            chunks = ingest_document(temp_path, chunk_size=200, overlap=20)

            assert len(chunks) > 0
            assert all(isinstance(c, ChunkRecord) for c in chunks)
        finally:
            os.unlink(temp_path)


class TestFileHashAndVersioning:
    """Tests for file hashing and version detection."""

    def test_file_hash_generated(self):
        """Test that file hash is generated."""
        ingester = DocumentIngester()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            chunks = ingester.ingest_file(temp_path)

            assert all(c.file_hash != "" for c in chunks)
            assert all(len(c.file_hash) == 32 for c in chunks)  # MD5 hex length
        finally:
            os.unlink(temp_path)

    def test_same_content_same_hash(self):
        """Test that identical content produces identical hash."""
        ingester = DocumentIngester()
        content = "Identical content for testing"

        # Create two files with same content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f1:
            f1.write(content)
            path1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f2:
            f2.write(content)
            path2 = f2.name

        try:
            chunks1 = ingester.ingest_file(path1)
            chunks2 = ingester.ingest_file(path2)

            # Same content should produce same hash
            assert chunks1[0].file_hash == chunks2[0].file_hash
        finally:
            os.unlink(path1)
            os.unlink(path2)

    def test_different_content_different_hash(self):
        """Test that different content produces different hash."""
        ingester = DocumentIngester()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f1:
            f1.write("Content A")
            path1 = f1.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f2:
            f2.write("Content B")
            path2 = f2.name

        try:
            chunks1 = ingester.ingest_file(path1)
            chunks2 = ingester.ingest_file(path2)

            # Different content should produce different hash
            assert chunks1[0].file_hash != chunks2[0].file_hash
        finally:
            os.unlink(path1)
            os.unlink(path2)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
