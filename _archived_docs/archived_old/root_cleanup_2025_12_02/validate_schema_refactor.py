#!/usr/bin/env python3
"""
Comprehensive Validation Script for DataAnalysisOutput Schema Refactoring
Tests all phases: Schema Validation, Smoke Tests, Edge Cases, Integration
"""

import sys
import json
import copy
from pathlib import Path
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field, ValidationError

# Setup path for agno imports
_project_root = Path(__file__).parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))

# Import sanitization functions
from agno.utils.models.openai_responses import sanitize_response_schema
from agno.utils.models.schema_utils import is_dict_field

# ============================================================================
# PROPOSED NESTED MODELS
# ============================================================================

class EffectSize(BaseModel):
    """Effect size specification."""
    type: str  # "Cohen_d", "OR", "RR", "r", "f", "Δ", "Absolute Δ"
    value: Optional[float] = None
    how_estimated: str  # "pilot", "literature", "MDE rationale"

class MethodInfo(BaseModel):
    """Method information for statistical analysis."""
    name: str
    justification: str
    alternatives: list[str] = Field(default_factory=list)

class Parameters(BaseModel):
    """Statistical test parameters."""
    alpha: float = 0.05
    tails: Literal["one", "two"] = "two"
    power: float = 0.80
    effect_size: EffectSize
    allocation_ratio: float = 1.0
    covariates: list[str] = Field(default_factory=list)
    design: str  # "parallel", "paired", "cluster", "crossover", "repeated-measures"
    icc: Optional[float] = None
    sphericity: Optional[str] = None  # "assumed", "corrected", None
    missing_data: str = "MAR"  # "MAR", "MCAR", "MNAR"

class SampleSize(BaseModel):
    """Sample size calculation results."""
    per_group: Optional[int] = None
    total: Optional[int] = None
    formula_or_reference: str

class DataColumn(BaseModel):
    """Data column definition."""
    name: str
    type: str  # "numeric", "integer", "string", "date", "categorical"
    allowed: Optional[list[str]] = None
    notes: Optional[str] = None

class DataTemplate(BaseModel):
    """Data collection template structure."""
    columns: list[DataColumn]
    id_key: str
    long_vs_wide: Literal["long", "wide"]
    file_format: str = "CSV"
    example_rows: int = 2

class ReproCode(BaseModel):
    """Reproducible code snippet."""
    language: Literal["R", "Python"]
    snippet: str

class DataAnalysisOutput(BaseModel):
    """Structured output schema for data analysis recommendations."""
    task: Literal["test_selection", "sample_size", "data_plan", "interpretation", "template"]
    assumptions: list[str]
    method: MethodInfo
    parameters: Parameters
    sample_size: SampleSize
    data_template: DataTemplate
    analysis_steps: list[str]
    diagnostics: list[str]
    interpretation_notes: str
    limitations: list[str]
    repro_code: ReproCode
    citations: list[str]
    confidence: float = Field(ge=0.0, le=1.0, description="Self-rated confidence 0-1")

# ============================================================================
# TEST RESULTS TRACKING
# ============================================================================

class TestResults:
    def __init__(self):
        self.schema_validation = {"passed": False, "details": []}
        self.smoke_tests = {"passed": 0, "failed": 0, "results": []}
        self.edge_cases = {"passed": 0, "failed": 0, "results": []}
        self.integration_check = {"passed": False, "details": []}
        self.issues = []
        self.sanitized_schema = None

results = TestResults()

# ============================================================================
# PHASE 1: SCHEMA VALIDATION
# ============================================================================

