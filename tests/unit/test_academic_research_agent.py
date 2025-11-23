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
sys.modules['src'] = MagicMock()
sys.modules['src.services'] = MagicMock()
sys.modules['src.services.api_tools'] = MagicMock()

from academic_research_agent import AcademicResearchAgent


class TestAcademicResearchAgentInitialization:
    """Test AcademicResearchAgent initialization"""

    @patch('academic_research_agent.create_arxiv_tools_safe')
    @patch('academic_research_agent.build_tools_list')
    def test_initialization_creates_tools(self, mock_build_tools, mock_arxiv):
        """Test that initialization creates Arxiv tools"""
        mock_arxiv.return_value = Mock(name="arxiv_tool")
        mock_build_tools.return_value = [Mock()]

        agent = AcademicResearchAgent()

        mock_arxiv.assert_called_once_with(required=False)
        mock_build_tools.assert_called_once()

    @patch('academic_research_agent.create_arxiv_tools_safe')
    @patch('academic_research_agent.build_tools_list')
    def test_initialization_sets_agent_name(self, mock_build_tools, mock_arxiv):
        """Test that initialization sets correct agent name"""
        mock_build_tools.return_value = []

        agent = AcademicResearchAgent()

        assert agent.agent_name == "Academic Research Agent"
        assert agent.agent_key == "academic_research"


class TestCreateAgent:
    """Test the _create_agent method"""

    @patch('academic_research_agent.Agent')
    @patch('academic_research_agent.get_db_path')
    @patch('academic_research_agent.create_arxiv_tools_safe', return_value=None)
    @patch('academic_research_agent.build_tools_list', return_value=[])
    def test_create_agent_uses_correct_database(
        self, mock_build, mock_arxiv, mock_get_db, mock_agent
    ):
        """Test that agent uses correct database path"""
        mock_get_db.return_value = "/tmp/academic_research_agent.db"

        agent = AcademicResearchAgent()

        mock_get_db.assert_called_with("academic_research")


class TestAcademicResearchAgentIntegration:
    """Integration tests for AcademicResearchAgent"""

    @patch('academic_research_agent.Agent')
    @patch('academic_research_agent.create_arxiv_tools_safe')
    @patch('academic_research_agent.build_tools_list')
    def test_agent_inherits_from_base_agent(self, mock_build, mock_arxiv, mock_agent):
        """Test that AcademicResearchAgent inherits from BaseAgent"""
        from base_agent import BaseAgent

        mock_build.return_value = []
        agent = AcademicResearchAgent()

        assert isinstance(agent, BaseAgent)
