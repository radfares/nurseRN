"""
Unit tests for nursing_research_agent.py
Tests the NursingResearchAgent class and its methods
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch, call
from io import StringIO

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

from agents.nursing_research_agent import NursingResearchAgent


class TestNursingResearchAgentInitialization:
    """Test NursingResearchAgent initialization"""

    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_initialization_creates_tools(self, mock_build_tools, mock_serp, mock_exa):
        """Test that initialization creates tools"""
        mock_exa.return_value = Mock(name="exa_tool")
        mock_serp.return_value = Mock(name="serp_tool")
        mock_build_tools.return_value = [Mock(), Mock()]

        agent = NursingResearchAgent()

        # Verify tools were created
        mock_exa.assert_called_once_with(required=False)
        mock_serp.assert_called_once_with(required=False)
        mock_build_tools.assert_called_once()

    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_initialization_sets_agent_name(self, mock_build_tools, mock_serp, mock_exa):
        """Test that initialization sets correct agent name"""
        mock_build_tools.return_value = []

        agent = NursingResearchAgent()

        assert agent.agent_name == "Nursing Research Agent"
        assert agent.agent_key == "nursing_research"

    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_initialization_stores_tools(self, mock_build_tools, mock_serp, mock_exa):
        """Test that tools are stored in the agent"""
        test_tools = [Mock(name="tool1"), Mock(name="tool2")]
        mock_build_tools.return_value = test_tools

        agent = NursingResearchAgent()

        assert agent.tools == test_tools


class TestCreateTools:
    """Test the _create_tools method"""

    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_create_tools_with_both_apis(self, mock_build_tools, mock_serp, mock_exa, capsys):
        """Test tool creation when both APIs are available"""
        exa_tool = Mock(name="exa")
        serp_tool = Mock(name="serp")
        mock_exa.return_value = exa_tool
        mock_serp.return_value = serp_tool
        mock_build_tools.return_value = [exa_tool, serp_tool]

        agent = NursingResearchAgent()

        # Verify both tools created
        assert len(agent.tools) == 2

        # Verify success messages
        captured = capsys.readouterr()
        assert "✅ Exa search available" in captured.out
        assert "✅ SerpAPI search available" in captured.out

    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_create_tools_with_no_apis(self, mock_build_tools, mock_serp, mock_exa, capsys):
        """Test tool creation when no APIs are available"""
        mock_exa.return_value = None
        mock_serp.return_value = None
        mock_build_tools.return_value = []

        agent = NursingResearchAgent()

        # Verify no tools
        assert len(agent.tools) == 0

        # Verify warning messages
        captured = capsys.readouterr()
        assert "⚠️ Exa search unavailable" in captured.out
        assert "⚠️ SerpAPI unavailable" in captured.out
        assert "❌ No search tools available" in captured.out

    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_create_tools_with_only_exa(self, mock_build_tools, mock_serp, mock_exa, capsys):
        """Test tool creation with only Exa available"""
        exa_tool = Mock(name="exa")
        mock_exa.return_value = exa_tool
        mock_serp.return_value = None
        mock_build_tools.return_value = [exa_tool]

        agent = NursingResearchAgent()

        assert len(agent.tools) == 1
        captured = capsys.readouterr()
        assert "✅ Exa search available" in captured.out
        assert "⚠️ SerpAPI unavailable" in captured.out


class TestCreateAgent:
    """Test the _create_agent method"""

    @patch('nursing_research_agent.Agent')
    @patch('nursing_research_agent.OpenAIChat')
    @patch('nursing_research_agent.SqliteDb')
    @patch('nursing_research_agent.get_db_path')
    @patch('nursing_research_agent.create_exa_tools_safe', return_value=None)
    @patch('nursing_research_agent.create_serp_tools_safe', return_value=None)
    @patch('nursing_research_agent.build_tools_list', return_value=[])
    def test_create_agent_configures_correctly(
        self, mock_build, mock_serp, mock_exa,
        mock_get_db, mock_sqlite, mock_openai, mock_agent
    ):
        """Test that _create_agent configures the agent correctly"""
        mock_get_db.return_value = "/tmp/nursing_research_agent.db"
        mock_db_instance = Mock()
        mock_sqlite.return_value = mock_db_instance
        mock_model_instance = Mock()
        mock_openai.return_value = mock_model_instance

        agent = NursingResearchAgent()

        # Verify Agent was created with correct parameters
        mock_agent.assert_called_once()
        call_kwargs = mock_agent.call_args.kwargs

        assert call_kwargs['name'] == "Nursing Research Agent"
        assert call_kwargs['role'] == "Healthcare improvement project research specialist"
        assert call_kwargs['model'] == mock_model_instance
        assert call_kwargs['tools'] == []
        assert call_kwargs['add_history_to_context'] is True
        assert call_kwargs['add_datetime_to_context'] is True
        assert call_kwargs['enable_agentic_memory'] is True
        assert call_kwargs['markdown'] is True
        assert call_kwargs['db'] == mock_db_instance

    @patch('nursing_research_agent.Agent')
    @patch('nursing_research_agent.OpenAIChat')
    @patch('nursing_research_agent.create_exa_tools_safe', return_value=None)
    @patch('nursing_research_agent.create_serp_tools_safe', return_value=None)
    @patch('nursing_research_agent.build_tools_list', return_value=[])
    def test_create_agent_uses_gpt4o_model(
        self, mock_build, mock_serp, mock_exa, mock_openai, mock_agent
    ):
        """Test that agent uses gpt-4o model"""
        agent = NursingResearchAgent()

        mock_openai.assert_called_once_with(id="gpt-4o")

    @patch('nursing_research_agent.Agent')
    @patch('nursing_research_agent.SqliteDb')
    @patch('nursing_research_agent.get_db_path')
    @patch('nursing_research_agent.create_exa_tools_safe', return_value=None)
    @patch('nursing_research_agent.create_serp_tools_safe', return_value=None)
    @patch('nursing_research_agent.build_tools_list', return_value=[])
    def test_create_agent_uses_correct_database(
        self, mock_build, mock_serp, mock_exa,
        mock_get_db, mock_sqlite, mock_agent
    ):
        """Test that agent uses correct database path"""
        mock_get_db.return_value = "/tmp/nursing_research_agent.db"

        agent = NursingResearchAgent()

        mock_get_db.assert_called_with("nursing_research")
        mock_sqlite.assert_called_once_with(db_file="/tmp/nursing_research_agent.db")


class TestShowUsageExamples:
    """Test the show_usage_examples method"""

    @patch('nursing_research_agent.get_api_status')
    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_show_usage_all_apis_configured(
        self, mock_build, mock_serp, mock_exa, mock_api_status, capsys
    ):
        """Test usage examples when all APIs are configured"""
        mock_api_status.return_value = {
            "openai": {"key_set": True},
            "exa": {"key_set": True},
            "serp": {"key_set": True}
        }
        mock_build.return_value = [Mock(), Mock()]

        agent = NursingResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "✅ OpenAI API - Configured (REQUIRED)" in captured.out
        assert "✅ Exa API - Configured (literature search)" in captured.out
        assert "✅ SerpAPI - Configured (web search)" in captured.out
        assert "🏥 Nursing Research Agent Ready!" in captured.out

    @patch('nursing_research_agent.get_api_status')
    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_show_usage_no_apis_configured(
        self, mock_build, mock_serp, mock_exa, mock_api_status, capsys
    ):
        """Test usage examples when no APIs are configured"""
        mock_api_status.return_value = {
            "openai": {"key_set": False},
            "exa": {"key_set": False},
            "serp": {"key_set": False}
        }
        mock_build.return_value = []

        agent = NursingResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "❌ OpenAI API - NOT configured (REQUIRED)" in captured.out
        assert "⚠️ Exa API - NOT configured" in captured.out
        assert "⚠️ SerpAPI - NOT configured" in captured.out
        assert "⚠️ WARNING: No search tools configured!" in captured.out

    @patch('nursing_research_agent.get_api_status')
    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_show_usage_displays_examples(
        self, mock_build, mock_serp, mock_exa, mock_api_status, capsys
    ):
        """Test that usage examples are displayed"""
        mock_api_status.return_value = {
            "openai": {"key_set": True},
            "exa": {"key_set": True},
            "serp": {"key_set": True}
        }
        mock_build.return_value = [Mock(), Mock()]

        agent = NursingResearchAgent()
        agent.show_usage_examples()

        captured = capsys.readouterr()
        assert "PICOT Development:" in captured.out
        assert "Literature Search:" in captured.out
        assert "Standards Research:" in captured.out
        assert "With Streaming" in captured.out
        assert "patient falls" in captured.out
        assert "catheter-associated" in captured.out


class TestNursingResearchAgentIntegration:
    """Integration tests for NursingResearchAgent"""

    @patch('nursing_research_agent.Agent')
    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_agent_inherits_from_base_agent(
        self, mock_build, mock_serp, mock_exa, mock_agent
    ):
        """Test that NursingResearchAgent inherits from BaseAgent"""
        from agents.base_agent import BaseAgent

        mock_build.return_value = []
        agent = NursingResearchAgent()

        assert isinstance(agent, BaseAgent)

    @patch('nursing_research_agent.Agent')
    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_agent_has_required_methods(
        self, mock_build, mock_serp, mock_exa, mock_agent
    ):
        """Test that agent has all required methods"""
        mock_build.return_value = []
        agent = NursingResearchAgent()

        assert hasattr(agent, '_create_tools')
        assert hasattr(agent, '_create_agent')
        assert hasattr(agent, 'show_usage_examples')
        assert hasattr(agent, 'run_with_error_handling')

    @patch('nursing_research_agent.create_exa_tools_safe')
    @patch('nursing_research_agent.create_serp_tools_safe')
    @patch('nursing_research_agent.build_tools_list')
    def test_global_instance_created(
        self, mock_build, mock_serp, mock_exa
    ):
        """Test that global instance variables are created"""
        import nursing_research_agent as nra_module

        mock_build.return_value = []

        # Force reload to test global instance creation
        # (Already created during import, but we verify it exists)
        assert hasattr(nra_module, '_nursing_research_agent_instance')
        assert hasattr(nra_module, 'nursing_research_agent')

        # Verify global agent points to the instance's agent
        assert nra_module.nursing_research_agent == nra_module._nursing_research_agent_instance.agent
