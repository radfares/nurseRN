"""
Unit tests for base_agent.py
Tests shared functionality, error handling, and BaseAgent class
"""

import pytest
import logging
import sys
from unittest.mock import Mock, MagicMock, patch, call
from abc import ABC

# Mock agno modules before importing base_agent
sys.modules['agno'] = MagicMock()
sys.modules['agno.agent'] = MagicMock()
sys.modules['agno.db'] = MagicMock()
sys.modules['agno.db.sqlite'] = MagicMock()
sys.modules['agno.models'] = MagicMock()
sys.modules['agno.models.openai'] = MagicMock()

from base_agent import (
    setup_agent_logging,
    run_agent_with_error_handling,
    BaseAgent
)


class TestSetupAgentLogging:
    """Test the setup_agent_logging function"""

    def test_returns_logger_instance(self):
        """Test that setup_agent_logging returns a logger"""
        logger = setup_agent_logging("test_agent")
        assert isinstance(logger, logging.Logger)

    def test_logger_has_correct_name(self):
        """Test that logger has the correct name"""
        logger = setup_agent_logging("my_special_agent")
        assert logger.name == "my_special_agent"

    def test_multiple_calls_return_same_logger(self):
        """Test that calling with same name returns same logger instance"""
        logger1 = setup_agent_logging("test_agent")
        logger2 = setup_agent_logging("test_agent")
        assert logger1 is logger2

    def test_different_names_return_different_loggers(self):
        """Test that different agent names get different loggers"""
        logger1 = setup_agent_logging("agent_1")
        logger2 = setup_agent_logging("agent_2")
        assert logger1 is not logger2
        assert logger1.name == "agent_1"
        assert logger2.name == "agent_2"

    @patch('base_agent.logging.getLogger')
    def test_configures_root_logging_if_no_handlers(self, mock_get_logger):
        """Test that root logging is configured when no handlers exist"""
        mock_root = Mock()
        mock_root.hasHandlers.return_value = False
        mock_get_logger.return_value = mock_root

        with patch('base_agent.logging.basicConfig') as mock_config:
            setup_agent_logging("test")
            mock_config.assert_called_once()

    @patch('base_agent.logging.getLogger')
    def test_skips_config_if_handlers_exist(self, mock_get_logger):
        """Test that root logging config is skipped if handlers already exist"""
        mock_root = Mock()
        mock_root.hasHandlers.return_value = True
        mock_get_logger.return_value = mock_root

        with patch('base_agent.logging.basicConfig') as mock_config:
            setup_agent_logging("test")
            mock_config.assert_not_called()


class TestRunAgentWithErrorHandling:
    """Test the run_agent_with_error_handling function"""

    def test_successful_execution(self, caplog):
        """Test successful agent execution"""
        logger = logging.getLogger("test_agent")
        setup_func = Mock()

        with caplog.at_level(logging.INFO):
            run_agent_with_error_handling("test_agent", logger, setup_func)

        # Verify setup function was called
        setup_func.assert_called_once()

        # Verify logging messages
        assert "Starting test_agent" in caplog.text
        assert "test_agent ready" in caplog.text

    def test_keyboard_interrupt_handling(self, caplog, capsys):
        """Test that KeyboardInterrupt is handled gracefully"""
        logger = logging.getLogger("test_agent")
        setup_func = Mock(side_effect=KeyboardInterrupt())

        with caplog.at_level(logging.INFO):
            run_agent_with_error_handling("test_agent", logger, setup_func)

        # Verify logging
        assert "Agent interrupted by user" in caplog.text

        # Verify user message
        captured = capsys.readouterr()
        assert "Interrupted by user" in captured.out

    def test_exception_handling_and_reraise(self, caplog, capsys):
        """Test that exceptions are logged and re-raised"""
        logger = logging.getLogger("test_agent")
        test_error = ValueError("Test error message")
        setup_func = Mock(side_effect=test_error)

        with pytest.raises(ValueError, match="Test error message"):
            run_agent_with_error_handling("test_agent", logger, setup_func)

        # Verify error logging
        assert "Agent execution failed" in caplog.text
        assert "ValueError" in caplog.text

        # Verify user-friendly error message
        captured = capsys.readouterr()
        assert "Error type: ValueError" in captured.out
        assert "Test error message" in captured.out

    def test_custom_exception_handling(self, caplog):
        """Test handling of custom exceptions"""
        logger = logging.getLogger("test_agent")

        class CustomError(Exception):
            pass

        setup_func = Mock(side_effect=CustomError("Custom error"))

        with pytest.raises(CustomError):
            run_agent_with_error_handling("test_agent", logger, setup_func)

        assert "CustomError" in caplog.text


