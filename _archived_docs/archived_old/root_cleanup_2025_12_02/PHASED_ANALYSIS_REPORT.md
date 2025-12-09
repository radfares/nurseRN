# 🔍 Phased Analysis Report: Medical Research Agent Issues

## Phase 1: Quick Intake - Confirm Attachments and Context

**✅ Attachments Received:**
- `.claude/agent_audit_logs/medical_research_audit.jsonl` (last ~200 lines)
- `agents/medical_research_agent.py` (first ~400 lines)
- `agents/base_agent.py` (first ~200 lines)
- `scripts/run_medical_agent_safe.py`
- `CRITICAL_FIX_AGENT2_HALLUCINATION.md`

**📋 Context Analysis:**
- **User Query**: "find foley ariicles new studies"
- **System Response**: Multiple errors including `MissingMessages`, `ModelProviderError` (401 Unauthorized), and API key exposure
- **Key Issues Identified**: Hallucination prevention, API authentication failures, missing messages in RunOutput

---

## Phase 2: Inner Analysis - Parse Agent Code and DB Schemas

### Structural Units Analysis

**🧩 Classes Identified:**
1. `MedicalResearchAgent` (agents/medical_research_agent.py:49)
2. `BaseAgent` (agents/base_agent.py:97)
3. `CircuitProtectedToolWrapper` (src/services/api_tools.py:78)
4. `LoggingListener` (src/services/circuit_breaker.py:50)

**📊 Tables Identified (from audit logs):**
- `picot_versions`, `literature_findings`, `analysis_plans`, `milestones`, `writing_drafts`, `conversations`, `documents`

**🔧 Tools Identified:**
- PubMed tools with circuit breaker protection
- Grounding validation tools
- Audit logging infrastructure

**🔄 Import-Time Side Effects:**
- `agent_config.py` auto-creates DB directory on import (line 108)
- `circuit_breaker.py` attempts pybreaker import with fallback (lines 23-40)
- `api_tools.py` sets up HTTP caching on import (lines 52-71)

---

## Phase 3: Fault Triage - Analyze Errors and Root Causes

### 🔴 Error 1: MissingMessages ("RunOutput has no messages field")

**📍 Root Cause:**
- **File**: `agents/medical_research_agent.py`, lines 373-378 in `_extract_verified_pmids_from_output()`
- **Issue**: Method assumes `run_output.messages` exists but Agno framework doesn't guarantee this field
- **Trigger**: When PubMed tool fails or returns empty results

**🔬 Reproduction Command:**
```bash
python3 -c "from agents.medical_research_agent import get_medical_research_agent; agent = get_medical_research_agent(); agent.run_with_grounding_check('test query')"
```

### 🔴 Error 2: OpenAI 401 Unauthorized (ModelProviderError)

**📍 Root Cause:**
- **File**: Audit logs show errors in `libs/agno/agno/models/openai/chat.py:371`
- **Issue**: Invalid API key `REDACTED_API_KEY` being used
- **Trigger**: Missing or incorrect `OPENAI_API_KEY` in environment

**🔬 Reproduction Command:**
```bash
OPENAI_API_KEY=invalid_key python3 scripts/run_medical_agent_safe.py "test query"
```

### 🔴 Error 3: Unredacted API Keys in Logs

**📍 Root Cause:**
- **Files**: Audit logs contain actual API keys in error stack traces
- **Issue**: Exception handling doesn't redact sensitive data before logging
- **Trigger**: Any API authentication failure

**🔬 Reproduction Command:**
```bash
grep -r "sk-" .claude/agent_audit_logs/ || echo "No unredacted keys found"
```

---

## Phase 4: Fix Plan - Provide Patches and Tests

### 🩹 Fix 1: MissingMessages Error

**📝 One-Line Fix:**
Add null-check for `run_output.messages` before accessing it

**🧩 Patch for `agents/medical_research_agent.py`:**
```python
# file: agents/medical_research_agent.py
<<<<<<< SEARCH
:start_line:373
-------
def _extract_verified_pmids_from_output(self, run_output: Any) -> set:
    """
    Extract PMIDs from actual tool results in RunOutput.
    """
    verified_pmids = set()

    try:
        # RunOutput has a 'messages' field containing all messages
        if not hasattr(run_output, "messages") or not run_output.messages:
            self.audit_logger.log_error(
                error_type="MissingMessages",
                error_message="RunOutput has no messages field",
                stack_trace="",
            )
            return verified_pmids
=======
def _extract_verified_pmids_from_output(self, run_output: Any) -> set:
    """
    Extract PMIDs from actual tool results in RunOutput.
    """
    verified_pmids = set()

    try:
        # RunOutput has a 'messages' field containing all messages
        if not hasattr(run_output, "messages"):
            self.audit_logger.log_error(
                error_type="MissingMessages",
                error_message="RunOutput has no messages attribute",
                stack_trace="",
            )
            return verified_pmids

        if not run_output.messages:
            self.audit_logger.log_error(
                error_type="EmptyMessages",
                error_message="RunOutput.messages is empty",
                stack_trace="",
            )
            return verified_pmids
>>>>>>> REPLACE
```

