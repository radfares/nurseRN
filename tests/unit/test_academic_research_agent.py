"""
Unit tests for academic_research_agent.py
Tests the AcademicResearchAgent class and its methods
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

from agents.academic_research_agent import AcademicResearchAgent


class TestAcademicResearchAgentInitialization:
    """Test AcademicResearchAgent initialization"""

    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_initialization_creates_tools(self, mock_build_tools, mock_arxiv):
        """Test that initialization creates Arxiv tools"""
        mock_arxiv.return_value = Mock(name="arxiv_tool")
        mock_build_tools.return_value = [Mock()]

        agent = AcademicResearchAgent()

        mock_arxiv.assert_called_once_with(required=False)
        mock_build_tools.assert_called_once()

    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_initialization_sets_agent_name(self, mock_build_tools, mock_arxiv):
        """Test that initialization sets correct agent name"""
        mock_build_tools.return_value = []

        agent = AcademicResearchAgent()

        assert agent.agent_name == "Academic Research Agent"
        assert agent.agent_key == "academic_research"


class TestCreateAgent:
    """Test the _create_agent method"""

    @patch('agents.academic_research_agent.Agent')
    @patch('agents.academic_research_agent.get_db_path')
    @patch('agents.academic_research_agent.create_arxiv_tools_safe', return_value=None)
    @patch('agents.academic_research_agent.build_tools_list', return_value=[])
    def test_create_agent_uses_correct_database(
        self, mock_build, mock_arxiv, mock_get_db, mock_agent
    ):
        """Test that agent uses correct database path"""
        mock_get_db.return_value = "/tmp/academic_research_agent.db"

        agent = AcademicResearchAgent()

        mock_get_db.assert_called_with("academic_research")


class TestAcademicResearchAgentIntegration:
    """Integration tests for AcademicResearchAgent"""

    @patch('agents.academic_research_agent.Agent')
    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_agent_inherits_from_base_agent(self, mock_build, mock_arxiv, mock_agent):
        """Test that AcademicResearchAgent inherits from BaseAgent"""
        from agents.base_agent import BaseAgent

        mock_build.return_value = []
        agent = AcademicResearchAgent()

        assert isinstance(agent, BaseAgent)

    @patch('agents.academic_research_agent.Agent')
    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_agent_has_required_methods(self, mock_build, mock_arxiv, mock_agent):
        """Test that agent has all required methods"""
        mock_build.return_value = []
        agent = AcademicResearchAgent()

        assert hasattr(agent, '_create_tools')
        assert hasattr(agent, '_create_agent')
        assert hasattr(agent, 'show_usage_examples')


class TestShowUsageExamples:
    """Test the show_usage_examples method"""

    @patch('agents.academic_research_agent.get_api_status')
    @patch('agents.academic_research_agent.Agent')
    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_show_usage_examples_with_openai_configured(
        self, mock_build, mock_arxiv, mock_agent, mock_api_status, capsys
    ):
        """Test show_usage_examples when OpenAI is configured"""
        mock_build.return_value = [Mock(name="arxiv_tool")]
        mock_api_status.return_value = {
            "openai": {"key_set": True},
            "arxiv": {"available": True}
        }

        agent = AcademicResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "Academic Research Agent (Arxiv) Ready!" in captured.out
        assert "OpenAI API - Configured (REQUIRED)" in captured.out
        assert "Arxiv - No authentication required" in captured.out

    @patch('agents.academic_research_agent.get_api_status')
    @patch('agents.academic_research_agent.Agent')
    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_show_usage_examples_without_openai(
        self, mock_build, mock_arxiv, mock_agent, mock_api_status, capsys
    ):
        """Test show_usage_examples when OpenAI is not configured"""
        mock_build.return_value = [Mock(name="arxiv_tool")]
        mock_api_status.return_value = {
            "openai": {"key_set": False}
        }

        agent = AcademicResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "OpenAI API - NOT configured (REQUIRED)" in captured.out
        assert "Set OPENAI_API_KEY environment variable" in captured.out

    @patch('agents.academic_research_agent.get_api_status')
    @patch('agents.academic_research_agent.Agent')
    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_show_usage_examples_no_tools_warning(
        self, mock_build, mock_arxiv, mock_agent, mock_api_status, capsys
    ):
        """Test show_usage_examples warning when no tools available"""
        mock_build.return_value = []  # No tools
        mock_api_status.return_value = {
            "openai": {"key_set": True}
        }

        agent = AcademicResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "WARNING: Arxiv tool not available!" in captured.out

    @patch('agents.academic_research_agent.get_api_status')
    @patch('agents.academic_research_agent.Agent')
    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_show_usage_examples_includes_examples(
        self, mock_build, mock_arxiv, mock_agent, mock_api_status, capsys
    ):
        """Test that usage examples include code examples"""
        mock_build.return_value = [Mock(name="arxiv_tool")]
        mock_api_status.return_value = {
            "openai": {"key_set": True}
        }

        agent = AcademicResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        # Check for example queries
        assert "Find statistical methods:" in captured.out
        assert "Search for AI/ML applications:" in captured.out
        assert "Methodological papers:" in captured.out
        assert "With Streaming:" in captured.out
        assert "academic_research_agent.run(" in captured.out

    @patch('agents.academic_research_agent.get_api_status')
    @patch('agents.academic_research_agent.Agent')
    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_show_usage_examples_includes_tips(
        self, mock_build, mock_arxiv, mock_agent, mock_api_status, capsys
    ):
        """Test that usage examples include helpful tips"""
        mock_build.return_value = [Mock(name="arxiv_tool")]
        mock_api_status.return_value = {
            "openai": {"key_set": True}
        }

        agent = AcademicResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "TIP:" in captured.out
        assert "Arxiv is great for theoretical and methodological research" in captured.out
        assert "stream=True" in captured.out


class TestGlobalInstance:
    """Test global instance creation"""

    @patch('agents.academic_research_agent.Agent')
    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_global_instance_exists(self, mock_build, mock_arxiv, mock_agent):
        """Test that global instance is created"""
        mock_build.return_value = []

        # The module creates a global instance
        from agents.academic_research_agent import _academic_research_agent_instance, academic_research_agent

        assert _academic_research_agent_instance is not None
        assert academic_research_agent is not None

    @patch('agents.academic_research_agent.Agent')
    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_global_instance_is_academic_research_agent(self, mock_build, mock_arxiv, mock_agent):
        """Test that global instance is an AcademicResearchAgent"""
        mock_build.return_value = []

        from agents.academic_research_agent import _academic_research_agent_instance

        assert isinstance(_academic_research_agent_instance, AcademicResearchAgent)


class TestCreateTools:
    """Test the _create_tools method"""

    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_create_tools_with_arxiv(self, mock_build_tools, mock_arxiv, capsys):
        """Test tool creation when Arxiv is available"""
        arxiv_tool = Mock(name="arxiv")
        mock_arxiv.return_value = arxiv_tool
        mock_build_tools.return_value = [arxiv_tool]

        agent = AcademicResearchAgent()

        assert len(agent.tools) == 1
        captured = capsys.readouterr()
        assert "✅ Arxiv search available" in captured.out

    @patch('agents.academic_research_agent.create_arxiv_tools_safe')
    @patch('agents.academic_research_agent.build_tools_list')
    def test_create_tools_without_arxiv(self, mock_build_tools, mock_arxiv, capsys):
        """Test tool creation when Arxiv is not available"""
        mock_arxiv.return_value = None
        mock_build_tools.return_value = []

        agent = AcademicResearchAgent()

        assert len(agent.tools) == 0
        captured = capsys.readouterr()
        assert "⚠️ Arxiv search unavailable" in captured.out
        assert "❌ No search tools available" in captured.out
