
# IMPLEMENTATION CHECKLIST
**Created:** 2025-12-09
**Status:** IN PROGRESS
**Rule:** Check box when VALIDATION GATE passes, then delete the completed task

---

## HOW TO USE THIS FILE

1. Work through tasks IN ORDER (do not skip)
2. Run the VALIDATION GATE for each task
3. If gate PASSES: Check the box `[x]` then delete the entire task block
4. If gate FAILS: Fix and re-run (per CLAUDE.md rules)
5. Log failures in `.claude/agent_audit.md`

---

## PHASE 1: AGENT 3 (Academic Research) - ✅ COMPLETE (2025-12-09)

**Validation Summary:**
- [x] Task 1.1: Blocked run() method - PASSED
- [x] Task 1.2: Extraction method - PASSED
- [x] Task 1.3: _validate_run_output() - PASSED
- [x] Task 1.4: run_with_grounding_check() - PASSED
- [x] Task 1.5: arxiv_validation_tools.py - PASSED
- [x] Task 1.6: Full Integration Test - PASSED

**Files Modified:**
- `agents/academic_research_agent.py` (lines 213, 219, 258, 153)
- `src/tools/arxiv_validation_tools.py` (created)

**Audit Trail:** See `.claude/agent_audit_logs/academic_research_audit.jsonl`

---

## PHASE 2: AGENT 5 (Research Writing) - ✅ COMPLETE (2025-12-09)

**Validation Summary:**
- [x] Task 2.1: _validate_run_output() with citation blocking - PASSED
- [x] Task 2.2: run_with_grounding_check() with ValueError handling - PASSED

**Files Modified:**
- `agents/research_writing_agent.py:265` - Blocking _validate_run_output()
- `agents/research_writing_agent.py:208` - Updated run_with_grounding_check()

**Test Results:**
- ✅ Blocks PMID fabrication (PMID: 12345678)
- ✅ Blocks DOI fabrication (10.1234/example.2024)
- ✅ Allows valid content without citations

**Audit Trail:** See `.claude/agent_audit_logs/research_writing_audit.jsonl`

---

## PHASE 3: AGENT 6 (Timeline) - ✅ COMPLETE (2025-12-09)

**Validation Summary:**
- [x] Task 3.1: _validate_run_output() with date blocking - PASSED
- [x] Task 3.2: run_with_grounding_check() with ValueError handling - PASSED

**Files Modified:**
- `agents/nursing_project_timeline_agent.py:222` - Blocking _validate_run_output()
- `agents/nursing_project_timeline_agent.py:168` - Updated run_with_grounding_check()

**Test Results:**
- ✅ Blocks fabricated dates (December 17, 2025)
- ✅ Blocks milestone content without database query
- ✅ Allows valid content without dates

**Audit Trail:** See `.claude/agent_audit_logs/project_timeline_audit.jsonl`

---

## PHASE 4: FINAL INTEGRATION TEST - ✅ COMPLETE (2025-12-09)

**All System Validation Gates Passed:**
- [x] Agent 3: Direct run blocked ✅
- [x] Agent 3: Hallucination blocked (9999.99999) ✅
- [x] Agent 5: Citation fabrication blocked (PMID: 12345) ✅
- [x] Agent 6: Date fabrication blocked (December 17) ✅
- [x] ArxivValidationTools: Working ✅

---

### [ ] Task 3.1: Replace _validate_run_output() with blocking version

**File:** `agents/nursing_project_timeline_agent.py`
**Location:** Replace existing method at lines 206-231

```python
def _validate_run_output(self, run_output: Any) -> bool:
    """
    Ensure milestone dates match database.
    BLOCKS if dates mentioned without database query.
    """
    import re

    content = str(run_output.content) if hasattr(run_output, 'content') else str(run_output)
    tools = getattr(run_output, 'tools', None) or []

    date_pattern = r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,?\s*\d{4})?|202\d-\d{2}-\d{2}"
    dates_found = re.findall(date_pattern, content, re.IGNORECASE)

    milestone_keywords = ["milestone", "deliverable", "deadline", "due date", "due by"]
    has_milestone_content = any(kw in content.lower() for kw in milestone_keywords)

    if (dates_found or has_milestone_content) and not tools:
        if self.audit_logger:
            self.audit_logger.log_validation_check(
                "database_grounding",
                False,
                {
                    "dates_found": dates_found,
                    "has_milestone_content": has_milestone_content,
                    "reason": "Timeline data mentioned without database query"
                }
            )

        raise ValueError(
            f"DATABASE GROUNDING VIOLATION\n"
            f"Timeline information provided without querying the database.\n"
            f"Dates found: {dates_found}\n"
            f"REQUIRED: Query milestones table before providing timeline information."
        )

    if self.audit_logger:
        self.audit_logger.log_validation_check("database_grounding", True, {})

    return True
```

**VALIDATION GATE 3.1:**
```bash
python -c "
from agents.nursing_project_timeline_agent import ProjectTimelineAgent
a = ProjectTimelineAgent()

class MockOutput:
    content = 'Your deadline is December 17, 2025'
    tools = []

try:
    a._validate_run_output(MockOutput())
    print('FAIL: Should block ungrounded dates')
    exit(1)
except ValueError as e:
    if 'DATABASE GROUNDING' in str(e):
        print('PASS: Blocks fabricated dates')
    else:
        print(f'FAIL: Wrong error: {e}')
        exit(1)
"
```

