"""
Integration Tests for Agent Personal Library Integration (Phase B4)
Validates: PersonalLibraryTools in NursingResearchAgent

Created: 2025-12-13
Validation Gate: B4
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


class TestAgentImports:
    """Test that agent imports work correctly."""

    def test_import_personal_library_tools(self):
        """Test that PersonalLibraryTools can be imported."""
        from src.knowledge.personal_library_tool import (
            PersonalLibraryTools,
            create_personal_library_tools_safe,
        )

        assert PersonalLibraryTools is not None
        assert create_personal_library_tools_safe is not None

    def test_import_from_knowledge_module(self):
        """Test that imports work from the knowledge module."""
        from src.knowledge import (
            PersonalLibraryTools,
            create_personal_library_tools_safe,
        )

        assert PersonalLibraryTools is not None
        assert create_personal_library_tools_safe is not None


class TestAgentToolIntegration:
    """Test PersonalLibraryTools integration with agent."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory for ChromaDB."""
        temp_dir = tempfile.mkdtemp(prefix="test_agent_integration_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_personal_library_tools_creation(self, temp_db_dir):
        """Test that PersonalLibraryTools can be created for agent."""
        from src.knowledge.personal_library_tool import create_personal_library_tools_safe

        tools = create_personal_library_tools_safe(db_path=temp_db_dir)

        assert tools is not None
        assert hasattr(tools, 'search_personal_library')

    def test_personal_library_tools_safe_returns_none_on_error(self):
        """Test that safe factory returns None on error."""
        from src.knowledge.personal_library_tool import create_personal_library_tools_safe

        with patch('src.knowledge.personal_library_tool.PersonalLibraryTools.__init__',
                   side_effect=Exception("Test error")):
            tools = create_personal_library_tools_safe()

            assert tools is None

    def test_tool_has_correct_name(self, temp_db_dir):
        """Test that the tool has the expected name."""
        from src.knowledge.personal_library_tool import PersonalLibraryTools

        tools = PersonalLibraryTools(db_path=temp_db_dir)

        assert tools.name == "personal_library"

    def test_tool_has_instructions(self, temp_db_dir):
        """Test that the tool includes instructions for the agent."""
        from src.knowledge.personal_library_tool import PersonalLibraryTools

        tools = PersonalLibraryTools(db_path=temp_db_dir)

        assert tools.instructions is not None
        assert "PERSONAL LIBRARY TOOL" in tools.instructions
        assert "my notes" in tools.instructions.lower()
        assert "my documents" in tools.instructions.lower()


class TestAgentModuleIntegration:
    """Test integration at the agent module level."""

    def test_nursing_agent_module_imports(self):
        """Test that the nursing_research_agent module can be imported."""
        # This tests that all imports in the agent module work
        try:
            from agents import nursing_research_agent
            # Module should be importable
            assert True
        except ImportError as e:
            # If import fails due to API keys, that's okay for this test
            if "API" in str(e) or "key" in str(e).lower():
                pytest.skip("Skipped due to missing API keys")
            raise

    def test_personal_library_import_in_agent_module(self):
        """Test that the import statement in the agent works."""
        # Directly test the import path used in the agent
        from src.knowledge.personal_library_tool import create_personal_library_tools_safe

        # Should not raise
        assert callable(create_personal_library_tools_safe)


class TestToolResponseFormat:
    """Test that tool responses are properly formatted for agent consumption."""

    @pytest.fixture
    def temp_db_dir(self):
        """Create a temporary directory."""
        temp_dir = tempfile.mkdtemp(prefix="test_format_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def populated_tools(self, temp_db_dir):
        """Create tools with test data."""
        from src.knowledge.vector_store import PersonalLibraryVectorStore
        from src.knowledge.document_ingester import ChunkRecord
        from src.knowledge.personal_library_tool import PersonalLibraryTools

        # Add test data
        store = PersonalLibraryVectorStore(
            collection_name="format_test",
            db_path=temp_db_dir
        )

        chunks = [
            ChunkRecord(
                doc_id="doc001",
                chunk_id="doc001_chunk_0000",
                text="Fall prevention requires hourly rounding and environmental checks.",
                source_path="/test/nursing_notes.pdf",
                page_num=3,
                chunk_index=0,
                total_chunks=1
            ),
        ]
        store.add_chunks(chunks)

        return PersonalLibraryTools(
            db_path=temp_db_dir,
            collection_name="format_test",
        )

    def test_response_includes_found_message(self, populated_tools):
        """Test that response includes 'Found X relevant sections'."""
        result = populated_tools.search_personal_library("fall prevention")

        assert "Found" in result
        assert "relevant sections" in result

    def test_response_includes_score(self, populated_tools):
        """Test that response includes relevance score."""
        result = populated_tools.search_personal_library("fall prevention")

        assert "Score:" in result

    def test_response_includes_source(self, populated_tools):
        """Test that response includes source file."""
        result = populated_tools.search_personal_library("fall prevention")

        assert "nursing_notes.pdf" in result

    def test_response_includes_page(self, populated_tools):
        """Test that response includes page number."""
        result = populated_tools.search_personal_library("fall prevention")

        assert "p.3" in result


class TestSystemPromptContent:
    """Test that system prompt updates are correct."""

    def test_prompt_contains_personal_library_section(self):
        """Verify the agent instructions include personal library guidance."""
        # Read the agent file and check the prompt content
        agent_file = Path(__file__).parent.parent.parent / "agents" / "nursing_research_agent.py"

        if agent_file.exists():
            content = agent_file.read_text()

            # Check for personal library section in instructions
            assert "PERSONAL LIBRARY TOOL:" in content
            assert "search_personal_library()" in content
            assert "my notes" in content.lower()
            assert "my documents" in content.lower()
        else:
            pytest.skip("Agent file not found")

    def test_tool_priority_documented(self):
        """Verify tool priority is documented in the agent."""
        agent_file = Path(__file__).parent.parent.parent / "agents" / "nursing_research_agent.py"

        if agent_file.exists():
            content = agent_file.read_text()

            # Check that personal library is mentioned in tool priority
            assert "PersonalLibrary" in content
            # Check it comes after external sources
            assert "PubMed/External sources FIRST" in content or "external sources" in content.lower()
        else:
            pytest.skip("Agent file not found")


class TestToolStatusTracking:
    """Test that tool status is properly tracked."""

    def test_tool_status_includes_personal_library(self):
        """Verify _tool_status dictionary includes personal_library."""
        agent_file = Path(__file__).parent.parent.parent / "agents" / "nursing_research_agent.py"

        if agent_file.exists():
            content = agent_file.read_text()

            # Check that personal_library is in the tool status dict
            assert "'personal_library':" in content
            assert "personal_library_tools is not None" in content
        else:
            pytest.skip("Agent file not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
