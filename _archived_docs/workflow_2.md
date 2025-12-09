# Agent Workflow Automation - Phase 5: Intelligent Evolution
**Created**: 2025-12-07
**Previous Plan**: [WORKFLOW_AUTOMATION_PLAN.md](WORKFLOW_AUTOMATION_PLAN.md) (Phases 1-4 Complete)
**Status**: 🔄 Planning
**Focus**: LLM-Based Routing, Systemic Reviews, and Interaction Polish

## Rules and Instructions


## 📋 Executive Summary
With the foundation (Phase 1-2) and initial templates (Phase 3) integrated into the CLI (Phase 4), the "Smart Mode" currently relies on keyword matching (Regex). The next phase, **Phase 5**, aims to replace this heuristic layer with true semantic understanding and expand the system"s capability to handle complex, multi-day research tasks.

## 🎯 Phase 5 Objectives
1.  **Upgrade "Smart Mode" to Semantic Routing**: Replace/Augment capabilities of `QueryRouter` with an LLM-based classifier (using Mistral/OpenAI) to handle ambiguous queries.
2.  **Stateful Conversations**: Enable "Follow-up" questions in Smart Mode (currently every query is treated largely independently unless in a specific agent flow).
3.  **Advanced Workflow: Systematic Review**: Create a long-running workflow that performs exhaustive search across multiple agents and synthesizes results.
4.  **UI/UX Refinements**: Improve the CLI experience with streaming status indicators and better error recovery.

---

## 🛠 Detailed Tasks (Week 5+)

### 1. Intelligent Query Router (LLM Upgrade)
**Current State**: `src/orchestration/query_router.py` uses Regex.
**New Feature**: `LLMQueryRouter`.
-   **Implementation**: Use a lightweight LLM call to classify intent.
-   **Benefit**: Can distinguish "Help me write a PICOT" vs "Critique this PICOT" vs "Find articles about PICOT".
-   **Fallback**: Keep Regex as a fast fallback or pre-filter.

### 2. Context & Memory Persistence
**Current State**: `ContextManager` exists but is tied to the session/lifecycle of the orchestrator.
**New Feature**: `ProjectMemory`.
-   **Implementation**: Persist conversation turns and context variables in `project.db` (tables: `conversation_history`, `context_variables`).
-   **Integration**: Allow agents to read "last 5 turns" summary before answering.

### 3. Workflow: Systematic Review Generator
**New Template**: `systematic_review.yaml`
**Steps**:
1.  **Protocol Definition** (User + Research Writing Agent)
2.  **Parallel Search** (Medical + Nursing + Academic Agents)
3.  **Deduplication** (Python Logic)
4.  **Screening** (Citation Validation Agent - Check retraction/impact)
5.  **Synthesis** (Research Writing Agent)

### 4. Interactive "Smart Mode"
**Improvement**: Make Option 8 (Smart Mode) conversational.
-   Instead of `One Query -> Route -> Execute -> Return`, loop until user says "done".
-   Allow user to refine the route: "No, send that to the Writer, not the Researcher."

---

## �� Implementation Roadmap

| Task | Description | Est. Effort |
| :--- | :--- | :--- |
| **5.1** | **LLM Router Prototype**<br>Create `src/orchestration/llm_router.py` using `agno`. | 1 Day |
| **5.2** | **Memory Database Schema**<br>Add migrations for `conversation_history` to `project.db`. | 0.5 Days |
| **5.3** | **Smart Mode 2.0 Loop**<br>Update `run_nursing_project.py` to support conversational tracking. | 1 Day |
| **5.4** | **Systematic Review Workflow**<br>Code `src/workflows/systematic_review.py` and template. | 2 Days |
| **5.5** | **Testing & QA**<br>Verify no regressions in basic routing. | 1 Day |

---

## ✅ Success Criteria
-   [ ] **Routing Accuracy**: ambiguous queries (e.g., "Review this") correctly routed to Writer vs Researcher.
-   [ ] **Follow-ups**: System understands "give me 3 more" refers to the previous search.
-   [ ] **Safety**: Systematic Review workflow respects API rate limits.
-   [ ] **Stability**: All existing tests (Phase 1-4) continue to pass.

## 🔗 Dependencies
-   Requires `MISTRAL_API_KEY` or `OPENAI_API_KEY` for the router (already available).
-   Uses existing `ContextManager` logic as a base.
