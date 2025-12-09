"""
Test Suite for Data Analysis Agent
Tests statistical reasoning, JSON output structure, and nursing QI scenarios.
"""

import os
import json
from data_analysis_agent import data_analysis_agent

# Test scenarios for nursing quality improvement
TEST_SCENARIOS = [
    {
        "id": "test_1",
        "name": "Sample Size Calculation (Binary Outcome)",
        "query": "Catheter infection rate: baseline 15%, target 8%. Need sample size for α=0.05, power=0.80",
        "expected": {
            "task": "sample_size",
            "method_should_include": ["proportion", "Fisher"],
            "sample_size_expected": "Should calculate N for two proportions",
        }
    },
    {
        "id": "test_2",
        "name": "Test Selection (Continuous, Small Sample)",
        "query": "Compare pain scores (0-10 NRS) between 2 units, n≈25 per group. Unequal variances suspected.",
        "expected": {
            "task": "test_selection",
            "method_should_include": ["Welch", "t-test"],
            "alternatives_should_include": ["Mann-Whitney", "nonparametric"],
        }
    },
    {
        "id": "test_3",
        "name": "Data Template Design (Repeated Measures)",
        "query": "Track fall rates monthly for 6 months; need data collection template with patient demographics.",
        "expected": {
            "task": "template",
            "data_template_should_have": ["columns", "participant_id", "time"],
            "format": "CSV",
        }
    },
    {
        "id": "test_4",
        "name": "Edge Case (Insufficient Information)",
        "query": "Need to compare two groups",
        "expected": {
            "should_request": ["outcome type", "sample size", "effect size"],
            "should_not_fabricate": True,
        }
    }
]

def extract_json_from_response(response_text):
    """
    Extract JSON object from agent response.
    Handles cases where JSON is embedded in markdown or prose.
    """
    try:
        # Try direct JSON parse first
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Look for JSON code block
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
            return json.loads(json_str)
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
            return json.loads(json_str)
        else:
            # Look for JSON object markers
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
    return None

def validate_json_structure(json_obj):
    """
    Validate that JSON has required fields from the schema.
    """
    required_fields = [
        "task", "assumptions", "method", "parameters", 
        "sample_size", "data_template", "analysis_steps",
        "diagnostics", "interpretation_notes", "limitations",
        "repro_code", "citations", "confidence"
    ]
    
    missing_fields = [field for field in required_fields if field not in json_obj]
    return len(missing_fields) == 0, missing_fields

def run_test(scenario, verbose=True):
    """
    Run a single test scenario and return results.
    """
    if verbose:
        print("\n" + "=" * 80)
        print(f"TEST: {scenario['name']}")
        print("=" * 80)
        print(f"Query: {scenario['query']}")
        print("-" * 80)
    
    result = {
        "scenario_id": scenario["id"],
        "scenario_name": scenario["name"],
        "query": scenario["query"],
        "success": False,
        "json_valid": False,
        "json_complete": False,
        "response_text": None,
        "parsed_json": None,
        "missing_fields": [],
        "errors": [],
        "notes": []
    }
    
    try:
        # Run agent query
        response = data_analysis_agent.run(scenario["query"])
        result["response_text"] = response.content
        
        if verbose:
            print("\nAgent Response:")
            print(response.content)
            print("-" * 80)
        
        # Try to extract and parse JSON
        json_obj = extract_json_from_response(response.content)
        
        if json_obj:
            result["json_valid"] = True
            result["parsed_json"] = json_obj
            
            # Validate structure
            is_complete, missing = validate_json_structure(json_obj)
            result["json_complete"] = is_complete
            result["missing_fields"] = missing
            
            # Check confidence score
            if "confidence" in json_obj:
                conf = json_obj["confidence"]
                if 0 <= conf <= 1:
                    result["notes"].append(f"✓ Confidence score valid: {conf}")
                else:
                    result["errors"].append(f"✗ Confidence score out of range: {conf}")
            
            # Check for repro code
            if "repro_code" in json_obj and "snippet" in json_obj["repro_code"]:
                result["notes"].append("✓ Reproducible code provided")
            
            # Check for citations
            if "citations" in json_obj and len(json_obj["citations"]) > 0:
                result["notes"].append(f"✓ Citations provided: {len(json_obj['citations'])}")
            
            if is_complete:
                result["success"] = True
                result["notes"].append("✓ All required JSON fields present")
            else:
                result["errors"].append(f"✗ Missing fields: {', '.join(missing)}")
        else:
            result["errors"].append("✗ Could not extract valid JSON from response")
    
    except Exception as e:
        result["errors"].append(f"✗ Exception: {str(e)}")
    
    if verbose:
        print("\nTest Result:")
        if result["success"]:
            print("✅ PASS")
        else:
            print("❌ FAIL")
        
        if result["notes"]:
            print("\nNotes:")
            for note in result["notes"]:
                print(f"  {note}")
        
        if result["errors"]:
            print("\nErrors:")
            for error in result["errors"]:
                print(f"  {error}")
    
    return result

def run_all_tests():
    """
    Run all test scenarios and generate summary report.
    """
    print("\n" + "=" * 80)
    print("DATA ANALYSIS AGENT - TEST SUITE")
    print("=" * 80)
    print(f"Testing {len(TEST_SCENARIOS)} scenarios")
    print("=" * 80)
    
    # Check for API key
    if not os.getenv("MISTRAL_API_KEY"):
        print("\n❌ ERROR: MISTRAL_API_KEY not found in environment variables")
        print("Please set your Mistral API key:")
        print("  export MISTRAL_API_KEY='your-key-here'")
        return None
    
    results = []
    
    for scenario in TEST_SCENARIOS:
        result = run_test(scenario, verbose=True)
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    print("\n" + "-" * 80)
    print("Individual Results:")
    for r in results:
        status = "✅ PASS" if r["success"] else "❌ FAIL"
        print(f"  {status} - {r['scenario_name']}")
    
    print("\n" + "=" * 80)
    
    return results

if __name__ == "__main__":
    # Run all tests
    test_results = run_all_tests()
    
    # Save results to file for documentation
    if test_results:
        output_file = "test_results.json"
        with open(output_file, "w") as f:
            json.dump(test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {output_file}")

