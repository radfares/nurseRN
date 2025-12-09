# Agent Workflow Automation & Efficiency Enhancement Plan
**Created**: 2025-12-02
**Purpose**: Make the 6-agent system more autonomous, efficient, and productive
**Constraint**: NO changes to production files during testing phase

---

## Executive Summary

**Goal**: Transform the manual agent-selection workflow into an intelligent orchestration system that routes tasks automatically, coordinates multi-agent workflows, and eliminates repetitive manual steps.

**Current Pain Points**:
- Manual agent selection for every query
- No context sharing between agents
- Sequential-only execution (no parallelization)
- User must manually combine results
- Repetitive menu navigation

**Target State**:
- Single query automatically routes to appropriate agent(s)
- Agents share context via centralized store
- Parallel execution for independent research tasks
- Automatic result aggregation and synthesis
- Workflow templates for common research patterns

---

## Current System Analysis

### Agent Inventory (All in `agents/` directory)
1. **NursingResearchAgent** (482 LOC)
   - Multi-API healthcare research
   - Tools: PubMed, ClinicalTrials, medRxiv, Semantic Scholar, CORE, DOAJ, SafetyTools, SerpAPI
   - ArXiv/Exa disabled (not healthcare-appropriate)

2. **MedicalResearchAgent** (643 LOC)
   - PubMed specialist with hallucination prevention
   - Temperature=0, strict grounding validation
   - Complete audit logging

3. **AcademicResearchAgent** (357 LOC)
   - ArXiv for academic/statistical methods
   - Grounding checks for ArXiv IDs

4. **ResearchWritingAgent** (263 LOC)
   - Content synthesis, PICOT writing
   - No external tools (pure GPT-4o)

5. **ProjectTimelineAgent** (371 LOC)
   - Milestone tracking with MilestoneTools
   - Database-driven guidance

6. **DataAnalysisAgent** (640 LOC)
   - Statistical planning with Pydantic validation
   - Sample size calculations, data templates

### Existing Infrastructure (Can Leverage)
- ✅ **BaseAgent** inheritance pattern
- ✅ **Circuit breakers** for all APIs
- ✅ **Audit logging** (JSONL immutable trails)
- ✅ **Project-centric database** (7 tables)
- ✅ **Safe tool wrappers** with graceful fallback
- ✅ **94% test coverage**

### Critical Gaps (Need to Build)
- ❌ Inter-agent communication protocol
- ❌ Shared context manager
- ❌ Query intent classifier
- ❌ Workflow orchestrator
- ❌ Parallel execution engine
- ❌ Result aggregation layer

---

## Proposed Architecture: 3-Layer System

### Layer 1: Query Intelligence
**Purpose**: Analyze queries and determine agent requirements

**Components**:
```python
class QueryRouter:
    """Route queries to appropriate agent(s)"""
    def classify_intent(query: str) -> Intent
    def extract_entities(query: str) -> Entities
    def determine_agents(intent: Intent, entities: Entities) -> List[AgentKey]
    def estimate_confidence() -> float
```

**Intent Categories**:
- `PICOT_DEVELOPMENT`: Route to ResearchWritingAgent
- `LITERATURE_SEARCH`: Route to Medical/Nursing/AcademicResearchAgent
- `STATISTICAL_PLANNING`: Route to DataAnalysisAgent
- `TIMELINE_CHECK`: Route to ProjectTimelineAgent
- `MULTI_AGENT`: Needs orchestration

**Implementation**:
- Simple keyword/regex matching (Phase 1)
- GPT-4o classification (Phase 2, if needed)
- Confidence threshold: 0.8 (below = ask user)

---

### Layer 2: Agent Orchestration
**Purpose**: Coordinate agent execution and manage workflow state

**Components**:
```python
class WorkflowOrchestrator:
    """Coordinate multi-agent workflows"""
    def __init__(self, context_manager: ContextManager)
    def execute_single_agent(agent_key: str, query: str) -> Result
    def execute_parallel(agents: List[str], query: str) -> List[Result]
    def execute_workflow(template: WorkflowTemplate) -> WorkflowResult
    def aggregate_results(results: List[Result]) -> AggregatedResult
```

