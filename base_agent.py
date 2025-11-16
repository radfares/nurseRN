"""
Base Agent Utilities for Nursing Research Agents
Provides shared functionality, error handling, logging, and configuration
for all 6 nursing research agents.

Created: 2025-11-16 (Phase 2 - Architecture, Reuse & Streaming)

This module provides helper functions that can be used by all agents to reduce
code duplication while allowing each agent to maintain its unique characteristics.
"""

import logging
import os
from typing import Optional, Any, Dict, List, Callable
from textwrap import dedent

from agent_config import LOG_LEVEL, LOG_FORMAT


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


# Example usage (this won't run when imported)
if __name__ == "__main__":
    print("This is the base agent utilities module.")
    print("\nProvides helper functions for nursing research agents:")
    print("  - setup_agent_logging(): Setup logging with standard config")
    print("  - run_agent_with_error_handling(): Wrap agent execution with error handling")
    print("\nExample:")
    print("  from base_agent import setup_agent_logging, run_agent_with_error_handling")
    print("")
    print("  logger = setup_agent_logging('My Agent')")
    print("  ")
    print("  def show_usage():")
    print("      print('Agent Ready!')")
    print("  ")
    print("  if __name__ == '__main__':")
    print("      run_agent_with_error_handling('My Agent', logger, show_usage)")
