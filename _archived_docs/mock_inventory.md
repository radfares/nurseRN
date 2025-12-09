# Mock Code Inventory

**Created**: 2025-12-07
**Purpose**: Complete record of all mock patterns from Agent 1-3 test files before cleanup
**Backup Location**: `tests/unit/backup/`

---

## Summary Statistics

| File | @patch Count | MagicMock Count | Mock() Count | Total |
|------|-------------|-----------------|--------------|-------|
| `test_nursing_research_agent.py` | 54 | 11 | 16 | **81** |
| `test_medical_research_agent.py` | 52 | 11 | 15 | **78** |
| `test_academic_research_agent.py` | 40 | 11 | 11 | **62** |
| **TOTAL** | 146 | 33 | 42 | **221** |

---

## 1. Shared Mock Fixture (Duplicated in All 3 Files)

```python
# Lines 10-36 in each file - IDENTICAL CODE
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

    # Remove agent module if present to force re-import with mocks
    if 'agents.{agent_name}' in sys.modules:
        del sys.modules['agents.{agent_name}']

    with patch.dict(sys.modules, mocks):
        from agents.{agent_name} import {AgentClass}
        yield {AgentClass}

    # Cleanup
    if 'agents.{agent_name}' in sys.modules:
        del sys.modules['agents.{agent_name}']
```

**Problem**: This fixture mocks `sys.modules` but the real imports happen BEFORE the mock is applied due to Python's import caching.

---

## 2. Agent 1: Nursing Research Agent Mocks

### @patch Decorators Used

```python
# Tool creation mocks (OUTDATED - code now uses 9 different tools)
@patch('agents.nursing_research_agent.create_exa_tools_safe')      # 12 uses
@patch('agents.nursing_research_agent.create_serp_tools_safe')     # 12 uses
@patch('agents.nursing_research_agent.build_tools_list')           # 15 uses

# Agent infrastructure mocks
@patch('agents.nursing_research_agent.Agent')                      # 5 uses
@patch('agents.nursing_research_agent.OpenAIChat')                 # 2 uses
@patch('agents.nursing_research_agent.SqliteDb')                   # 2 uses
@patch('agents.nursing_research_agent.get_db_path')                # 2 uses
@patch('agents.nursing_research_agent.get_api_status')             # 4 uses
```

### Mock Objects Created

```python
Mock(name="exa_tool")
Mock(name="serp_tool")
Mock(name="tool1")
Mock(name="tool2")
Mock(name="exa")
Mock(name="serp")
mock_db_instance = Mock()
mock_model_instance = Mock()
```

### What Was MISSING (why tests failed)

```python
# These were NOT mocked but ARE used by current code:
@patch('agents.nursing_research_agent.create_pubmed_tools_safe')        # MISSING
@patch('agents.nursing_research_agent.create_clinicaltrials_tools_safe') # MISSING
@patch('agents.nursing_research_agent.create_medrxiv_tools_safe')       # MISSING
@patch('agents.nursing_research_agent.create_semantic_scholar_tools_safe') # MISSING
@patch('agents.nursing_research_agent.create_core_tools_safe')          # MISSING
@patch('agents.nursing_research_agent.create_doaj_tools_safe')          # MISSING
@patch('agents.nursing_research_agent.create_safety_tools_safe')        # MISSING
@patch('agents.nursing_research_agent.LiteratureTools')                 # MISSING
```

---

## 3. Agent 2: Medical Research Agent Mocks

### @patch Decorators Used

```python
# Tool creation mocks
@patch('agents.medical_research_agent.create_pubmed_tools_safe')   # 14 uses
@patch('agents.medical_research_agent.build_tools_list')           # 14 uses

# Agent infrastructure mocks
@patch('agents.medical_research_agent.Agent')                      # 10 uses
@patch('agents.medical_research_agent.OpenAIChat')                 # 1 use
@patch('agents.medical_research_agent.SqliteDb')                   # 1 use
@patch('agents.medical_research_agent.get_db_path')                # 2 uses
@patch('agents.medical_research_agent.get_api_status')             # 6 uses
```

### Mock Objects Created

```python
Mock(name="pubmed_tool")
mock_db_instance = Mock()
mock_model_instance = Mock()
```

### What Was MISSING

```python
# LiteratureTools not mocked (used for saving findings)
@patch('agents.medical_research_agent.LiteratureTools')            # MISSING
```

---

## 4. Agent 3: Academic Research Agent Mocks

### @patch Decorators Used

```python
# Tool creation mocks
@patch('agents.academic_research_agent.create_arxiv_tools_safe')   # 14 uses
@patch('agents.academic_research_agent.build_tools_list')          # 14 uses

# Agent infrastructure mocks
@patch('agents.academic_research_agent.Agent')                     # 8 uses
@patch('agents.academic_research_agent.get_db_path')               # 1 use
@patch('agents.academic_research_agent.get_api_status')            # 5 uses
```

### Mock Objects Created

```python
Mock(name="arxiv_tool")
Mock(name="arxiv")
```

### What Was MISSING (CRITICAL - caused StopIteration)

```python
# This was the killer - LiteratureTools imported from src.tools, not agno
@patch('agents.academic_research_agent.LiteratureTools')           # MISSING
@patch('src.tools.literature_tools.LiteratureTools')               # MISSING
```

---

## 5. Complete @patch Reference by Test Class

### Agent 1: test_nursing_research_agent.py