**Execution Modes**:
1. **Single Agent Mode**: Direct pass-through (current behavior)
2. **Parallel Mode**: Run multiple agents concurrently
3. **Sequential Mode**: Chain agents with context passing
4. **Template Mode**: Execute predefined workflow

---

### Layer 3: Context Management
**Purpose**: Enable agents to share results and maintain workflow state

**Components**:
```python
class ContextManager:
    """SQLite-backed shared context store"""
    def store_result(agent_key: str, result: Any, ttl: int = 3600)
    def get_result(agent_key: str) -> Optional[Any]
    def get_workflow_context(workflow_id: str) -> WorkflowContext
    def clear_expired()
```

**Database Schema** (new table):
```sql
CREATE TABLE workflow_context (
    context_id INTEGER PRIMARY KEY,
    workflow_id TEXT NOT NULL,
    agent_key TEXT NOT NULL,
    context_key TEXT NOT NULL,
    context_value TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    INDEX idx_workflow (workflow_id),
    INDEX idx_agent (agent_key)
);
```

---

## Workflow Templates (Common Research Patterns)

### Template 1: Quick Literature Search
**Pattern**: Single-agent, auto-routed
```yaml
name: quick_search
trigger: "find", "search", "literature"
steps:
  - classify_topic:  # healthcare → Medical, methods → Academic
  - route_to_agent
  - return_results
```

### Template 2: PICOT Development
**Pattern**: Writing → Validation → Refinement
```yaml
name: picot_development
steps:
  - agent: research_writing
    task: "Draft PICOT from: {{user_query}}"
  - validate_picot:  # Check P-I-C-O-T components
  - agent: nursing_research
    task: "Find 2 similar studies for: {{picot}}"
    context: inherit
  - agent: research_writing
    task: "Refine PICOT based on findings"
    context: inherit
```

### Template 3: Comprehensive Literature Review
**Pattern**: Parallel search → Synthesis
```yaml
name: literature_review
steps:
  - parallel:
      - agent: medical_research
        query: "{{topic}} clinical studies"
      - agent: nursing_research
        query: "{{topic}} quality improvement"
      - agent: academic_research
        query: "{{topic}} statistical methods"
  - agent: research_writing
    task: "Synthesize findings from 3 sources"
    context: inherit_all
```

### Template 4: Full Analysis Planning
**Pattern**: Timeline → Research → Analysis → Timeline Update
```yaml
name: analysis_planning
steps:
  - agent: project_timeline
    task: "When is data analysis due?"
  - agent: medical_research
    query: "{{intervention}} sample size studies"
  - agent: data_analysis
    task: "Calculate sample size for {{intervention}}"
    context: inherit
  - agent: project_timeline
    task: "Update milestone with n={{sample_size}}"
    context: inherit
```

---

## Implementation Plan (Non-Production Testing)

### Phase 1: Foundation (Week 1)
**Goal**: Build core infrastructure without touching production agents

**Tasks**:
1. Create `src/orchestration/` directory structure
2. Implement `ContextManager` with SQLite backend
3. Implement simple `QueryRouter` (keyword-based)
4. Write unit tests for each component
5. Create test fixtures for agent simulation

**Deliverables**:
- `src/orchestration/context_manager.py`
- `src/orchestration/query_router.py`
- `src/orchestration/orchestrator.py`
- `tests/orchestration/test_*.py`

**Test Strategy**:
```python
# Test with mock agents (not real agents)
class MockAgent:
    def run(self, query, **kwargs):
        return MockResult(content=f"Mock response to: {query}")

def test_parallel_execution():
    orchestrator = WorkflowOrchestrator(mock_context)
    results = orchestrator.execute_parallel(
        agents=['mock_medical', 'mock_academic'],
        query="Find CAUTI prevention studies"
    )
    assert len(results) == 2
    assert all(r.status == "success" for r in results)
```

---

### Phase 2: Integration Testing (Week 2)
**Goal**: Test with real agents in isolated environment

**Tasks**:
1. Create separate test database (`test_project.db`)
2. Test single-agent orchestration
3. Test parallel execution with 2 agents
4. Test context passing between agents
5. Measure performance (execution time, accuracy)

