# Semantic Analysis: Mock Files & Test Cleanup Plan

**Analysis Date**: 2025-12-07
**Purpose**: Identify removable mocks and tests for cleanup

---

## 1. Root Cause: Why Mocks Fail

### The Import Timing Problem

```
WHAT TESTS EXPECT:
┌─────────────────────────────────────────────────────────────────┐
│  1. Test runs                                                   │
│  2. mock_agno() fixture creates MagicMock for 'agno'            │
│  3. patch.dict(sys.modules, mocks) activates                    │
│  4. from agents.nursing_research_agent import NursingResearchAgent│
│  5. Agent uses mocked agno → TEST PASSES                        │
└─────────────────────────────────────────────────────────────────┘

WHAT ACTUALLY HAPPENS:
┌─────────────────────────────────────────────────────────────────┐
│  1. Python imports test file                                    │
│  2. Test file imports: from unittest.mock import Mock           │
│  3. Python sees: from agents.nursing_research_agent import...   │
│  4. Python IMMEDIATELY imports the agent module                 │
│  5. Agent module does: from agno.agent import Agent  ← REAL IMPORT│
│  6. NOW test runs and applies mock  ← TOO LATE                  │
│  7. Agent already has REAL agno reference → TEST FAILS          │
└─────────────────────────────────────────────────────────────────┘
```

### The Missing Mock Problem (Agent 3 Specific)

```python
# academic_research_agent.py line 35:
from src.tools.literature_tools import LiteratureTools  # NOT MOCKED

# Test fixture only mocks:
mocks = {
    'agno': MagicMock(),
    'agno.tools': MagicMock(),
    # MISSING: 'src.tools.literature_tools'
}

# Result: Real LiteratureTools() is called → needs project_manager → fails
```

---

## 2. Mock Inventory by File

### Files with Excessive Mocks (CLEANUP CANDIDATES)

| File | Mock Count | Tests | Problem |
|------|-----------|-------|---------|
| `test_nursing_research_agent.py` | **81** | 15 | Mocks don't work; tests outdated |
| `test_medical_research_agent.py` | **78** | 17 | 4 tests fail due to assertion drift |
| `test_academic_research_agent.py` | **62** | 14 | Missing LiteratureTools mock |
| `test_api_tools.py` | 51 | ~12 | Module-level mocks (actually work) |
| `test_milestone_tools.py` | 37 | ~11 | Working |

### Duplicate Fixtures (CONSOLIDATION NEEDED)

Each of these files has an **identical** `mock_agno()` fixture:

```python
# DUPLICATED in 3 files (copy-paste)
@pytest.fixture
def mock_agno():
    """Mock agno dependencies and ensure clean import"""
    mocks = {
        'agno': MagicMock(),
        'agno.agent': MagicMock(),
        'agno.db': MagicMock(),
        'agno.db.sqlite': MagicMock(),
        'agno.models': MagicMock(),
        'agno.models.openai': MagicMock(),
        'agno.models.response': MagicMock(),
        'agno.run': MagicMock(),
        'agno.run.agent': MagicMock(),
        'agno.tools': MagicMock(),
    }
    ...
```

**Files with duplicate fixture**:
1. `test_nursing_research_agent.py` (lines 10-36)
2. `test_medical_research_agent.py` (lines 10-36)
3. `test_academic_research_agent.py` (lines 10-36)

---

## 3. Test Categories: Keep vs Remove

### REMOVE: Tests That Can Never Pass (22 tests)