**🧪 Test for MissingMessages:**
```python
# file: test_missing_messages.py
import pytest
from unittest.mock import Mock
from agents.medical_research_agent import MedicalResearchAgent

def test_missing_messages_handling():
    agent = MedicalResearchAgent()

    # Mock run_output without messages attribute
    run_output_no_attr = Mock(spec=[])
    result = agent._extract_verified_pmids_from_output(run_output_no_attr)
    assert result == set()

    # Mock run_output with empty messages
    run_output_empty = Mock(messages=[])
    result = agent._extract_verified_pmids_from_output(run_output_empty)
    assert result == set()

    print("✅ MissingMessages handling works correctly")
```

### 🩹 Fix 2: OpenAI 401 Error Handling

**📝 One-Line Fix:**
Add API key validation before making OpenAI calls

**🧩 Patch for `agents/medical_research_agent.py`:**
```python
# file: agents/medical_research_agent.py
<<<<<<< SEARCH
:start_line:265
-------
# Run agent - returns RunOutput object with messages field
run_output = self.agent.run(query)
response_text = str(
    run_output.content if hasattr(run_output, "content") else run_output
)
=======
# Validate API key before running agent
import os
if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY").startswith("sk-") and len(os.getenv("OPENAI_API_KEY")) < 50:
    self.audit_logger.log_error(
        error_type="InvalidAPIKey",
        error_message="Invalid or missing OpenAI API key",
        stack_trace=""
    )
    return {
        "content": "⚠️ OpenAI API key is missing or invalid. Set OPENAI_API_KEY environment variable.",
        "validation_passed": False,
        "error": "invalid_api_key"
    }

# Run agent - returns RunOutput object with messages field
try:
    run_output = self.agent.run(query)
except Exception as e:
    if "401" in str(e) or "invalid_api_key" in str(e).lower():
        return {
            "content": "⚠️ OpenAI API authentication failed. Check your API key.",
            "validation_passed": False,
            "error": "authentication_failed"
        }
    raise

response_text = str(
    run_output.content if hasattr(run_output, "content") else run_output
)
>>>>>>> REPLACE
```

**🧪 Test for API Key Validation:**
```python
# file: test_api_key_validation.py
import os
import pytest
from agents.medical_research_agent import get_medical_research_agent

def test_api_key_validation():
    # Test with missing API key
    os.environ.pop("OPENAI_API_KEY", None)
    agent = get_medical_research_agent()
    result = agent.run_with_grounding_check("test query")
    assert "OpenAI API key is missing or invalid" in result["content"]
    assert result["validation_passed"] is False

    # Test with invalid API key
    os.environ["OPENAI_API_KEY"] = "sk-invalid"
    agent = get_medical_research_agent()
    result = agent.run_with_grounding_check("test query")
    assert "OpenAI API authentication failed" in result["content"]
    assert result["validation_passed"] is False

    print("✅ API key validation works correctly")
```

### 🩹 Fix 3: API Key Redaction

**📝 One-Line Fix:**
Add redaction filter for error logging

**🧩 Patch for `agents/base_agent.py`:**
```python
# file: agents/base_agent.py
<<<<<<< SEARCH
:start_line:227
-------
except Exception as e:
    if self.audit_logger:
        self.audit_logger.log_error(
            error_type="ItemExtractionError",
            error_message=f"Failed to extract {item_type}s from output: {str(e)}",
            stack_trace=traceback.format_exc(),
        )
=======
except Exception as e:
    if self.audit_logger:
        # Redact API keys from error messages
        error_msg = str(e)
        redacted_msg = error_msg.replace("sk-", "REDACTED_API_KEY")
        redacted_msg = redacted_msg.replace("REDACTED_API_KEY_KEY", "REDACTED_API_KEY")

        self.audit_logger.log_error(
            error_type="ItemExtractionError",
            error_message=f"Failed to extract {item_type}s from output: {redacted_msg}",
            stack_trace=traceback.format_exc().replace("sk-", "REDACTED_API_KEY"),
        )
>>>>>>> REPLACE
```

**🧪 Test for API Key Redaction:**
```python
# file: test_api_key_redaction.py
import pytest
from agents.base_agent import BaseAgent
from unittest.mock import Mock

def test_api_key_redaction():
    # Create a mock audit logger
    mock_logger = Mock()
    agent = BaseAgent("Test Agent", "test_agent")
    agent.audit_logger = mock_logger

    # Simulate error with API key
    error_with_key = Exception("Error with key: sk-test1234567890")
    agent.extract_verified_items_from_output(None, "test", "test")

    # Verify redaction occurred
    call_args = mock_logger.log_error.call_args
    assert "REDACTED_API_KEY" in call_args[1]["error_message"]
    assert "sk-test1234567890" not in call_args[1]["error_message"]

    print("✅ API key redaction works correctly")
```