**Test Scenarios**:
```python
# Test 1: Single agent (baseline)
def test_single_agent_baseline():
    result = orchestrator.execute_single_agent(
        'medical_research',
        "Find CAUTI prevention articles"
    )
    assert result.agent_used == 'medical_research'
    assert len(result.findings) > 0

# Test 2: Parallel execution (should be faster)
def test_parallel_performance():
    start = time.time()
    results = orchestrator.execute_parallel(
        ['medical_research', 'academic_research'],
        "Find CAUTI prevention studies"
    )
    duration = time.time() - start
    assert duration < (2 * baseline_duration * 0.8)  # At least 20% faster

# Test 3: Context passing
def test_context_inheritance():
    result1 = orchestrator.execute_single_agent(
        'research_writing',
        "Draft PICOT for reducing patient falls"
    )
    context_manager.store_result('research_writing', result1.picot)
    
    result2 = orchestrator.execute_single_agent(
        'medical_research',
        "Find studies for: {{picot}}",  # Should inject from context
        use_context=True
    )
    assert result1.picot in result2.query_used
```

---

### Phase 3: Workflow Templates (Week 3)
**Goal**: Build and test common research workflows

**Tasks**:
1. Implement YAML workflow parser
2. Create 4 workflow templates (see above)
3. Test each template end-to-end
4. Measure time savings vs manual
5. Validate result quality

**Test Metrics**:
- **Execution Time**: Compare automated vs manual (target: 50% faster)
- **Accuracy**: Verify results match manual execution
- **User Effort**: Count clicks/commands (target: 80% reduction)

**Example Test**:
```python
def test_picot_workflow():
    workflow = load_workflow('picot_development')
    result = orchestrator.execute_workflow(
        workflow,
        variables={'user_query': 'Reduce catheter infections in ICU'}
    )
    
    # Verify workflow completed all steps
    assert len(result.steps_completed) == 4
    
    # Verify PICOT was refined
    assert result.final_picot != result.initial_draft
    
    # Verify literature was found
    assert len(result.supporting_studies) >= 2
```

---

### Phase 4: Production Integration (Week 4)
**Goal**: Add orchestration to `run_nursing_project.py` WITHOUT breaking existing workflow

**Approach**:
1. Add new menu option: "5. Smart Mode (Experimental)"
2. Preserve existing manual agent selection (options 1-6)
3. Add orchestrator as optional enhancement
4. Log all orchestration decisions for review

**Menu Structure**:
```python
def show_agent_menu():
    print("\nAvailable Agents:")
    print("1-6. [Existing agents - unchanged]")
    print("7. Smart Mode (Auto-route query to best agent)")
    print("8. Workflow Mode (Run predefined workflow)")
    print("back, exit")
```

**Implementation**:
```python
def handle_smart_mode():
    query = input("Enter your query: ")
    
    # Route query
    intent = router.classify_intent(query)
    agents = router.determine_agents(intent)
    
    # Show routing decision
    print(f"\nRouting to: {', '.join(agents)}")
    print(f"Confidence: {intent.confidence:.0%}")
    
    # Confirm with user
    if intent.confidence < 0.9:
        confirm = input("Proceed? (y/n): ")
        if confirm.lower() != 'y':
            return
    
    # Execute
    if len(agents) == 1:
        result = orchestrator.execute_single_agent(agents[0], query)
    else:
        result = orchestrator.execute_parallel(agents, query)
    
    # Display results
    display_result(result)
```

---

## Expected Benefits

### Quantitative
- **50% faster** literature reviews (parallel execution)
- **80% fewer clicks** for common tasks
- **95% automatic routing** for simple queries
- **3x productivity** for multi-agent workflows

### Qualitative
- Less context switching between agents
- Automatic result aggregation
- Reduced cognitive load
- More time for analysis vs navigation

---

## Risk Mitigation

### Risk 1: Orchestrator Routes to Wrong Agent
**Mitigation**:
- Show routing decision to user
- Require confirmation if confidence < 90%
- Log all routing decisions for review
- Keep manual mode as fallback

