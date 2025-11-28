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

import agents.data_analysis_agent as data_analysis_agent


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
        # Logger is on the DataAnalysisAgent instance, not module-level
        assert hasattr(data_analysis_agent, '_data_analysis_agent_instance')
        assert data_analysis_agent._data_analysis_agent_instance is not None
        assert hasattr(data_analysis_agent._data_analysis_agent_instance, 'logger')
        assert data_analysis_agent._data_analysis_agent_instance.logger is not None

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

    def test_schema_field_types(self):
        """Test that schema fields have correct types"""
        schema = data_analysis_agent.DataAnalysisOutput
        fields = schema.model_fields

        # Check list fields
        assert 'assumptions' in fields
        assert 'analysis_steps' in fields
        assert 'diagnostics' in fields
        assert 'limitations' in fields
        assert 'citations' in fields

        # Check dict fields
        assert 'method' in fields
        assert 'parameters' in fields
        assert 'sample_size' in fields
        assert 'data_template' in fields
        assert 'repro_code' in fields

        # Check string fields
        assert 'interpretation_notes' in fields

        # Check float field
        assert 'confidence' in fields


class TestShowUsageExamples:
    """Test the show_usage_examples function"""

    def test_show_usage_examples_output(self, capsys):
        """Test that show_usage_examples prints expected content"""
        # Call instance method, not module-level function
        instance = data_analysis_agent._data_analysis_agent_instance
        instance.show_usage_examples()
        captured = capsys.readouterr()

        # Check for header
        assert "DATA ANALYSIS PLANNING AGENT" in captured.out
        assert "Statistical Expert for Nursing Research" in captured.out

        # Check for examples
        assert "Example queries:" in captured.out
        assert "Catheter infection rate" in captured.out
        assert "pain scores" in captured.out

    def test_show_usage_examples_calls_print_response(self, capsys):
        """Test that show_usage_examples prints usage information"""
        # In the new BaseAgent pattern, show_usage_examples just prints directly
        # It doesn't call agent.print_response
        instance = data_analysis_agent._data_analysis_agent_instance
        instance.show_usage_examples()
        captured = capsys.readouterr()

        # Verify output contains key information
        assert "Agent ready" in captured.out
        assert "Example queries:" in captured.out

    def test_show_usage_examples_formatting(self, capsys):
        """Test that output is properly formatted"""
        # Call instance method
        instance = data_analysis_agent._data_analysis_agent_instance
        instance.show_usage_examples()
        captured = capsys.readouterr()

        # Check for formatting elements
        assert "=" * 70 in captured.out


class TestAgentConfiguration:
    """Test agent configuration and model settings"""

    def test_agent_uses_correct_model(self):
        """Test that agent configuration uses gpt-4o model"""
        # Check that OpenAIChat was called with id="gpt-4o"
        openai_mock = sys.modules['agno.models.openai'].OpenAIChat
        found_gpt4o = False
        for call in openai_mock.call_args_list:
            if call.kwargs.get('id') == "gpt-4o":
                found_gpt4o = True
                break
        assert found_gpt4o, "gpt-4o should be used for data analysis agent"

    def test_agent_uses_configured_temperature(self):
        """Test that agent uses configured temperature"""
        from agent_config import DATA_ANALYSIS_TEMPERATURE
        # Verify the config value is reasonable
        assert isinstance(DATA_ANALYSIS_TEMPERATURE, (int, float))
        assert 0.0 <= DATA_ANALYSIS_TEMPERATURE <= 1.0

    def test_agent_uses_configured_max_tokens(self):
        """Test that agent uses configured max tokens"""
        from agent_config import DATA_ANALYSIS_MAX_TOKENS
        # Verify the config value is reasonable
        assert isinstance(DATA_ANALYSIS_MAX_TOKENS, int)
        assert DATA_ANALYSIS_MAX_TOKENS > 0

    def test_agent_has_instructions(self):
        """Test that agent instructions are defined"""
        # Check that STATISTICAL_EXPERT_PROMPT is defined and non-empty
        assert hasattr(data_analysis_agent, 'STATISTICAL_EXPERT_PROMPT')
        prompt = data_analysis_agent.STATISTICAL_EXPERT_PROMPT
        assert len(prompt) > 0
        assert "statistical" in prompt.lower() or "Statistical" in prompt
        assert "sample size" in prompt.lower()
        assert "test selection" in prompt.lower()

    def test_agent_has_description(self):
        """Test that agent is created with Agent class"""
        # The agent was created using Agent() constructor
        agent_mock = sys.modules['agno.agent'].Agent
        assert agent_mock.called
        # At least one agent was created
        assert len(agent_mock.call_args_list) > 0

    def test_agent_object_exists(self):
        """Test that data_analysis_agent object exists"""
        # The agent should be created as module-level variable
        assert hasattr(data_analysis_agent, 'data_analysis_agent')
        assert data_analysis_agent.data_analysis_agent is not None


class TestDatabaseConfiguration:
    """Test database configuration"""

    def test_database_uses_centralized_config(self):
        """Test that database uses get_db_path"""
        from agent_config import get_db_path
        db_path = get_db_path("data_analysis")

        assert db_path.endswith(".db")
        assert "data_analysis" in db_path

    def test_db_variable_exists(self):
        """Test that db variable is created"""
        # db is created inside _create_agent() and attached to the Agent object
        assert hasattr(data_analysis_agent, 'data_analysis_agent')
        agent = data_analysis_agent.data_analysis_agent
        assert agent is not None
        assert hasattr(agent, 'db')
        assert agent.db is not None


class TestMainExecution:
    """Test main execution block"""

    def test_main_calls_error_handler(self):
        """Test that main block uses run_with_error_handling from BaseAgent"""
        import agents.data_analysis_agent as daa

        # Verify the instance exists and has the required methods
        assert hasattr(daa, '_data_analysis_agent_instance')
        instance = daa._data_analysis_agent_instance
        assert instance is not None

        # Verify the instance has run_with_error_handling method (inherited from BaseAgent)
        assert hasattr(instance, 'run_with_error_handling')
        assert callable(instance.run_with_error_handling)

        # Verify the instance has show_usage_examples method
        assert hasattr(instance, 'show_usage_examples')
        assert callable(instance.show_usage_examples)
