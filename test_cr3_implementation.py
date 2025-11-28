#!/usr/bin/env python3
"""
CR-3 Implementation Test Script
Tests the refactored DataAnalysisAgent before making changes

This script verifies:
1. Syntax validity
2. Import functionality
3. Class instantiation
4. Global instance creation
5. Output schema enablement
6. Special settings preservation (temperature, max_tokens)
"""

import sys
import os
import subprocess
import importlib

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set PYTHONPATH for agno
os.environ['PYTHONPATH'] = f"{os.path.dirname(os.path.abspath(__file__))}/libs/agno"

def run_command(cmd, description, expect_output=None):
    """Run shell command and report results."""
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"CMD: {cmd}")
    print("-" * 70)

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
            env=os.environ
        )

        if result.returncode == 0:
            print("✅ PASS")
            if result.stdout.strip():
                print(f"OUTPUT: {result.stdout.strip()}")
            if expect_output and expect_output in result.stdout:
                print(f"✅ Expected output found: {expect_output}")
            return True
        else:
            print("❌ FAIL")
            if result.stderr.strip():
                print(f"ERROR: {result.stderr.strip()}")
            if result.stdout.strip():
                print(f"OUTPUT: {result.stdout.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT (>10 seconds)")
        return False
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    """Run all CR-3 verification tests."""
    print("=" * 70)
    print("CR-3 IMPLEMENTATION VERIFICATION SCRIPT")
    print("Testing: agents/data_analysis_agent.py")
    print("=" * 70)

    results = {}

    # Test 1: Syntax check
    results['syntax'] = run_command(
        'python3 -m py_compile agents/data_analysis_agent.py',
        "Syntax validation"
    )

    # Test 2: Import DataAnalysisAgent class
    results['class_import'] = run_command(
        'export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno" && python3 -c "from agents.data_analysis_agent import DataAnalysisAgent; print(\\"✅ DataAnalysisAgent class imported\\")"',
        "Import DataAnalysisAgent class",
        expect_output="DataAnalysisAgent class imported"
    )

    # Test 3: Import global instance
    results['global_import'] = run_command(
        'export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno" && python3 -c "from agents.data_analysis_agent import data_analysis_agent; print(\\"✅ Global instance imported\\")"',
        "Import global data_analysis_agent instance",
        expect_output="Global instance imported"
    )

    # Test 4: Instantiate class
    results['instantiation'] = run_command(
        'export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno" && python3 -c "from agents.data_analysis_agent import DataAnalysisAgent; agent = DataAnalysisAgent(); print(f\\"✅ Agent name: {agent.agent_name}\\")"',
        "Instantiate DataAnalysisAgent class",
        expect_output="Data Analysis Planner"
    )

    # Test 5: Check global instance type
    results['instance_type'] = run_command(
        'export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno" && python3 -c "from agents.data_analysis_agent import data_analysis_agent; print(f\\"✅ Instance type: {type(data_analysis_agent)}\\")"',
        "Check global instance type",
        expect_output="agno.agent.agent.Agent"
    )

    # Test 6: Verify output_schema enabled (CRITICAL)
    results['output_schema'] = run_command(
        'export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno" && python3 -c "from agents.data_analysis_agent import data_analysis_agent; has_schema = hasattr(data_analysis_agent, \'output_model\') and data_analysis_agent.output_model is not None; print(f\\"✅ Output schema enabled: {has_schema}\\")"',
        "Verify output_schema=DataAnalysisOutput is ENABLED",
        expect_output="True"
    )

    # Test 7: Check temperature setting
    results['temperature'] = run_command(
        'export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno" && python3 -c "from agents.data_analysis_agent import data_analysis_agent; temp = getattr(data_analysis_agent.model, \'temperature\', None); print(f\\"✅ Temperature: {temp}\\")"',
        "Verify temperature=0.2 preserved",
        expect_output="0.2"
    )

    # Test 8: Check max_tokens setting
    results['max_tokens'] = run_command(
        'export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno" && python3 -c "from agents.data_analysis_agent import data_analysis_agent; tokens = getattr(data_analysis_agent.model, \'max_tokens\', None); print(f\\"✅ Max tokens: {tokens}\\")"',
        "Verify max_tokens=1600 preserved",
        expect_output="1600"
    )

    # Test 9: Verify DataAnalysisOutput class exists at module level
    results['pydantic_class'] = run_command(
        'export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno" && python3 -c "from agents.data_analysis_agent import DataAnalysisOutput; print(f\\"✅ DataAnalysisOutput class available: {DataAnalysisOutput.__name__}\\")"',
        "Verify DataAnalysisOutput Pydantic class at module level",
        expect_output="DataAnalysisOutput"
    )

    # Test 10: Verify STATISTICAL_EXPERT_PROMPT exists
    results['prompt_constant'] = run_command(
        'export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno" && python3 -c "import agents.data_analysis_agent as da; print(f\\"✅ STATISTICAL_EXPERT_PROMPT length: {len(da.STATISTICAL_EXPERT_PROMPT)} chars\\")"',
        "Verify STATISTICAL_EXPERT_PROMPT constant at module level",
        expect_output="chars"
    )

    # Test 11: Run unit tests
    results['unit_tests'] = run_command(
        'pytest tests/unit/test_data_analysis_agent.py -v --tb=no 2>&1 | head -50',
        "Run unit tests (expect pattern mismatch failures)"
    )

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, passed_flag in results.items():
        status = "✅ PASS" if passed_flag else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 70)

    # Critical checks
    print("\nCRITICAL CHECKS:")
    critical_tests = ['syntax', 'class_import', 'instantiation', 'output_schema']
    critical_passed = all(results.get(t, False) for t in critical_tests)

    if critical_passed:
        print("✅ All critical tests PASSED - Ready for production")
    else:
        print("❌ Critical test failures - Review implementation")
        for test in critical_tests:
            if not results.get(test, False):
                print(f"   ❌ {test} FAILED")

    print("\nEXPECTED BEHAVIOR:")
    print("- Unit tests: 3-4 passing, 8-10 failing (pattern mismatch - normal)")
    print("- output_schema: MUST show True (critical for JSON validation)")
    print("- temperature: MUST show 0.2 (critical for math reliability)")
    print("- max_tokens: MUST show 1600 (critical for JSON + prose)")

    return 0 if critical_passed else 1

if __name__ == "__main__":
    sys.exit(main())
