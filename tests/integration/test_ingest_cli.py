"""
Integration Tests for Ingestion CLI (Phase B5)
Validates: CLI commands (add, add-folder, list, remove, stats, search)

Created: 2025-12-13
Validation Gate: B5
"""

import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

import pytest

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
CLI_PATH = PROJECT_ROOT / "scripts" / "ingest_documents.py"


def run_cli(*args, db_path: str = None) -> subprocess.CompletedProcess:
    """Run the CLI with given arguments."""
    cmd = [sys.executable, str(CLI_PATH)]
    if db_path:
        cmd.extend(["--db-path", db_path])
    cmd.extend(args)

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT)
    )


class TestCLIHelp:
    """Test CLI help and basic structure."""

    def test_cli_help(self):
        """Test that CLI shows help."""
        result = run_cli("--help")

        assert result.returncode == 0
        assert "Personal Knowledge Library" in result.stdout
        assert "add" in result.stdout
        assert "add-folder" in result.stdout
        assert "list" in result.stdout
        assert "remove" in result.stdout
        assert "stats" in result.stdout

    def test_cli_no_command(self):
        """Test CLI with no command shows help."""
        result = run_cli()

        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "Usage" in result.stdout

    def test_add_help(self):
        """Test add command help."""
        result = run_cli("add", "--help")

        assert result.returncode == 0
        assert "chunk-size" in result.stdout
        assert "overlap" in result.stdout


class TestAddCommand:
    """Test the 'add' command."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary database directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_cli_add_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def temp_text_file(self):
        """Create a temporary text file."""
        content = "Test document content for CLI testing. " * 50
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    def test_add_single_file(self, temp_db_dir, temp_text_file):
        """Test adding a single file."""
        result = run_cli("add", temp_text_file, db_path=temp_db_dir)

        assert result.returncode == 0
        assert "Added" in result.stdout or "✅" in result.stdout

    def test_add_file_not_found(self, temp_db_dir):
        """Test adding a non-existent file."""
        result = run_cli("add", "/nonexistent/file.txt", db_path=temp_db_dir)

        assert result.returncode == 1
        assert "not found" in result.stdout.lower() or "❌" in result.stdout

    def test_add_unsupported_format(self, temp_db_dir):
        """Test adding an unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            result = run_cli("add", temp_path, db_path=temp_db_dir)

            assert result.returncode == 1
            assert "Unsupported" in result.stdout or "❌" in result.stdout
        finally:
            os.unlink(temp_path)


class TestAddFolderCommand:
    """Test the 'add-folder' command."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary database directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_cli_folder_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def temp_folder(self):
        """Create a temporary folder with test files."""
        temp_dir = tempfile.mkdtemp(prefix="test_docs_")

        # Create test files
        (Path(temp_dir) / "doc1.txt").write_text("Document one content. " * 20)
        (Path(temp_dir) / "doc2.md").write_text("# Document Two\nContent here. " * 20)

        # Create subdirectory
        subdir = Path(temp_dir) / "subdir"
        subdir.mkdir()
        (subdir / "doc3.txt").write_text("Subdirectory document. " * 20)

        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_add_folder(self, temp_db_dir, temp_folder):
        """Test adding a folder."""
        result = run_cli("add-folder", temp_folder, db_path=temp_db_dir)

        assert result.returncode == 0
        assert "Successfully processed" in result.stdout

    def test_add_folder_recursive(self, temp_db_dir, temp_folder):
        """Test adding a folder recursively."""
        result = run_cli("add-folder", temp_folder, "--recursive", db_path=temp_db_dir)

        assert result.returncode == 0
        # Should process files from subdirectory too
        assert "3" in result.stdout or "Successfully" in result.stdout

    def test_add_folder_not_found(self, temp_db_dir):
        """Test adding a non-existent folder."""
        result = run_cli("add-folder", "/nonexistent/folder", db_path=temp_db_dir)

        assert result.returncode == 1
        assert "not found" in result.stdout.lower()


class TestListCommand:
    """Test the 'list' command."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary database directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_cli_list_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_list_empty(self, temp_db_dir):
        """Test listing empty library."""
        result = run_cli("list", db_path=temp_db_dir)

        assert result.returncode == 0
        assert "No documents" in result.stdout or "add" in result.stdout.lower()

    def test_list_with_documents(self, temp_db_dir):
        """Test listing after adding a document."""
        # First add a document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for listing. " * 50)
            temp_path = f.name

        try:
            run_cli("add", temp_path, db_path=temp_db_dir)
            result = run_cli("list", db_path=temp_db_dir)

            assert result.returncode == 0
            assert "Document ID" in result.stdout or "Total:" in result.stdout
        finally:
            os.unlink(temp_path)


