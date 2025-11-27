"""
Base Agent Utilities for Nursing Research Agents
Provides shared functionality, error handling, logging, and configuration
for all 6 nursing research agents.

Created: 2025-11-16 (Phase 2 - Architecture, Reuse & Streaming)
Updated: 2025-11-23 (Phase 2 Complete - BaseAgent class for inheritance pattern)

This module provides helper functions that can be used by all agents to reduce
code duplication while allowing each agent to maintain its unique characteristics.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List, Callable

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

from agent_config import LOG_LEVEL, LOG_FORMAT, get_db_path


def setup_agent_logging(agent_name: str) -> logging.Logger:
    """
    Setup logging for an agent with standard configuration.

    Args:
        agent_name: Name of the agent for the logger

    Returns:
        Configured logger instance
    """
    # Configure root logging if not already configured
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format=LOG_FORMAT
        )

    # Create and return logger for this agent
    logger = logging.getLogger(agent_name)
    return logger


def run_agent_with_error_handling(
    agent_name: str,
    logger: logging.Logger,
    setup_func: Callable[[], None]
) -> None:
    """
    Run an agent with comprehensive error handling.

    This wraps the agent's main execution in try/except blocks following
    the Phase 1 error handling pattern.

    Args:
        agent_name: Name of the agent
        logger: Logger instance for the agent
        setup_func: Function that sets up and displays the agent (usage examples, etc.)

    Example:
        def show_usage():
            print("Agent Ready!")
            print("Usage examples...")

        if __name__ == "__main__":
            logger = setup_agent_logging("My Agent")
            run_agent_with_error_handling("My Agent", logger, show_usage)
    """
    try:
        logger.info(f"Starting {agent_name}")

        # Run the setup function (shows usage examples, etc.)
        setup_func()

        logger.info(f"{agent_name} ready")

    except KeyboardInterrupt:
        logger.info("Agent interrupted by user")
        print("\n\nInterrupted by user. Goodbye!")

    except Exception as e:
        logger.error(f"Agent execution failed: {type(e).__name__}: {str(e)}", exc_info=True)
        print(f"\n❌ Error: An unexpected error occurred.")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nPlease check the logs for details or contact support.")
        raise  # Re-raise to preserve stack trace for debugging


class BaseAgent(ABC):
    """
    Base class for all nursing research agents.
    Provides common functionality for logging, error handling, and agent creation.

    Subclasses must implement:
    - _create_agent(): Create and return the Agent instance
    - show_usage_examples(): Display usage examples

    Optional to override:
    - _create_tools(): Create and return tools list (default returns empty list)
    """

    def __init__(self, agent_name: str, agent_key: str, tools: list = None):
        """
        Initialize the base agent.

        Args:
            agent_name: Display name for the agent
            agent_key: Key for database path (e.g., 'medical_research')
            tools: List of tools for the agent (can be None or empty)
        """
        self.agent_name = agent_name
        self.agent_key = agent_key
        self.tools = tools or []

        # Setup logging
        self.logger = setup_agent_logging(agent_name)

        # Create the agent
        self.agent = self._create_agent()

        # Log initialization
        db_path = get_db_path(agent_key)
        self.logger.info(f"{agent_name} initialized: {db_path}")

    @abstractmethod
    def _create_agent(self) -> Agent:
        """
        Create and return the Agent instance.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def show_usage_examples(self):
        """
        Display usage examples for the agent.
        Must be implemented by subclasses.
        """
        pass

    def run_with_error_handling(self):
        """Run the agent with comprehensive error handling."""
        run_agent_with_error_handling(
            self.agent_name,
            self.logger,
            self.show_usage_examples
        )


# Example usage (this won't run when imported)
if __name__ == "__main__":
    print("This is the base agent utilities module.")
    print("\nProvides helper functions for nursing research agents:")
    print("  - setup_agent_logging(): Setup logging with standard config")
    print("  - run_agent_with_error_handling(): Wrap agent execution with error handling")
    print("  - BaseAgent: Base class for agent inheritance pattern")
    print("\nExample:")
    print("  from agents.base_agent import BaseAgent")
    print("")
    print("  class MyAgent(BaseAgent):")
    print("      def __init__(self):")
    print("          super().__init__('My Agent', 'my_agent')")
    print("      ")
    print("      def _create_agent(self):")
    print("          return Agent(...)")
    print("      ")
    print("      def show_usage_examples(self):")
    print("          print('Agent Ready!')")
