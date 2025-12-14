import re
from pathlib import Path


AGENT_FILES = {
    "nursing_research": Path("agents/nursing_research_agent.py"),
    "medical_research": Path("agents/medical_research_agent.py"),
    "academic_research": Path("agents/academic_research_agent.py"),
    "research_writing": Path("agents/research_writing_agent.py"),
    "project_timeline": Path("agents/nursing_project_timeline_agent.py"),
    "data_analysis": Path("agents/data_analysis_agent.py"),
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_reasoning_tools_present_and_enabled():
    """Verify ReasoningTools(add_instructions=True) appears in all agents."""
    missing = []
    for name, path in AGENT_FILES.items():
        src = read(path)
        if re.search(r"ReasoningTools\(\s*add_instructions\s*=\s*True\s*\)", src) is None:
            missing.append(name)

    assert not missing, f"Missing ReasoningTools(add_instructions=True) in: {', '.join(missing)}"


def test_reasoning_tools_is_first_in_tools_list():
    """Verify ReasoningTools is first argument in tools list construction for each agent."""
    offenders = []
    for name, path in AGENT_FILES.items():
        src = read(path)
        # Accept two common patterns:
        # 1) tools = build_tools_list(reasoning_tools, ...)
        # 2) return [reasoning_tools, other_tool]
        has_build = re.search(r"build_tools_list\(\s*reasoning_tools\s*,", src) is not None
        has_list_first = re.search(r"return \[\s*reasoning_tools\s*,", src) is not None

        if not (has_build or has_list_first):
            offenders.append(name)

    assert not offenders, f"ReasoningTools not first in tools list for: {', '.join(offenders)}"

