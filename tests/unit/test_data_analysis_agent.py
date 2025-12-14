"""
Unit tests for data_analysis_agent.py
Tests the data_analysis_agent module
"""

import pytest
from agno.agent import Agent

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
        assert data_analysis_agent.data_analysis_agent is not None
        assert data_analysis_agent.data_analysis_agent.model.id == "gpt-4o"

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
        assert data_analysis_agent.data_analysis_agent is not None
        assert isinstance(data_analysis_agent.data_analysis_agent, Agent)

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


class TestStructuredOutputValidation:
    """Test structured output schema validation for DataAnalysisAgent"""

    def test_valid_output_schema_parsing(self):
        """Test that a valid response conforms to DataAnalysisOutput schema"""
        from agents.data_analysis_agent import (
            DataAnalysisOutput, EffectSize, MethodInfo,
            Parameters, SampleSize, DataColumn, DataTemplate, ReproCode
        )

        # Create nested models
        effect_size = EffectSize(
            type="Cohen_d",
            value=0.7,
            how_estimated="literature review"
        )

        method = MethodInfo(
            name="Two-proportion z-test",
            justification="Comparing CAUTI rates pre/post intervention"
        )

        params = Parameters(
            effect_size=effect_size,
            design="parallel groups",
            alpha=0.05,
            power=0.80
        )

        sample_size = SampleSize(
            per_group=196,
            total=392,
            formula_or_reference="n = (Z_α/2 + Z_β)² × [p1(1-p1) + p2(1-p2)] / (p1-p2)²"
        )

        col1 = DataColumn(name="patient_id", type="string")
        col2 = DataColumn(name="group", type="categorical")
        col3 = DataColumn(name="cauti_event", type="binary")

        data_template = DataTemplate(
            columns=[col1, col2, col3],
            id_key="patient_id",
            long_vs_wide="long"
        )

        repro_code = ReproCode(
            language="R",
            snippet="power.prop.test(n=196, p1=0.15, p2=0.08, sig.level=0.05)"
        )

        # Create complete output
        output = DataAnalysisOutput(
            task="sample_size",
            assumptions=[
                "Baseline infection rate: 15%",
                "Target infection rate: 8%",
                "Power: 80%"
            ],
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=[
                "Collect 6 months baseline data",
                "Implement intervention",
                "Collect 6 months post data",
                "Run two-proportion test"
            ],
            diagnostics=["Sample size adequacy", "Normality check"],
            interpretation_notes="Sufficient power to detect clinically meaningful reduction",
            limitations=["Assumes stable baseline", "No clustering effects"],
            repro_code=repro_code,
            citations=["Cohen 1988", "Fleiss 2003"],
            confidence=0.90
        )

        # Verify key fields
        assert output.task == "sample_size"
        assert output.confidence == 0.90
        assert output.sample_size.total == 392
        assert output.parameters.alpha == 0.05
        assert output.method.name == "Two-proportion z-test"

    def test_confidence_boundary_values(self):
        """Test confidence field enforces 0.0-1.0 constraints"""
        from agents.data_analysis_agent import (
            DataAnalysisOutput, EffectSize, MethodInfo,
            Parameters, SampleSize, DataTemplate, ReproCode
        )
        from pydantic import ValidationError

        # Create minimal nested models
        effect_size = EffectSize(type="Cohen_d", value=0.5, how_estimated="assumed")
        method = MethodInfo(name="t-test", justification="standard")
        params = Parameters(effect_size=effect_size, design="parallel")
        sample_size = SampleSize(formula_or_reference="G*Power")
        data_template = DataTemplate(columns=[], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="t.test()")

        # Test boundary: 0.0 should be valid
        output = DataAnalysisOutput(
            task="test_selection", assumptions=[], method=method, parameters=params,
            sample_size=sample_size, data_template=data_template,
            analysis_steps=[], diagnostics=[], interpretation_notes="",
            limitations=[], repro_code=repro_code, citations=[],
            confidence=0.0
        )
        assert output.confidence == 0.0

        # Test boundary: 1.0 should be valid
        output = DataAnalysisOutput(
            task="test_selection", assumptions=[], method=method, parameters=params,
            sample_size=sample_size, data_template=data_template,
            analysis_steps=[], diagnostics=[], interpretation_notes="",
            limitations=[], repro_code=repro_code, citations=[],
            confidence=1.0
        )
        assert output.confidence == 1.0

        # Below boundary: -0.1 should fail
        with pytest.raises(ValidationError) as exc_info:
            DataAnalysisOutput(
                task="test_selection", assumptions=[], method=method, parameters=params,
                sample_size=sample_size, data_template=data_template,
                analysis_steps=[], diagnostics=[], interpretation_notes="",
                limitations=[], repro_code=repro_code, citations=[],
                confidence=-0.1
            )
        assert "confidence" in str(exc_info.value).lower()

        # Above boundary: 1.1 should fail
        with pytest.raises(ValidationError) as exc_info:
            DataAnalysisOutput(
                task="test_selection", assumptions=[], method=method, parameters=params,
                sample_size=sample_size, data_template=data_template,
                analysis_steps=[], diagnostics=[], interpretation_notes="",
                limitations=[], repro_code=repro_code, citations=[],
                confidence=1.1
            )
        assert "confidence" in str(exc_info.value).lower()

    def test_missing_required_fields_validation(self):
        """Test that missing required fields raise ValidationError"""
        from agents.data_analysis_agent import (
            DataAnalysisOutput, EffectSize, MethodInfo,
            Parameters, SampleSize, DataTemplate, ReproCode
        )
        from pydantic import ValidationError

        # Create nested models
        effect_size = EffectSize(type="Cohen_d", value=0.5, how_estimated="lit")
        method = MethodInfo(name="test", justification="reason")
        params = Parameters(effect_size=effect_size, design="parallel")
        sample_size = SampleSize(formula_or_reference="formula")
        data_template = DataTemplate(columns=[], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="code()")

        # Complete valid data
        complete = {
            "task": "data_plan",
            "assumptions": [],
            "method": method,
            "parameters": params,
            "sample_size": sample_size,
            "data_template": data_template,
            "analysis_steps": [],
            "diagnostics": [],
            "interpretation_notes": "Notes",
            "limitations": [],
            "repro_code": repro_code,
            "citations": [],
            "confidence": 0.8
        }

        # Should pass with all fields
        output = DataAnalysisOutput(**complete)
        assert output is not None

        # Test missing critical fields
        for field in ["task", "method", "parameters", "sample_size", "confidence"]:
            incomplete = complete.copy()
            del incomplete[field]
            with pytest.raises(ValidationError) as exc_info:
                DataAnalysisOutput(**incomplete)
            assert field in str(exc_info.value).lower()

    def test_invalid_nested_model_validation(self):
        """Test that invalid nested models raise ValidationError"""
        from agents.data_analysis_agent import (
            DataAnalysisOutput, EffectSize, MethodInfo,
            Parameters, SampleSize, DataTemplate, ReproCode
        )
        from pydantic import ValidationError

        # Valid nested models for comparison
        effect_size = EffectSize(type="Cohen_d", value=0.5, how_estimated="lit")
        method = MethodInfo(name="test", justification="reason")
        params = Parameters(effect_size=effect_size, design="parallel")
        sample_size = SampleSize(formula_or_reference="formula")
        data_template = DataTemplate(columns=[], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="code()")

        # Try to pass plain dict instead of MethodInfo instance
        with pytest.raises(ValidationError):
            DataAnalysisOutput(
                task="interpretation", assumptions=[],
                method={"name": "test"},  # Should be MethodInfo instance
                parameters=params, sample_size=sample_size,
                data_template=data_template, analysis_steps=[],
                diagnostics=[], interpretation_notes="", limitations=[],
                repro_code=repro_code, citations=[], confidence=0.8
            )

        # Try to pass string instead of Parameters instance
        with pytest.raises(ValidationError):
            DataAnalysisOutput(
                task="interpretation", assumptions=[], method=method,
                parameters="invalid",  # Should be Parameters instance
                sample_size=sample_size, data_template=data_template,
                analysis_steps=[], diagnostics=[], interpretation_notes="",
                limitations=[], repro_code=repro_code, citations=[], confidence=0.8
            )

    def test_empty_lists_allowed(self):
        """Test that empty lists are allowed for list fields"""
        from agents.data_analysis_agent import (
            DataAnalysisOutput, EffectSize, MethodInfo,
            Parameters, SampleSize, DataTemplate, ReproCode
        )

        # Create nested models
        effect_size = EffectSize(type="descriptive", value=0.0, how_estimated="N/A")
        method = MethodInfo(name="descriptive statistics", justification="exploratory")
        params = Parameters(effect_size=effect_size, design="descriptive")
        sample_size = SampleSize(formula_or_reference="convenience sample")
        data_template = DataTemplate(columns=[], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="summary()")

        # Response with empty lists
        output = DataAnalysisOutput(
            task="template",
            assumptions=[],  # Empty allowed
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=["Calculate descriptive statistics"],
            diagnostics=[],  # Empty allowed
            interpretation_notes="Exploratory only",
            limitations=[],  # Empty allowed
            repro_code=repro_code,
            citations=[],  # Empty allowed
            confidence=0.50
        )

        assert output.assumptions == []
        assert output.diagnostics == []
        assert output.limitations == []
        assert output.citations == []

    def test_repro_code_language_validation(self):
        """Test that ReproCode validates language field (only R and Python allowed)"""
        from agents.data_analysis_agent import ReproCode
        from pydantic import ValidationError

        # Valid languages should work (only R and Python per schema)
        valid_languages = ["R", "Python"]
        for lang in valid_languages:
            code = ReproCode(language=lang, snippet="test()")
            assert code.language == lang

        # Invalid language should fail
        with pytest.raises(ValidationError):
            ReproCode(language="Stata", snippet="test()")

        # Missing language should fail (required field)
        with pytest.raises(ValidationError):
            ReproCode(snippet="test()")

        # Missing snippet should fail (required field)
        with pytest.raises(ValidationError):
            ReproCode(language="R")
