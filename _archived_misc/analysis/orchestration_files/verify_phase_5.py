#!/usr/bin/env python3
"""
Phase 5 Verification Script
Audit 'src/' for "Hardening" requirements:
1. Type Hints (Arguments & Return values)
2. Docstrings (Functions & Classes)

Generates report at: scripts/analysis/orchestration_files/phase_5_audit_report.md
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set, Optional
import datetime

class ComplianceCollector(ast.NodeVisitor):
    def __init__(self, rel_path: str):
        self.rel_path = rel_path
        self.issues = [] # List of strings describing issues
        self.stats = {
            "functions": 0,
            "functions_with_docstrings": 0,
            "functions_fully_typed": 0,
            "classes": 0,
            "classes_with_docstrings": 0
        }

    def visit_FunctionDef(self, node):
        self.stats["functions"] += 1
        
        # Check Docstring
        if ast.get_docstring(node):
            self.stats["functions_with_docstrings"] += 1
        else:
            self.issues.append(f"Function `{node.name}` missing docstring")

        # Check Type Hints
        # 1. Start with Assumption: Compliant
        missing_types = []
        
        # Check Arguments
        for arg in node.args.args:
            if arg.arg == 'self' or arg.arg == 'cls':
                continue # skip self/cls
            if arg.annotation is None:
                missing_types.append(f"arg `{arg.arg}`")
                
        # Check Return
        if node.returns is None:
            # __init__ usually returns None implicitly, strictly it should be -> None but acceptable to skip?
            # Phase 5 requirements usually strict. Let's flag it but note if it's init.
            if node.name != "__init__":
                missing_types.append("return value")
        
        if not missing_types:
            self.stats["functions_fully_typed"] += 1
        else:
            self.issues.append(f"Function `{node.name}` missing types: {', '.join(missing_types)}")

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.stats["classes"] += 1
        if ast.get_docstring(node):
            self.stats["classes_with_docstrings"] += 1
        else:
            self.issues.append(f"Class `{node.name}` missing docstring")
        self.generic_visit(node)

def get_python_files(directory: Path) -> List[Path]:
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                py_files.append(Path(root) / file)
    return py_files

def main():
    base_dir = Path.cwd()
    src_dir = base_dir / "src"
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = Path(__file__).parent / f"phase_5_audit_report_{timestamp}.md"
    
    print(f"🔍 Audit started on {src_dir}...")
    
    all_files_stats = {
        "functions": 0,
        "functions_with_docstrings": 0,
        "functions_fully_typed": 0,
        "classes": 0,
        "classes_with_docstrings": 0
    }
    
    file_issues = {} # filepath -> list of issues

    for file_path in get_python_files(src_dir):
        try:
            rel_path = str(file_path.relative_to(base_dir))
            content = file_path.read_text()
            tree = ast.parse(content)
            
            collector = ComplianceCollector(rel_path)
            collector.visit(tree)
            
            # Aggregate stats
            for k in all_files_stats:
                all_files_stats[k] += collector.stats[k]
                
            if collector.issues:
                file_issues[rel_path] = collector.issues
                
        except Exception as e:
            print(f"⚠️ Error parsing {file_path}: {e}")

    # Generate Report
    lines = []
    lines.append("# Phase 5 Hardening Audit Report")
    lines.append(f"**Date**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Calculate Percentages
    total_funcs = all_files_stats["functions"]
    total_classes = all_files_stats["classes"]
    
    doc_compat_funcs = all_files_stats["functions_with_docstrings"]
    type_compat_funcs = all_files_stats["functions_fully_typed"]
    doc_compat_classes = all_files_stats["classes_with_docstrings"]
    
    pct_doc_funcs = (doc_compat_funcs / total_funcs * 100) if total_funcs else 100
    pct_type_funcs = (type_compat_funcs / total_funcs * 100) if total_funcs else 100
    pct_doc_classes = (doc_compat_classes / total_classes * 100) if total_classes else 100
    
    lines.append(f"## 📊 Summary Statistics")
    lines.append(f"- **Total Files Scanned**: {len(get_python_files(src_dir))}")
    lines.append(f"- **Total Functions**: {total_funcs}")
    lines.append(f"- **Total Classes**: {total_classes}")
    lines.append("")
    lines.append("### Compliance Rates")
    lines.append(f"- **Function Docstrings**: {pct_doc_funcs:.1f}% ({doc_compat_funcs}/{total_funcs})")
    lines.append(f"- **Function Type Hints**: {pct_type_funcs:.1f}% ({type_compat_funcs}/{total_funcs})")
    lines.append(f"- **Class Docstrings**:    {pct_doc_classes:.1f}% ({doc_compat_classes}/{total_classes})")
    lines.append("")
    
    lines.append("## ❌ Compliance Issues")
    if not file_issues:
        lines.append("✅ **No issues found! Project is 100% compliant.**")
        print("\n✅ Project is 100% Phase 5 Compliant!")
    else:
        print(f"\n⚠️ Found issues in {len(file_issues)} files.")
        for fpath, issues in sorted(file_issues.items()):
            lines.append(f"### `{fpath}`")
            for issue in issues:
                lines.append(f"- {issue}")
            lines.append("")
            
    report_file.write_text("\n".join(lines))
    print(f"📝 Report generated: {report_file}")

if __name__ == "__main__":
    main()
