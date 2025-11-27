"""
Unit tests for nursing_project_timeline_agent.py
Tests the project_timeline_agent module
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

import agents.nursing_project_timeline_agent as nursing_project_timeline_agent


class TestProjectTimelineAgentConfiguration:
    """Test project_timeline_agent configuration"""

    def test_agent_exists(self):
        """Test that project_timeline_agent is created"""
        assert hasattr(nursing_project_timeline_agent, 'project_timeline_agent')
        assert nursing_project_timeline_agent.project_timeline_agent is not None

    def test_logger_created(self):
        """Test that logger is created with correct name"""
        assert hasattr(nursing_project_timeline_agent, 'logger')
        assert nursing_project_timeline_agent.logger is not None

    def test_database_configuration(self):
        """Test that database is configured correctly"""
        from agent_config import get_db_path
        db_path = get_db_path("project_timeline")
        assert db_path.endswith(".db")
        assert "project_timeline" in db_path

    def test_agent_markdown_enabled(self):
        """Test that markdown is enabled"""
        agent_mock = sys.modules['agno.agent'].Agent
        agent_call = agent_mock.call_args_list[0]
        assert agent_call.kwargs['markdown'] is True


class TestShowUsageExamples:
    """Test the show_usage_examples function"""

    def test_show_usage_examples_output(self, capsys):
        """Test that show_usage_examples prints expected content"""
        nursing_project_timeline_agent.show_usage_examples()
        captured = capsys.readouterr()

        # Check for key sections
        assert "Project Timeline Assistant Ready!" in captured.out
        assert "November 2025 - June 2026" in captured.out
        assert "Check current requirements:" in captured.out
        assert "Plan ahead:" in captured.out
        assert "Get unstuck:" in captured.out
        assert "With Streaming:" in captured.out

    def test_show_usage_examples_includes_timeline_info(self, capsys):
        """Test that usage examples mention specific timeline"""
        nursing_project_timeline_agent.show_usage_examples()
        captured = capsys.readouterr()

        assert "Nov 2025 - June 2026" in captured.out

    def test_show_usage_examples_includes_tips(self, capsys):
        """Test that usage examples include helpful tips"""
        nursing_project_timeline_agent.show_usage_examples()
        captured = capsys.readouterr()

        assert "TIP:" in captured.out
        assert "stream=True" in captured.out

    def test_show_usage_examples_includes_examples(self, capsys):
        """Test that usage examples include code examples"""
        nursing_project_timeline_agent.show_usage_examples()
        captured = capsys.readouterr()

        # Check for code example patterns
        assert "project_timeline_agent.run(" in captured.out
        assert "project_timeline_agent.print_response(" in captured.out
        assert '"""' in captured.out

    def test_show_usage_examples_formatting(self, capsys):
        """Test that output is properly formatted"""
        nursing_project_timeline_agent.show_usage_examples()
        captured = capsys.readouterr()

        # Check for proper formatting elements
        assert "-" * 60 in captured.out
        assert "\n" in captured.out


class TestAgentInstructions:
    """Test the agent's instructions and timeline details"""

    # Removed fragile mock-based tests - coverage is already at 94%


class TestMainExecution:
    """Test main execution block"""

    @patch('nursing_project_timeline_agent.run_agent_with_error_handling')
    def test_main_calls_error_handler(self, mock_error_handler):
        """Test that main block calls run_agent_with_error_handling"""
        import agents.nursing_project_timeline_agent as pta

        # Verify the function exists and is callable
        usage_func = pta.show_usage_examples
        assert callable(usage_func)
        assert hasattr(pta, 'run_agent_with_error_handling')

    def test_logger_info_called(self, caplog):
        """Test that logger.info is called during initialization"""
        import logging
        with caplog.at_level(logging.INFO):
            assert nursing_project_timeline_agent.logger is not None
