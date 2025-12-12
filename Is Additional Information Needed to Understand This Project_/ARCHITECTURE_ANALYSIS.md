# Multi-Agent Architecture Analysis

**Created:** 2025-12-10
**Purpose:** Find the best architecture for nursing research workflow

---

## THE REAL PROBLEM

User input: "I want research on Foley catheter intervention"

Expected output: Complete research package with:
1. PICOT question
2. Literature with real PMIDs (validated, not retracted)
3. Evidence synthesis
4. Implementation plan
5. Data collection template

Current state: User must manually run 7 agents and copy/paste between them.

---

## ARCHITECTURE OPTIONS

### Option A: Sequential Pipeline (Current)

```
User → Agent1 → Agent2 → Agent3 → ... → Output
```

**How it works:**
- Fixed order of agent execution
- Each agent's output feeds next agent's input
- No branching, no parallel execution

**Pros:**
- Simple to implement
- Easy to debug
- Predictable execution

**Cons:**
- Slow (agents wait for each other)
- Inflexible (can't skip steps)
- One failure stops everything
- Doesn't match how real research works

**Verdict:** TOO RIGID. Real research isn't linear.

---

### Option B: Supervisor/Worker (Hierarchical)

```
        Supervisor
       /    |    \
   Agent1 Agent2 Agent3
```

**How it works:**
- Supervisor agent decides what to do
- Supervisor delegates to worker agents
- Workers report back to supervisor
- Supervisor decides next step

**Pros:**
- Flexible - supervisor can adapt
- Can handle failures gracefully
- Matches management structure

**Cons:**
- Supervisor becomes bottleneck
- Extra LLM calls for supervisor decisions
- Complex state management
- Supervisor can make bad decisions

**Verdict:** OVERHEAD TOO HIGH. Adds cost without clear benefit.

---

### Option C: Parallel Search + Merge

```
            Topic
           /  |  \
     PubMed ClinTrials Arxiv
           \  |  /
          Validator
              |
           Synthesis
```

**How it works:**
- Search multiple sources simultaneously
- Merge and deduplicate results
- Validate all citations
- Synthesize findings

**Pros:**
- Fast (parallel execution)
- Comprehensive coverage
- Good for literature review

**Cons:**
- Only solves search problem
- Doesn't help with PICOT or writing
- Results can be overwhelming

**Verdict:** GOOD FOR SEARCH PHASE ONLY.

---

### Option D: State Machine Workflow

```
[START] → [PICOT] → [SEARCH] → [VALIDATE] → [SYNTHESIZE] → [END]
              ↓           ↓           ↓
          [REFINE]   [EXPAND]    [FLAG]
```

**How it works:**
- Define explicit states and transitions
- Each state runs specific agents
- Transitions based on output quality
- Can loop back if results insufficient

**Pros:**
- Handles edge cases
- Can recover from poor results
- Checkpoints for resumption
- Matches real research process

**Cons:**
- Complex to design
- Need to define all transitions
- Testing all paths is hard

**Verdict:** MOST REALISTIC but complex.

---

### Option E: Goal-Oriented (Plan & Execute)

```
User Goal: "Research Foley intervention"
    ↓
Planner creates steps:
  1. Generate PICOT
  2. Search 3 databases
  3. Validate citations
  4. Write synthesis
    ↓
Executor runs steps
    ↓
Quality Check
    ↓
Output or Retry
```

**How it works:**
- Planner breaks goal into steps
- Executor runs steps in order
- Quality checker validates output
- Retry if quality insufficient

**Pros:**
- Adapts to different goals
- Clear separation of concerns
- Quality gate prevents bad output

**Cons:**
- Planner adds cost
- May plan poorly
- Still sequential

**Verdict:** PROMISING but planner adds overhead.

---

## RECOMMENDED ARCHITECTURE: Phased Pipeline with Quality Gates

This is a hybrid that takes the best of each:

```
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH PIPELINE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  PHASE 1: PLANNING                                          │
│  ┌─────────────────┐                                        │
│  │ Writing Agent   │ → PICOT Question                       │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼ [QUALITY GATE: Is PICOT searchable?]            │
│                                                              │
│  PHASE 2: SEARCH (Parallel)                                 │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ Nursing Agent   │  │ Medical Agent   │                   │
│  │ (PubMed)        │  │ (ClinTrials)    │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                             │
│           └────────┬───────────┘                             │
│                    ▼                                         │
│           ┌─────────────────┐                               │
│           │ Citation Agent  │ → Validate All PMIDs          │
│           └────────┬────────┘                               │
│                    │                                         │
│                    ▼ [QUALITY GATE: >3 valid studies?]      │
│                                                              │
│  PHASE 3: SYNTHESIS                                         │
│  ┌─────────────────┐                                        │
│  │ Writing Agent   │ → Literature Synthesis                 │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────┐                                        │
│  │ Data Agent      │ → Analysis Plan + Template             │
│  └────────┬────────┘                                        │
│           │                                                  │
│           ▼ [QUALITY GATE: Complete package?]               │
│                                                              │
│  OUTPUT: Save to Database                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## WHY THIS ARCHITECTURE

1. **Phases match real research process**
   - Planning → Search → Synthesis is how nurses actually do research

2. **Quality gates prevent garbage output**
   - If PICOT is bad, don't waste money searching
   - If no valid studies found, don't synthesize nothing

3. **Parallel search saves time**
   - PubMed and ClinicalTrials run simultaneously
   - Cuts search time in half

4. **No supervisor overhead**
   - Pipeline is predefined, no LLM deciding what to do next
   - Saves cost

5. **Checkpoints allow resumption**
   - If it fails at synthesis, don't redo search
   - State saved to database

---

## QUALITY GATES (Critical)

### Gate 1: PICOT Quality
```python
def check_picot_quality(picot_text: str) -> bool:
    """
    PICOT must have all 5 elements and be searchable.
    """
    required = ['population', 'intervention', 'comparison', 'outcome', 'time']
    has_all = all(elem.lower() in picot_text.lower() for elem in ['P:', 'I:', 'C:', 'O:', 'T:'])
    return has_all and len(picot_text) > 100
```

### Gate 2: Search Quality
```python
def check_search_quality(results: list) -> bool:
    """
    Must have at least 3 valid, non-retracted studies.
    """
    valid_count = sum(1 for r in results if r.get('validated') and not r.get('retracted'))
    return valid_count >= 3
```

### Gate 3: Output Completeness
```python
def check_output_complete(output: dict) -> bool:
    """
    Must have all required sections.
    """
    required = ['picot', 'articles', 'synthesis', 'analysis_plan']
    return all(key in output and output[key] for key in required)
```

---

## IMPLEMENTATION COST ESTIMATE

| Component | LLM Calls | Estimated Cost |
|-----------|-----------|----------------|
| PICOT Generation | 1 | $0.02 |
| PubMed Search | 1 | $0.02 |
| ClinTrials Search | 1 | $0.02 |
| Citation Validation | 1-3 | $0.03 |
| Literature Synthesis | 1 | $0.03 |
| Data Analysis Plan | 1 | $0.02 |
| **Total per run** | **6-8** | **~$0.15** |

This is reasonable for a complete research package.

---

## COMPARISON TO ALTERNATIVES

| Criteria | Sequential | Supervisor | Parallel | **Phased Pipeline** |
|----------|------------|------------|----------|---------------------|
| Cost | Low | High | Medium | **Medium** |
| Speed | Slow | Medium | Fast | **Fast** |
| Flexibility | None | High | Low | **Medium** |
| Quality Control | None | Variable | None | **Built-in** |
| Matches Research | No | No | Partial | **Yes** |
| Complexity | Simple | Complex | Medium | **Medium** |

---

## NEXT STEP

If you approve this architecture, I will:

1. Create `src/workflows/nursing_research_pipeline.py`
2. Implement the 3 phases with quality gates
3. Add database persistence
4. Integrate with `run_nursing_project.py`
5. Test with real query: "Foley catheter intervention"

---

**Do you approve this architecture?**
