"""
Gate 2: Test Integrity Validation
Tests that ensure test files have meaningful assertions and aren't fake/trivial
"""

import pytest
import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple


class TestAnalyzer:
    """Analyzes test files for quality metrics"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = file_path.read_text()
        self.tree = ast.parse(self.content)

    def count_assertions(self) -> int:
        """Count assertion statements in test file"""
        assertion_count = 0
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assert):
                assertion_count += 1
            # Count pytest.raises, pytest.fail, etc. as direct calls
            elif isinstance(node, ast.Expr):
                if isinstance(node.value, ast.Call):
                    if hasattr(node.value.func, 'attr'):
                        if node.value.func.attr in ['raises', 'fail', 'warns', 'skip']:
                            assertion_count += 1
            # Count pytest.raises used in 'with' statements
            elif isinstance(node, ast.With):
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call):
                        if hasattr(item.context_expr.func, 'attr'):
                            if item.context_expr.func.attr in ['raises', 'warns']:
                                assertion_count += 1
        return assertion_count

    def count_test_functions(self) -> int:
        """Count test functions in file"""
        test_count = 0
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    test_count += 1
        return test_count

    def get_test_functions(self) -> List[ast.FunctionDef]:
        """Get all test function nodes"""
        tests = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('test_'):
                    tests.append(node)
        return tests

    def count_lines(self) -> int:
        """Count non-empty, non-comment lines"""
        lines = self.content.split('\n')
        code_lines = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                code_lines += 1
        return code_lines

    def count_mock_usage(self) -> int:
        """Count mock-related imports and usage"""
        mock_count = 0
        # Count mock imports
        mock_imports = ['Mock', 'MagicMock', 'patch', 'mock']
        for pattern in mock_imports:
            mock_count += self.content.count(pattern)
        return mock_count

    def has_pass_only_tests(self) -> List[str]:
        """Find tests that only contain 'pass' statement"""
        pass_only = []
        for node in self.get_test_functions():
            # Check if function body only has pass or docstring
            if len(node.body) == 1:
                if isinstance(node.body[0], ast.Pass):
                    pass_only.append(node.name)
                elif isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant):
                    # Docstring only
                    pass_only.append(node.name)
            elif len(node.body) == 2:
                # Docstring + pass
                if (isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[1], ast.Pass)):
                    pass_only.append(node.name)
        return pass_only

    def get_assertion_ratio(self) -> float:
        """Calculate ratio of assertions to code lines"""
        lines = self.count_lines()
        assertions = self.count_assertions()
        if lines == 0:
            return 0.0
        return assertions / lines

    def get_mock_ratio(self) -> float:
        """Calculate ratio of mock usage to code lines"""
        lines = self.count_lines()
        mocks = self.count_mock_usage()
        if lines == 0:
            return 0.0
        return mocks / lines


def get_all_test_files() -> List[Path]:
    """Get all test files in tests directory"""
    test_files = []
    test_dirs = [Path("tests/unit"), Path("tests/integration")]

    for test_dir in test_dirs:
        if test_dir.exists():
            test_files.extend(test_dir.glob("test_*.py"))

    return sorted(test_files)


def test_no_pass_only_tests():
    """Verify no test files contain pass-only tests (fake tests)"""
    test_files = get_all_test_files()
    pass_only_found = {}

    for test_file in test_files:
        # Skip the test integrity test itself
        if test_file.name == "test_test_integrity.py":
            continue

        analyzer = TestAnalyzer(test_file)
        pass_only = analyzer.has_pass_only_tests()

        if pass_only:
            pass_only_found[str(test_file)] = pass_only

    assert len(pass_only_found) == 0, (
        f"Found pass-only tests (fake tests):\n"
        f"{format_dict(pass_only_found)}\n"
        f"These tests have no assertions and always pass.\n"
        f"Remove them or add real assertions."
    )


def test_minimum_assertion_ratio():
    """Verify test files have minimum assertion-to-line ratio"""
    test_files = get_all_test_files()
    low_assertion_files = {}

    MIN_RATIO = 0.05  # At least 5% of lines should be assertions

    for test_file in test_files:
        # Skip certain test files that are configuration/fixtures
        if test_file.name in ["test_test_integrity.py", "__init__.py", "conftest.py"]:
            continue

        analyzer = TestAnalyzer(test_file)
        ratio = analyzer.get_assertion_ratio()

        if ratio < MIN_RATIO:
            assertions = analyzer.count_assertions()
            lines = analyzer.count_lines()
            low_assertion_files[str(test_file)] = {
                "ratio": round(ratio, 3),
                "assertions": assertions,
                "lines": lines
            }

    assert len(low_assertion_files) == 0, (
        f"Found test files with low assertion ratio (< {MIN_RATIO}):\n"
        f"{format_dict(low_assertion_files)}\n"
        f"Tests should have meaningful assertions.\n"
        f"Add more assertions or remove trivial code."
    )


def test_no_excessive_mocking():
    """Verify test files don't have excessive mocking (>90% mock ratio)"""
    test_files = get_all_test_files()
    excessive_mock_files = {}

    MAX_MOCK_RATIO = 0.9  # No more than 90% mocking

    for test_file in test_files:
        # Skip test integrity test
        if test_file.name == "test_test_integrity.py":
            continue

        analyzer = TestAnalyzer(test_file)
        mock_ratio = analyzer.get_mock_ratio()

        if mock_ratio > MAX_MOCK_RATIO:
            mocks = analyzer.count_mock_usage()
            lines = analyzer.count_lines()
            excessive_mock_files[str(test_file)] = {
                "ratio": round(mock_ratio, 3),
                "mocks": mocks,
                "lines": lines
            }

    assert len(excessive_mock_files) == 0, (
        f"Found test files with excessive mocking (> {MAX_MOCK_RATIO}):\n"
        f"{format_dict(excessive_mock_files)}\n"
        f"Tests should exercise real code paths.\n"
        f"Reduce mocking or refactor tests."
    )


