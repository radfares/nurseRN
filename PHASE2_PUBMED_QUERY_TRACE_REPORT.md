# Phase 2 — PubMed Query=None Trace Report

## Status: ✅ QUERY FLOW VALIDATED - No None detected in current implementation

**Date**: 2025-12-12
**Test**: Orchestrator → Medical Research Agent → PubMed Tool
**Result**: Query parameter flows correctly through entire chain

---

## Executive Summary

Successfully traced the PubMed `query` parameter through the entire call chain from user input to tool execution. **The query is NOT None** in the tested scenario. The defensive guards added in Phase 1 are working correctly, and the parameter validation prevents None from reaching the PubMed API.

### Key Finding
The earlier issue where "PubMed tool isn't loading because Pydantic blocks it with query=None" is **not currently reproducible** in the standard orchestration flow. Either:
1. It was fixed by the defensive guards added earlier
2. It occurs in a different edge case scenario
3. It happens when the agent receives an unclear prompt

---

## Trace Results

### Complete Query Flow (Tested Scenario)

```
User Input:
  "Find research articles about diabetes management in elderly patients"
      ↓
1. Orchestrator LLM Planning
   Raw plan from LLM:
   {
     "tasks": [{
       "task_id": "task_1",
       "agent_name": "medical_research",
       "action": "search_pubmed",
       "params": {
         "query": "diabetes management in elderly patients"  ← ✅ Query present
       }
     }]
   }
      ↓
2. Task Params (After Parsing)
   Task task_1 params: {'query': 'diabetes management in elderly patients'}  ← ✅ Query present
      ↓
3. Resolved Params (After Dependency Resolution)
   Resolved params for task_1: {'query': 'diabetes management in elderly patients'}  ← ✅ Query present
      ↓
4. Agent Query Builder
   _build_agent_query(
     action='search_pubmed',
     params={'query': 'diabetes management in elderly patients'}  ← ✅ Query present
   )
   Built agent query: 'Search PubMed for articles about: diabetes management in elderly patients'
      ↓
5. Agent Receives Natural Language Query
   Agent input: "Search PubMed for articles about: diabetes management in elderly patients"
      ↓
6. Agent Tool Call (LLM decides tool arguments)
   [Agent's LLM extracts query from natural language prompt]
      ↓
7. PubMed Tool Entrypoint
   search_pubmed called with:
     query='diabetes management in elderly patients'  ← ✅ Query present, correct value
     max_results=10
      ↓
8. Defensive Guard Check
   ✅ Passed: query is not None and is a string
      ↓
9. PubMed API Call
   GET https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
   ?term=diabetes+management+in+elderly+patients  ← ✅ Query correctly formatted
      ↓
10. Success
    ✅ 10 articles retrieved and returned
```

---

## Logging Infrastructure Installed

### Location 1: PubMed Tool Entrypoint
**File**: `libs/agno/agno/tools/pubmed.py:152-160`

```python
def search_pubmed(self, query: str, max_results: Optional[int] = 10) -> str:
    # PHASE 2 TRACE: Log entry point with actual parameter values
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 PHASE2 TRACE: search_pubmed called with query={query!r} max_results={max_results}")

    # Defensive guard: validate query parameter
    if not query or not isinstance(query, str):
        logger.error(f"❌ PHASE2 TRACE: Invalid query parameter: query={query!r} type={type(query)}")
        raise ValueError("search_pubmed requires a non-empty string query")
```

### Location 2: Orchestrator Plan Parsing
**File**: `src/orchestration/intelligent_orchestrator.py:156-170`

```python
def _parse_plan(self, plan_json: Dict[str, Any]) -> List[AgentTask]:
    # PHASE 2 TRACE: Log the raw plan from LLM
    logger.info(f"🔍 PHASE2 TRACE: Raw plan from LLM: {json.dumps(plan_json, indent=2)}")

    for task_dict in plan_json.get("tasks", []):
        task = AgentTask(...)
        # PHASE 2 TRACE: Log each task's params
        logger.info(f"🔍 PHASE2 TRACE: Task {task.task_id} params: {task.params}")
```

### Location 3: Parameter Resolution
**File**: `src/orchestration/intelligent_orchestrator.py:437-438`

