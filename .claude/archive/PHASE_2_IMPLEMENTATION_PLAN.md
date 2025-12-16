# Phase 2 Implementation Plan: Apply Fixes to Remaining 5 Agents

**Date**: 2025-11-30  
**Status**: PLANNING PHASE  
**Objective**: Apply hallucination prevention fixes to all remaining agents  

---

## Executive Summary

After fixing medical_research_agent.py and discovering the validation system bug, we discovered that **nursing_research_agent.py already has a superior grounding validation system**. Phase 2 will:

1. **Standardize** the validation approach across all 6 agents
2. **Add audit logging** to all agents using the BaseAgent hook
3. **Ensure temperature=0** on all agent models
4. **Implement agent-specific validation** based on each agent's purpose

---

## Key Discovery: Two Validation Approaches

### Approach A: Tool Results Validation (nursing_research_agent)
Uses `run_output.tools` (ToolExecution objects) - **BETTER for research agents**

```python
tools = run_output.tools or []  # ToolExecution objects
pmids_from_tools = self._extract_pmids_from_tools(tools)
```

**Advantages**:
- ✅ Direct access to tool execution results
- ✅ Works with Agno's native ToolExecution objects
- ✅ More reliable than parsing messages
- ✅ Already proven to work

**Agents using this**: nursing_research_agent

### Approach B: Message Parsing (medical_research_agent - FIXED)
Uses `run_output.messages` (all messages including tool results) - **FALLBACK for simple agents**

```python
for message in run_output.messages:
    message_str = str(message)
    pmids = re.findall(r"PMID:\s*(\d+)", message_str, re.IGNORECASE)
```

**Advantages**:
- ✅ Works when ToolExecution not available
- ✅ More flexible for different message types
- ✅ Fallback when tools data is unavailable

**Agents using this**: medical_research_agent (fixed)

---

## Agent-by-Agent Implementation Strategy

### Agent 1: medical_research_agent ✅ DONE
**Status**: FIXED  
**Changes Made**:
- ✅ Set temperature = 0
- ✅ Fixed `_extract_verified_pmids_from_output()` to use `run_output.messages`
- ✅ Added 4 PMID regex patterns
- ✅ Added audit logging initialization
- ✅ Comprehensive error handling

**Validation Approach**: Message parsing (Approach B)  
**Test Status**: 7/7 tests passing

---

### Agent 2: nursing_research_agent ⚠️ NEEDS AUDIT LOGGING ONLY

**Current Status**: Already has superior grounding validation!
- ✅ Temperature = 0 (already set)
- ✅ PMID grounding validation (already implemented)
- ✅ Post-hook validation
- ✅ Comprehensive error handling

**What's Missing**: 
- ❌ Audit logging integration
- ❌ temperature=0 confirmation in docstring

**Changes Needed**:
1. Add audit logger initialization in `__init__`
2. Add audit logging calls to `_validate_run_output()`, `_grounding_post_hook()`
3. Update docstring to document temperature=0 hallucination prevention
4. Add note about using run_output.tools approach

**Effort**: SMALL (2-3 hours)

---

### Agent 3: academic_research_agent ⚠️ MEDIUM CHANGES

**Current Status**: Uses ArXiv (papers, not articles)
- ❌ Temperature not explicitly set (likely default 1.0)
- ❌ No validation system
- ❌ No audit logging

**Purpose**: Statistical methods, theoretical research

**Changes Needed**:
1. Set temperature = 0
2. Add audit logging initialization
3. Implement DOI/arXiv ID validation (similar to PMID)
4. Add post-hook or run_with_validation() method
5. Update instructions with grounding policy

**Validation Approach**: Message parsing (Approach B - simpler for this agent)  
**Effort**: MEDIUM (4-5 hours)

---

### Agent 4: research_writing_agent ⚠️ SMALL CHANGES

**Current Status**: Pure writing agent (no external tools)
- ❌ Temperature not explicitly set
- ❌ No validation system (not needed - no external sources)
- ❌ No audit logging

**Purpose**: PICOT writing, literature synthesis, intervention planning

**Changes Needed**:
1. Set temperature = 0 (for consistency)
2. Add audit logging initialization
3. Add input validation (e.g., check that PICOT data is present)
4. Add response validation (e.g., check that response is complete)
5. No external grounding needed (internal data synthesis)

**Validation Approach**: Schema validation (Approach C - validate response structure)  
**Effort**: SMALL (2-3 hours)

---

### Agent 5: project_timeline_agent ⚠️ MEDIUM CHANGES

**Current Status**: Uses MilestoneTools (database queries)
- ❌ Temperature not explicitly set
- ❌ No validation system
- ❌ No audit logging

**Purpose**: Database-driven milestone tracking

**Changes Needed**:
1. Set temperature = 0
2. Add audit logging initialization
3. Implement milestone validation (dates, status)
4. Add post-hook for response validation
5. Ensure dates come from milestone database

**Validation Approach**: Database grounding (Approach D - validate against DB)  
**Effort**: MEDIUM (4-5 hours)

---

### Agent 6: data_analysis_agent ⚠️ LARGE CHANGES

**Current Status**: Pure analysis (no tools)
- ❌ Temperature not explicitly set
- ✅ Has Pydantic schema validation (DataAnalysisOutput)
- ❌ No audit logging