class TestStatsCommand:
    """Test the 'stats' command."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary database directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_cli_stats_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_stats_empty(self, temp_db_dir):
        """Test stats on empty library."""
        result = run_cli("stats", db_path=temp_db_dir)

        assert result.returncode == 0
        assert "Collection" in result.stdout
        assert "Total" in result.stdout

    def test_stats_with_documents(self, temp_db_dir):
        """Test stats after adding documents."""
        # Add a document first
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content for stats. " * 50)
            temp_path = f.name

        try:
            run_cli("add", temp_path, db_path=temp_db_dir)
            result = run_cli("stats", db_path=temp_db_dir)

            assert result.returncode == 0
            assert "Total Documents:" in result.stdout
            assert "Total Chunks:" in result.stdout
        finally:
            os.unlink(temp_path)


class TestRemoveCommand:
    """Test the 'remove' command."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary database directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_cli_remove_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_remove_nonexistent(self, temp_db_dir):
        """Test removing a non-existent document."""
        result = run_cli("remove", "nonexistent_id", db_path=temp_db_dir)

        # Should indicate document not found
        assert "not found" in result.stdout.lower() or "⚠️" in result.stdout


class TestSearchCommand:
    """Test the 'search' command."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary database directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_cli_search_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_search_empty(self, temp_db_dir):
        """Test searching empty library."""
        result = run_cli("search", "test query", db_path=temp_db_dir)

        assert result.returncode == 0
        assert "No results" in result.stdout or "0" in result.stdout

    def test_search_with_results(self, temp_db_dir):
        """Test searching with indexed documents."""
        # Add a document with specific content
        content = "Fall prevention is important in nursing. Hourly rounding reduces falls." * 10

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            run_cli("add", temp_path, db_path=temp_db_dir)
            result = run_cli("search", "fall prevention", db_path=temp_db_dir)

            assert result.returncode == 0
            assert "Found" in result.stdout or "Score:" in result.stdout
        finally:
            os.unlink(temp_path)


class TestCLIIntegration:
    """Full integration tests for CLI workflow."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create temporary database directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_cli_integration_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_full_workflow(self, temp_db_dir):
        """Test complete workflow: add -> list -> search -> stats."""
        # Create test file
        content = "Patient safety guidelines for nursing practice. " * 30

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            # Step 1: Add document
            result = run_cli("add", temp_path, db_path=temp_db_dir)
            assert result.returncode == 0, f"Add failed: {result.stdout}"

            # Step 2: List documents
            result = run_cli("list", db_path=temp_db_dir)
            assert result.returncode == 0, f"List failed: {result.stdout}"
            assert "Total:" in result.stdout

            # Step 3: Search
            result = run_cli("search", "patient safety", db_path=temp_db_dir)
            assert result.returncode == 0, f"Search failed: {result.stdout}"

            # Step 4: Stats
            result = run_cli("stats", db_path=temp_db_dir)
            assert result.returncode == 0, f"Stats failed: {result.stdout}"
            assert "Total Documents: 1" in result.stdout

        finally:
            os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
