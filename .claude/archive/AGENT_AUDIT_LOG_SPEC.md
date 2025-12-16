# Agent Audit Logging Specification

**Created**: 2025-11-30  
**Purpose**: Complete traceability of ALL agent actions - no exceptions, no excuses

---

## 🚨 MANDATORY LOGGING REQUIREMENTS

Every agent MUST log:
1. **Query received** - Exact user input
2. **Tool calls made** - Which tools, with what parameters
3. **Tool results** - Raw output from tools
4. **Response generated** - What agent returned to user
5. **Decisions made** - Why agent chose that response
6. **Hallucination checks** - Did response pass validation?
7. **Errors encountered** - Every exception
8. **Timestamps** - Exact time of every action

---

## 📁 Folder Structure

```
.claude/
├── AGENT_AUDIT_LOG_SPEC.md (this file)
├── agent_audit_logs/
│   ├── nursing_research_agent_audit.jsonl
│   ├── medical_research_agent_audit.jsonl
│   ├── academic_research_agent_audit.jsonl
│   ├── research_writing_agent_audit.jsonl
│   ├── project_timeline_agent_audit.jsonl
│   ├── data_analysis_agent_audit.jsonl
│   └── base_agent_audit.jsonl (parent class logs)
```

---

## 📋 Log Entry Format (JSONL - one JSON per line)

```json
{
  "timestamp": "2025-11-30T15:45:32.123456Z",
  "agent_name": "Medical Research Agent",
  "agent_key": "medical_research",
  "session_id": "proj_cauti_reduction_20251130_154532",
  "action_type": "query_received|tool_call|tool_result|response_generated|validation_check|error|decision",
  "query": "Find articles on catheter infection prevention",
  "tool_name": "PubmedTools (if applicable)",
  "tool_params": {"query": "...", "max_results": 10},
  "tool_result": "raw tool output",
  "response": "what agent returned",
  "validation_status": "passed|failed|skipped",
  "validation_details": "hallucination check details if failed",
  "temperature": 0,
  "model": "gpt-4o",
  "error": null,
  "error_stack_trace": null,
  "decision_rationale": "why agent chose this response",
  "grounding_pmids_cited": ["12345678", "87654321"],
  "grounding_pmids_verified": ["12345678"],
  "grounding_pmids_unverified": ["87654321"],
  "hallucination_detected": false,
  "duration_ms": 2345
}
```

---

## 🔴 NON-NEGOTIABLE RULES

1. **Every query logged** - No exceptions
2. **Every tool call logged with parameters AND results**
3. **Every response logged** - Even errors
4. **Every hallucination check logged** - Pass or fail
5. **Every error logged with stack trace**
6. **Timestamps in ISO 8601 UTC**
7. **Append-only** - Never delete, never modify old entries
8. **Immutable** - Once logged, log entry cannot change
9. **Human readable** - JSONL format allows line-by-line inspection
10. **Daily rotation** - New file per day for size management

---

## 🔐 What Gets Logged (COMPLETE LIST)

### Action Type: `query_received`
```json
{
  "action_type": "query_received",
  "query": "exact user input",
  "project_name": "cauti_reduction",
  "user_query_length": 125
}
```

### Action Type: `tool_call`
```json
{
  "action_type": "tool_call",
  "tool_name": "PubmedTools",
  "tool_method": "search_pubmed",
  "tool_params": {
    "query": "catheter infection prevention",
    "max_results": 10,
    "results_expanded": true
  },
  "circuit_breaker_status": "closed"
}
```

### Action Type: `tool_result`
```json
{
  "action_type": "tool_result",
  "tool_name": "PubmedTools",
  "result_type": "string|error|timeout",
  "result_length": 2500,
  "result_preview": "[{'pmid': '12345678', 'title': '...'}]",
  "error": null
}
```

### Action Type: `validation_check`
```json
{
  "action_type": "validation_check",
  "check_type": "grounding|sample_size|path_traversal|pii",
  "check_passed": true,
  "check_details": {
    "pmids_cited": ["12345678"],
    "pmids_verified": ["12345678"],
    "unverified_pmids": []
  }
}
```

### Action Type: `response_generated`
```json
{
  "action_type": "response_generated",
  "response_length": 1500,
  "response_preview": "I found 3 articles...",
  "response_type": "success|hallucination_detected|error|refusal",
  "all_validation_passed": true
}
```

### Action Type: `error`
```json
{
  "action_type": "error",
  "error_type": "APIError|ValidationError|TimeoutError",
  "error_message": "PubMed API timeout after 30s",
  "error_stack_trace": "[full Python traceback]",
  "recovery_attempted": true,
  "recovery_status": "success|failed"
}
```

---

## 📊 Daily Log Analysis

Run daily to check agent behavior:

```bash
# Count queries per agent
grep '"agent_name"' .claude/agent_audit_logs/*_audit.jsonl | wc -l

# Find all hallucinations
grep '"hallucination_detected": true' .claude/agent_audit_logs/*_audit.jsonl

# Find all errors
grep '"action_type": "error"' .claude/agent_audit_logs/*_audit.jsonl

# Find validation failures
grep '"validation_status": "failed"' .claude/agent_audit_logs/*_audit.jsonl

# Find unverified PMIDs
grep '"grounding_pmids_unverified":\s*\[.*[0-9]' .claude/agent_audit_logs/*_audit.jsonl
```

---

## 🔧 Implementation Requirements

Every agent MUST:

1. **Import audit logger** in `__init__`
   ```python
   from src.services.agent_audit_logger import AuditLogger
   self.audit_logger = AuditLogger(agent_key="medical_research")
   ```

2. **Log query received** at start of agent.run()
   ```python
   self.audit_logger.log_query_received(query, project_name)
   ```

3. **Log tool calls** before and after
   ```python
   self.audit_logger.log_tool_call(tool_name, tool_params)
   # ... tool executes ...
   self.audit_logger.log_tool_result(tool_name, result, error)
   ```

4. **Log validation checks**
   ```python
   self.audit_logger.log_validation_check(
       check_type="grounding",
       passed=hallucination_check_passed,
       details=validation_details
   )
   ```

5. **Log final response**
   ```python
   self.audit_logger.log_response_generated(
       response=final_response,
       validation_passed=all_checks_passed
   )
   ```

6. **Log any errors**
   ```python
   self.audit_logger.log_error(
       error_type=type(e).__name__,
       error_message=str(e),
       stack_trace=traceback.format_exc()
   )
   ```

---

## ✅ Verification Checklist

Before any agent goes to production:
- [ ] Audit logger imported
- [ ] Query logging implemented
- [ ] Tool call logging implemented
- [ ] Tool result logging implemented
- [ ] Validation logging implemented
- [ ] Response logging implemented
- [ ] Error logging implemented
- [ ] Test log file created and readable
- [ ] JSONL format verified (one valid JSON per line)
- [ ] No sensitive data in logs (strip API keys, emails)

---

## 🔍 Audit Log Review Schedule

- **Daily**: Check for hallucinations and errors
- **Weekly**: Review validation failure patterns
- [ ] **Monthly**: Analyze agent accuracy trends
- **On-demand**: When issues reported

---

**END OF SPECIFICATION**

No excuses. Every action tracked. Every agent accountable.