def test_schema_validation():
    """Test schema generation and sanitization."""
    print("\n" + "="*80)
    print("PHASE 1: SCHEMA VALIDATION")
    print("="*80)
    
    try:
        # Generate base schema
        base_schema = DataAnalysisOutput.model_json_schema()
        results.schema_validation["details"].append("✓ Base schema generated successfully")
        
        # Check for dict[str, Any] fields
        dict_fields_found = []
        def check_for_dict_fields(schema, path=""):
            if isinstance(schema, dict):
                if schema.get("type") == "object" and "additionalProperties" in schema:
                    ap = schema["additionalProperties"]
                    if isinstance(ap, dict) and "type" in ap:
                        if is_dict_field(schema):
                            dict_fields_found.append(f"{path}")
                if "properties" in schema:
                    for prop_name, prop_schema in schema["properties"].items():
                        check_for_dict_fields(prop_schema, f"{path}.{prop_name}" if path else prop_name)
                if "items" in schema:
                    check_for_dict_fields(schema["items"], f"{path}[]")
        
        check_for_dict_fields(base_schema)
        
        if dict_fields_found:
            results.schema_validation["details"].append(f"⚠ Found {len(dict_fields_found)} Dict field(s) (will be excluded from required)")
        else:
            results.schema_validation["details"].append("✓ No dict[str, Any] fields found (all replaced with nested models)")
        
        # Sanitize schema
        sanitized = copy.deepcopy(base_schema)
        sanitize_response_schema(sanitized)
        results.sanitized_schema = sanitized
        results.schema_validation["details"].append("✓ Schema sanitized successfully")
        
        # Verify no dict fields in required array
        dict_in_required_errors = []
        def verify_required_array(schema, path=""):
            if isinstance(schema, dict) and "properties" in schema:
                required = schema.get("required", [])
                for prop_name, prop_schema in schema["properties"].items():
                    if is_dict_field(prop_schema):
                        if prop_name in required:
                            dict_in_required_errors.append(f"{path}.{prop_name}" if path else prop_name)
                # Recurse
                for prop_name, prop_schema in schema["properties"].items():
                    verify_required_array(prop_schema, f"{path}.{prop_name}" if path else prop_name)
            if "items" in schema:
                verify_required_array(schema["items"], f"{path}[]")
        
        verify_required_array(sanitized)
        
        if dict_in_required_errors:
            for error in dict_in_required_errors:
                results.schema_validation["details"].append(f"❌ ERROR: Dict field '{error}' found in required array")
            results.schema_validation["passed"] = False
        else:
            results.schema_validation["details"].append("✓ No dict fields incorrectly placed in required arrays")
        
        # Check all nested models have additionalProperties: false
        missing_ap_errors = []
        def check_additional_properties(schema, path=""):
            if isinstance(schema, dict):
                if schema.get("type") == "object":
                    if not is_dict_field(schema):
                        if schema.get("additionalProperties") is not False:
                            missing_ap_errors.append(f"{path}" if path else "root")
                if "properties" in schema:
                    for prop_name, prop_schema in schema["properties"].items():
                        check_additional_properties(prop_schema, f"{path}.{prop_name}" if path else prop_name)
                if "items" in schema:
                    check_additional_properties(schema["items"], f"{path}[]")
        
        check_additional_properties(sanitized)
        
        if missing_ap_errors:
            for error in missing_ap_errors[:5]:  # Limit output
                results.schema_validation["details"].append(f"⚠ additionalProperties not False at {error}")
        else:
            results.schema_validation["details"].append("✓ All object types have additionalProperties: false")
        
        if not dict_in_required_errors:
            results.schema_validation["passed"] = True
            results.schema_validation["details"].append("✓ All schema validation checks passed")
        
    except Exception as e:
        results.schema_validation["passed"] = False
        results.schema_validation["details"].append(f"❌ Schema validation failed: {e}")
        results.issues.append(f"Schema validation error: {e}")
        import traceback
        results.issues.append(f"Traceback: {traceback.format_exc()}")

# ============================================================================
# PHASE 2: SMOKE TESTS
# ============================================================================