---

### [ ] Task 3.2: Update run_with_grounding_check() for Agent 6

**File:** `agents/nursing_project_timeline_agent.py`
**Location:** Replace existing method at lines 168-204

```python
def run_with_grounding_check(self, query: str, **kwargs) -> Any:
    """Execute the agent with database grounding enforcement."""
    import traceback

    project_name = kwargs.get("project_name")
    if self.audit_logger:
        self.audit_logger.log_query_received(query, project_name)

    stream_requested = bool(kwargs.get("stream"))

    try:
        response = self.agent.run(query, **kwargs)

        if stream_requested:
            return response

        self._validate_run_output(response)

        if self.audit_logger:
            self.audit_logger.log_response_generated(
                response=str(response.content),
                response_type="success",
                validation_passed=True
            )

        return response

    except ValueError as validation_error:
        if self.audit_logger:
            self.audit_logger.log_error(
                error_type="DatabaseGroundingViolation",
                error_message=str(validation_error),
                stack_trace=traceback.format_exc()
            )

        return {
            "content": (
                "DATABASE GROUNDING SYSTEM ACTIVATED\n\n"
                f"{str(validation_error)}\n\n"
                "I must query the database before providing timeline information.\n"
                "Please rephrase your question so I can look up the actual milestones."
            ),
            "validation_passed": False
        }

    except Exception as e:
        if self.audit_logger:
            self.audit_logger.log_error(
                error_type=type(e).__name__,
                error_message=str(e),
                stack_trace=traceback.format_exc()
            )
        raise
```

**VALIDATION GATE 3.2:**
```bash
python -c "
from agents.nursing_project_timeline_agent import ProjectTimelineAgent
a = ProjectTimelineAgent()
assert hasattr(a, 'run_with_grounding_check')
print('PASS: run_with_grounding_check exists for Agent 6')
"
```

---

## PHASE 4: FINAL INTEGRATION TEST - Day 13

### [ ] Task 4.1: Run complete system validation

**VALIDATION GATE 4.1 (FINAL):**
```bash
python -c "
print('=' * 60)
print('FINAL SYSTEM VALIDATION')
print('=' * 60)
print()

# Agent 3
from agents.academic_research_agent import AcademicResearchAgent
a3 = AcademicResearchAgent()
try:
    a3.run('test')
    print('[X] Agent 3: Direct run NOT blocked')
    exit(1)
except RuntimeError:
    print('[OK] Agent 3: Direct run blocked')

class Mock3:
    content = 'Paper 9999.99999'
    messages = []
try:
    a3._validate_run_output(Mock3())
    print('[X] Agent 3: Hallucination NOT blocked')
    exit(1)
except ValueError:
    print('[OK] Agent 3: Hallucination blocked')

# Agent 5
from agents.research_writing_agent import ResearchWritingAgent
a5 = ResearchWritingAgent()
class Mock5:
    content = 'PMID: 12345'
try:
    a5._validate_run_output(Mock5())
    print('[X] Agent 5: Citation fabrication NOT blocked')
    exit(1)
except ValueError:
    print('[OK] Agent 5: Citation fabrication blocked')

# Agent 6
from agents.nursing_project_timeline_agent import ProjectTimelineAgent
a6 = ProjectTimelineAgent()
class Mock6:
    content = 'Deadline: December 17'
    tools = []
try:
    a6._validate_run_output(Mock6())
    print('[X] Agent 6: Date fabrication NOT blocked')
    exit(1)
except ValueError:
    print('[OK] Agent 6: Date fabrication blocked')

# ArxivValidationTools
from src.tools.arxiv_validation_tools import ArxivValidationTools
result = ArxivValidationTools.assess_preprint_status('2103.12345')
if result['is_preprint']:
    print('[OK] ArxivValidationTools: Working')
else:
    print('[X] ArxivValidationTools: Failed')
    exit(1)

print()
print('=' * 60)
print('ALL VALIDATION GATES PASSED')
print('IMPLEMENTATION COMPLETE')
print('=' * 60)
"
```

---

## COMPLETION LOG

When ALL tasks are checked and deleted, add entry to `.claude/agent_audit.md`:

```markdown
## 2025-12-XX: Phase 1-4 Implementation Complete

### Agent 3 (Academic Research)
- Added: blocked run() method
- Added: _extract_verified_arxiv_ids_from_output()
- Replaced: _validate_run_output() with blocking version
- Updated: run_with_grounding_check() with ValueError handling
- Created: src/tools/arxiv_validation_tools.py

### Agent 5 (Research Writing)
- Replaced: _validate_run_output() with citation blocking
- Updated: run_with_grounding_check() with ValueError handling

### Agent 6 (Timeline)
- Replaced: _validate_run_output() with date blocking
- Updated: run_with_grounding_check() with ValueError handling

### All Validation Gates: PASSED
```

---

**END OF CHECKLIST**
