"""
Agent capability specifications for planning/validation.

The orchestrator's "agent_name" / "action" contract is an orchestration-layer API,
not a direct reflection of underlying agent class methods. These specs describe
which (agent, action) pairs are intended to be used by the planner and enable
plan validation/repair without instantiating agents.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping, Sequence, Tuple


@dataclass(frozen=True)
class ActionSpec:
    action: str
    description: str
    required_params: Tuple[str, ...] = ()
    optional_params: Tuple[str, ...] = ()
    output_hints: Tuple[str, ...] = ()


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str
    actions: Mapping[str, ActionSpec] = field(default_factory=dict)

    def supports(self, action: str) -> bool:
        return action in self.actions

    def action_spec(self, action: str) -> ActionSpec | None:
        return self.actions.get(action)


def build_default_agent_specs() -> Dict[str, AgentSpec]:
    """
    Default orchestration-layer capabilities for the built-in agents.

    Keep these aligned with IntelligentOrchestrator._build_agent_query() templates
    and with the AgentRegistry's registered agents.
    """
    return {
        "nursing_research": AgentSpec(
            name="nursing_research",
            description=(
                "Broad nursing/healthcare research (PubMed-first), guidelines, and safety lookups."
            ),
            actions={
                "generate_picot": ActionSpec(
                    action="generate_picot",
                    description="Generate a PICOT question for a topic.",
                    required_params=("topic",),
                    output_hints=("picot",),
                ),
                "search_pubmed": ActionSpec(
                    action="search_pubmed",
                    description="Search PubMed for peer-reviewed healthcare literature.",
                    required_params=("query",),
                    output_hints=("results", "articles", "pmids"),
                ),
                "search": ActionSpec(
                    action="search",
                    description="General search for guidelines/standards/recalls or broader web context.",
                    required_params=("query",),
                    output_hints=("results",),
                ),
                "search_clinicaltrials": ActionSpec(
                    action="search_clinicaltrials",
                    description="Search ClinicalTrials.gov for trial data relevant to a query.",
                    required_params=("query",),
                    output_hints=("trials", "results"),
                ),
            },
        ),
        "academic_research": AgentSpec(
            name="academic_research",
            description="Academic discovery (preprints, citation discovery) and methodology support.",
            actions={
                "search_arxiv": ActionSpec(
                    action="search_arxiv",
                    description="Search arXiv for relevant preprints.",
                    required_params=("query",),
                    output_hints=("results",),
                ),
                "search_semantic_scholar": ActionSpec(
                    action="search_semantic_scholar",
                    description="Search Semantic Scholar for papers/citations.",
                    required_params=("query",),
                    output_hints=("results",),
                ),
                "search": ActionSpec(
                    action="search",
                    description="General academic search when a specific source isn't required.",
                    required_params=("query",),
                    output_hints=("results",),
                ),
            },
        ),
        "research_writing": AgentSpec(
            name="research_writing",
            description="Writing/synthesis help: PICOT refinement, drafting, and summarizing findings.",
            actions={
                "generate_picot": ActionSpec(
                    action="generate_picot",
                    description="Generate/refine a PICOT question for a topic.",
                    required_params=("topic",),
                    output_hints=("picot",),
                ),
                "synthesize": ActionSpec(
                    action="synthesize",
                    description="Synthesize findings into a concise nursing research summary.",
                    optional_params=("topic", "findings"),
                    output_hints=("summary", "text"),
                ),
            },
        ),
        # Note: "medical_research" is currently a document synthesis agent (legacy name retained).
        "medical_research": AgentSpec(
            name="medical_research",
            description="Document/library synthesis and cross-document comparison (legacy name).",
            actions={
                "synthesize_documents": ActionSpec(
                    action="synthesize_documents",
                    description="Synthesize local documents/library content into themes and recommendations.",
                    required_params=("query",),
                    output_hints=("summary", "themes", "citations", "text"),
                ),
            },
        ),
        "project_timeline": AgentSpec(
            name="project_timeline",
            description="Project management: milestones, deadlines, and planning.",
            actions={
                "get_milestones": ActionSpec(
                    action="get_milestones",
                    description="List milestones and deadlines for the current project.",
                    optional_params=("topic",),
                    output_hints=("milestones", "deadlines", "text"),
                ),
                "get_next_milestone": ActionSpec(
                    action="get_next_milestone",
                    description="Return the next upcoming milestone/deadline.",
                    output_hints=("next_milestone", "text"),
                ),
            },
        ),
        "data_analysis": AgentSpec(
            name="data_analysis",
            description="Study design and basic statistics support (sample size, power, test selection).",
            actions={
                "calculate_sample_size": ActionSpec(
                    action="calculate_sample_size",
                    description="Estimate sample size/power analysis for a given study design.",
                    required_params=("topic",),
                    optional_params=("design", "effect_size"),
                    output_hints=("sample_size", "plan", "text"),
                ),
            },
        ),
        "citation_validation": AgentSpec(
            name="citation_validation",
            description="Evidence grading, retraction checks, and citation quality validation.",
            actions={
                "validate": ActionSpec(
                    action="validate",
                    description="Validate citations/articles and grade evidence levels.",
                    optional_params=("topic", "articles"),
                    output_hints=("validated", "evidence", "retractions", "text"),
                ),
                "grade_evidence": ActionSpec(
                    action="grade_evidence",
                    description="Grade evidence level/quality for provided articles.",
                    optional_params=("articles",),
                    output_hints=("evidence", "text"),
                ),
            },
        ),
        "notion_documents": AgentSpec(
            name="notion_documents",
            description="Manage Notion workspace: search, read, and update pages.",
            actions={
                "search": ActionSpec(
                    action="search",
                    description="Search for pages and databases in Notion.",
                    required_params=("query",),
                    output_hints=("results", "text"),
                ),
                "read": ActionSpec(
                    action="read",
                    description="Read the content of a specific Notion page.",
                    required_params=("query",),
                    output_hints=("content", "text"),
                ),
                "update": ActionSpec(
                    action="update",
                    description="Update or create a page in Notion.",
                    required_params=("query",),
                    output_hints=("result", "text"),
                ),
            },
        ),
    }


def iter_action_specs(specs: Mapping[str, AgentSpec]) -> Iterable[ActionSpec]:
    for agent in specs.values():
        yield from agent.actions.values()