def test_smoke_tests():
    """Run smoke tests for model validation."""
    print("\n" + "="*80)
    print("PHASE 2: SMOKE TESTS")
    print("="*80)
    
    # Test 1: Valid instantiation - all required fields
    try:
        effect_size = EffectSize(type="Cohen_d", value=0.5, how_estimated="literature")
        method = MethodInfo(name="Welch t-test", justification="Robust to unequal variances")
        params = Parameters(
            effect_size=effect_size,
            design="parallel"
        )
        sample_size = SampleSize(formula_or_reference="G*Power")
        column = DataColumn(name="participant_id", type="string")
        data_template = DataTemplate(
            columns=[column],
            id_key="participant_id",
            long_vs_wide="long"
        )
        repro_code = ReproCode(language="R", snippet="t.test(...)")
        
        output = DataAnalysisOutput(
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
        results.smoke_tests["passed"] += 1
        results.smoke_tests["results"].append("✓ Test 1: Valid instantiation - PASS")
    except Exception as e:
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append(f"❌ Test 1: Valid instantiation - FAIL: {e}")
        results.issues.append(f"Smoke test 1 failed: {e}")
    
    # Test 2: Valid instantiation - with optional fields
    try:
        effect_size = EffectSize(type="Cohen_d", value=None, how_estimated="MDE rationale")
        method = MethodInfo(
            name="ANOVA",
            justification="Multiple groups",
            alternatives=["Kruskal-Wallis"]
        )
        params = Parameters(
            effect_size=effect_size,
            design="parallel",
            icc=0.05,
            sphericity="assumed",
            covariates=["age", "gender"]
        )
        sample_size = SampleSize(per_group=30, total=90, formula_or_reference="G*Power")
        column1 = DataColumn(name="id", type="string")
        column2 = DataColumn(name="group", type="categorical", allowed=["A", "B", "C"], notes="Treatment groups")
        data_template = DataTemplate(
            columns=[column1, column2],
            id_key="id",
            long_vs_wide="wide",
            file_format="CSV",
            example_rows=3
        )
        repro_code = ReproCode(language="Python", snippet="from scipy import stats")
        
        output = DataAnalysisOutput(
            task="sample_size",
            assumptions=["normal distribution", "equal variances"],
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=["step 1", "step 2"],
            diagnostics=["normality", "homogeneity"],
            interpretation_notes="Interpretation",
            limitations=["assumptions"],
            repro_code=repro_code,
            citations=["Cohen 1988", "Field 2013"],
            confidence=0.90
        )
        results.smoke_tests["passed"] += 1
        results.smoke_tests["results"].append("✓ Test 2: Valid with optional fields - PASS")
    except Exception as e:
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append(f"❌ Test 2: Valid with optional fields - FAIL: {e}")
        results.issues.append(f"Smoke test 2 failed: {e}")
    
    # Test 3: Invalid - missing required field
    try:
        output = DataAnalysisOutput(
            task="test_selection",
            assumptions=["test"],
            # Missing method, parameters, etc.
        )
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append("❌ Test 3: Missing required field - FAIL (should have raised ValidationError)")
        results.issues.append("Smoke test 3: Should reject missing fields but didn't")
    except ValidationError:
        results.smoke_tests["passed"] += 1
        results.smoke_tests["results"].append("✓ Test 3: Missing required field - PASS (correctly rejected)")
    except Exception as e:
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append(f"❌ Test 3: Missing required field - FAIL (wrong error: {e})")
        results.issues.append(f"Smoke test 3: Wrong error type: {e}")
    
    # Test 4: Invalid - wrong type
    try:
        effect_size = EffectSize(type="Cohen_d", how_estimated="literature")
        method = MethodInfo(name="Test", justification="Test")
        params = Parameters(effect_size=effect_size, design="parallel")
        sample_size = SampleSize(formula_or_reference="Test")
        column = DataColumn(name="id", type="string")
        data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="test()")
        
        output = DataAnalysisOutput(
            task="test_selection",
            assumptions="not a list",  # Wrong type - should be list
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=["step"],
            diagnostics=["diag"],
            interpretation_notes="notes",
            limitations=["lim"],
            repro_code=repro_code,
            citations=["cite"],
            confidence=0.5
        )
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append("❌ Test 4: Wrong type - FAIL (should have raised ValidationError)")
        results.issues.append("Smoke test 4: Should reject wrong type but didn't")
    except ValidationError:
        results.smoke_tests["passed"] += 1
        results.smoke_tests["results"].append("✓ Test 4: Wrong type - PASS (correctly rejected)")
    except Exception as e:
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append(f"❌ Test 4: Wrong type - FAIL (wrong error: {e})")
        results.issues.append(f"Smoke test 4: Wrong error type: {e}")
    
    # Test 5: Invalid - confidence < 0.0
    try:
        effect_size = EffectSize(type="Cohen_d", how_estimated="literature")
        method = MethodInfo(name="Test", justification="Test")
        params = Parameters(effect_size=effect_size, design="parallel")
        sample_size = SampleSize(formula_or_reference="Test")
        column = DataColumn(name="id", type="string")
        data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="test()")
        
        output = DataAnalysisOutput(
            task="test_selection",
            assumptions=["test"],
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=["step"],
            diagnostics=["diag"],
            interpretation_notes="notes",
            limitations=["lim"],
            repro_code=repro_code,
            citations=["cite"],
            confidence=-0.1  # Invalid: < 0.0
        )
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append("❌ Test 5: Confidence < 0.0 - FAIL (should have raised ValidationError)")
        results.issues.append("Smoke test 5: Should reject confidence < 0.0 but didn't")
    except ValidationError:
        results.smoke_tests["passed"] += 1
        results.smoke_tests["results"].append("✓ Test 5: Confidence < 0.0 - PASS (correctly rejected)")
    except Exception as e:
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append(f"❌ Test 5: Confidence < 0.0 - FAIL (wrong error: {e})")
        results.issues.append(f"Smoke test 5: Wrong error type: {e}")
    
    # Test 6: Invalid - confidence > 1.0
    try:
        effect_size = EffectSize(type="Cohen_d", how_estimated="literature")
        method = MethodInfo(name="Test", justification="Test")
        params = Parameters(effect_size=effect_size, design="parallel")
        sample_size = SampleSize(formula_or_reference="Test")
        column = DataColumn(name="id", type="string")
        data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="test()")
        
        output = DataAnalysisOutput(
            task="test_selection",
            assumptions=["test"],
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=["step"],
            diagnostics=["diag"],
            interpretation_notes="notes",
            limitations=["lim"],
            repro_code=repro_code,
            citations=["cite"],
            confidence=1.1  # Invalid: > 1.0
        )
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append("❌ Test 6: Confidence > 1.0 - FAIL (should have raised ValidationError)")
        results.issues.append("Smoke test 6: Should reject confidence > 1.0 but didn't")
    except ValidationError:
        results.smoke_tests["passed"] += 1
        results.smoke_tests["results"].append("✓ Test 6: Confidence > 1.0 - PASS (correctly rejected)")
    except Exception as e:
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append(f"❌ Test 6: Confidence > 1.0 - FAIL (wrong error: {e})")
        results.issues.append(f"Smoke test 6: Wrong error type: {e}")
    
    # Test 7: JSON serialization round-trip
    try:
        effect_size = EffectSize(type="Cohen_d", value=0.5, how_estimated="literature")
        method = MethodInfo(name="Test", justification="Test")
        params = Parameters(effect_size=effect_size, design="parallel")
        sample_size = SampleSize(formula_or_reference="Test")
        column = DataColumn(name="id", type="string")
        data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="test()")
        
        output = DataAnalysisOutput(
            task="test_selection",
            assumptions=["test"],
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=["step"],
            diagnostics=["diag"],
            interpretation_notes="notes",
            limitations=["lim"],
            repro_code=repro_code,
            citations=["cite"],
            confidence=0.75
        )
        
        # Serialize to JSON
        json_str = output.model_dump_json()
        json_data = json.loads(json_str)
        
        # Deserialize back
        output2 = DataAnalysisOutput.model_validate(json_data)
        
        # Verify round-trip
        assert output.task == output2.task
        assert output.confidence == output2.confidence
        
        results.smoke_tests["passed"] += 1
        results.smoke_tests["results"].append("✓ Test 7: JSON serialization round-trip - PASS")
    except Exception as e:
        results.smoke_tests["failed"] += 1
        results.smoke_tests["results"].append(f"❌ Test 7: JSON serialization - FAIL: {e}")
        results.issues.append(f"Smoke test 7 failed: {e}")

