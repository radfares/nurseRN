"""
Base Agent Utilities for Nursing Research Agents
Provides shared functionality, error handling, logging, and configuration
for all 6 nursing research agents.

Created: 2025-11-16 (Phase 2 - Architecture, Reuse & Streaming)
Updated: 2025-11-23 (Phase 2 Complete - BaseAgent class for inheritance pattern)
Updated: 2025-11-30 (Audit Logging Hook - All agents track actions)

This module provides helper functions that can be used by all agents to reduce
code duplication while allowing each agent to maintain its unique characteristics.

AUDIT LOGGING (2025-11-30):
Every BaseAgent subclass automatically supports audit logging via the
get_audit_logger() system in src/services/agent_audit_logger.py.
Each agent maintains an immutable JSONL audit trail in .claude/agent_audit_logs/
"""

import logging
import os
import traceback
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.openai import OpenAIChat

from agent_config import LOG_FORMAT, LOG_LEVEL, get_db_path


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
        logging.basicConfig(level=getattr(logging, LOG_LEVEL), format=LOG_FORMAT)

    # Create and return logger for this agent
    logger = logging.getLogger(agent_name)
    return logger


def run_agent_with_error_handling(
    agent_name: str, logger: logging.Logger, setup_func: Callable[[], None]
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
        logger.error(
            f"Agent execution failed: {type(e).__name__}: {str(e)}", exc_info=True
        )
        print(f"\n❌ Error: An unexpected error occurred.")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nPlease check the logs for details or contact support.")
        raise  # Re-raise to preserve stack trace for debugging


class BaseAgent(ABC):
    """
    Base class for all nursing research agents.
    Provides common functionality for logging, error handling, agent creation, and audit logging.

    AUDIT LOGGING (2025-11-30):
    All subclasses automatically support audit logging. Each agent maintains an
    immutable JSONL audit trail that records every action:
    - Query received
    - Tool calls and results
    - Validation checks
    - Responses generated
    - Errors encountered

    Subclasses must implement:
    - _create_agent(): Create and return the Agent instance
    - show_usage_examples(): Display usage examples

    Optional to override:
    - _create_tools(): Create and return tools list (default returns empty list)

    Example with audit logging:
        class MyAgent(BaseAgent):
            def __init__(self):
                super().__init__("My Agent", "my_agent", tools=[...])
                # Audit logger automatically available
                self.audit_logger = get_audit_logger("my_agent", "My Agent Name")

            def some_method(self):
                self.audit_logger.log_query_received("user query")
                # ... do work ...
                self.audit_logger.log_response_generated("response")
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
        self.audit_logger = None  # Will be set by subclass if needed

        # Setup logging
        self.logger = setup_agent_logging(agent_name)

        # Create the agent
        self.agent = self._create_agent()

        # Log initialization
        db_path = get_db_path(agent_key)
        self.logger.info(f"{agent_name} initialized: {db_path}")
        
        # Initialize Audit Logger
        # Phase 2 (2025-11-30): All agents must have audit logging
        from src.services.agent_audit_logger import get_audit_logger
        self.audit_logger = get_audit_logger(agent_key, agent_name)
        
        self.logger.info(
            f"Audit logging initialized: {self.audit_logger.log_file}"
        )

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
            self.agent_name, self.logger, self.show_usage_examples
        )

    def _audit_pre_hook(self, message: Any, **kwargs) -> None:
        """Pre-hook to log query reception."""
        if self.audit_logger:
            # Extract query text
            query = str(message)
            if hasattr(message, "content"):
                query = message.content
            
            # Try to get project name from kwargs or context
            project_name = kwargs.get("project_name")
            
            self.audit_logger.log_query_received(query, project_name)

    def _audit_post_hook(self, run_output: Any, **kwargs) -> None:
        """Post-hook to log response and run validation."""
        # 1. Run validation
        validation_passed = self._validate_run_output(run_output)
        
        # 2. Log response
        if self.audit_logger:
            content = str(run_output.content)
            self.audit_logger.log_response_generated(
                response=content,
                response_type="success",
                validation_passed=validation_passed
            )

    def _validate_run_output(self, run_output: Any) -> bool:
        """
        Validate the agent's output.
        Subclasses should override this to implement specific validation logic.
        """
        return True

    def extract_verified_items_from_output(
        self,
        run_output: Any,
        item_pattern: str,
        item_type: str = "item",
    ) -> set:
        """
        Generic method to extract verified items from RunOutput messages.

        This is a utility method that subclasses can use for validation.
        Works with any item type (PMIDs, DOIs, URLs, etc.).

        Args:
            run_output: The RunOutput object returned by agent.run()
            item_pattern: Regex pattern to extract items
            item_type: Description of item type (for logging)

        Returns:
            Set of verified items extracted from tool results

        Example:
            verified_pmids = self.extract_verified_items_from_output(
                run_output,
                r"PMID:\s*(\d+)",
                "PMID"
            )
        """
        import re

        verified_items = set()

        try:
            if not hasattr(run_output, "messages") or not run_output.messages:
                if self.audit_logger:
                    self.audit_logger.log_error(
                        error_type="MissingMessages",
                        error_message=f"RunOutput has no messages field",
                        stack_trace="",
                    )
                return verified_items

            # Iterate through all messages looking for items
            for message in run_output.messages:
                message_str = str(message)
                items = re.findall(item_pattern, message_str, re.IGNORECASE)
                verified_items.update(items)

        except Exception as e:
            if self.audit_logger:
                self.audit_logger.log_error(
                    error_type="ItemExtractionError",
                    error_message=f"Failed to extract {item_type}s from output: {str(e)}",
                    stack_trace=traceback.format_exc(),
                )

        return verified_items

    def print_response(self, query: str, project_name: Optional[str] = None, stream: bool = False) -> None:
        """
        Generic print_response method that can be used by all agents.
        This method provides a standard interface for the UI to call agents.

        Subclasses can override this method for custom behavior.

        Args:
            query: User's query
            project_name: Associated project for context
            stream: Whether to stream the response (not fully implemented yet)
        """
        try:
            # Try to call a custom method if the agent has one
            if hasattr(self, 'run_with_grounding_check'):
                result = self.run_with_grounding_check(query, project_name=project_name)
                content = result.get("content") if isinstance(result, dict) else str(result)
            elif hasattr(self, 'run'):
                # For agents that have a direct run method
                result = self.run(query)
                content = str(result)
            else:
                # Fallback to agent.run if available
                if hasattr(self.agent, 'run'):
                    result = self.agent.run(query)
                    content = str(result)
                else:
                    content = "❌ Agent does not have a run method available"

            print(content)

        except Exception as e:
            # Fail safely for the UI
            print(f"❌ Agent error: {type(e).__name__}: {e}")

    @staticmethod
    def print_watermark():
        """
        Print clinical disclaimer watermark after agent responses.

        Phase 1, Task 5 (2025-11-29) - Liability protection.
        This should be called after EVERY agent response to remind users
        that outputs must be reviewed by clinical experts.

        Usage:
            agent.print_response(query, stream=True)
            BaseAgent.print_watermark()  # Call after response
        """
        print("\n" + "─" * 80)
        print("⚠️  IMPORTANT: Review all outputs with clinical experts before use")
        print("   This tool provides planning guidance, not clinical recommendations")
        print("   See startup disclaimer for full terms and conditions")
        print("─" * 80)


# Example usage (this won't run when imported)
if __name__ == "__main__":
    print("This is the base agent utilities module.")
    print("\nProvides helper functions for nursing research agents:")
    print("  - setup_agent_logging(): Setup logging with standard config")
    print(
        "  - run_agent_with_error_handling(): Wrap agent execution with error handling"
    )
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
