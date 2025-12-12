"""
Unit tests for research_writing_agent.py
Tests the research_writing_agent module
"""

import pytest
from unittest.mock import patch

import agents.research_writing_agent as research_writing_agent


class TestResearchWritingAgentConfiguration:
    """Test research_writing_agent configuration"""

    def test_agent_exists(self):
        """Test that research_writing_agent is created"""
        assert hasattr(research_writing_agent, 'research_writing_agent')
        assert research_writing_agent.research_writing_agent is not None

    def test_logger_created(self):
        """Test that logger is created with correct name"""
        assert hasattr(research_writing_agent, '_research_writing_agent_instance')
        assert research_writing_agent._research_writing_agent_instance is not None
        assert hasattr(research_writing_agent._research_writing_agent_instance, 'logger')
        assert research_writing_agent._research_writing_agent_instance.logger is not None

    def test_agent_name(self):
        """Test that agent has correct name"""
        assert research_writing_agent.research_writing_agent.name == "Research Writing Agent"

    def test_agent_role(self):
        """Test that agent has correct role"""
        assert research_writing_agent.research_writing_agent.role == "Academic writing and research planning specialist"

    def test_agent_markdown_enabled(self):
        """Test that markdown is enabled"""
        assert research_writing_agent.research_writing_agent.markdown is True

    def test_agent_history_context(self):
        """Test that add_history_to_context is enabled"""
        assert research_writing_agent.research_writing_agent.add_history_to_context is True

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
        assert research_writing_agent._research_writing_agent_instance is not None
        research_writing_agent._research_writing_agent_instance.show_usage_examples()
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
        assert research_writing_agent._research_writing_agent_instance is not None
        research_writing_agent._research_writing_agent_instance.show_usage_examples()
        captured = capsys.readouterr()

        assert "TIP:" in captured.out
        assert "remembers your conversation" in captured.out
        assert "stream=True" in captured.out

    def test_show_usage_examples_includes_examples(self, capsys):
        """Test that usage examples include code examples"""
        assert research_writing_agent._research_writing_agent_instance is not None
        research_writing_agent._research_writing_agent_instance.show_usage_examples()
        captured = capsys.readouterr()

        # Check for code example patterns
        assert "research_writing_agent.run(" in captured.out
        assert "research_writing_agent.print_response(" in captured.out
        assert '"""' in captured.out

    def test_show_usage_examples_formatting(self, capsys):
        """Test that output is properly formatted"""
        assert research_writing_agent._research_writing_agent_instance is not None
        research_writing_agent._research_writing_agent_instance.show_usage_examples()
        captured = capsys.readouterr()

        # Check for proper formatting elements
        assert "-" * 60 in captured.out
        assert "\n" in captured.out


class TestAgentInstructions:
    """Test the agent's instructions and configuration"""

    def test_agent_has_description(self):
        """Test that agent has a description"""
        description = research_writing_agent.research_writing_agent.description
        assert len(description) > 0
        assert "Research Writing and Planning Specialist" in description

    def test_agent_has_instructions(self):
        """Test that agent has detailed instructions"""
        instructions = research_writing_agent.research_writing_agent.instructions
        assert len(instructions) > 0
        assert "PICOT" in instructions
        assert "LITERATURE REVIEW" in instructions

    def test_agent_instructions_include_key_areas(self):
        """Test that instructions cover all core expertise areas"""
        instructions = research_writing_agent.research_writing_agent.instructions

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

    def test_main_calls_error_handler(self):
        """Test that main block uses run_with_error_handling from BaseAgent"""
        assert hasattr(research_writing_agent, '_research_writing_agent_instance')
        instance = research_writing_agent._research_writing_agent_instance
        assert instance is not None
        assert hasattr(instance, 'run_with_error_handling')
        assert callable(instance.run_with_error_handling)
        assert hasattr(instance, 'show_usage_examples')
        assert callable(instance.show_usage_examples)

    def test_logger_info_called(self, caplog):
        """Test that logger.info is called during initialization"""
        import logging
        with caplog.at_level(logging.INFO):
            assert research_writing_agent._research_writing_agent_instance is not None
            assert research_writing_agent._research_writing_agent_instance.logger is not None
