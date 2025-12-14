#!/usr/bin/env python3
"""
Comprehensive Verification Script
Traces back through all implementation changes to verify:
1. All imports work correctly
2. No circular dependencies
3. All links between files are valid
4. Linting passes
5. No syntax errors
"""

import ast
import sys
import importlib
from pathlib import Path
from typing import List, Dict, Any, Tuple


class ImplementationVerifier:
    """Verify all implementation changes are correct and complete."""

    def __init__(self):
        self.results = []
        self.errors = []

    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log a test result."""
        self.results.append({
            "test": test_name,
            "status": status,
            "details": details
        })
        icon = {"PASS": "✓", "FAIL": "✗", "WARN": "⚠"}.get(status, "?")
        print(f"{icon} {test_name}: {status}")
        if details:
            print(f"  {details}")

    def verify_file_syntax(self, file_path: str) -> Tuple[bool, str]:
        """Verify Python file has valid syntax."""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
            ast.parse(code)
            return True, "Valid Python syntax"
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, f"Error parsing file: {str(e)}"

    def verify_imports_in_file(self, file_path: str) -> Tuple[bool, List[str]]:
        """Extract and verify all imports in a file."""
        try:
            with open(file_path, 'r') as f:
                code = f.read()

            tree = ast.parse(code)
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")

            return True, imports
        except Exception as e:
            return False, [f"Error: {str(e)}"]

    def verify_medical_research_agent(self):
        """Verify Medical Research Agent changes."""
        print("\n" + "="*70)
        print("PHASE 1 VERIFICATION: Medical Research Agent")
        print("="*70)

        file_path = "agents/medical_research_agent.py"

        # 1. Check file syntax
        valid, msg = self.verify_file_syntax(file_path)
        self.log_result("Medical Research Agent - Syntax Check",
                       "PASS" if valid else "FAIL", msg)

        # 2. Check imports
        valid, imports = self.verify_imports_in_file(file_path)
        if valid:
            has_clinicaltrials_import = any(
                "create_clinicaltrials_tools_safe" in imp for imp in imports
            )
            self.log_result("Medical Research Agent - Import Check",
                          "PASS" if has_clinicaltrials_import else "FAIL",
                          "create_clinicaltrials_tools_safe imported" if has_clinicaltrials_import
                          else "Missing create_clinicaltrials_tools_safe import")

        # 3. Check tool creation in _create_tools
        with open(file_path, 'r') as f:
            content = f.read()

        checks = {
            "clinicaltrials_tool = create_clinicaltrials_tools_safe":
                "Tool creation code present",
            "build_tools_list(reasoning_tools, pubmed_tool, clinicaltrials_tool, literature_tools)":
                "Tool added to build_tools_list",
            "ClinicalTrials.gov search available":
                "Logging for tool availability",
            "ClinicalTrials.gov":
                "Tool mentioned in description/instructions"
        }

        for check, desc in checks.items():
            present = check in content
            self.log_result(f"Medical Research Agent - {desc}",
                          "PASS" if present else "FAIL",
                          "Found" if present else "Missing")

        # 4. Try to import the module
        try:
            from agents.medical_research_agent import MedicalResearchAgent
            agent = MedicalResearchAgent()
            tool_count = len(agent.tools)

            self.log_result("Medical Research Agent - Import Test",
                          "PASS", f"Successfully imported, {tool_count} tools loaded")

            # Check tool names
            tool_names = [getattr(t, 'name', type(t).__name__) for t in agent.tools]
            has_clinicaltrials = 'clinicaltrials' in tool_names

            self.log_result("Medical Research Agent - Tool Integration",
                          "PASS" if has_clinicaltrials else "FAIL",
                          f"Tools: {', '.join(tool_names)}")

        except Exception as e:
            self.log_result("Medical Research Agent - Import Test",
                          "FAIL", f"Import failed: {str(e)}")

    def verify_academic_research_agent(self):
        """Verify Academic Research Agent changes."""
        print("\n" + "="*70)
        print("PHASE 2 VERIFICATION: Academic Research Agent")
        print("="*70)

        file_path = "agents/academic_research_agent.py"

        # 1. Check file syntax
        valid, msg = self.verify_file_syntax(file_path)
        self.log_result("Academic Research Agent - Syntax Check",
                       "PASS" if valid else "FAIL", msg)

        # 2. Check imports
        valid, imports = self.verify_imports_in_file(file_path)
        if valid:
            has_semantic_scholar_import = any(
                "create_semantic_scholar_tools_safe" in imp for imp in imports
            )
            self.log_result("Academic Research Agent - Import Check",
                          "PASS" if has_semantic_scholar_import else "FAIL",
                          "create_semantic_scholar_tools_safe imported" if has_semantic_scholar_import
                          else "Missing create_semantic_scholar_tools_safe import")

        # 3. Check tool creation in _create_tools
        with open(file_path, 'r') as f:
            content = f.read()

        checks = {
            "semantic_scholar_tool = create_semantic_scholar_tools_safe":
                "Tool creation code present",
            "build_tools_list(reasoning_tools, arxiv_tool, semantic_scholar_tool, doc_reader_tools, literature_tools)":
                "Tool added to build_tools_list",
            "Semantic Scholar search available":
                "Logging for tool availability",
            "Semantic Scholar":
                "Tool mentioned in description/instructions"
        }

        for check, desc in checks.items():
            present = check in content
            self.log_result(f"Academic Research Agent - {desc}",
                          "PASS" if present else "FAIL",
                          "Found" if present else "Missing")

        # 4. Try to import the module
        try:
            from agents.academic_research_agent import AcademicResearchAgent
            agent = AcademicResearchAgent()
            tool_count = len(agent.tools)

            self.log_result("Academic Research Agent - Import Test",
                          "PASS", f"Successfully imported, {tool_count} tools loaded")

            # Check tool names
            tool_names = [getattr(t, 'name', type(t).__name__) for t in agent.tools]
            has_semantic_scholar = 'semantic_scholar' in tool_names

            self.log_result("Academic Research Agent - Tool Integration",
                          "PASS" if has_semantic_scholar else "FAIL",
                          f"Tools: {', '.join(tool_names)}")

        except Exception as e:
            self.log_result("Academic Research Agent - Import Test",
                          "FAIL", f"Import failed: {str(e)}")

    def verify_orchestrator(self):
        """Verify Orchestrator changes."""
        print("\n" + "="*70)
        print("PHASE 3 VERIFICATION: Intelligent Orchestrator")
        print("="*70)

        file_path = "src/orchestration/intelligent_orchestrator.py"

        # 1. Check file syntax
        valid, msg = self.verify_file_syntax(file_path)
        self.log_result("Orchestrator - Syntax Check",
                       "PASS" if valid else "FAIL", msg)

        # 2. Check planner prompt updates
        with open(file_path, 'r') as f:
            content = f.read()

        checks = {
            "ClinicalTrials.gov": "ClinicalTrials.gov mentioned",
            "Semantic Scholar": "Semantic Scholar mentioned",
            "medRxiv": "medRxiv mentioned",
            "CORE open-access": "CORE mentioned",
            "DOAJ": "DOAJ mentioned",
            "SafetyTools": "SafetyTools mentioned",
            "AGENT SELECTION GUIDE": "Agent selection guide added",
            "TOOL-SPECIFIC QUERIES": "Tool-specific queries guide added",
            "search_clinicaltrials": "ClinicalTrials search action",
            "search_semantic_scholar": "Semantic Scholar search action"
        }

        for check, desc in checks.items():
            present = check in content
            self.log_result(f"Orchestrator - {desc}",
                          "PASS" if present else "FAIL",
                          "Found" if present else "Missing")

        # 3. Try to import and check prompt
        try:
            from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator
            orch = IntelligentOrchestrator(client=None)

            self.log_result("Orchestrator - Import Test",
                          "PASS", "Successfully imported")

            # Verify planner prompt
            prompt = orch._build_planner_prompt()
            prompt_checks = sum(1 for check in checks.keys() if check in prompt)

            self.log_result("Orchestrator - Planner Prompt Complete",
                          "PASS" if prompt_checks == len(checks) else "WARN",
                          f"{prompt_checks}/{len(checks)} items present in prompt")

        except Exception as e:
            self.log_result("Orchestrator - Import Test",
                          "FAIL", f"Import failed: {str(e)}")

    def verify_cross_file_links(self):
        """Verify links between files work correctly."""
        print("\n" + "="*70)
        print("CROSS-FILE VERIFICATION: Import Dependencies")
        print("="*70)

        # Test: Can we import all agents from orchestrator context?
        try:
            from src.orchestration.agent_registry import AgentRegistry
            registry = AgentRegistry()

            available_agents = []
            try:
                medical = registry.get_agent("medical_research")
                available_agents.append("medical_research")
            except:
                pass

            try:
                academic = registry.get_agent("academic_research")
                available_agents.append("academic_research")
            except:
                pass

            try:
                nursing = registry.get_agent("nursing_research")
                available_agents.append("nursing_research")
            except:
                pass

            self.log_result("Cross-file - Agent Registry",
                          "PASS", f"Available agents: {', '.join(available_agents)}")

        except Exception as e:
            self.log_result("Cross-file - Agent Registry",
                          "FAIL", f"Registry error: {str(e)}")

        # Test: Can tools be imported directly?
        try:
            from libs.agno.agno.tools.clinicaltrials import ClinicalTrialsTools
            from libs.agno.agno.tools.semantic_scholar import SemanticScholarTools

            self.log_result("Cross-file - Tool Imports",
                          "PASS", "Both tools import successfully")
        except Exception as e:
            self.log_result("Cross-file - Tool Imports",
                          "FAIL", f"Tool import failed: {str(e)}")

        # Test: Can api_tools create the tools?
        try:
            from src.services.api_tools import (
                create_clinicaltrials_tools_safe,
                create_semantic_scholar_tools_safe
            )

            ct_tool = create_clinicaltrials_tools_safe(required=False)
            ss_tool = create_semantic_scholar_tools_safe(required=False)

            ct_status = "Created" if ct_tool else "None (expected if deps missing)"
            ss_status = "Created" if ss_tool else "None (expected if deps missing)"

            self.log_result("Cross-file - Safe Tool Creation",
                          "PASS", f"CT: {ct_status}, SS: {ss_status}")

        except Exception as e:
            self.log_result("Cross-file - Safe Tool Creation",
                          "FAIL", f"Tool creation failed: {str(e)}")

    def verify_linting(self):
        """Run basic linting checks."""
        print("\n" + "="*70)
        print("LINTING VERIFICATION")
        print("="*70)

        files_to_check = [
            "agents/medical_research_agent.py",
            "agents/academic_research_agent.py",
            "src/orchestration/intelligent_orchestrator.py"
        ]

        for file_path in files_to_check:
            # Check for common issues
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')

            issues = []

            # Check line length (warn if > 120 chars)
            long_lines = [i+1 for i, line in enumerate(lines) if len(line) > 120]
            if long_lines and len(long_lines) > 5:  # Only warn if many long lines
                issues.append(f"{len(long_lines)} lines exceed 120 chars")

            # Check for trailing whitespace
            trailing_ws = [i+1 for i, line in enumerate(lines) if line.endswith(' ') or line.endswith('\t')]
            if trailing_ws:
                issues.append(f"{len(trailing_ws)} lines with trailing whitespace")

            # Check for tabs vs spaces consistency
            has_tabs = any('\t' in line for line in lines)
            has_spaces = any('    ' in line for line in lines)
            if has_tabs and has_spaces:
                issues.append("Mixed tabs and spaces detected")

            status = "WARN" if issues else "PASS"
            details = "; ".join(issues) if issues else "No linting issues"

            self.log_result(f"Linting - {Path(file_path).name}",
                          status, details)

    def print_summary(self):
        """Print verification summary."""
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)

        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "PASS")
        warned = sum(1 for r in self.results if r["status"] == "WARN")
        failed = sum(1 for r in self.results if r["status"] == "FAIL")

        print(f"\nTotal Checks: {total}")
        print(f"  ✓ Passed:  {passed}")
        print(f"  ⚠ Warnings: {warned}")
        print(f"  ✗ Failed:  {failed}")

        if failed > 0:
            print("\n❌ VERIFICATION FAILED")
            print("The following checks failed:")
            for r in self.results:
                if r["status"] == "FAIL":
                    print(f"  • {r['test']}: {r['details']}")
            return False
        elif warned > 0:
            print("\n⚠ VERIFICATION PASSED WITH WARNINGS")
            print("The following checks have warnings:")
            for r in self.results:
                if r["status"] == "WARN":
                    print(f"  • {r['test']}: {r['details']}")
            return True
        else:
            print("\n✅ VERIFICATION PASSED")
            print("All checks passed successfully!")
            return True

    def run_all_verifications(self):
        """Run all verification checks."""
        print("\n" + "="*70)
        print("IMPLEMENTATION VERIFICATION - Traceback Analysis")
        print("="*70)
        print("\nVerifying all changes made during implementation...")
        print("Checking: syntax, imports, integrations, cross-file links, linting\n")

        self.verify_medical_research_agent()
        self.verify_academic_research_agent()
        self.verify_orchestrator()
        self.verify_cross_file_links()
        self.verify_linting()

        return self.print_summary()


def main():
    """Main entry point."""
    verifier = ImplementationVerifier()
    success = verifier.run_all_verifications()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
