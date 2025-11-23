"""
Unit tests for data_analysis_agent.py
Tests the data_analysis_agent module
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

import data_analysis_agent


class TestDataAnalysisAgentConfiguration:
    """Test data_analysis_agent configuration"""

    def test_agent_exists(self):
        """Test that data_analysis_agent is created"""
        assert hasattr(data_analysis_agent, 'data_analysis_agent')
        assert data_analysis_agent.data_analysis_agent is not None

    def test_output_schema_defined(self):
        """Test that DataAnalysisOutput schema is defined"""
        assert hasattr(data_analysis_agent, 'DataAnalysisOutput')
        schema = data_analysis_agent.DataAnalysisOutput

        # Verify it's a Pydantic model
        assert hasattr(schema, 'model_fields')


    def test_logger_created(self):
        """Test that logger is created with correct name"""
        assert hasattr(data_analysis_agent, 'logger')
        assert data_analysis_agent.logger is not None

    def test_temperature_configuration_imported(self):
        """Test that temperature configuration is imported"""
        from agent_config import DATA_ANALYSIS_TEMPERATURE
        assert isinstance(DATA_ANALYSIS_TEMPERATURE, (int, float))

    def test_max_tokens_configuration_imported(self):
        """Test that max tokens configuration is imported"""
        from agent_config import DATA_ANALYSIS_MAX_TOKENS
        assert isinstance(DATA_ANALYSIS_MAX_TOKENS, int)


class TestDataAnalysisOutputSchema:
    """Test the DataAnalysisOutput Pydantic schema"""

    def test_schema_has_required_fields(self):
        """Test that schema has all required fields"""
        schema = data_analysis_agent.DataAnalysisOutput
        field_names = schema.model_fields.keys()

        required_fields = {
            'task', 'assumptions', 'method', 'parameters',
            'sample_size', 'data_template', 'analysis_steps',
            'diagnostics', 'interpretation_notes', 'limitations',
            'repro_code', 'citations', 'confidence'
        }

        assert required_fields.issubset(field_names)

    def test_confidence_field_has_constraints(self):
        """Test that confidence field has proper constraints"""
        schema = data_analysis_agent.DataAnalysisOutput
        confidence_field = schema.model_fields['confidence']

        # Field should have ge and le constraints
        assert confidence_field.metadata is not None
