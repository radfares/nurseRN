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

        # Check nested Pydantic model fields (replaced dict[str, Any])
        assert 'method' in fields
        assert 'parameters' in fields
        assert 'sample_size' in fields
        assert 'data_template' in fields
        assert 'repro_code' in fields

        # Check string fields
        assert 'interpretation_notes' in fields

        # Check float field
        assert 'confidence' in fields

    def test_nested_models_exist(self):
        """Test that nested Pydantic models are defined"""
        # Verify all nested models exist
        assert hasattr(data_analysis_agent, 'EffectSize')
        assert hasattr(data_analysis_agent, 'MethodInfo')
        assert hasattr(data_analysis_agent, 'Parameters')
        assert hasattr(data_analysis_agent, 'SampleSize')
        assert hasattr(data_analysis_agent, 'DataColumn')
        assert hasattr(data_analysis_agent, 'DataTemplate')
        assert hasattr(data_analysis_agent, 'ReproCode')

        # Verify they are Pydantic models
        from pydantic import BaseModel
        assert issubclass(data_analysis_agent.EffectSize, BaseModel)
        assert issubclass(data_analysis_agent.MethodInfo, BaseModel)
        assert issubclass(data_analysis_agent.Parameters, BaseModel)
        assert issubclass(data_analysis_agent.SampleSize, BaseModel)
        assert issubclass(data_analysis_agent.DataColumn, BaseModel)
        assert issubclass(data_analysis_agent.DataTemplate, BaseModel)
        assert issubclass(data_analysis_agent.ReproCode, BaseModel)

    def test_schema_uses_nested_models(self):
        """Test that DataAnalysisOutput uses nested models instead of dict[str, Any]"""
        schema = data_analysis_agent.DataAnalysisOutput
        fields = schema.model_fields

        # Verify method field is MethodInfo, not dict
        method_field = fields['method']
        assert hasattr(method_field, 'annotation')
        # Check that annotation is MethodInfo (not dict)
        assert method_field.annotation != dict
        assert method_field.annotation == data_analysis_agent.MethodInfo

        # Verify parameters field is Parameters, not dict
        parameters_field = fields['parameters']
        assert parameters_field.annotation == data_analysis_agent.Parameters

        # Verify sample_size field is SampleSize, not dict
        sample_size_field = fields['sample_size']
        assert sample_size_field.annotation == data_analysis_agent.SampleSize

        # Verify data_template field is DataTemplate, not dict
        data_template_field = fields['data_template']
        assert data_template_field.annotation == data_analysis_agent.DataTemplate

        # Verify repro_code field is ReproCode, not dict
        repro_code_field = fields['repro_code']
        assert repro_code_field.annotation == data_analysis_agent.ReproCode

    def test_nested_model_validation(self):
        """Test that nested models can be instantiated and validated"""
        # Test EffectSize
        effect_size = data_analysis_agent.EffectSize(
            type="Cohen_d",
            value=0.5,
            how_estimated="literature"
        )
        assert effect_size.type == "Cohen_d"
        assert effect_size.value == 0.5

        # Test MethodInfo
        method = data_analysis_agent.MethodInfo(
            name="Welch t-test",
            justification="Robust to unequal variances",
            alternatives=["Mann-Whitney U"]
        )
        assert method.name == "Welch t-test"
        assert len(method.alternatives) == 1

        # Test Parameters
        params = data_analysis_agent.Parameters(
            effect_size=effect_size,
            design="parallel"
        )
        assert params.design == "parallel"
        assert params.alpha == 0.05  # Default value
        assert params.tails == "two"  # Default value

        # Test SampleSize
        sample_size = data_analysis_agent.SampleSize(
            per_group=30,
            total=60,
            formula_or_reference="G*Power"
        )
        assert sample_size.per_group == 30

        # Test DataColumn
        column = data_analysis_agent.DataColumn(
            name="participant_id",
            type="string"
        )
        assert column.name == "participant_id"

        # Test DataTemplate
        template = data_analysis_agent.DataTemplate(
            columns=[column],
            id_key="participant_id",
            long_vs_wide="long"
        )
        assert len(template.columns) == 1
        assert template.file_format == "CSV"  # Default value

        # Test ReproCode
        repro_code = data_analysis_agent.ReproCode(
            language="R",
            snippet="t.test(...)"
        )
        assert repro_code.language == "R"

    def test_full_schema_validation(self):
        """Test that DataAnalysisOutput can be instantiated with nested models"""
        # Create nested model instances
        effect_size = data_analysis_agent.EffectSize(
            type="Cohen_d",
            value=0.5,
            how_estimated="literature"
        )
        method = data_analysis_agent.MethodInfo(
            name="Welch t-test",
            justification="Robust to unequal variances"
        )
        params = data_analysis_agent.Parameters(
            effect_size=effect_size,
            design="parallel"
        )
        sample_size = data_analysis_agent.SampleSize(
            formula_or_reference="G*Power"
        )
        column = data_analysis_agent.DataColumn(
            name="participant_id",
            type="string"
        )
        data_template = data_analysis_agent.DataTemplate(
            columns=[column],
            id_key="participant_id",
            long_vs_wide="long"
        )
        repro_code = data_analysis_agent.ReproCode(
            language="R",
            snippet="t.test(...)"
        )

        # Create full DataAnalysisOutput instance
        output = data_analysis_agent.DataAnalysisOutput(
            task="test_selection",
            assumptions=["independent samples"],
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=["step 1"],
            diagnostics=["normality check"],
            interpretation_notes="Test interpretation",
            limitations=["small sample"],
            repro_code=repro_code,
            citations=["Cohen 1988"],
            confidence=0.85
        )

        # Verify the nested models are properly assigned
        assert isinstance(output.method, data_analysis_agent.MethodInfo)
        assert isinstance(output.parameters, data_analysis_agent.Parameters)
        assert isinstance(output.sample_size, data_analysis_agent.SampleSize)
        assert isinstance(output.data_template, data_analysis_agent.DataTemplate)
        assert isinstance(output.repro_code, data_analysis_agent.ReproCode)
        assert output.confidence == 0.85


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