| File | Test | Reason |
|------|------|--------|
| `test_nursing_research_agent.py` | `test_initialization_creates_tools` | Mocks Exa/Serp but code uses PubMed |
| `test_nursing_research_agent.py` | `test_initialization_sets_agent_name` | Same - PubMed required=True kills it |
| `test_nursing_research_agent.py` | `test_initialization_stores_tools` | Same |
| `test_nursing_research_agent.py` | `test_create_tools_with_both_apis` | Tests Exa+Serp, code has 9 different tools |
| `test_nursing_research_agent.py` | `test_create_tools_with_no_apis` | Outdated tool list |
| `test_nursing_research_agent.py` | `test_create_tools_with_only_exa` | Exa is now DISABLED in code |
| `test_nursing_research_agent.py` | `test_create_agent_configures_correctly` | Mock timing issue |
| `test_nursing_research_agent.py` | `test_create_agent_uses_gpt4o_model` | Mock timing issue |
| `test_nursing_research_agent.py` | `test_create_agent_uses_correct_database` | Mock timing issue |
| `test_nursing_research_agent.py` | `test_show_usage_all_apis_configured` | Tests Exa/Serp, code shows PubMed |
| `test_nursing_research_agent.py` | `test_show_usage_no_apis_configured` | Outdated output assertions |
| `test_nursing_research_agent.py` | `test_show_usage_displays_examples` | Outdated string assertions |
| `test_nursing_research_agent.py` | `test_agent_inherits_from_base_agent` | Mock timing issue |
| `test_nursing_research_agent.py` | `test_agent_has_required_methods` | Mock timing issue |
| `test_academic_research_agent.py` | `test_initialization_creates_tools` | Missing LiteratureTools mock |
| `test_academic_research_agent.py` | `test_initialization_sets_agent_name` | Same |
| `test_academic_research_agent.py` | `test_create_agent_uses_correct_database` | Same |
| `test_academic_research_agent.py` | `test_agent_inherits_from_base_agent` | Same |
| `test_academic_research_agent.py` | `test_agent_has_required_methods` | Same |
| `test_academic_research_agent.py` | `test_show_usage_*` (5 tests) | Same |
| `test_academic_research_agent.py` | `test_create_tools_with_arxiv` | Same |
| `test_academic_research_agent.py` | `test_create_tools_without_arxiv` | Same |

### FIX: Tests That Need Assertion Updates (4 tests)

| File | Test | Fix Needed |
|------|------|------------|
| `test_medical_research_agent.py` | `test_show_usage_examples_includes_examples` | Change "Find clinical studies:" → "EXAMPLE QUERIES:" |
| `test_medical_research_agent.py` | `test_show_usage_examples_includes_tips` | Change "PubMed has millions..." → "Be specific!" |
| `test_medical_research_agent.py` | `test_global_instance_exists` | Call `get_medical_research_agent()` first |
| `test_medical_research_agent.py` | `test_global_instance_is_medical_research_agent` | Same |

### KEEP: Tests That Work (15 tests)

| File | Test | Status |
|------|------|--------|
| `test_nursing_research_agent.py` | `test_global_instance_created` | PASSES |
| `test_medical_research_agent.py` | 13 tests | PASS |
| `test_academic_research_agent.py` | `test_global_instance_exists` | PASSES |
| `test_academic_research_agent.py` | `test_global_instance_is_academic_research_agent` | PASSES |

---

## 4. Semantic Mismatch Analysis

### Agent 1: NursingResearchAgent

**Tests expect** (written ~Nov 2024):
```python
# Old tool structure
create_exa_tools_safe(required=False)
create_serp_tools_safe(required=False)
# 2 tools: Exa, SerpAPI
```

**Code now has** (updated Nov 26):
```python
# New tool structure (9 tools)
create_pubmed_tools_safe(required=True)      # PRIMARY
create_clinicaltrials_tools_safe()           # Free
create_medrxiv_tools_safe()                  # Free
create_semantic_scholar_tools_safe()         # Free
create_core_tools_safe()                     # Free
create_doaj_tools_safe()                     # Free
create_safety_tools_safe()                   # OpenFDA
create_serp_tools_safe()                     # Optional
LiteratureTools()                            # Project DB
# Exa DISABLED, ArXiv DISABLED
```

**Semantic Gap**: Tests are 100% obsolete. They test for tools that no longer exist.

### Agent 2: MedicalResearchAgent