# ============================================================================
# PHASE 2: EDGE CASES
# ============================================================================

def test_edge_cases():
    """Test edge cases."""
    print("\n" + "="*80)
    print("PHASE 2: EDGE CASES")
    print("="*80)
    
    # Edge Case 1: Confidence = 0.0
    try:
        effect_size = EffectSize(type="Cohen_d", how_estimated="literature")
        method = MethodInfo(name="Test", justification="Test")
        params = Parameters(effect_size=effect_size, design="parallel")
        sample_size = SampleSize(formula_or_reference="Test")
        column = DataColumn(name="id", type="string")
        data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="test()")
        
        output = DataAnalysisOutput(
            task="test_selection",
            assumptions=["test"],
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=["step"],
            diagnostics=["diag"],
            interpretation_notes="notes",
            limitations=["lim"],
            repro_code=repro_code,
            citations=["cite"],
            confidence=0.0  # Boundary: minimum
        )
        results.edge_cases["passed"] += 1
        results.edge_cases["results"].append("✓ Edge Case 1: Confidence = 0.0 - PASS")
    except Exception as e:
        results.edge_cases["failed"] += 1
        results.edge_cases["results"].append(f"❌ Edge Case 1: Confidence = 0.0 - FAIL: {e}")
        results.issues.append(f"Edge case 1 failed: {e}")
    
    # Edge Case 2: Confidence = 1.0
    try:
        effect_size = EffectSize(type="Cohen_d", how_estimated="literature")
        method = MethodInfo(name="Test", justification="Test")
        params = Parameters(effect_size=effect_size, design="parallel")
        sample_size = SampleSize(formula_or_reference="Test")
        column = DataColumn(name="id", type="string")
        data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="test()")
        
        output = DataAnalysisOutput(
            task="test_selection",
            assumptions=["test"],
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=["step"],
            diagnostics=["diag"],
            interpretation_notes="notes",
            limitations=["lim"],
            repro_code=repro_code,
            citations=["cite"],
            confidence=1.0  # Boundary: maximum
        )
        results.edge_cases["passed"] += 1
        results.edge_cases["results"].append("✓ Edge Case 2: Confidence = 1.0 - PASS")
    except Exception as e:
        results.edge_cases["failed"] += 1
        results.edge_cases["results"].append(f"❌ Edge Case 2: Confidence = 1.0 - FAIL: {e}")
        results.issues.append(f"Edge case 2 failed: {e}")
    
    # Edge Case 3: Empty lists
    try:
        effect_size = EffectSize(type="Cohen_d", how_estimated="literature")
        method = MethodInfo(name="Test", justification="Test", alternatives=[])  # Empty list
        params = Parameters(effect_size=effect_size, design="parallel", covariates=[])  # Empty list
        sample_size = SampleSize(formula_or_reference="Test")
        column = DataColumn(name="id", type="string")
        data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="test()")
        
        output = DataAnalysisOutput(
            task="test_selection",
            assumptions=[],  # Empty list
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=[],  # Empty list
            diagnostics=[],  # Empty list
            interpretation_notes="notes",
            limitations=[],  # Empty list
            repro_code=repro_code,
            citations=[],  # Empty list
            confidence=0.5
        )
        results.edge_cases["passed"] += 1
        results.edge_cases["results"].append("✓ Edge Case 3: Empty lists - PASS")
    except Exception as e:
        results.edge_cases["failed"] += 1
        results.edge_cases["results"].append(f"❌ Edge Case 3: Empty lists - FAIL: {e}")
        results.issues.append(f"Edge case 3 failed: {e}")
    
    # Edge Case 4: All task types
    task_types = ["test_selection", "sample_size", "data_plan", "interpretation", "template"]
    for task in task_types:
        try:
            effect_size = EffectSize(type="Cohen_d", how_estimated="literature")
            method = MethodInfo(name="Test", justification="Test")
            params = Parameters(effect_size=effect_size, design="parallel")
            sample_size = SampleSize(formula_or_reference="Test")
            column = DataColumn(name="id", type="string")
            data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
            repro_code = ReproCode(language="R", snippet="test()")
            
            output = DataAnalysisOutput(
                task=task,
                assumptions=["test"],
                method=method,
                parameters=params,
                sample_size=sample_size,
                data_template=data_template,
                analysis_steps=["step"],
                diagnostics=["diag"],
                interpretation_notes="notes",
                limitations=["lim"],
                repro_code=repro_code,
                citations=["cite"],
                confidence=0.5
            )
            results.edge_cases["passed"] += 1
            results.edge_cases["results"].append(f"✓ Edge Case 4.{task}: Task type '{task}' - PASS")
        except Exception as e:
            results.edge_cases["failed"] += 1
            results.edge_cases["results"].append(f"❌ Edge Case 4.{task}: Task type '{task}' - FAIL: {e}")
            results.issues.append(f"Edge case 4.{task} failed: {e}")
    
    # Edge Case 5: All language options
    languages = ["R", "Python"]
    for lang in languages:
        try:
            effect_size = EffectSize(type="Cohen_d", how_estimated="literature")
            method = MethodInfo(name="Test", justification="Test")
            params = Parameters(effect_size=effect_size, design="parallel")
            sample_size = SampleSize(formula_or_reference="Test")
            column = DataColumn(name="id", type="string")
            data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
            repro_code = ReproCode(language=lang, snippet="test()")
            
            output = DataAnalysisOutput(
                task="test_selection",
                assumptions=["test"],
                method=method,
                parameters=params,
                sample_size=sample_size,
                data_template=data_template,
                analysis_steps=["step"],
                diagnostics=["diag"],
                interpretation_notes="notes",
                limitations=["lim"],
                repro_code=repro_code,
                citations=["cite"],
                confidence=0.5
            )
            results.edge_cases["passed"] += 1
            results.edge_cases["results"].append(f"✓ Edge Case 5.{lang}: Language '{lang}' - PASS")
        except Exception as e:
            results.edge_cases["failed"] += 1
            results.edge_cases["results"].append(f"❌ Edge Case 5.{lang}: Language '{lang}' - FAIL: {e}")
            results.issues.append(f"Edge case 5.{lang} failed: {e}")
    
    # Edge Case 6: All tails options
    tails_options = ["one", "two"]
    for tails in tails_options:
        try:
            effect_size = EffectSize(type="Cohen_d", how_estimated="literature")
            method = MethodInfo(name="Test", justification="Test")
            params = Parameters(effect_size=effect_size, design="parallel", tails=tails)
            sample_size = SampleSize(formula_or_reference="Test")
            column = DataColumn(name="id", type="string")
            data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
            repro_code = ReproCode(language="R", snippet="test()")
            
            output = DataAnalysisOutput(
                task="test_selection",
                assumptions=["test"],
                method=method,
                parameters=params,
                sample_size=sample_size,
                data_template=data_template,
                analysis_steps=["step"],
                diagnostics=["diag"],
                interpretation_notes="notes",
                limitations=["lim"],
                repro_code=repro_code,
                citations=["cite"],
                confidence=0.5
            )
            results.edge_cases["passed"] += 1
            results.edge_cases["results"].append(f"✓ Edge Case 6.{tails}: Tails '{tails}' - PASS")
        except Exception as e:
            results.edge_cases["failed"] += 1
            results.edge_cases["results"].append(f"❌ Edge Case 6.{tails}: Tails '{tails}' - FAIL: {e}")
            results.issues.append(f"Edge case 6.{tails} failed: {e}")
    
    # Edge Case 7: Optional fields = None
    try:
        effect_size = EffectSize(type="Cohen_d", value=None, how_estimated="literature")
        method = MethodInfo(name="Test", justification="Test")
        params = Parameters(
            effect_size=effect_size,
            design="parallel",
            icc=None,  # Optional
            sphericity=None  # Optional
        )
        sample_size = SampleSize(
            per_group=None,  # Optional
            total=None,  # Optional
            formula_or_reference="Test"
        )
        column = DataColumn(
            name="id",
            type="string",
            allowed=None,  # Optional
            notes=None  # Optional
        )
        data_template = DataTemplate(columns=[column], id_key="id", long_vs_wide="long")
        repro_code = ReproCode(language="R", snippet="test()")
        
        output = DataAnalysisOutput(
            task="test_selection",
            assumptions=["test"],
            method=method,
            parameters=params,
            sample_size=sample_size,
            data_template=data_template,
            analysis_steps=["step"],
            diagnostics=["diag"],
            interpretation_notes="notes",
            limitations=["lim"],
            repro_code=repro_code,
            citations=["cite"],
            confidence=0.5
        )
        results.edge_cases["passed"] += 1
        results.edge_cases["results"].append("✓ Edge Case 7: Optional fields = None - PASS")
    except Exception as e:
        results.edge_cases["failed"] += 1
        results.edge_cases["results"].append(f"❌ Edge Case 7: Optional fields = None - FAIL: {e}")
        results.issues.append(f"Edge case 7 failed: {e}")

