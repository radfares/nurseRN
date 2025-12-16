# Agent Collaboration Design Document

**Author**: Claude Opus 4.5
**Date**: 2025-12-08
**Status**: AWAITING APPROVAL

---

## Executive Summary

**Key Discovery**: Agent collaboration infrastructure **ALREADY EXISTS** but is **NOT EXPOSED** to users.

The `ValidatedResearchWorkflow` already implements the full pipeline:
```
PICOT → Search → Validate → Filter → Write
```

**The actual gap**: Workflows are dead code - imported but never callable from the CLI.

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     run_nursing_project.py                       │
│                     (Main Entry Point)                           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    agent_selection_loop()                        │
│           Routes user to SINGLE AGENT only                       │
│                                                                  │
│   Options: 1-7 → Individual agents                               │
│   NO WORKFLOW OPTION EXISTS                                      │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┬─────────────┐
          ▼               ▼               ▼             ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Agent 1  │   │ Agent 2  │   │ Agent 3  │   │ Agent N  │
    │ Nursing  │   │ Medical  │   │ Academic │   │   ...    │
    │ Research │   │ Research │   │ Research │   │          │
    └──────────┘   └──────────┘   └──────────┘   └──────────┘
                          │
                   [ISOLATED - No handoffs]
```

### Dead Code (Imported but Unused)

```python
# run_nursing_project.py lines 43-46
from src.workflows.research_workflow import ResearchWorkflow
from src.workflows.parallel_search import ParallelSearchWorkflow
from src.workflows.timeline_planner import TimelinePlannerWorkflow
from src.workflows.validated_research_workflow import ValidatedResearchWorkflow
```

These are **never called** from the CLI.

---

## Existing Workflow Infrastructure

### `src/workflows/validated_research_workflow.py`

Already implements collaboration:

```python
class ValidatedResearchWorkflow(WorkflowTemplate):
    """
    PICOT → Search → Validate → Filter → Write
    """

    def execute(self, **kwargs):
        # Step 1: PICOT Development
        picot_result = self.orchestrator.execute_single_agent(
            agent=kwargs["picot_agent"],
            query=picot_query,
            workflow_id=self.workflow_id
        )

        # Step 2: Literature Search
        search_result = self.orchestrator.execute_single_agent(
            agent=kwargs["search_agent"],
            query=search_query,
            workflow_id=self.workflow_id
        )

        # Step 3: Validation (passes search results)
        validation_result = self.orchestrator.execute_single_agent(
            agent=kwargs["validation_agent"],
            query=f"Validate: {search_result.content}",  # ← HANDOFF
            workflow_id=self.workflow_id
        )

        # Step 4: Writing (passes PICOT + validated evidence)
        writing_result = self.orchestrator.execute_single_agent(
            agent=kwargs["writing_agent"],
            query=f"Draft based on: {picot_result.content} + {validation_result.content}",
            workflow_id=self.workflow_id
        )
```

**This is real collaboration** - Agent outputs flow to next agent as input.

---

## Supporting Infrastructure

### `src/orchestration/orchestrator.py`
- `execute_single_agent()` - Runs one agent
- `execute_parallel()` - Runs multiple agents concurrently
- `aggregate_results()` - Combines outputs
- Stores results in ContextManager

### `src/orchestration/context_manager.py`
- SQLite-backed shared state (`workflow_context.db`)
- Stores workflow results with TTL
- Enables stateless agents to share data

### `src/orchestration/query_router.py`
- **Regex-based** intent classification
- Routes to **single intent** (PICOT, SEARCH, WRITING, etc.)
- Does NOT detect multi-step workflows

---

## The Problem

| Component | Status | Issue |
|-----------|--------|-------|
| Workflow Classes | ✅ Built | Never instantiated from CLI |
| Orchestrator | ✅ Built | Not accessible to users |
| ContextManager | ✅ Built | Separate from project.db |
| QueryRouter | ⚠️ Limited | No workflow detection |
| CLI Menu | ❌ Missing | No "workflow" option |

**Result**: Users can only interact with isolated agents, despite collaboration code existing.

---

## Proposed Solution

### Architecture After Changes

```
┌─────────────────────────────────────────────────────────────────┐
│                     run_nursing_project.py                       │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    agent_selection_loop()                        │
│                                                                  │
│   Options: 1-7 → Individual agents                               │
│   NEW: 8 → Workflows Menu                                        │
│   NEW: 9 → Smart Mode (auto-route)                               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          ▼                               ▼
    ┌──────────────┐              ┌──────────────────┐
    │ Single Agent │              │ Workflow Menu    │
    │ (existing)   │              │ (NEW)            │
    └──────────────┘              └────────┬─────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
           ┌────────────────┐    ┌────────────────┐    ┌────────────────┐
           │ Research       │    │ Validated      │    │ Parallel       │
           │ Workflow       │    │ Research       │    │ Search         │
           │ (PICOT→Write)  │    │ (with grade)   │    │                │
           └────────────────┘    └────────────────┘    └────────────────┘
```

---

## Implementation Plan

### Phase 2A: Expose Existing Workflows (LOW RISK)

**Files to Modify:**
1. `run_nursing_project.py` - Add workflow menu option
2. No new code - just wire existing workflows to CLI

**Changes:**

```python
# run_nursing_project.py - Add to agent_selection_loop()

def show_workflow_menu():
    print("\n" + "="*60)
    print("WORKFLOW ORCHESTRATION")
    print("="*60)
    print("\n1. Research Workflow (PICOT → Search → Write)")
    print("2. Validated Research (+ Evidence Grading)")
    print("3. Parallel Search (Multi-database)")
    print("4. Back to agents")