**Tests expect**:
```python
"Find clinical studies:"
"Search for specific conditions:"
"PubMed has millions of biomedical articles"
```

**Code now outputs**:
```python
"EXAMPLE QUERIES:"
"1. \"Find a systematic review on pressure ulcer prevention\""
"TIP: Be specific! You can ask for 'recent', 'peer-reviewed'..."
```

**Semantic Gap**: Copy changed but assertions didn't update. Easy fix.

### Agent 3: AcademicResearchAgent

**Tests mock**:
```python
'agno.tools': MagicMock()  # Mocked
```

**Code imports**:
```python
from src.tools.literature_tools import LiteratureTools  # NOT in agno!
```

**Semantic Gap**: Test fixture doesn't know about project-specific tools.

---

## 5. Cleanup Plan

### Phase 1: Delete Broken Tests (Immediate)

**Files to modify**:

#### `test_nursing_research_agent.py`
```
DELETE: Lines 39-306 (all tests except test_global_instance_created)
KEEP: Lines 342-363 (test_global_instance_created)
RESULT: 14 tests removed, 1 test kept
```

#### `test_academic_research_agent.py`
```
DELETE: Lines 39-231 (TestAcademicResearchAgentInitialization, TestCreateAgent,
                      TestAcademicResearchAgentIntegration, TestShowUsageExamples)
DELETE: Lines 265-294 (TestCreateTools)
KEEP: Lines 233-262 (TestGlobalInstance - 2 tests)
RESULT: 12 tests removed, 2 tests kept
```

### Phase 2: Fix Assertion Drift (Quick)

#### `test_medical_research_agent.py`

**Fix test_show_usage_examples_includes_examples (line 281-300)**:
```python
# BEFORE:
assert "Find clinical studies:" in captured.out

# AFTER:
assert "EXAMPLE QUERIES:" in captured.out or "example" in captured.out.lower()
```

**Fix test_show_usage_examples_includes_tips (line 306-321)**:
```python
# BEFORE:
assert "PubMed has millions of biomedical articles" in captured.out

# AFTER:
assert "TIP:" in captured.out
```

**Fix test_global_instance_* (lines 339, 352)**:
```python
# BEFORE:
assert mra_module._medical_research_agent_instance is not None

# AFTER:
agent = mra_module.get_medical_research_agent()  # Trigger lazy init
assert agent is not None
assert mra_module._medical_research_agent_instance is not None
```

### Phase 3: Consolidate Fixtures (Clean Architecture)

**Move to `conftest.py`**:
```python
# tests/conftest.py - ADD THIS

@pytest.fixture
def mock_agno_modules():
    """Shared fixture for mocking agno framework dependencies.

    Use this when you need to test agent initialization without
    actually importing the agno framework.
    """
    mocks = {
        'agno': MagicMock(),
        'agno.agent': MagicMock(),
        'agno.db': MagicMock(),
        'agno.db.sqlite': MagicMock(),
        'agno.models': MagicMock(),
        'agno.models.openai': MagicMock(),
        'agno.models.response': MagicMock(),
        'agno.run': MagicMock(),
        'agno.run.agent': MagicMock(),
        'agno.tools': MagicMock(),
        # ADD: Project-specific tools
        'src.tools.literature_tools': MagicMock(
            LiteratureTools=MagicMock(return_value=MagicMock())
        ),
        'src.tools.milestone_tools': MagicMock(
            MilestoneTools=MagicMock(return_value=MagicMock())
        ),
    }

    with patch.dict(sys.modules, mocks):
        yield mocks
```

**Delete from individual test files**:
- `test_nursing_research_agent.py`: Remove lines 10-36
- `test_medical_research_agent.py`: Remove lines 10-36
- `test_academic_research_agent.py`: Remove lines 10-36

### Phase 4: Write New Tests (Proper Architecture)

**New test pattern** (integration-focused, not mock-heavy):