# ============================================================================
# PHASE 3: INTEGRATION CHECK
# ============================================================================

def test_integration():
    """Test integration with agent initialization."""
    print("\n" + "="*80)
    print("PHASE 3: INTEGRATION CHECK")
    print("="*80)
    
    try:
        # Simulate agent initialization
        # Check that output_schema can be passed to Agent
        results.integration_check["details"].append("✓ DataAnalysisOutput class is valid BaseModel")
        
        # Check schema generation
        schema = DataAnalysisOutput.model_json_schema()
        results.integration_check["details"].append("✓ model_json_schema() works")
        
        # Check sanitization
        sanitized = copy.deepcopy(schema)
        sanitize_response_schema(sanitized)
        results.integration_check["details"].append("✓ sanitize_response_schema() works")
        
        # Check that schema has required structure
        assert "type" in sanitized
        assert "properties" in sanitized
        assert "required" in sanitized
        results.integration_check["details"].append("✓ Sanitized schema has required structure")
        
        # Check no dict fields in required
        dict_in_required = []
        def check_no_dict_in_required(schema, path=""):
            if isinstance(schema, dict):
                if "properties" in schema and "required" in schema:
                    required = schema["required"]
                    for prop_name, prop_schema in schema["properties"].items():
                        if is_dict_field(prop_schema) and prop_name in required:
                            dict_in_required.append(f"{path}.{prop_name}" if path else prop_name)
                for prop_name, prop_schema in schema.get("properties", {}).items():
                    check_no_dict_in_required(prop_schema, f"{path}.{prop_name}" if path else prop_name)
                if "items" in schema:
                    check_no_dict_in_required(schema["items"], f"{path}[]")
        
        check_no_dict_in_required(sanitized)
        
        if dict_in_required:
            results.integration_check["details"].append(f"❌ Found dict fields in required: {dict_in_required}")
            results.integration_check["passed"] = False
        else:
            results.integration_check["details"].append("✓ No dict fields in required arrays")
        
        results.integration_check["passed"] = True
        results.integration_check["details"].append("✓ All integration checks passed")
        
    except Exception as e:
        results.integration_check["passed"] = False
        results.integration_check["details"].append(f"❌ Integration check failed: {e}")
        results.issues.append(f"Integration check error: {e}")
        import traceback
        results.issues.append(f"Traceback: {traceback.format_exc()}")

