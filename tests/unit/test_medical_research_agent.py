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
# Don't mock src module globally - let real imports work

from agents.medical_research_agent import MedicalResearchAgent


class TestMedicalResearchAgentInitialization:
    """Test MedicalResearchAgent initialization"""

    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_initialization_creates_tools(self, mock_build_tools, mock_pubmed):
        """Test that initialization creates PubMed tools"""
        mock_pubmed.return_value = Mock(name="pubmed_tool")
        mock_build_tools.return_value = [Mock()]

        agent = MedicalResearchAgent()

        mock_pubmed.assert_called_once_with(required=False)
        mock_build_tools.assert_called_once()

    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_initialization_sets_agent_name(self, mock_build_tools, mock_pubmed):
        """Test that initialization sets correct agent name"""
        mock_build_tools.return_value = []

        agent = MedicalResearchAgent()

        assert agent.agent_name == "Medical Research Agent"
        assert agent.agent_key == "medical_research"

    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_initialization_stores_tools(self, mock_build_tools, mock_pubmed):
        """Test that tools are stored in the agent"""
        test_tools = [Mock(name="pubmed_tool")]
        mock_build_tools.return_value = test_tools

        agent = MedicalResearchAgent()

        assert agent.tools == test_tools


class TestCreateTools:
    """Test the _create_tools method"""

    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_create_tools_with_pubmed(self, mock_build_tools, mock_pubmed, capsys):
        """Test tool creation when PubMed is available"""
        pubmed_tool = Mock(name="pubmed")
        mock_pubmed.return_value = pubmed_tool
        mock_build_tools.return_value = [pubmed_tool]

        agent = MedicalResearchAgent()

        assert len(agent.tools) == 1
        captured = capsys.readouterr()
        assert "✅ PubMed search available" in captured.out

    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
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

    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.OpenAIChat')
    @patch('agents.medical_research_agent.SqliteDb')
    @patch('agents.medical_research_agent.get_db_path')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe', return_value=None)
    @patch('agents.medical_research_agent.build_tools_list', return_value=[])
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

    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.get_db_path')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe', return_value=None)
    @patch('agents.medical_research_agent.build_tools_list', return_value=[])
    def test_create_agent_uses_correct_database(
        self, mock_build, mock_pubmed, mock_get_db, mock_agent
    ):
        """Test that agent uses correct database path"""
        mock_get_db.return_value = "/tmp/medical_research_agent.db"

        agent = MedicalResearchAgent()

        mock_get_db.assert_called_with("medical_research")


class TestMedicalResearchAgentIntegration:
    """Integration tests for MedicalResearchAgent"""

    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_agent_inherits_from_base_agent(self, mock_build, mock_pubmed, mock_agent):
        """Test that MedicalResearchAgent inherits from BaseAgent"""
        from agents.base_agent import BaseAgent

        mock_build.return_value = []
        agent = MedicalResearchAgent()

        assert isinstance(agent, BaseAgent)

    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_agent_has_required_methods(self, mock_build, mock_pubmed, mock_agent):
        """Test that agent has all required methods"""
        mock_build.return_value = []
        agent = MedicalResearchAgent()

        assert hasattr(agent, '_create_tools')
        assert hasattr(agent, '_create_agent')
        assert hasattr(agent, 'show_usage_examples')