def test_all_tests_have_assertions():
    """Verify all test functions have at least one assertion"""
    test_files = get_all_test_files()
    tests_without_assertions = {}

    for test_file in test_files:
        # Skip test integrity test
        if test_file.name == "test_test_integrity.py":
            continue

        analyzer = TestAnalyzer(test_file)

        # Check each test function
        for test_func in analyzer.get_test_functions():
            has_assertion = False

            # Look for assertions in the function body
            for node in ast.walk(test_func):
                if isinstance(node, ast.Assert):
                    has_assertion = True
                    break
                # Check for pytest assertions as direct calls
                elif isinstance(node, ast.Expr):
                    if isinstance(node.value, ast.Call):
                        if hasattr(node.value.func, 'attr'):
                            if node.value.func.attr in ['raises', 'fail', 'warns']:
                                has_assertion = True
                                break
                # Check for pytest.raises in 'with' statements
                elif isinstance(node, ast.With):
                    for item in node.items:
                        if isinstance(item.context_expr, ast.Call):
                            if hasattr(item.context_expr.func, 'attr'):
                                if item.context_expr.func.attr in ['raises', 'warns']:
                                    has_assertion = True
                                    break
                    if has_assertion:
                        break

            if not has_assertion:
                if str(test_file) not in tests_without_assertions:
                    tests_without_assertions[str(test_file)] = []
                tests_without_assertions[str(test_file)].append(test_func.name)

    assert len(tests_without_assertions) == 0, (
        f"Found test functions without assertions:\n"
        f"{format_dict(tests_without_assertions)}\n"
        f"Every test must have at least one assertion.\n"
        f"Add assertions or remove empty tests."
    )


def test_minimum_tests_per_file():
    """Verify test files have minimum number of tests (not nearly empty)"""
    test_files = get_all_test_files()
    sparse_test_files = {}

    MIN_TESTS = 1  # At least 1 test per file

    for test_file in test_files:
        # Skip test integrity test and utility files
        if test_file.name in ["test_test_integrity.py", "__init__.py"]:
            continue

        analyzer = TestAnalyzer(test_file)
        test_count = analyzer.count_test_functions()

        if test_count < MIN_TESTS:
            sparse_test_files[str(test_file)] = {
                "test_count": test_count,
                "lines": analyzer.count_lines()
            }

    assert len(sparse_test_files) == 0, (
        f"Found test files with too few tests (< {MIN_TESTS}):\n"
        f"{format_dict(sparse_test_files)}\n"
        f"Test files should have at least {MIN_TESTS} test(s).\n"
        f"Add tests or remove empty file."
    )


def format_dict(d: Dict) -> str:
    """Format dictionary for error messages"""
    lines = []
    for key, value in d.items():
        lines.append(f"  {key}: {value}")
    return "\n".join(lines)
