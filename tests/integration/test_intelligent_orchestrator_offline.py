import pytest

from src.orchestration.conversation_context import ConversationContext
from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator, AgentTask


class _FakeAgent:
    def __init__(self):
        self.agent_name = "FakeAgent"
        self.queries = []

    def run(self, query: str, **_kwargs):
        self.queries.append(query)
        if query.startswith("Generate a PICOT question"):
            return {
                "full_question": "In older adults (P), does hourly rounding (I) vs usual care (C) reduce falls (O) over 6 months (T)?"
            }
        if query.startswith("Search PubMed for articles about:"):
            return {"results": [{"pmid": "123", "title": "Hourly rounding and falls"}]}
        return {"text": "ok"}


@pytest.mark.integration
def test_execute_plan_dependency_substitution_offline(monkeypatch):
    orch = IntelligentOrchestrator(client=None, use_resilient_execution=False)
    ctx = ConversationContext(project_name="test")
    fake = _FakeAgent()

    # Avoid instantiating real agents/tools.
    monkeypatch.setattr(orch.agent_registry, "get_agent", lambda _name: fake)

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
            agent_name="nursing_research",
            action="search_pubmed",
            params={"query": "<task_1.picot>"},
            depends_on=["task_1"],
        ),
    ]

    results = orch._execute_plan(plan, ctx, user_message="fall prevention")
    assert results["task_1"]["success"] is True
    assert results["task_2"]["success"] is True

    # The second query should include the resolved PICOT full question.
    assert any("older adults" in q for q in fake.queries), fake.queries