class TestBaseAgent:
    """Test the BaseAgent abstract class"""

    @pytest.fixture
    def concrete_agent_class(self):
        """Create a concrete implementation of BaseAgent for testing"""
        class ConcreteAgent(BaseAgent):
            def _create_agent(self):
                """Mock implementation"""
                mock_agent = Mock()
                mock_agent.name = "Concrete Test Agent"
                return mock_agent

            def show_usage_examples(self):
                """Mock implementation"""
                print("Usage: concrete_agent.run()")

        return ConcreteAgent

    def test_base_agent_is_abstract(self):
        """Test that BaseAgent cannot be instantiated directly"""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            BaseAgent("Test", "test_key")

    def test_concrete_agent_initialization(self, concrete_agent_class):
        """Test that concrete agent can be initialized"""
        agent = concrete_agent_class("Test Agent", "nursing_research")

        assert agent.agent_name == "Test Agent"
        assert agent.agent_key == "nursing_research"
        assert agent.tools == []
        assert hasattr(agent, 'logger')
        assert hasattr(agent, 'agent')

    def test_initialization_with_tools(self, concrete_agent_class):
        """Test initialization with custom tools list"""
        tools = [Mock(), Mock()]
        agent = concrete_agent_class("Test Agent", "nursing_research", tools=tools)

        assert agent.tools == tools
        assert len(agent.tools) == 2

    def test_initialization_with_none_tools(self, concrete_agent_class):
        """Test that None tools defaults to empty list"""
        agent = concrete_agent_class("Test Agent", "nursing_research", tools=None)
        assert agent.tools == []

    def test_logger_created_with_agent_name(self, concrete_agent_class):
        """Test that logger uses the agent name"""
        agent = concrete_agent_class("Special Agent", "nursing_research")
        assert agent.logger.name == "Special Agent"

    def test_create_agent_called_during_init(self, concrete_agent_class):
        """Test that _create_agent is called during initialization"""
        with patch.object(concrete_agent_class, '_create_agent',
                         return_value=Mock()) as mock_create:
            agent = concrete_agent_class("Test Agent", "nursing_research")
            mock_create.assert_called_once()

    def test_logging_during_initialization(self, concrete_agent_class, caplog):
        """Test that initialization logs database path"""
        with caplog.at_level(logging.INFO):
            agent = concrete_agent_class("Test Agent", "nursing_research")

        # Check that initialization was logged
        assert "Test Agent initialized" in caplog.text
        assert "nursing_research" in caplog.text or ".db" in caplog.text

    def test_invalid_agent_key_raises_error(self, concrete_agent_class):
        """Test that invalid agent_key raises ValueError from get_db_path"""
        with pytest.raises(ValueError, match="Unknown agent"):
            agent = concrete_agent_class("Test Agent", "invalid_agent_key")

    def test_run_with_error_handling_method(self, concrete_agent_class, capsys):
        """Test that run_with_error_handling method works"""
        agent = concrete_agent_class("Test Agent", "nursing_research")

        # This should execute without errors
        agent.run_with_error_handling()

        # Verify usage examples were printed
        captured = capsys.readouterr()
        assert "Usage:" in captured.out

    def test_run_with_error_handling_catches_exceptions(self, concrete_agent_class):
        """Test that run_with_error_handling catches exceptions from show_usage_examples"""
        class FailingAgent(BaseAgent):
            def _create_agent(self):
                return Mock()

            def show_usage_examples(self):
                raise RuntimeError("Usage examples failed")

        agent = FailingAgent("Failing Agent", "nursing_research")

        with pytest.raises(RuntimeError, match="Usage examples failed"):
            agent.run_with_error_handling()

    def test_multiple_agents_independent(self, concrete_agent_class):
        """Test that multiple agent instances are independent"""
        agent1 = concrete_agent_class("Agent 1", "nursing_research")
        agent2 = concrete_agent_class("Agent 2", "medical_research")

        assert agent1.agent_name != agent2.agent_name
        assert agent1.agent_key != agent2.agent_key
        assert agent1.logger.name != agent2.logger.name
        assert agent1.agent is not agent2.agent


class TestBaseAgentAbstractMethods:
    """Test that abstract methods must be implemented"""

    def test_missing_create_agent_raises_error(self):
        """Test that missing _create_agent implementation raises TypeError"""
        class IncompleteAgent(BaseAgent):
            def show_usage_examples(self):
                pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            agent = IncompleteAgent("Incomplete", "nursing_research")

    def test_missing_show_usage_examples_raises_error(self):
        """Test that missing show_usage_examples implementation raises TypeError"""
        class IncompleteAgent(BaseAgent):
            def _create_agent(self):
                return Mock()

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            agent = IncompleteAgent("Incomplete", "nursing_research")

    def test_both_methods_must_be_implemented(self):
        """Test that both abstract methods must be implemented"""
        class NoMethods(BaseAgent):
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            agent = NoMethods("No Methods", "nursing_research")


class TestBaseAgentIntegration:
    """Integration tests for BaseAgent with real logging"""

    def test_full_agent_lifecycle(self, capsys, caplog):
        """Test complete agent lifecycle from init to execution"""
        class LifecycleAgent(BaseAgent):
            def _create_agent(self):
                mock = Mock()
                mock.name = "Lifecycle Test Agent"
                return mock

            def show_usage_examples(self):
                print("Agent is ready!")
                print("Try: agent.agent.run('test query')")

        with caplog.at_level(logging.INFO):
            # Initialize
            agent = LifecycleAgent("Lifecycle Agent", "nursing_research")

            # Verify initialization
            assert agent.agent_name == "Lifecycle Agent"
            assert "Lifecycle Agent initialized" in caplog.text

            # Run with error handling
            agent.run_with_error_handling()

            # Verify execution
            captured = capsys.readouterr()
            assert "Agent is ready!" in captured.out
            assert "Lifecycle Agent ready" in caplog.text

    def test_agent_with_actual_tools(self):
        """Test agent initialization with actual tool objects"""
        mock_tool1 = Mock()
        mock_tool1.name = "Tool1"  # Set attribute directly, not as a Mock
        mock_tool2 = Mock()
        mock_tool2.name = "Tool2"
        tools = [mock_tool1, mock_tool2]

        class ToolAgent(BaseAgent):
            def _create_agent(self):
                # Agent would use self.tools here
                return Mock(tools=self.tools)

            def show_usage_examples(self):
                print(f"Agent has {len(self.tools)} tools")

        agent = ToolAgent("Tool Agent", "nursing_research", tools=tools)

        assert len(agent.tools) == 2
        assert agent.tools[0].name == "Tool1"
        assert agent.tools[1].name == "Tool2"
