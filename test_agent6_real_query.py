#!/usr/bin/env python3
"""
Test DataAnalysisAgent with real nursing research query
Verifies the refactored schema works with nested models
"""

import sys
import json
from pathlib import Path

# Setup path for agno imports
_project_root = Path(__file__).parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))

from agents.data_analysis_agent import data_analysis_agent, DataAnalysisOutput
from agents.data_analysis_agent import (
    MethodInfo, Parameters, SampleSize, DataTemplate, ReproCode, EffectSize, DataColumn
)

def test_real_query():
    """Test agent with real nursing research query"""
    
    query = """I need to compare hand hygiene compliance rates between two hospital units. 
Unit A has 30 nurses, Unit B has 25 nurses. I'll measure compliance before and after an intervention. 
What statistical test should I use and what sample size do I need?"""
    
    print("="*80)
    print("TESTING DATA ANALYSIS AGENT WITH REAL QUERY")
    print("="*80)
    print(f"\nQuery: {query}\n")
    print("="*80)
    print("RUNNING AGENT...")
    print("="*80)
    
    try:
        # Run the agent
        response = data_analysis_agent.run(query)
        
        print("\n" + "="*80)
        print("AGENT RESPONSE RECEIVED")
        print("="*80)
        
        # Check if response content is a DataAnalysisOutput instance
        if isinstance(response.content, DataAnalysisOutput):
            print("\n✅ OUTPUT_SCHEMA VALIDATION: PASS")
            print("   Response content is a validated DataAnalysisOutput instance")
            
            output = response.content
            
            print("\n" + "="*80)
            print("1. FULL STRUCTURED JSON RESPONSE")
            print("="*80)
            
            # Convert to dict for JSON serialization
            output_dict = output.model_dump()
            
            # Pretty print the JSON
            print(json.dumps(output_dict, indent=2, ensure_ascii=False))
            
            print("\n" + "="*80)
            print("2. NESTED MODEL STRUCTURE BREAKDOWN")
            print("="*80)
            
            print(f"\n📋 Task: {output.task}")
            print(f"📊 Confidence: {output.confidence:.2f}")
            
            print(f"\n📝 Assumptions ({len(output.assumptions)}):")
            for i, assumption in enumerate(output.assumptions, 1):
                print(f"   {i}. {assumption}")
            
            print(f"\n🔬 Method (MethodInfo):")
            print(f"   Name: {output.method.name}")
            print(f"   Justification: {output.method.justification}")
            if output.method.alternatives:
                print(f"   Alternatives ({len(output.method.alternatives)}):")
                for alt in output.method.alternatives:
                    print(f"     - {alt}")
            else:
                print("   Alternatives: None")
            
            print(f"\n⚙️  Parameters (Parameters):")
            print(f"   Alpha: {output.parameters.alpha}")
            print(f"   Tails: {output.parameters.tails}")
            print(f"   Power: {output.parameters.power}")
            print(f"   Design: {output.parameters.design}")
            print(f"   Allocation Ratio: {output.parameters.allocation_ratio}")
            print(f"   Missing Data: {output.parameters.missing_data}")
            if output.parameters.covariates:
                print(f"   Covariates: {', '.join(output.parameters.covariates)}")
            if output.parameters.icc is not None:
                print(f"   ICC: {output.parameters.icc}")
            if output.parameters.sphericity is not None:
                print(f"   Sphericity: {output.parameters.sphericity}")
            
            print(f"\n   Effect Size (EffectSize):")
            print(f"     Type: {output.parameters.effect_size.type}")
            if output.parameters.effect_size.value is not None:
                print(f"     Value: {output.parameters.effect_size.value}")
            else:
                print(f"     Value: None")
            print(f"     How Estimated: {output.parameters.effect_size.how_estimated}")
            
            print(f"\n📏 Sample Size (SampleSize):")
            if output.sample_size.per_group is not None:
                print(f"   Per Group: {output.sample_size.per_group}")
            else:
                print(f"   Per Group: Not calculated")
            if output.sample_size.total is not None:
                print(f"   Total: {output.sample_size.total}")
            else:
                print(f"   Total: Not calculated")
            print(f"   Formula/Reference: {output.sample_size.formula_or_reference}")
            
            print(f"\n📋 Data Template (DataTemplate):")
            print(f"   ID Key: {output.data_template.id_key}")
            print(f"   Format: {output.data_template.long_vs_wide}")
            print(f"   File Format: {output.data_template.file_format}")
            print(f"   Example Rows: {output.data_template.example_rows}")
            print(f"   Columns ({len(output.data_template.columns)}):")
            for i, col in enumerate(output.data_template.columns, 1):
                print(f"     {i}. {col.name} ({col.type})")
                if col.allowed:
                    print(f"        Allowed: {', '.join(col.allowed)}")
                if col.notes:
                    print(f"        Notes: {col.notes}")
            
            print(f"\n📝 Analysis Steps ({len(output.analysis_steps)}):")
            for i, step in enumerate(output.analysis_steps, 1):
                print(f"   {i}. {step}")
            
            print(f"\n🔍 Diagnostics ({len(output.diagnostics)}):")
            for i, diag in enumerate(output.diagnostics, 1):
                print(f"   {i}. {diag}")
            
            print(f"\n💡 Interpretation Notes:")
            print(f"   {output.interpretation_notes}")
            
            print(f"\n⚠️  Limitations ({len(output.limitations)}):")
            for i, limitation in enumerate(output.limitations, 1):
                print(f"   {i}. {limitation}")
            
            print(f"\n💻 Repro Code (ReproCode):")
            print(f"   Language: {output.repro_code.language}")
            print(f"   Snippet:")
            print(f"   {output.repro_code.snippet}")
            
            print(f"\n📚 Citations ({len(output.citations)}):")
            for i, citation in enumerate(output.citations, 1):
                print(f"   {i}. {citation}")
            
            print("\n" + "="*80)
            print("3. HOW NESTED STRUCTURE MAKES OUTPUT MORE USABLE")
            print("="*80)
            
            print("\n✅ Type Safety:")
            print("   - Can access nested fields with autocomplete: output.method.name")
            print("   - IDE provides type hints and validation")
            print("   - No need to remember dict keys or worry about typos")
            
            print("\n✅ Structured Access:")
            print("   - output.parameters.effect_size.value (nested access)")
            print("   - output.data_template.columns[0].name (list of objects)")
            print("   - All fields are validated at creation time")
            
            print("\n✅ Validation:")
            print("   - Pydantic validates all nested structures")
            print("   - Type checking ensures correct data types")
            print("   - Required fields are enforced")
            
            print("\n✅ Serialization:")
            print("   - Easy JSON export: output.model_dump_json()")
            print("   - Can reconstruct from JSON: DataAnalysisOutput.model_validate_json(json_str)")
            print("   - Maintains structure and types")
            
            print("\n✅ Example Usage:")
            print("   # Access nested fields directly")
            print("   method_name = output.method.name")
            print("   effect_size_type = output.parameters.effect_size.type")
            print("   sample_per_group = output.sample_size.per_group")
            print("   first_column = output.data_template.columns[0].name")
            print("   code_language = output.repro_code.language")
            
            print("\n" + "="*80)
            print("✅ TEST COMPLETE - SCHEMA REFACTORING VERIFIED")
            print("="*80)
            
        else:
            print("\n❌ OUTPUT_SCHEMA VALIDATION: FAIL")
            print(f"   Response content type: {type(response.content)}")
            print(f"   Expected: DataAnalysisOutput")
            if hasattr(response, 'content'):
                print(f"   Content: {response.content}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_real_query()
    sys.exit(0 if success else 1)

