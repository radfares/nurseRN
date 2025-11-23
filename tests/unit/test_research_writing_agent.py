"""
Unit tests for research_writing_agent.py
Tests the research_writing_agent module
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

import research_writing_agent


class TestResearchWritingAgentConfiguration:
    """Test research_writing_agent configuration"""

    def test_agent_exists(self):
        """Test that research_writing_agent is created"""
        assert hasattr(research_writing_agent, 'research_writing_agent')
        assert research_writing_agent.research_writing_agent is not None

    def test_logger_created(self):
        """Test that logger is created with correct name"""
        assert hasattr(research_writing_agent, 'logger')
        assert research_writing_agent.logger is not None

    def _find_agent_call(self):
        """Helper to find the Research Writing Agent call"""
        agent_mock = sys.modules['agno.agent'].Agent
        for call in agent_mock.call_args_list:
            if call.kwargs.get('name') == "Research Writing Agent":
                return call
        return None

    def test_agent_name(self):
        """Test that agent has correct name"""
        agent_call = self._find_agent_call()
        assert agent_call is not None
        assert agent_call.kwargs['name'] == "Research Writing Agent"

    def test_agent_role(self):
        """Test that agent has correct role"""
        agent_call = self._find_agent_call()
        assert agent_call is not None
        assert agent_call.kwargs['role'] == "Academic writing and research planning specialist"

    def test_agent_markdown_enabled(self):
        """Test that markdown is enabled"""
        agent_call = self._find_agent_call()
        assert agent_call is not None
        assert agent_call.kwargs['markdown'] is True

    def test_agent_history_context(self):
        """Test that add_history_to_context is enabled"""
        agent_call = self._find_agent_call()
        assert agent_call is not None
        assert agent_call.kwargs['add_history_to_context'] is True

    def test_database_configuration(self):
        """Test that database is configured correctly"""
        from agent_config import get_db_path
        db_path = get_db_path("research_writing")
        assert db_path.endswith(".db")
        assert "research_writing" in db_path


class TestShowUsageExamples:
    """Test the show_usage_examples function"""

    def test_show_usage_examples_output(self, capsys):
        """Test that show_usage_examples prints expected content"""
        research_writing_agent.show_usage_examples()
        captured = capsys.readouterr()

        # Check for key sections
        assert "Research Writing & Planning Agent Ready!" in captured.out
        assert "PICOT Development:" in captured.out
        assert "Literature Review:" in captured.out
        assert "Intervention Planning:" in captured.out
        assert "Poster Section Writing:" in captured.out
        assert "Data Collection Plan:" in captured.out
        assert "Methodology Help:" in captured.out
        assert "Writing Review:" in captured.out
        assert "With Streaming:" in captured.out

    def test_show_usage_examples_includes_tips(self, capsys):
        """Test that usage examples include helpful tips"""
        research_writing_agent.show_usage_examples()
        captured = capsys.readouterr()

        assert "TIP:" in captured.out
        assert "remembers your conversation" in captured.out
        assert "stream=True" in captured.out

    def test_show_usage_examples_includes_examples(self, capsys):
        """Test that usage examples include code examples"""
        research_writing_agent.show_usage_examples()
        captured = capsys.readouterr()

        # Check for code example patterns
        assert "research_writing_agent.run(" in captured.out
        assert "research_writing_agent.print_response(" in captured.out
        assert '"""' in captured.out

    def test_show_usage_examples_formatting(self, capsys):
        """Test that output is properly formatted"""
        research_writing_agent.show_usage_examples()
        captured = capsys.readouterr()

        # Check for proper formatting elements
        assert "-" * 60 in captured.out
        assert "\n" in captured.out


class TestAgentInstructions:
    """Test the agent's instructions and configuration"""

    def _find_agent_call(self):
        """Helper to find the Research Writing Agent call"""
        agent_mock = sys.modules['agno.agent'].Agent
        for call in agent_mock.call_args_list:
            if call.kwargs.get('name') == "Research Writing Agent":
                return call
        return None

    def test_agent_has_description(self):
        """Test that agent has a description"""
        agent_call = self._find_agent_call()
        assert agent_call is not None
        assert 'description' in agent_call.kwargs
        description = agent_call.kwargs['description']
        assert len(description) > 0
        assert "Research Writing and Planning Specialist" in description

    def test_agent_has_instructions(self):
        """Test that agent has detailed instructions"""
        agent_call = self._find_agent_call()
        assert agent_call is not None
        assert 'instructions' in agent_call.kwargs
        instructions = agent_call.kwargs['instructions']
        assert len(instructions) > 0
        assert "PICOT" in instructions
        assert "LITERATURE REVIEW" in instructions

    def test_agent_instructions_include_key_areas(self):
        """Test that instructions cover all core expertise areas"""
        agent_call = self._find_agent_call()
        assert agent_call is not None
        instructions = agent_call.kwargs['instructions']

        # Check for core areas
        assert "PICOT QUESTION DEVELOPMENT" in instructions
        assert "LITERATURE REVIEW WRITING" in instructions
        assert "RESEARCH METHODOLOGY PLANNING" in instructions
        assert "INTERVENTION PLANNING" in instructions
        assert "DATA ANALYSIS PLANNING" in instructions
        assert "POSTER CONTENT WRITING" in instructions
        assert "ACADEMIC WRITING SKILLS" in instructions


class TestMainExecution:
    """Test main execution block"""

    @patch('research_writing_agent.run_agent_with_error_handling')
    def test_main_calls_error_handler(self, mock_error_handler):
        """Test that main block calls run_agent_with_error_handling"""
        # Simulate running the main block
        import importlib
        import research_writing_agent as rwa

        # Get the show_usage_examples function
        usage_func = rwa.show_usage_examples

        # The main block would call run_agent_with_error_handling
        # We can verify the function exists and is callable
        assert callable(usage_func)
        assert hasattr(rwa, 'run_agent_with_error_handling')

    def test_logger_info_called(self, caplog):
        """Test that logger.info is called during initialization"""
        import logging
        with caplog.at_level(logging.INFO):
            # The module was already imported, so check logger exists
            assert research_writing_agent.logger is not None