**Purpose**: Statistical analysis, sample size, test selection

**Changes Needed**:
1. Set temperature = 0
2. Add audit logging initialization
3. Schema validation already exists (keep it)
4. Add confidence score validation
5. Add R/Python code syntax validation

**Validation Approach**: Schema + Code validation (Approach E)  
**Effort**: SMALL-MEDIUM (3-4 hours)

---

## Four Validation Approaches

### Approach A: Tool Execution Validation (nursing_research)
For agents with tool calls

```python
# Extract from ToolExecution objects
tools = run_output.tools or []
for execution in tools:
    result = execution.result
    # Validate against result
```

### Approach B: Message Parsing (medical_research - FIXED)
For agents with message-based tool results

```python
# Extract from messages
for message in run_output.messages:
    message_str = str(message)
    # Parse for citations
```

### Approach C: Schema Validation (research_writing, data_analysis)
For agents with structured output

```python
# Validate response schema
output = DataAnalysisOutput.parse_obj(response)
# Validates Pydantic models
```

### Approach D: Database Grounding (project_timeline)
For agents querying databases

```python
# Validate dates come from milestone DB
db_dates = fetch_milestone_dates()
response_dates = extract_dates(response)
assert response_dates.issubset(db_dates)
```

### Approach E: Code Validation (data_analysis)
For agents generating code

```python
# Validate R/Python syntax
try:
    ast.parse(code)  # Python
    # or rparse for R
except SyntaxError:
    # Hallucinated code
```

---

## Unified Audit Logging Pattern

All 6 agents will use the same audit logging pattern:

```python
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__("My Agent", "my_agent", tools=[...])
        # Initialize audit logger
        from src.services.agent_audit_logger import get_audit_logger
        self.audit_logger = get_audit_logger("my_agent", "My Agent")
    
    def run_with_validation(self, query, **kwargs):
        session_id = f"my_agent_{int(time.time() * 1000)}"
        self.audit_logger.set_session(session_id)
        self.audit_logger.log_query_received(query)
        
        # Run agent
        run_output = self.agent.run(query, **kwargs)
        
        # Validate response
        is_valid = self._validate_response(run_output)
        
        # Log result
        if is_valid:
            self.audit_logger.log_response_generated(
                response=run_output.content,
                response_type="success",
                validation_passed=True
            )
        else:
            self.audit_logger.log_response_generated(
                response="VALIDATION FAILED",
                response_type="validation_failed",
                validation_passed=False
            )
        
        return run_output
```

---

## Implementation Order (Priority)

1. **Agent 6: data_analysis_agent** (SMALLEST - only audit logging, schema already exists)
2. **Agent 4: research_writing_agent** (SMALL - simple validation)
3. **Agent 2: nursing_research_agent** (SMALL - just add audit logging to existing)
4. **Agent 5: project_timeline_agent** (MEDIUM - DB grounding)
5. **Agent 3: academic_research_agent** (MEDIUM - DOI validation)

---

## Testing Strategy

### Unit Tests (Per Agent)
- Temperature = 0 verification
- Audit logger initialization
- Validation function correctness
- Error handling

### Integration Tests
- End-to-end with mock tools
- Validation with real API responses
- Audit trail completeness

### System Tests
- All agents log to `.claude/agent_audit_logs/`
- JSONL format integrity
- Performance impact < 5%

---

## Expected Results

### Before Phase 2
```
medical_research_agent:    ✅ Fixed
nursing_research_agent:    ❌ No audit logging
academic_research_agent:   ❌ No validation, no logging
research_writing_agent:    ❌ No validation, no logging
project_timeline_agent:    ❌ No validation, no logging
data_analysis_agent:       ❌ No audit logging
```

### After Phase 2
```
medical_research_agent:    ✅ Fixed + logged
nursing_research_agent:    ✅ Validated + logged
academic_research_agent:   ✅ Validated + logged
research_writing_agent:    ✅ Validated + logged
project_timeline_agent:    ✅ Validated + logged
data_analysis_agent:       ✅ Validated + logged

All agents:
  - Temperature = 0 set
  - Audit logging enabled
  - Validation implemented
  - Immutable JSONL audit trail
```

---

## Timeline Estimate

- **Agent 6 (data_analysis)**: 1-2 hours
- **Agent 4 (research_writing)**: 2-3 hours
- **Agent 2 (nursing_research)**: 2-3 hours
- **Agent 5 (project_timeline)**: 3-4 hours
- **Agent 3 (academic_research)**: 4-5 hours
- **Test Suite**: 3-4 hours
- **Documentation**: 2-3 hours

**Total**: 17-24 hours of work

---

## Success Criteria

✅ All 6 agents have:
- [ ] Temperature = 0 set
- [ ] Audit logging initialized
- [ ] Validation implemented
- [ ] Error handling
- [ ] Documentation updated
- [ ] Tests passing

✅ All agents log to `.claude/agent_audit_logs/` with:
- [ ] JSONL format
- [ ] Thread-safe writes
- [ ] ISO 8601 timestamps
- [ ] Session tracking
- [ ] Action logging

✅ System tests pass:
- [ ] No validation breaks functionality
- [ ] Audit logging doesn't slow performance > 5%
- [ ] All agents handle errors gracefully