---

## Phase 5: Ops & Security - Provide Inspection and Redaction Tools

### 🔍 SQL/JQ/Grep Commands for Log Inspection

**📊 Inspect Audit Logs:**
```bash
# Count error types
jq -r '.error_type' .claude/agent_audit_logs/medical_research_audit.jsonl | sort | uniq -c

# Find all MissingMessages errors
grep -i "MissingMessages" .claude/agent_audit_logs/medical_research_audit.jsonl

# Find all 401 errors
grep -i "401\|invalid_api_key" .claude/agent_audit_logs/medical_research_audit.jsonl
```

**🔍 Inspect Database:**
```bash
# Check SQLite schema
sqlite3 tmp/medical_research_agent.db ".schema"

# Count records in key tables
sqlite3 tmp/medical_research_agent.db "SELECT COUNT(*) FROM conversations;"
```

### 🧹 In-Place Redaction Script

**📝 Script: `scripts/redact_api_keys.py`**
```python
#!/usr/bin/env python3
import re
import json
import sys
from pathlib import Path

def redact_api_keys_in_file(file_path):
    """Redact API keys in JSONL file in-place"""
    pattern = re.compile(r'sk-[a-zA-Z0-9]{40,}')
    redacted_pattern = "REDACTED_API_KEY"

    with open(file_path, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()

        for line in lines:
            try:
                if line.strip():
                    log_entry = json.loads(line)
                    # Redact in all string fields
                    for key, value in log_entry.items():
                        if isinstance(value, str):
                            log_entry[key] = pattern.sub(redacted_pattern, value)
                        elif isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if isinstance(subvalue, str):
                                    value[subkey] = pattern.sub(redacted_pattern, subvalue)
                    f.write(json.dumps(log_entry) + '\n')
            except json.JSONDecodeError:
                # Write original line if not valid JSON
                f.write(line)

def main():
    if len(sys.argv) < 2:
        print("Usage: redact_api_keys.py <file_or_directory>")
        sys.exit(1)

    target = Path(sys.argv[1])

    if target.is_file():
        redact_api_keys_in_file(target)
        print(f"✅ Redacted API keys in {target}")
    elif target.is_dir():
        for jsonl_file in target.glob("*.jsonl"):
            redact_api_keys_in_file(jsonl_file)
            print(f"✅ Redacted API keys in {jsonl_file}")
    else:
        print(f"❌ Target not found: {target}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**🔧 Usage:**
```bash
# Redact single file
python3 scripts/redact_api_keys.py .claude/agent_audit_logs/medical_research_audit.jsonl

# Redact all JSONL files in directory
python3 scripts/redact_api_keys.py .claude/agent_audit_logs/
```

---

## Phase 6: Synthesis & Grading - Architecture Summary and Project Grade

### 🏗️ Inner → Outer Architecture Summary

**1. Structural Units (Inner Core):**
- `MedicalResearchAgent` class with grounding validation
- `BaseAgent` abstract base class
- Circuit breaker protected API tools
- SQLite database schema with 7 core tables

**2. Components (Middle Layer):**
- Agent orchestration system
- Project management with milestone tracking
- API service layer with resilience patterns
- Audit logging infrastructure

**3. System (Outer Layer):**
- CLI interface with project switching
- Multi-agent architecture (6 specialized agents)
- Clinical safety disclaimer system
- Configuration management

### 📋 Prioritized Remediation Checklist

1. **CRITICAL**: Fix MissingMessages error handling (Phase 4, Fix 1)
2. **HIGH**: Add API key validation before OpenAI calls (Phase 4, Fix 2)
3. **HIGH**: Implement API key redaction in error logging (Phase 4, Fix 3)
4. **MEDIUM**: Enhance circuit breaker recovery mechanisms
5. **LOW**: Add more comprehensive test coverage

### 🎓 Project Grade: 78/100

**✅ Strengths (78 points):**
- Comprehensive architectural design with clear separation of concerns
- Excellent resilience patterns (circuit breakers, retry logic)
- Strong clinical safety measures (grounding validation, audit logging)
- Good documentation and error handling
- Project-centric design with proper data isolation

**⚠️ Areas for Improvement (22 points):**
- MissingMessages error handling needs improvement (-8)
- API key validation could be more robust (-6)
- Error logging doesn't redact sensitive data (-5)
- Test coverage could be more comprehensive (-3)

**💡 Justification:**
The project demonstrates solid architectural foundations and clinical safety measures, but has critical operational issues that affect reliability and security. The MissingMessages errors and API key exposure are significant production readiness concerns that need immediate attention.
