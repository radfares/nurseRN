#!/usr/bin/env python3
"""
Safer test script to verify agents are accessible and expose print_response.
"""

import sys
import os
from typing import Optional

ROOT = os.path.dirname(os.path.abspath(__file__))
# If your project root is one level up, uncomment the next line:
# sys.path.insert(0, os.path.dirname(ROOT))
sys.path.insert(0, ROOT)

# Add libs directory to path for agno module
LIBS_PATH = os.path.join(ROOT, "libs")
sys.path.insert(0, LIBS_PATH)

AGENT_SPECS = [
    # (import path, accessor name or None, friendly name)
    ("agents.nursing_research_agent", "nursing_research_agent", "Nursing Research Agent"),
    ("agents.medical_research_agent", "get_medical_research_agent", "Medical Research Agent"),
    ("agents.academic_research_agent", "academic_research_agent", "Academic Research Agent"),
    ("agents.research_writing_agent", "research_writing_agent", "Research Writing Agent"),
    ("agents.nursing_project_timeline_agent", "project_timeline_agent", "Project Timeline Agent"),
    ("agents.data_analysis_agent", "data_analysis_agent", "Data Analysis Agent"),
]

def safe_import(module_name: str):
    try:
        return __import__(module_name, fromlist=["*"])
    except Exception as e:
        print(f"❌ Failed to import {module_name}: {e}")
        return None

def resolve_agent(mod, accessor: Optional[str]):
    if mod is None:
        return None
    if accessor is None:
        return None
    # If accessor looks like a getter function name, call it if callable
    obj = getattr(mod, accessor, None)
    if callable(obj) and accessor.startswith("get_"):
        try:
            return obj()
        except Exception as e:
            print(f"❌ Error calling {mod.__name__}.{accessor}(): {e}")
            return None
    return obj

def has_print_response(agent) -> bool:
    return bool(agent) and callable(getattr(agent, "print_response", None))

def test_agents() -> int:
    failures = 0
    for module_path, accessor, friendly in AGENT_SPECS:
        print(f"\n🧪 Testing {friendly} ({module_path})...")
        mod = safe_import(module_path)
        agent = resolve_agent(mod, accessor)
        if agent is None:
            print(f"❌ {friendly}: Not available")
            failures += 1
            continue
        print(f"✅ {friendly}: Available")
        if has_print_response(agent):
            print(f"✅ {friendly}: Has callable print_response")
        else:
            print(f"❌ {friendly}: Missing callable print_response")
            failures += 1
    print("\n🎉 Agent testing complete!")
    return failures

if __name__ == "__main__":
    exit_code = test_agents()
    sys.exit(0 if exit_code == 0 else 2)