```python
# tests/unit/test_nursing_research_agent_v2.py

import pytest
from unittest.mock import patch, MagicMock

class TestNursingResearchAgentToolCreation:
    """Test tool creation with proper mocking at function level."""

    @patch('agents.nursing_research_agent.create_pubmed_tools_safe')
    @patch('agents.nursing_research_agent.create_clinicaltrials_tools_safe')
    @patch('agents.nursing_research_agent.create_medrxiv_tools_safe')
    @patch('agents.nursing_research_agent.create_semantic_scholar_tools_safe')
    @patch('agents.nursing_research_agent.create_core_tools_safe')
    @patch('agents.nursing_research_agent.create_doaj_tools_safe')
    @patch('agents.nursing_research_agent.create_safety_tools_safe')
    @patch('agents.nursing_research_agent.create_serp_tools_safe')
    @patch('agents.nursing_research_agent.LiteratureTools')
    @patch('agents.nursing_research_agent.build_tools_list')
    def test_creates_all_healthcare_tools(self, mock_build, mock_lit,
                                          mock_serp, mock_safety, mock_doaj,
                                          mock_core, mock_semantic, mock_medrxiv,
                                          mock_clinical, mock_pubmed):
        """Verify agent attempts to create all 9 tools."""
        # Setup
        mock_pubmed.return_value = MagicMock(name="pubmed")
        mock_build.return_value = [MagicMock()]

        # Import AFTER patches are in place
        from agents.nursing_research_agent import NursingResearchAgent

        # Create agent
        agent = NursingResearchAgent()

        # Verify all tool creation functions were called
        mock_pubmed.assert_called_once()
        mock_clinical.assert_called_once()
        mock_medrxiv.assert_called_once()
        # ... etc
```

---

## 6. Files Summary

### Files to Delete Tests From:

| File | Current Tests | After Cleanup | Lines Removed |
|------|--------------|---------------|---------------|
| `test_nursing_research_agent.py` | 15 | 1 | ~270 |
| `test_academic_research_agent.py` | 14 | 2 | ~230 |

### Files to Fix:

| File | Tests to Fix | Lines Changed |
|------|--------------|---------------|
| `test_medical_research_agent.py` | 4 | ~20 |

### Files to Add:

| File | Purpose |
|------|---------|
| `conftest.py` | Add shared mock_agno_modules fixture |

---

## 7. Quick Reference: What Each Mock Does

| Mock | Purpose | Still Needed? |
|------|---------|---------------|
| `'agno'` | Base agno package | YES - but use at function level |
| `'agno.agent'` | Agent class | YES |
| `'agno.db.sqlite'` | SqliteDb | YES |
| `'agno.models.openai'` | OpenAIChat | YES |
| `'agno.tools'` | Tool base classes | PARTIAL - add specific tools |
| `'agno.tools.pubmed'` | PubmedTools | ADD - currently missing |
| `'agno.tools.arxiv'` | ArxivTools | ADD - currently missing |
| `'src.tools.literature_tools'` | LiteratureTools | ADD - currently missing |
| `'src.tools.milestone_tools'` | MilestoneTools | ADD - for Agent 5 tests |

---

## 8. Execution Commands

### Step 1: Backup current tests
```bash
cp tests/unit/test_nursing_research_agent.py tests/unit/test_nursing_research_agent.py.bak
cp tests/unit/test_academic_research_agent.py tests/unit/test_academic_research_agent.py.bak
cp tests/unit/test_medical_research_agent.py tests/unit/test_medical_research_agent.py.bak
```

### Step 2: Run cleanup (after edits)
```bash
# Verify only expected tests remain
pytest tests/unit/test_nursing_research_agent.py --collect-only
pytest tests/unit/test_academic_research_agent.py --collect-only
pytest tests/unit/test_medical_research_agent.py --collect-only
```

### Step 3: Verify tests pass
```bash
pytest tests/unit/test_nursing_research_agent.py -v
pytest tests/unit/test_medical_research_agent.py -v
pytest tests/unit/test_academic_research_agent.py -v
```

---

*End of Semantic Analysis*