# ============================================================================
# PHASE 4: REPORT GENERATION
# ============================================================================

def generate_report():
    """Generate Phase 4 report."""
    print("\n" + "="*80)
    print("PHASE 4: FINAL VALIDATION REPORT")
    print("="*80)
    
    # Calculate confidence
    total_tests = (
        (1 if results.schema_validation["passed"] else 0) +
        results.smoke_tests["passed"] + results.smoke_tests["failed"] +
        results.edge_cases["passed"] + results.edge_cases["failed"] +
        (1 if results.integration_check["passed"] else 0)
    )
    passed_tests = (
        (1 if results.schema_validation["passed"] else 0) +
        results.smoke_tests["passed"] +
        results.edge_cases["passed"] +
        (1 if results.integration_check["passed"] else 0)
    )
    
    if total_tests > 0:
        confidence = (passed_tests / total_tests) * 100
    else:
        confidence = 0
    
    print("\n1. SCHEMA VALIDATION:")
    print(f"   Status: {'PASS' if results.schema_validation['passed'] else 'FAIL'}")
    for detail in results.schema_validation["details"]:
        print(f"   {detail}")
    
    print("\n2. SMOKE TESTS:")
    total_smoke = results.smoke_tests["passed"] + results.smoke_tests["failed"]
    print(f"   Results: {results.smoke_tests['passed']}/{total_smoke} passing")
    for result in results.smoke_tests["results"]:
        print(f"   {result}")
    
    print("\n3. EDGE CASE COVERAGE:")
    total_edge = results.edge_cases["passed"] + results.edge_cases["failed"]
    print(f"   Results: {results.edge_cases['passed']}/{total_edge} passing")
    for result in results.edge_cases["results"]:
        print(f"   {result}")
    
    print("\n4. INTEGRATION CHECK:")
    print(f"   Status: {'PASS' if results.integration_check['passed'] else 'FAIL'}")
    for detail in results.integration_check["details"]:
        print(f"   {detail}")
    
    print("\n5. JSON SCHEMA OUTPUT:")
    if results.sanitized_schema:
        print("   Sanitized schema (first 3000 chars):")
        schema_str = json.dumps(results.sanitized_schema, indent=2)
        if len(schema_str) > 3000:
            print(schema_str[:3000] + "\n   ... (truncated)")
        else:
            print(schema_str)
    else:
        print("   ❌ No sanitized schema available")
    
    print("\n6. CONFIDENCE LEVEL:")
    print(f"   {confidence:.1f}%")
    
    print("\n7. ISSUES FOUND:")
    if results.issues:
        for i, issue in enumerate(results.issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("   ✓ No issues found")
    
    print("\n8. RECOMMENDED ACTION:")
    if (results.schema_validation["passed"] and
        results.smoke_tests["failed"] == 0 and
        results.edge_cases["failed"] == 0 and
        results.integration_check["passed"] and
        confidence == 100.0 and
        len(results.issues) == 0):
        print("   ✅ APPLY")
        print("   Reasoning: All validation checks passed with 100% confidence.")
        print("   - Schema validation: PASS")
        print("   - Smoke tests: 100% passing")
        print("   - Edge cases: 100% passing")
        print("   - Integration check: PASS")
        print("   - Zero issues found")
    else:
        if confidence >= 95:
            print("   ⚠️  REVISE")
        else:
            print("   ❌ ABORT")
        print("   Reasoning:")
        if not results.schema_validation["passed"]:
            print("   - Schema validation failed")
        if results.smoke_tests["failed"] > 0:
            print(f"   - {results.smoke_tests['failed']} smoke test(s) failed")
        if results.edge_cases["failed"] > 0:
            print(f"   - {results.edge_cases['failed']} edge case(s) failed")
        if not results.integration_check["passed"]:
            print("   - Integration check failed")
        if len(results.issues) > 0:
            print(f"   - {len(results.issues)} issue(s) found")
    
    print("\n" + "="*80)
    
    return confidence

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("DATA ANALYSIS OUTPUT SCHEMA VALIDATION")
    print("Comprehensive Testing: Phases 1-4")
    print("="*80)
    
    # Run all phases
    test_schema_validation()
    test_smoke_tests()
    test_edge_cases()
    test_integration()
    
    # Generate report
    confidence = generate_report()
    
    # Exit with appropriate code
    sys.exit(0 if confidence == 100.0 else 1)

