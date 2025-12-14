"""
Gate 1: File Organization Validation
Tests that misplaced test files have been moved to correct locations
"""

import pytest
from pathlib import Path

def test_no_test_files_in_root():
    """Verify no test files remain in project root"""
    root_test_files = list(Path(".").glob("test_*.py"))

    assert len(root_test_files) == 0, (
        f"Found test files in root directory: {root_test_files}\n"
        f"All test files must be in tests/ directory"
    )

def test_no_test_files_in_tests_root():
    """Verify no test files remain in tests/ root (should be in unit/ or integration/)"""
    tests_root = Path("tests")
    test_files_in_root = [
        f for f in tests_root.glob("test_*.py")
        if f.is_file()
    ]

    assert len(test_files_in_root) == 0, (
        f"Found test files in tests/ root: {test_files_in_root}\n"
        f"Test files must be in tests/unit/ or tests/integration/\n"
        f"Move them to appropriate subdirectory"
    )

def test_pytest_output_not_in_root():
    """Verify pytest_full_output.txt is moved or deleted"""
    root_output = Path("pytest_full_output.txt")

    assert not root_output.exists(), (
        f"pytest_full_output.txt still in root\n"
        f"Move to tests/output/ or delete it"
    )

def test_tests_directory_structure():
    """Verify tests/ directory has proper structure"""
    required_dirs = [
        Path("tests/unit"),
        Path("tests/integration"),
        Path("tests/gates")
    ]

    for dir_path in required_dirs:
        assert dir_path.exists(), f"Required directory missing: {dir_path}"
        assert dir_path.is_dir(), f"Not a directory: {dir_path}"

def test_discovery_in_correct_location():
    """Verify test_discovery.py is in tests/unit/ or tests/integration/"""
    wrong_path = Path("tests/test_discovery.py")
    unit_path = Path("tests/unit/test_discovery.py")
    integration_path = Path("tests/integration/test_discovery.py")

    # Should not exist in tests/ root
    assert not wrong_path.exists(), (
        f"test_discovery.py still in tests/ root\n"
        f"Move to tests/unit/ or tests/integration/"
    )

    # Should exist in either unit or integration
    assert unit_path.exists() or integration_path.exists(), (
        f"test_discovery.py not found in tests/unit/ or tests/integration/\n"
        f"It should be moved from tests/ to appropriate subdirectory"
    )

def test_safety_tools_in_correct_location():
    """Verify test_safety_tools_integration.py is in tests/integration/"""
    wrong_path = Path("tests/test_safety_tools_integration.py")
    correct_path = Path("tests/integration/test_safety_tools_integration.py")

    assert not wrong_path.exists(), (
        f"test_safety_tools_integration.py still in tests/ root\n"
        f"Move to tests/integration/"
    )

    assert correct_path.exists(), (
        f"test_safety_tools_integration.py not found in tests/integration/\n"
        f"It should be moved from tests/ to tests/integration/"
    )

def test_wrapping_in_correct_location():
    """Verify test_wrapping.py is in tests/unit/"""
    wrong_path = Path("tests/test_wrapping.py")
    correct_path = Path("tests/unit/test_wrapping.py")

    assert not wrong_path.exists(), (
        f"test_wrapping.py still in tests/ root\n"
        f"Move to tests/unit/"
    )

    assert correct_path.exists(), (
        f"test_wrapping.py not found in tests/unit/\n"
        f"It should be moved from tests/ to tests/unit/"
    )
