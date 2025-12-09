#!/usr/bin/env python3
"""
AST-based Unused Class Detector
Scans the src/ directory for class definitions and checks if they are used
anywhere in the codebase coverage (src/, tests/, scripts/).
Records findings to 'scripts/analysis/unused_classes_report.md'.
"""

import ast
import os
from pathlib import Path
from typing import Dict, Set, List
import sys
import datetime

def get_python_files(directory: str) -> List[Path]:
    """recursively yield all python files"""
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                py_files.append(Path(root) / file)
    return py_files

class ClassDefinitionCollector(ast.NodeVisitor):
    def __init__(self):
        self.defined_classes = {}  # name -> filepath

    def visit_ClassDef(self, node):
        self.defined_classes[node.name] = "CurrentFile" 
        self.generic_visit(node)

class UsageCollector(ast.NodeVisitor):
    def __init__(self, target_names: Set[str]):
        self.target_names = target_names
        self.found_usages = set()  # Names that were found used

    def visit_Name(self, node):
        if node.id in self.target_names:
            if isinstance(node.ctx, ast.Load): 
                self.found_usages.add(node.id)
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if node.attr in self.target_names:
            self.found_usages.add(node.attr)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node):
        for name in node.names:
            if name.name in self.target_names:
                self.found_usages.add(name.name)
        self.generic_visit(node)

def main():
    base_dir = Path.cwd()
    src_dir = base_dir / "src"
    # Output file path
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = Path(__file__).parent / f"unused_classes_report_{timestamp}.md"
    
    scan_dirs = [
        base_dir / "src",
        base_dir / "tests",
        base_dir / "scripts"
    ]
    
    print("🔍 Scanning for class definitions in src/...")
    
    # 1. Find Definitions
    definitions = {} 
    
    for file_path in get_python_files(src_dir):
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            collector = ClassDefinitionCollector()
            collector.visit(tree)
            
            for class_name in collector.defined_classes:
                definitions[class_name] = str(file_path.relative_to(base_dir))
        except Exception as e:
            print(f"⚠️  Could not parse {file_path}: {e}")

    all_class_names = set(definitions.keys())
    print(f"✅ Found {len(all_class_names)} classes defined.")

    # 2. Find Usages
    print("running usage analysis across project...")
    used_classes = set()
    
    all_scan_files = []
    for d in scan_dirs:
        if d.exists():
            all_scan_files.extend(get_python_files(d))
            
    for file_path in all_scan_files:
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            collector = UsageCollector(all_class_names)
            collector.visit(tree)
            used_classes.update(collector.found_usages)
        except Exception as e:
            pass

    # 3. Calculate Difference
    unused = all_class_names - used_classes
    
    # 4. Generate Report
    lines = []
    lines.append(f"# Unused Classes Report")
    lines.append(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"## Statistics")
    lines.append(f"- **Total Classes Defined in src/**: {len(all_class_names)}")
    lines.append(f"- **Used Classes**: {len(used_classes)}")
    lines.append(f"- **Potentially Unused**: {len(unused)}")
    lines.append("")
    
    print("\n📊 Results:")
    print(f"Total Classes: {len(all_class_names)}")
    print(f"Used Classes:  {len(used_classes)}")
    print(f"Unused Classes: {len(unused)}")
    
    if unused:
        lines.append("## ❌ Potentially Unused Classes")
        lines.append("| Class Name | Defined In |")
        lines.append("|------------|------------|")
        
        print("\n❌ Potentially Unused Classes:")
        print("-" * 60)
        
        unused_list = sorted(list(unused))
        for cls in unused_list:
            file_loc = definitions.get(cls, "Unknown")
            print(f"• {cls:<30} (defined in {file_loc})")
            lines.append(f"| `{cls}` | `{file_loc}` |")
            
        print("-" * 60)
        lines.append("")
        lines.append("> **Note:** This is a static analysis based on name matching. Dynamic usage (e.g. `getattr(module, 'ClassName')`) is not detected.")
    else:
        print("\n✅ All classes appear to be used!")
        lines.append("## ✅ All classes appear to be used!")

    # Write report
    report_file.write_text("\n".join(lines))
    print(f"\n📝 Report recorded to: {report_file}")

if __name__ == "__main__":
    main()
