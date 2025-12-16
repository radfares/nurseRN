import pytest

from src.orchestration.conversation_context import ConversationContext
from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator, AgentTask


def test_plan_repairs_medical_research_pubmed_to_nursing_research():
    orch = IntelligentOrchestrator(client=None, use_resilient_execution=False)
    ctx = ConversationContext(project_name="test")

    plan = [
        AgentTask(
            task_id="task_1",
            agent_name="research_writing",
            action="generate_picot",
            params={"topic": "fall prevention"},
            depends_on=[],
        ),
        AgentTask(
            task_id="task_2",
            agent_name="medical_research",  # legacy name; should not do PubMed searches
            action="search_pubmed",
            params={"query": "<task_1.picot>"},
            depends_on=["task_1"],
        ),
    ]

    repaired = orch._validate_and_repair_plan(plan, user_message="fall prevention", context=ctx)
    assert repaired[1].agent_name == "nursing_research"


def test_plan_fills_missing_required_query_param():
    orch = IntelligentOrchestrator(client=None, use_resilient_execution=False)
    ctx = ConversationContext(project_name="test")

    plan = [
        AgentTask(
            task_id="task_1",
            agent_name="nursing_research",
            action="search_pubmed",
            params={},  # missing query should be filled
            depends_on=[],
        ),
    ]

    repaired = orch._validate_and_repair_plan(plan, user_message="CAUTI prevention", context=ctx)
    assert repaired[0].params.get("query") == "CAUTI prevention"


def test_generate_picot_output_normalization_adds_picot_key():
    orch = IntelligentOrchestrator(client=None, use_resilient_execution=False)

    output = {"full_question": "In adults (P), does X (I) vs Y (C) reduce Z (O) over 6 months (T)?"}
    normalized = orch._normalize_agent_output("generate_picot", output)
    assert normalized["picot"].startswith("In adults")