### Risk 2: Parallel Execution Causes API Rate Limits
**Mitigation**:
- Limit parallel execution to 3 agents max
- Existing circuit breakers handle failures
- Add exponential backoff if needed

### Risk 3: Context Passing Introduces Errors
**Mitigation**:
- Validate context data with Pydantic schemas
- Clear context after workflow completion
- Log all context operations to audit trail

### Risk 4: Workflow Templates Don't Match Use Cases
**Mitigation**:
- Start with 4 common patterns
- Gather user feedback on template usage
- Make templates easy to customize
- Support manual agent selection always

---

## Testing Checklist (Before Production)

### Unit Tests
- [ ] ContextManager stores and retrieves data correctly
- [ ] ContextManager expires old data (TTL)
- [ ] QueryRouter classifies 10 test queries correctly
- [ ] Orchestrator executes single agent
- [ ] Orchestrator executes parallel agents
- [ ] Orchestrator handles agent failures

### Integration Tests
- [ ] Real agent + orchestrator (single)
- [ ] Real agents + orchestrator (parallel)
- [ ] Context passing between real agents
- [ ] Workflow template execution (4 templates)

### Performance Tests
- [ ] Parallel execution faster than sequential
- [ ] Context operations under 100ms
- [ ] Workflow completion under 2 minutes
- [ ] No memory leaks in long-running sessions

### User Acceptance Tests
- [ ] Manual mode still works (no regression)
- [ ] Smart mode routes correctly (90%+ accuracy)
- [ ] Workflow mode saves time (50%+ faster)
- [ ] Error messages are clear and actionable

---

## File Structure (New Components)

```
src/orchestration/
├── __init__.py
├── context_manager.py       # Shared context SQLite store
├── query_router.py          # Intent classification & routing
├── orchestrator.py          # Workflow execution engine
└── workflow_loader.py       # YAML template parser

src/workflows/
├── __init__.py
├── templates/
│   ├── picot_development.yaml
│   ├── literature_review.yaml
│   ├── analysis_planning.yaml
│   └── quick_search.yaml
└── workflow_executor.py

tests/orchestration/
├── test_context_manager.py
├── test_query_router.py
├── test_orchestrator.py
├── test_workflow_loader.py
└── test_integration.py
```

---

## Success Criteria

### Phase 1 (Foundation) - Week 1
- ✅ All unit tests pass
- ✅ No dependencies on production agents
- ✅ 100% test coverage for orchestration module

### Phase 2 (Integration) - Week 2
- ✅ Real agents work with orchestrator
- ✅ Parallel execution 30%+ faster than sequential
- ✅ Context passing works correctly

### Phase 3 (Workflows) - Week 3
- ✅ 4 workflow templates implemented and tested
- ✅ Workflows 50%+ faster than manual
- ✅ Result quality matches manual execution

### Phase 4 (Production) - Week 4
- ✅ Smart mode added to menu (no breaking changes)
- ✅ 90%+ routing accuracy on test queries
- ✅ Zero regressions in existing functionality
- ✅ User documentation updated

---

## Next Steps (Immediate Actions)

1. **Create test environment**:
   ```bash
   mkdir -p src/orchestration
   mkdir -p src/workflows/templates
   mkdir -p tests/orchestration
   ```

2. **Implement ContextManager** (simplest component):
   - SQLite-backed key-value store
   - TTL expiration
   - Thread-safe operations

3. **Write unit tests for ContextManager**:
   - Test store/retrieve
   - Test expiration
   - Test concurrent access

4. **Test ContextManager in isolation** (no agents):
   - Verify all tests pass
   - Verify no performance issues
   - Verify no memory leaks

5. **Proceed to QueryRouter** only after ContextManager is solid

---

## Notes

- **DO NOT** modify any files in `agents/` during testing
- **DO NOT** change `run_nursing_project.py` until Phase 4
- **USE** mock agents for all Phase 1 testing
- **PRESERVE** existing functionality at all costs
- **MEASURE** everything (time, accuracy, user effort)

---

**Status**: ⏳ Planning Complete - Ready for Implementation
**Next**: Create test environment and implement ContextManager