class TestShowUsageExamples:
    """Test the show_usage_examples method"""

    @patch('agents.medical_research_agent.get_api_status')
    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_show_usage_examples_with_openai_configured(
        self, mock_build, mock_pubmed, mock_agent, mock_api_status, capsys
    ):
        """Test show_usage_examples when OpenAI is configured"""
        mock_build.return_value = [Mock(name="pubmed_tool")]
        mock_api_status.return_value = {
            "openai": {"key_set": True},
            "pubmed": {"email_set": True}
        }

        agent = MedicalResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "Medical Research Agent (PubMed) Ready!" in captured.out
        assert "OpenAI API - Configured (REQUIRED)" in captured.out
        assert "PubMed - Email configured" in captured.out

    @patch('agents.medical_research_agent.get_api_status')
    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_show_usage_examples_without_openai(
        self, mock_build, mock_pubmed, mock_agent, mock_api_status, capsys
    ):
        """Test show_usage_examples when OpenAI is not configured"""
        mock_build.return_value = [Mock(name="pubmed_tool")]
        mock_api_status.return_value = {
            "openai": {"key_set": False},
            "pubmed": {"email_set": False}
        }

        agent = MedicalResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "OpenAI API - NOT configured (REQUIRED)" in captured.out
        assert "Set OPENAI_API_KEY environment variable" in captured.out

    @patch('agents.medical_research_agent.get_api_status')
    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_show_usage_examples_without_pubmed_email(
        self, mock_build, mock_pubmed, mock_agent, mock_api_status, capsys
    ):
        """Test show_usage_examples when PubMed email is not set"""
        mock_build.return_value = [Mock(name="pubmed_tool")]
        mock_api_status.return_value = {
            "openai": {"key_set": True},
            "pubmed": {"email_set": False}
        }

        agent = MedicalResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "PubMed - Using default email" in captured.out
        assert "set PUBMED_EMAIL" in captured.out

    @patch('agents.medical_research_agent.get_api_status')
    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_show_usage_examples_no_tools_warning(
        self, mock_build, mock_pubmed, mock_agent, mock_api_status, capsys
    ):
        """Test show_usage_examples warning when no tools available"""
        mock_build.return_value = []  # No tools
        mock_api_status.return_value = {
            "openai": {"key_set": True},
            "pubmed": {"email_set": True}
        }

        agent = MedicalResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "WARNING: PubMed tool not available!" in captured.out

    @patch('agents.medical_research_agent.get_api_status')
    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_show_usage_examples_includes_examples(
        self, mock_build, mock_pubmed, mock_agent, mock_api_status, capsys
    ):
        """Test that usage examples include code examples"""
        mock_build.return_value = [Mock(name="pubmed_tool")]
        mock_api_status.return_value = {
            "openai": {"key_set": True},
            "pubmed": {"email_set": True}
        }

        agent = MedicalResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        # Check for example queries
        assert "Find clinical studies:" in captured.out
        assert "Search for specific conditions:" in captured.out
        assert "Literature review:" in captured.out
        assert "With Streaming:" in captured.out
        assert "medical_research_agent.run(" in captured.out

    @patch('agents.medical_research_agent.get_api_status')
    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_show_usage_examples_includes_tips(
        self, mock_build, mock_pubmed, mock_agent, mock_api_status, capsys
    ):
        """Test that usage examples include helpful tips"""
        mock_build.return_value = [Mock(name="pubmed_tool")]
        mock_api_status.return_value = {
            "openai": {"key_set": True},
            "pubmed": {"email_set": True}
        }

        agent = MedicalResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "TIP:" in captured.out
        assert "PubMed has millions of biomedical articles" in captured.out
        assert "Full metadata includes: DOI, URLs, MeSH terms" in captured.out


class TestGlobalInstance:
    """Test global instance creation"""

    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_global_instance_exists(self, mock_build, mock_pubmed, mock_agent):
        """Test that global instance is created"""
        mock_build.return_value = []

        # The module creates a global instance
        from agents.medical_research_agent import _medical_research_agent_instance, medical_research_agent

        assert _medical_research_agent_instance is not None
        assert medical_research_agent is not None

    @patch('agents.medical_research_agent.Agent')
    @patch('agents.medical_research_agent.create_pubmed_tools_safe')
    @patch('agents.medical_research_agent.build_tools_list')
    def test_global_instance_is_medical_research_agent(self, mock_build, mock_pubmed, mock_agent):
        """Test that global instance is a MedicalResearchAgent"""
        mock_build.return_value = []

        from agents.medical_research_agent import _medical_research_agent_instance

        assert isinstance(_medical_research_agent_instance, MedicalResearchAgent)
