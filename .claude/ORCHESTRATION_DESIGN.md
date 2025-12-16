# Agent Orchestration Design Document

**Created:** 2025-12-10
**Status:** PLANNING

---

## 1. AGENT TEST RESULTS SUMMARY

| Agent | Quality | Output Type | Issues Found |
|-------|---------|-------------|--------------|
| Agent 1 (Nursing Research) | EXCELLENT | Real PMIDs, summaries | None |
| Agent 2 (Medical Research) | EXCELLENT | Real DOIs, trials | None |
| Agent 3 (Academic Research) | EXCELLENT | Real Arxiv IDs | None |
| Agent 4 (Research Writing) | GOOD | PICOT, structure | No citations (by design) |
| Agent 5 (Timeline) | WORKING | DB queries | Needs milestones in DB |
| Agent 6 (Data Analysis) | EXCELLENT | Statistical plans | Structured output |
| Agent 7 (Citation Validation) | EXCELLENT | Retraction checks | None |

**Key Finding:** All agents produce quality output individually. The problem is **coordination** - they don't work together effectively.

---

## 2. CURRENT ARCHITECTURE PROBLEMS

### Problem 1: No Central Controller
- Each agent runs independently
- No agent knows what other agents found
- User must manually coordinate

### Problem 2: Disconnected Workflows
- `verify_workflow_e2e.py` is a standalone script
- Main app (`run_nursing_project.py`) has basic menu
- Workflows exist but are not optimized

### Problem 3: No Information Handoff
- Agent 1 finds PMIDs → Agent 7 should validate them
- Agent 4 writes PICOT → Agent 1/2 should search for it
- These connections are manual, not automatic

---

## 3. PROPOSED ARCHITECTURE: SUPERVISOR AGENT

```
                    ┌─────────────────────┐
                    │   SUPERVISOR AGENT  │
                    │  (Project Manager)  │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
     ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐
     │   PHASE 1   │    │   PHASE 2   │    │   PHASE 3   │
     │   PLANNING  │    │  RESEARCH   │    │  SYNTHESIS  │
     └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
            │                  │                  │
    ┌───────┴───────┐   ┌──────┴──────┐   ┌──────┴──────┐
    │ Writing Agent │   │Nursing Agent│   │Writing Agent│
    │ (PICOT)       │   │Medical Agent│   │ (Synthesis) │
    │ Timeline Agent│   │Academic Agt │   │Data Analysis│
    └───────────────┘   │Citation Val │   └─────────────┘
                        └─────────────┘
```

### Supervisor Agent Responsibilities:
1. Receive user's research topic
2. Coordinate phases in order
3. Pass results between agents
4. Track progress in database
5. Handle failures gracefully

---

## 4. WORKFLOW DESIGN

### Workflow 1: Complete Research Project

```
USER INPUT: "I want to study fall prevention in elderly patients using bed alarms"

PHASE 1: PLANNING (Supervisor coordinates)
├── Step 1.1: Writing Agent → Generate PICOT question
├── Step 1.2: Timeline Agent → Create project milestones
└── Step 1.3: Data Analysis Agent → Create data collection plan

PHASE 2: RESEARCH (Supervisor coordinates)
├── Step 2.1: Nursing Agent → Search PubMed for PICOT
├── Step 2.2: Medical Agent → Search for clinical trials
├── Step 2.3: Academic Agent → Search for methodology papers
└── Step 2.4: Citation Agent → Validate ALL found PMIDs

PHASE 3: SYNTHESIS (Supervisor coordinates)
├── Step 3.1: Writing Agent → Synthesize literature review
├── Step 3.2: Writing Agent → Write methods section
└── Step 3.3: Data Analysis Agent → Generate analysis code

OUTPUT: Complete research package in database
```

### Workflow 2: Quick Literature Search

```
USER INPUT: "Find recent studies on pressure ulcer prevention"

SINGLE PHASE:
├── Step 1: Nursing Agent → Search PubMed
├── Step 2: Citation Agent → Validate results
└── Step 3: Writing Agent → Format findings

OUTPUT: Validated citation list
```

### Workflow 3: PICOT Development Only

```
USER INPUT: "Help me create a PICOT question for my capstone"

SINGLE PHASE:
├── Step 1: Writing Agent → Generate PICOT
├── Step 2: Nursing Agent → Verify searchable terms
└── Step 3: Writing Agent → Refine if needed

OUTPUT: Polished PICOT question
```

---

## 5. IMPLEMENTATION PLAN

### Phase 1: Create Supervisor Agent
- New file: `agents/supervisor_agent.py`
- Orchestrates other agents
- Tracks workflow state
- Reports progress to user

### Phase 2: Create Workflow Registry
- Define standard workflows
- Allow custom workflows
- Store in database

### Phase 3: Update Main Application
- Integrate supervisor into `run_nursing_project.py`
- Add workflow selection menu
- Show progress updates

### Phase 4: Test End-to-End
- Run complete workflows
- Verify agent handoffs
- Check database persistence

---

## 6. SUPERVISOR AGENT DESIGN

```python
class SupervisorAgent:
    """
    Central orchestrator that coordinates all research agents.
    Acts as project manager - assigns tasks, tracks progress, aggregates results.
    """

    def __init__(self):
        # Initialize all child agents
        self.nursing_agent = NursingResearchAgent()
        self.medical_agent = MedicalResearchAgent()
        self.academic_agent = AcademicResearchAgent()
        self.writing_agent = ResearchWritingAgent()
        self.timeline_agent = ProjectTimelineAgent()
        self.data_agent = DataAnalysisAgent()
        self.citation_agent = CitationValidationAgent()

        # State tracking
        self.current_project = None
        self.workflow_state = {}

    def execute_workflow(self, workflow_name: str, user_input: dict) -> dict:
        """Execute a named workflow with coordinated agent calls."""
        pass

    def _handoff_results(self, from_agent: str, to_agent: str, data: dict):
        """Pass results from one agent to another."""
        pass

    def _save_checkpoint(self, phase: str, results: dict):
        """Save workflow state to database for recovery."""
        pass
```

---

## 7. NEXT STEPS

1. [ ] Get user approval on this design
2. [ ] Create `supervisor_agent.py`
3. [ ] Create workflow definitions
4. [ ] Integrate with main app
5. [ ] Test complete workflows

---

## 8. QUESTIONS FOR USER

1. Do you want ONE supervisor or multiple workflow-specific supervisors?
2. Should workflows be customizable or fixed?
3. What's the most important workflow to implement first?
4. Do you want real-time progress updates or batch results?

---

*Waiting for approval before implementation.*
