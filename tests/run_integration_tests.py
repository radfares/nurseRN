#!/usr/bin/env python3
"""
Comprehensive Integration Test Runner for Session 007
Runs all integration tests in sequence and reports results.

Created: 2025-12-11
Purpose: Validate all conversational workflow components
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("SESSION 007 - COMPREHENSIVE INTEGRATION TEST SUITE")
print("=" * 80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test suite definition
TESTS = [
    {
        "name": "Conversational Startup",
        "file": "test_conversational_startup.py",
        "description": "Verify conversational interface initialization",
        "critical": True
    },
    {
        "name": "Exa Integration",
        "file": "test_exa_integration.py",
        "description": "Verify Exa neural search integration",
        "critical": True
    },
    {
        "name": "Orchestrator Basic",
        "file": "test_orchestrator_basic.py",
        "description": "Test simple timeline query orchestration",
        "critical": False
    },
    {
        "name": "Orchestrator Data Analysis",
        "file": "test_orchestrator_data_analysis.py",
        "description": "Test sample size calculation orchestration",
        "critical": True
    },
    {
        "name": "Research Workflow",
        "file": "test_conversational_research_workflow.py",
        "description": "Test PICOT generation workflow (100% quality expected)",
        "critical": True
    },
    {
        "name": "Multi-Turn Conversation",
        "file": "test_conversational_multiturn.py",
        "description": "Test context persistence across turns",
        "critical": True
    },
    {
        "name": "Document Readers",
        "file": "test_document_readers_integration.py",
        "description": "Test document reader tools (may fail on missing dependency)",
        "critical": False
    },
    {
        "name": "Session Summary",
        "file": "test_session_007_summary.py",
        "description": "Overall integration summary and status",
        "critical": False
    }
]

# Test execution
test_dir = Path(__file__).parent / "integration"
results = []

print("Running tests...")
print("-" * 80)
print()

for i, test in enumerate(TESTS, 1):
    print(f"[{i}/{len(TESTS)}] {test['name']}")
    print(f"    {test['description']}")

    test_path = test_dir / test['file']

    if not test_path.exists():
        print(f"    ⚠️  SKIP: Test file not found")
        results.append({
            "name": test['name'],
            "status": "SKIP",
            "critical": test['critical']
        })
        print()
        continue

    try:
        result = subprocess.run(
            [sys.executable, str(test_path)],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            print(f"    ✅ PASS")
            results.append({
                "name": test['name'],
                "status": "PASS",
                "critical": test['critical']
            })
        else:
            print(f"    ❌ FAIL (exit code: {result.returncode})")
            if test['critical']:
                print(f"    🔴 CRITICAL TEST FAILED")
            results.append({
                "name": test['name'],
                "status": "FAIL",
                "critical": test['critical'],
                "error": result.stderr[:200] if result.stderr else "Unknown error"
            })
    except subprocess.TimeoutExpired:
        print(f"    ⏱️  TIMEOUT (exceeded 60s)")
        results.append({
            "name": test['name'],
            "status": "TIMEOUT",
            "critical": test['critical']
        })
    except Exception as e:
        print(f"    ❌ ERROR: {e}")
        results.append({
            "name": test['name'],
            "status": "ERROR",
            "critical": test['critical'],
            "error": str(e)
        })

    print()

# Summary
print("=" * 80)
print("TEST RESULTS SUMMARY")
print("=" * 80)
print()

passed = sum(1 for r in results if r['status'] == 'PASS')
failed = sum(1 for r in results if r['status'] == 'FAIL')
skipped = sum(1 for r in results if r['status'] == 'SKIP')
errors = sum(1 for r in results if r['status'] in ['ERROR', 'TIMEOUT'])
total = len(results)

print(f"Total Tests: {total}")
print(f"  ✅ Passed:  {passed}")
print(f"  ❌ Failed:  {failed}")
print(f"  ⚠️  Skipped: {skipped}")
print(f"  🔴 Errors:  {errors}")
print()

print("Detailed Results:")
print("-" * 80)
for result in results:
    status_icon = {
        'PASS': '✅',
        'FAIL': '❌',
        'SKIP': '⚠️ ',
        'ERROR': '🔴',
        'TIMEOUT': '⏱️ '
    }.get(result['status'], '❓')

    critical_marker = " [CRITICAL]" if result.get('critical') else ""
    print(f"{status_icon} {result['name']}{critical_marker}")

    if result['status'] in ['FAIL', 'ERROR'] and 'error' in result:
        print(f"    Error: {result['error'][:100]}...")

print()

# Critical test analysis
critical_failed = [r for r in results if r.get('critical') and r['status'] != 'PASS']
if critical_failed:
    print("🔴 CRITICAL TESTS FAILED:")
    for r in critical_failed:
        print(f"   - {r['name']}")
    print()
    print("⚠️  System may not be production ready")
else:
    print("✅ All critical tests passed")
    print("✅ System is production ready")

print()
print("=" * 80)
print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Exit code based on critical tests
if critical_failed:
    sys.exit(1)
else:
    sys.exit(0)
