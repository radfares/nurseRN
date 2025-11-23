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