def launch_workflow(choice, project_name):
    context_mgr = ContextManager()
    orchestrator = WorkflowOrchestrator(context_mgr)

    if choice == "1":
        workflow = ResearchWorkflow(orchestrator)
        # Collect inputs from user
        topic = input("Topic: ")
        setting = input("Setting: ")
        intervention = input("Intervention: ")

        result = workflow.execute(
            topic=topic,
            setting=setting,
            intervention=intervention,
            picot_agent=research_writing_agent,  # Uses PICOT expertise
            search_agent=nursing_research_agent,
            writing_agent=research_writing_agent
        )

        print_workflow_result(result)
```

### Phase 2B: Integrate Project DB (MEDIUM RISK)

**Problem**: Workflow results go to `workflow_context.db`, not `project.db`

**Solution**: After workflow completes, persist key outputs to project tables:
- `literature_findings` ← search results
- `writing_drafts` ← synthesis output
- `conversations` ← log workflow execution

**Files to Modify:**
1. `src/workflows/base.py` - Add project DB integration
2. `project_manager.py` - Add workflow result storage methods

### Phase 2C: Smart Router (HIGHER RISK)

**Problem**: User must manually choose workflow vs agent

**Solution**: Enhance QueryRouter to detect multi-step intents

```python
# New patterns in query_router.py
Intent.WORKFLOW_RESEARCH = "workflow_research"

workflow_patterns = [
    r'\b(start|begin|run)\b.*\b(research|project)\b',
    r'\bfull\b.*\b(literature|review)\b',
    r'\bcomplete\b.*\b(search|analysis)\b',
    r'\bfind.*validate.*write\b',
]
```

---

## Files to Modify

| File | Change Type | Risk |
|------|-------------|------|
| `run_nursing_project.py` | Add workflow menu | LOW |
| `src/orchestration/query_router.py` | Add workflow patterns | LOW |
| `src/workflows/base.py` | Add project DB hook | MEDIUM |
| `project_manager.py` | Add `save_workflow_result()` | MEDIUM |

**Files NOT Modified (per requirements):**
- Agent files (`agents/*.py`) - prompts unchanged
- Grounding validation - preserved as-is

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Workflow fails mid-execution | Medium | User loses partial results | Save each step to project DB |
| Agent timeout in workflow | Low | Workflow hangs | Existing timeout in orchestrator |
| Context DB out of sync | Medium | Stale data passed | Clear workflow context on start |
| Grounding validation bypassed | Low | Hallucinated citations | Validation runs per-agent (unchanged) |

---

## Testing Plan

Create `tests/test_agent_collaboration.py`:

```python
def test_research_agent_to_validation_agent_handoff():
    """Verify search results can be passed to validation"""
    # 1. Run nursing_research_agent with mock query
    # 2. Pass output to citation_validation_agent
    # 3. Assert validation grades are returned

def test_workflow_stores_to_project_db():
    """Verify workflow outputs persist to project.db"""
    # 1. Create test project
    # 2. Run ValidatedResearchWorkflow
    # 3. Query project.db for literature_findings
    # 4. Assert findings were saved

def test_validation_grades_persist():
    """Verify evidence grades are saved"""
    # 1. Run validation agent on test articles
    # 2. Query project.db
    # 3. Assert grades stored
```

---

## Sequence Diagram: Validated Research Workflow

```
User                CLI              Orchestrator          Agents
  │                  │                    │                   │
  │──"workflow 2"───▶│                    │                   │
  │                  │                    │                   │
  │◀─"Enter topic"───│                    │                   │
  │──"CAUTI"────────▶│                    │                   │
  │                  │                    │                   │
  │                  │──create workflow──▶│                   │
  │                  │                    │                   │
  │                  │                    │──PICOT query─────▶│ Writing Agent
  │                  │                    │◀─PICOT result─────│
  │                  │                    │                   │
  │                  │                    │──Search query────▶│ Nursing Research
  │                  │                    │◀─Articles + PMIDs─│
  │                  │                    │                   │
  │                  │                    │──Validate────────▶│ Citation Agent
  │                  │                    │◀─Grades + Flags───│
  │                  │                    │                   │
  │                  │                    │──Synthesize──────▶│ Writing Agent
  │                  │                    │◀─Draft────────────│
  │                  │                    │                   │
  │                  │◀─WorkflowResult────│                   │
  │◀─Display result──│                    │                   │
  │                  │                    │                   │
  │                  │──Save to project.db│                   │
```

---

## Deliverables

1. **Phase 2A**: Workflow menu in CLI (can demo immediately)
2. **Phase 2B**: Project DB integration (results persist)
3. **Phase 2C**: Smart routing (optional enhancement)

---

## Approval Request

**I am STOPPING here as requested.**

Before proceeding to implementation:
1. Do you approve this design?
2. Should I start with Phase 2A only (lowest risk)?
3. Any changes to the handoff flow?

---

## Appendix: Existing Agent Mapping

| Agent | Role in Workflow | Input From | Output To |
|-------|------------------|------------|-----------|
| Research Writing | PICOT development | User topic | Search Agent |
| Nursing Research | Literature search | PICOT | Validation Agent |
| Citation Validation | Evidence grading | Articles | Writing Agent |
| Research Writing | Synthesis | Validated articles | User |
| Data Analysis | Sample size | User params | (standalone) |
| Timeline | Deadline tracking | (standalone) | (optional context) |
