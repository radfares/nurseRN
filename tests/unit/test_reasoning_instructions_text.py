from pathlib import Path

import pytest

from agents.academic_research_agent import AcademicResearchAgent
from agents.data_analysis_agent import DataAnalysisAgent
from agents.medical_research_agent import MedicalResearchAgent
from agents.nursing_project_timeline_agent import ProjectTimelineAgent
from agents.nursing_research_agent import NursingResearchAgent
from agents.research_writing_agent import ResearchWritingAgent

from agent_config import is_reasoning_block_enabled


AGENT_FILES = {
    "nursing_research": Path("agents/nursing_research_agent.py"),
    "medical_research": Path("agents/medical_research_agent.py"),
    "academic_research": Path("agents/academic_research_agent.py"),
    "research_writing": Path("agents/research_writing_agent.py"),
    "project_timeline": Path("agents/nursing_project_timeline_agent.py"),
    "data_analysis": Path("agents/data_analysis_agent.py"),
}

EXPECTED_MARKERS = {
    "nursing_research": [
        "reasoning approach (clinical",
        "break down complex questions",
        "assumptions",
        "trade-offs",
        "alternatives",
    ],
    "medical_research": [
        "reasoning approach (pubmed-first",
        "break down complex questions",
        "assumptions",
        "trade-offs",
        "alternatives",
    ],
    "academic_research": [
        "reasoning approach (academic",
        "break down complex questions",
        "assumptions",
        "trade-offs",
        "alternatives",
    ],
    "research_writing": [
        "reasoning approach (writing",
        "break down complex writing requests",
        "assumptions",
        "trade-offs",
        "alternatives",
    ],
    "project_timeline": [
        "reasoning approach (project planning",
        "break down complex requests",
        "assumptions",
        "trade-offs",
        "alternatives",
    ],
    "data_analysis": [
        "reasoning approach (statistical",
        "break down complex questions",
        "assumptions",
        "trade-offs",
        "alternatives",
    ],
}

RUNTIME_MARKERS = [
    "reasoning approach",
    "break down complex",
    "assumptions",
    "trade-offs",
]

RUNTIME_AGENT_CLASSES = [
    ("nursing_research", NursingResearchAgent),
    ("medical_research", MedicalResearchAgent),
    ("academic_research", AcademicResearchAgent),
    ("research_writing", ResearchWritingAgent),
    ("project_timeline", ProjectTimelineAgent),
    ("data_analysis", DataAnalysisAgent),
]


def test_reasoning_blocks_present_in_instructions_text():
    """Static check: ensure each agent file includes the reasoning block markers."""
    missing = {}
    for name, path in AGENT_FILES.items():
        text = path.read_text(encoding="utf-8").lower()
        markers = EXPECTED_MARKERS[name]
        missing_markers = [marker for marker in markers if marker not in text]
        if missing_markers:
            missing[name] = missing_markers

    assert not missing, f"Missing reasoning markers: {missing}"


@pytest.mark.parametrize("name,agent_cls", RUNTIME_AGENT_CLASSES)
def test_agent_instructions_runtime_contains_reasoning_markers(name, agent_cls):
    """Runtime smoke test: instantiated agents expose reasoning markers in instructions."""
    agent_instance = agent_cls()
    instructions = str(getattr(agent_instance.agent, "instructions", "") or "").lower()

    missing_markers = [marker for marker in RUNTIME_MARKERS if marker not in instructions]
    if is_reasoning_block_enabled():
        assert not missing_markers, f"{name} missing markers at runtime: {missing_markers}"
    else:
        assert missing_markers, f"{name} should omit reasoning markers when REASONING_BLOCK is off"


def test_reasoning_block_can_be_disabled(monkeypatch):
    """Feature flag: REASONING_BLOCK=off removes standardized reasoning block at runtime."""
    monkeypatch.setenv("REASONING_BLOCK", "off")
    agent_instance = ResearchWritingAgent()
    instructions = str(getattr(agent_instance.agent, "instructions", "") or "").lower()

    assert "reasoning approach (writing" not in instructions
