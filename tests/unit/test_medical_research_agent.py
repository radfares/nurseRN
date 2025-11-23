"""
Unit tests for medical_research_agent.py
Tests the MedicalResearchAgent class and its methods
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch

# Mock all external dependencies before importing
sys.modules['agno'] = MagicMock()
sys.modules['agno.agent'] = MagicMock()
sys.modules['agno.db'] = MagicMock()
sys.modules['agno.db.sqlite'] = MagicMock()
sys.modules['agno.models'] = MagicMock()
sys.modules['agno.models.openai'] = MagicMock()
sys.modules['src'] = MagicMock()
sys.modules['src.services'] = MagicMock()
sys.modules['src.services.api_tools'] = MagicMock()

from medical_research_agent import MedicalResearchAgent


class TestMedicalResearchAgentInitialization:
    """Test MedicalResearchAgent initialization"""

    @patch('medical_research_agent.create_pubmed_tools_safe')
    @patch('medical_research_agent.build_tools_list')
    def test_initialization_creates_tools(self, mock_build_tools, mock_pubmed):
        """Test that initialization creates PubMed tools"""
        mock_pubmed.return_value = Mock(name="pubmed_tool")
        mock_build_tools.return_value = [Mock()]

        agent = MedicalResearchAgent()

        mock_pubmed.assert_called_once_with(required=False)
        mock_build_tools.assert_called_once()

    @patch('medical_research_agent.create_pubmed_tools_safe')
    @patch('medical_research_agent.build_tools_list')
    def test_initialization_sets_agent_name(self, mock_build_tools, mock_pubmed):
        """Test that initialization sets correct agent name"""
        mock_build_tools.return_value = []

        agent = MedicalResearchAgent()

        assert agent.agent_name == "Medical Research Agent"
        assert agent.agent_key == "medical_research"

    @patch('medical_research_agent.create_pubmed_tools_safe')
    @patch('medical_research_agent.build_tools_list')
    def test_initialization_stores_tools(self, mock_build_tools, mock_pubmed):
        """Test that tools are stored in the agent"""
        test_tools = [Mock(name="pubmed_tool")]
        mock_build_tools.return_value = test_tools

        agent = MedicalResearchAgent()

        assert agent.tools == test_tools


class TestCreateTools:
    """Test the _create_tools method"""

    @patch('medical_research_agent.create_pubmed_tools_safe')
    @patch('medical_research_agent.build_tools_list')
    def test_create_tools_with_pubmed(self, mock_build_tools, mock_pubmed, capsys):
        """Test tool creation when PubMed is available"""
        pubmed_tool = Mock(name="pubmed")
        mock_pubmed.return_value = pubmed_tool
        mock_build_tools.return_value = [pubmed_tool]

        agent = MedicalResearchAgent()

        assert len(agent.tools) == 1
        captured = capsys.readouterr()
        assert "✅ PubMed search available" in captured.out

    @patch('medical_research_agent.create_pubmed_tools_safe')
    @patch('medical_research_agent.build_tools_list')
    def test_create_tools_without_pubmed(self, mock_build_tools, mock_pubmed, capsys):
        """Test tool creation when PubMed is not available"""
        mock_pubmed.return_value = None
        mock_build_tools.return_value = []

        agent = MedicalResearchAgent()

        assert len(agent.tools) == 0
        captured = capsys.readouterr()
        assert "⚠️ PubMed search unavailable" in captured.out


class TestCreateAgent:
    """Test the _create_agent method"""

    @patch('medical_research_agent.Agent')
    @patch('medical_research_agent.OpenAIChat')
    @patch('medical_research_agent.SqliteDb')
    @patch('medical_research_agent.get_db_path')
    @patch('medical_research_agent.create_pubmed_tools_safe', return_value=None)
    @patch('medical_research_agent.build_tools_list', return_value=[])
    def test_create_agent_configures_correctly(
        self, mock_build, mock_pubmed, mock_get_db, mock_sqlite, mock_openai, mock_agent
    ):
        """Test that _create_agent configures the agent correctly"""
        mock_get_db.return_value = "/tmp/medical_research_agent.db"

        agent = MedicalResearchAgent()

        mock_agent.assert_called_once()
        call_kwargs = mock_agent.call_args.kwargs

        assert call_kwargs['name'] == "Medical Research Agent"
        assert call_kwargs['add_history_to_context'] is True
        assert call_kwargs['markdown'] is True

    @patch('medical_research_agent.Agent')
    @patch('medical_research_agent.get_db_path')
    @patch('medical_research_agent.create_pubmed_tools_safe', return_value=None)
    @patch('medical_research_agent.build_tools_list', return_value=[])
    def test_create_agent_uses_correct_database(
        self, mock_build, mock_pubmed, mock_get_db, mock_agent
    ):
        """Test that agent uses correct database path"""
        mock_get_db.return_value = "/tmp/medical_research_agent.db"

        agent = MedicalResearchAgent()

        mock_get_db.assert_called_with("medical_research")


class TestMedicalResearchAgentIntegration:
    """Integration tests for MedicalResearchAgent"""

    @patch('medical_research_agent.Agent')
    @patch('medical_research_agent.create_pubmed_tools_safe')
    @patch('medical_research_agent.build_tools_list')
    def test_agent_inherits_from_base_agent(self, mock_build, mock_pubmed, mock_agent):
        """Test that MedicalResearchAgent inherits from BaseAgent"""
        from base_agent import BaseAgent

        mock_build.return_value = []
        agent = MedicalResearchAgent()

        assert isinstance(agent, BaseAgent)

    @patch('medical_research_agent.Agent')
    @patch('medical_research_agent.create_pubmed_tools_safe')
    @patch('medical_research_agent.build_tools_list')
    def test_agent_has_required_methods(self, mock_build, mock_pubmed, mock_agent):
        """Test that agent has all required methods"""
        mock_build.return_value = []
        agent = MedicalResearchAgent()

        assert hasattr(agent, '_create_tools')
        assert hasattr(agent, '_create_agent')
        assert hasattr(agent, 'show_usage_examples')