```python
resolved_params = self._resolve_dependencies(task.params, results)
# PHASE 2 TRACE: Log resolved params after dependency resolution
logger.info(f"🔍 PHASE2 TRACE: Resolved params for {task.task_id}: {resolved_params}")
```

### Location 4: Query Builder
**File**: `src/orchestration/intelligent_orchestrator.py:583-617`

```python
def _build_agent_query(self, action: str, params: Dict[str, Any]) -> str:
    # PHASE 2 TRACE: Log inputs to query builder
    logger.info(f"🔍 PHASE2 TRACE: _build_agent_query(action={action!r}, params={params})")

    built_query = template.format(**params)
    # PHASE 2 TRACE: Log the built natural language query
    logger.info(f"🔍 PHASE2 TRACE: Built agent query: {built_query!r}")
```

---

## Potential Edge Cases Where query=None Could Occur

Based on the code analysis, here are scenarios where `query=None` might happen:

### 1. LLM Planning Failure
**Scenario**: LLM doesn't include query param in the plan

```json
{
  "tasks": [{
    "action": "search_pubmed",
    "params": {}  ← Missing query!
  }]
}
```

**Why it might happen**:
- Unclear user prompt
- LLM misunderstands the request
- System prompt doesn't emphasize required params

**Solution**: Already protected by defensive guard at tool entrypoint

### 2. Template Formatting Error
**Scenario**: Template requires `{query}` but params has different key

```python
template = "Search PubMed for articles about: {query}"
params = {"topic": "diabetes"}  # Wrong key!
```

**Why it might happen**:
- Inconsistent param naming between planner and templates
- LLM uses wrong param name

**Current behavior**: Catches KeyError, logs warning, falls back to generic query

### 3. Dependency Resolution Failure
**Scenario**: Task depends on previous result that didn't produce expected output

```python
params = {"query": "<task_1.picot>"}  # Reference to previous task
results = {"task_1": {"output": None}}  # Previous task failed
```

**Why it might happen**:
- Dependent task fails or returns unexpected structure
- Dependency path is incorrect

**Solution**: _resolve_dependencies returns None for missing paths

### 4. Agent LLM Misinterprets Natural Language Query
**Scenario**: Agent receives "Search PubMed for articles about: diabetes" but LLM calls tool with wrong args

**Agent receives**: `"Search PubMed for articles about: diabetes"`
**Agent LLM might call**: `search_pubmed(query=None)` if it fails to extract the query

**Why it might happen**:
- Agent's LLM doesn't properly parse the natural language instruction
- Tool schema doesn't make `query` param clear enough

**Solution**: Defensive guard blocks this at tool entrypoint

---

## Defensive Measures in Place

### 1. Tool-Level Validation (Primary Defense)
**Location**: `libs/agno/agno/tools/pubmed.py:157-160`

```python
if not query or not isinstance(query, str):
    logger.error(f"❌ PHASE2 TRACE: Invalid query parameter: query={query!r} type={type(query)}")
    raise ValueError("search_pubmed requires a non-empty string query")
```

**Protects against**:
- `query=None`
- `query=""`
- `query=123` (wrong type)

### 2. Pydantic Schema Validation (Secondary Defense)
**Location**: Schema generation from type hints

```python
def search_pubmed(self, query: str, max_results: Optional[int] = 10) -> str:
    # Type hint `query: str` (no Optional, no default)
    # → Pydantic marks as required in schema
    # → OpenAI validates before tool execution
```

**Protects against**:
- Missing query argument in tool call
- Wrong type (if strict mode enabled)

### 3. Comprehensive Logging (Diagnostic Tool)
All critical points now log with 🔍 PHASE2 TRACE markers:
- Plan creation
- Param resolution
- Query building
- Tool entry

**Enables**: Fast root cause analysis when issues occur

---

## Test Coverage

### Test 1: Standard Orchestration Flow
**File**: `test_pubmed_query_trace.py`
**Scenario**: User asks for research articles on a medical topic
**Result**: ✅ Query flows correctly, PubMed returns results
**Trace**: Complete logging from user input to API response

### Test 2: Missing Scenarios (Recommended)
These scenarios should be tested to verify defensive measures:

```python
# Test A: LLM plan missing query param
plan = {"tasks": [{"action": "search_pubmed", "params": {}}]}
# Expected: ValueError at tool entrypoint

# Test B: Dependency resolution returns None
params = {"query": "<missing_task.field>"}
# Expected: Query template formatting fails gracefully

# Test C: Agent LLM calls tool with None
# Mock agent to directly call search_pubmed(query=None)
# Expected: ValueError with clear error message
```

---

## Recommendations

### 1. Enhance LLM Planner Prompt
**Why**: Prevent None queries at the source

**Add to system prompt**:
```
CRITICAL: For search_pubmed action, the 'query' parameter is REQUIRED.
Always extract the search topic from the user's request and include it:

  CORRECT: {"action": "search_pubmed", "params": {"query": "diabetes management"}}
  WRONG: {"action": "search_pubmed", "params": {}}
```

### 2. Add Param Validation to Orchestrator
**Why**: Catch missing params before execution

```python
def _validate_task_params(self, task: AgentTask) -> None:
    required_params = {
        "search_pubmed": ["query"],
        "generate_picot": ["topic"],
        "calculate_sample_size": ["design", "effect_size"]
    }

    if task.action in required_params:
        for param in required_params[task.action]:
            if param not in task.params or task.params[param] is None:
                raise ValueError(f"Missing required param '{param}' for action '{task.action}'")
```

### 3. Improve Agent Tool Call Guidance
**Why**: Help agent LLM extract params from natural language

**Add to agent instructions**:
```
When you receive "Search PubMed for articles about: X", you MUST call:
  search_pubmed(query="X")

Extract the search topic after the colon and pass it as the query parameter.
```

### 4. Add Unit Tests for Edge Cases
**Location**: `tests/unit/test_orchestrator_edge_cases.py`

Test each potential failure mode:
- Missing query in plan
- None returned from dependency resolution
- Agent LLM fails to extract query from natural language
- Template formatting errors

---

## Conclusion

### ✅ Current Status
- Query flow is working correctly in standard scenarios
- Defensive guards prevent query=None from reaching PubMed API
- Comprehensive logging enables fast diagnosis

### 🔍 Mystery Solved?
The original issue ("PubMed isn't loading, it's being called with query=None") is **not currently reproducible**. Possible explanations:
1. ✅ Already fixed by Phase 1 defensive guards
2. ⚠️ Occurs in edge case not tested (see recommendations)
3. ℹ️ Happens with specific unclear user prompts

### 📋 Next Steps
1. Review historic logs to find actual query=None occurrence
2. Implement recommended preventive measures
3. Add unit tests for edge cases
4. Monitor production for query=None errors with new logging

---

## Files Modified

1. **`libs/agno/agno/tools/pubmed.py`** (lines 152-160)
   - Added entrypoint logging
   - Enhanced error message for validation failures

2. **`src/orchestration/intelligent_orchestrator.py`** (multiple locations)
   - Added plan parsing logging (lines 156-170)
   - Added param resolution logging (lines 437-438)
   - Added query builder logging (lines 583-617)

3. **`test_pubmed_query_trace.py`** (new file)
   - End-to-end trace test
   - Validates entire query flow

4. **`PHASE2_PUBMED_QUERY_TRACE_REPORT.md`** (this document)
   - Comprehensive trace analysis
   - Edge case documentation
   - Recommendations

---

## Trace Example Output

```
🔍 PHASE2 TRACE: Raw plan from LLM: {
  "tasks": [{
    "params": {"query": "diabetes management in elderly patients"}
  }]
}

🔍 PHASE2 TRACE: Task task_1 params: {'query': 'diabetes management in elderly patients'}

🔍 PHASE2 TRACE: Resolved params for task_1: {'query': 'diabetes management in elderly patients'}

🔍 PHASE2 TRACE: _build_agent_query(action='search_pubmed', params={'query': 'diabetes management in elderly patients'})

🔍 PHASE2 TRACE: Built agent query: 'Search PubMed for articles about: diabetes management in elderly patients'

🔍 PHASE2 TRACE: search_pubmed called with query='diabetes management in elderly patients' max_results=10

✅ PubMed API called successfully with query
```

---

**Report Generated**: 2025-12-12
**Status**: Phase 2 Complete - Query flow validated, logging infrastructure in place