| Test Class | Patches Used |
|------------|--------------|
| `TestNursingResearchAgentInitialization` | `create_exa_tools_safe`, `create_serp_tools_safe`, `build_tools_list` |
| `TestCreateTools` | `create_exa_tools_safe`, `create_serp_tools_safe`, `build_tools_list` |
| `TestCreateAgent` | `Agent`, `OpenAIChat`, `SqliteDb`, `get_db_path`, `create_exa_tools_safe`, `create_serp_tools_safe`, `build_tools_list` |
| `TestShowUsageExamples` | `get_api_status`, `create_exa_tools_safe`, `create_serp_tools_safe`, `build_tools_list` |
| `TestNursingResearchAgentIntegration` | `Agent`, `create_exa_tools_safe`, `create_serp_tools_safe`, `build_tools_list` |

### Agent 2: test_medical_research_agent.py

| Test Class | Patches Used |
|------------|--------------|
| `TestMedicalResearchAgentInitialization` | `create_pubmed_tools_safe`, `build_tools_list` |
| `TestCreateTools` | `create_pubmed_tools_safe`, `build_tools_list` |
| `TestCreateAgent` | `Agent`, `OpenAIChat`, `SqliteDb`, `get_db_path`, `create_pubmed_tools_safe`, `build_tools_list` |
| `TestMedicalResearchAgentIntegration` | `Agent`, `create_pubmed_tools_safe`, `build_tools_list` |
| `TestShowUsageExamples` | `get_api_status`, `Agent`, `create_pubmed_tools_safe`, `build_tools_list` |
| `TestGlobalInstance` | `Agent`, `create_pubmed_tools_safe`, `build_tools_list` |

### Agent 3: test_academic_research_agent.py

| Test Class | Patches Used |
|------------|--------------|
| `TestAcademicResearchAgentInitialization` | `create_arxiv_tools_safe`, `build_tools_list` |
| `TestCreateAgent` | `Agent`, `get_db_path`, `create_arxiv_tools_safe`, `build_tools_list` |
| `TestAcademicResearchAgentIntegration` | `Agent`, `create_arxiv_tools_safe`, `build_tools_list` |
| `TestShowUsageExamples` | `get_api_status`, `Agent`, `create_arxiv_tools_safe`, `build_tools_list` |
| `TestGlobalInstance` | `Agent`, `create_arxiv_tools_safe`, `build_tools_list` |
| `TestCreateTools` | `create_arxiv_tools_safe`, `build_tools_list` |

---

## 6. Why These Mocks Failed

### Problem 1: Import Timing

```python
# Test file structure:
from unittest.mock import patch  # Step 1: Import mock

@pytest.fixture
def mock_agno():
    mocks = {'agno': MagicMock()}
    with patch.dict(sys.modules, mocks):  # Step 3: Apply mock
        from agents.nursing_research_agent import NursingResearchAgent  # Step 4: Import
        yield NursingResearchAgent

# BUT Python already did this when loading the test file:
# Step 2: Python sees the import in the fixture and pre-loads the module
# So by Step 3, the real 'agno' is already imported
```

### Problem 2: Incomplete Coverage

```python
# Tests mocked:
'agno.tools': MagicMock()

# But code imports:
from src.tools.literature_tools import LiteratureTools  # NOT in agno namespace!
```

### Problem 3: Semantic Drift

```python
# Tests expected (old code):
create_exa_tools_safe(required=False)
create_serp_tools_safe(required=False)

# Code now uses (new code):
create_pubmed_tools_safe(required=True)  # PRIMARY
create_clinicaltrials_tools_safe()
create_medrxiv_tools_safe()
# ... 6 more tools
```

---

## 7. Recommended Mock Pattern (For Future Tests)

```python
# CORRECT: Patch at the point of use, not at import
@patch('agents.nursing_research_agent.create_pubmed_tools_safe')
@patch('agents.nursing_research_agent.create_clinicaltrials_tools_safe')
@patch('agents.nursing_research_agent.create_medrxiv_tools_safe')
@patch('agents.nursing_research_agent.create_semantic_scholar_tools_safe')
@patch('agents.nursing_research_agent.create_core_tools_safe')
@patch('agents.nursing_research_agent.create_doaj_tools_safe')
@patch('agents.nursing_research_agent.create_safety_tools_safe')
@patch('agents.nursing_research_agent.create_serp_tools_safe')
@patch('agents.nursing_research_agent.LiteratureTools')  # Don't forget this!
@patch('agents.nursing_research_agent.build_tools_list')
def test_creates_all_tools(self, mock_build, mock_lit, ...):
    # Setup mocks
    mock_pubmed.return_value = MagicMock(name="pubmed")
    mock_lit.return_value = MagicMock(name="literature_tools")
    mock_build.return_value = [MagicMock()]

    # Import AFTER patches applied
    from agents.nursing_research_agent import NursingResearchAgent

    # Test
    agent = NursingResearchAgent()
    assert ...
```

---

## 8. Files Reference

| File | Location | Status |
|------|----------|--------|
| Original `test_nursing_research_agent.py` | `tests/unit/backup/` | Preserved |
| Original `test_medical_research_agent.py` | `tests/unit/backup/` | Preserved |
| Original `test_academic_research_agent.py` | `tests/unit/backup/` | Preserved |
| Cleaned `test_nursing_research_agent.py` | `tests/unit/` | 6 tests, all pass |
| Fixed `test_medical_research_agent.py` | `tests/unit/` | 17 tests, all pass |
| Cleaned `test_academic_research_agent.py` | `tests/unit/` | 8 tests, all pass |

---

*End of Mock Inventory*
