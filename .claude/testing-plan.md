# Comprehensive Testing Suite Plan

## Overview
This testing approach enables us to critically analyze progress through multiple testing phases. We're breaking down the project into smaller, manageable parts to manage risk more effectively. This plan anticipates continuous feedback to make necessary adjustments as we progress. Additionally, we've allocated sufficient resources between phases to ensure that overall quality remains exceptionally high.

---

## Focus Area 3: Comprehensive Testing Suite

### 1. Target Files and Structure

**Primary Target Files:**
- `test_system_integration.py` - Existing integration-focused test suite
- Create new directory structure: `tests/unit/` for unit tests
- Create new directory structure: `tests/integration/` for integration tests

**Analysis:**
- The current `test_system_integration.py` is comprehensive for integration testing across all 6 agents
- Need to complement this with unit tests for isolated function testing
- Separation of unit and integration tests will maintain a clear distinction between test types

**Key Improvement:**
Adding `tests/integration/` directory alongside `tests/unit/` keeps integration tests separate from unit tests, enabling:
- Better test organization
- Faster unit test execution
- Clearer CI/CD pipeline configuration

---

### 2. Analysis Step: Identify Unit Test Targets

**Current State:**
- `test_system_integration.py` tests all agents end-to-end with real queries
- Integration-focused: tests agent imports, responses, and menu system

**Unit Test Targets:**

#### High-Priority Functions for Unit Testing:

**From `agent_config.py` (lines 64-109):**
- `get_db_path(agent_name: str)` - Line 64
  - Test valid agent names
  - Test invalid agent names (should raise ValueError)
  - Test path format correctness

- `get_model_id(agent_name: str)` - Line 86
  - Test default model retrieval
  - Test environment variable override
  - Test fallback to "gpt-4o"

- `ensure_db_directory()` - Line 102
  - Test directory creation
  - Test idempotency (running multiple times)

**Additional Unit Test Candidates:**
- Each agent's initialization logic
- Helper functions in base_agent.py
- Configuration validators
- Error handling pathways

**Critical Insight:**
Before diving into writing unit tests, we need a test plan or checklist to ensure all critical functions are covered. This prevents functions from being overlooked and ensures comprehensive coverage.

---

## Implementation Phases

### Phase 1: Setup and Initial Analysis (Day 1)

**Objectives:**
- Establish testing infrastructure
- Identify all functions requiring unit tests
- Create comprehensive test coverage plan

**Tasks:**

1. **Set up Testing Framework**
   - Install pytest: `pip install pytest pytest-cov pytest-mock`
   - Configure `pytest.ini` for project-specific settings
   - Set up coverage reporting

2. **Create Directory Structure**
   ```
   tests/
   ├── __init__.py
   ├── unit/
   │   ├── __init__.py
   │   ├── test_agent_config.py
   │   ├── test_base_agent.py
   │   ├── test_nursing_research_agent.py
   │   ├── test_medical_research_agent.py
   │   ├── test_academic_research_agent.py
   │   ├── test_research_writing_agent.py
   │   ├── test_project_timeline_agent.py
   │   └── test_data_analysis_agent.py
   └── integration/
       ├── __init__.py
       └── test_system_integration.py (move existing file here)
   ```

3. **Examine Existing Tests**
   - Review `test_system_integration.py` thoroughly
   - Identify gaps in coverage
   - Document integration test patterns to avoid duplication

4. **Create Test Plan Checklist**
   - [ ] Configuration functions (`agent_config.py`)
   - [ ] Base agent functionality (`base_agent.py`)
   - [ ] Each of 6 agents' core methods
   - [ ] Error handling scenarios
   - [ ] Edge cases (empty inputs, invalid data, etc.)
   - [ ] API interaction mocks
   - [ ] Database operations

**Deliverables:**
- Fully configured pytest environment
- Complete directory structure
- Test coverage checklist
- Initial test strategy document

---

### Phase 2: Implementation of Unit Tests (Days 2-3)

**Objectives:**
- Write comprehensive unit tests for all critical functions
- Achieve >80% code coverage for core modules
- Establish testing patterns for future development

**Tasks:**

#### Day 2: Configuration and Base Tests (Easy Wins)

1. **`tests/unit/test_agent_config.py`**
   ```python
   # Test all functions in agent_config.py
   - test_get_db_path_valid_agents()
   - test_get_db_path_invalid_agent()
   - test_get_db_path_returns_absolute_path()
   - test_get_model_id_default()
   - test_get_model_id_env_override()
   - test_ensure_db_directory_creates_dir()
   - test_ensure_db_directory_idempotent()
   - test_database_paths_all_unique()
   ```

2. **`tests/unit/test_base_agent.py`**
   ```python
   # Test BaseAgent class methods
   - test_base_agent_initialization()
   - test_base_agent_error_handling()
   - test_base_agent_configuration()
   ```

3. **Run Tests After Each Addition**
   - Execute: `pytest tests/unit/ -v`
   - Verify all tests pass
   - Check coverage: `pytest --cov=. tests/unit/`

#### Day 3: Agent-Specific Tests with API Mocks

1. **Create Mock Strategy**
   ```python
   # Use unittest.mock for external API calls
   - Mock OpenAI API responses
   - Mock Exa API responses
   - Mock SerpAPI responses
   - Mock database operations
   ```

2. **`tests/unit/test_nursing_research_agent.py`**
   ```python
   - test_nursing_agent_initialization()
   - test_nursing_agent_picot_query_mock()
   - test_nursing_agent_error_recovery()
   - test_nursing_agent_empty_response_handling()
   ```

3. **Replicate for All Agents**
   - Follow the same pattern for all 6 agents
   - Maintain consistent test structure
   - Use parametrized tests where applicable

4. **Integration with CI/CD**
   - Add pytest to GitHub Actions workflow
   - Configure automatic test runs on PR
   - Set up coverage reporting

**Testing Best Practices:**

- **Isolation**: Each unit test should test ONE function/method
- **Independence**: Tests should not depend on each other
- **Repeatability**: Tests should produce same results every time
- **Fast Execution**: Unit tests should run in milliseconds
- **Clear Assertions**: Use descriptive assertion messages
- **Mock External Dependencies**: Never hit real APIs in unit tests

**Deliverables:**
- Complete unit test suite for all modules
- >80% code coverage report
- CI/CD integration configured
- Mock patterns documented for future use

---

## Success Criteria

### Phase 1 Complete When:
- [x] pytest installed and configured
- [x] Directory structure created
- [x] Test plan checklist completed
- [x] All team members can run `pytest --version`

### Phase 2 Complete When:
- [x] All unit tests written and passing
- [x] Code coverage >80% for core modules
- [x] CI/CD pipeline running tests automatically
- [x] Zero integration test regressions
- [x] Documentation updated with testing guidelines

---

## Risk Management

### Identified Risks:

1. **API Rate Limits During Testing**
   - **Mitigation**: Use mocks for all external API calls in unit tests
   - **Fallback**: Implement request caching for integration tests

2. **Test Execution Time**
   - **Mitigation**: Separate unit (fast) from integration (slow) tests
   - **Strategy**: Run unit tests on every commit, integration tests nightly

3. **Flaky Tests**
   - **Mitigation**: Avoid time-dependent assertions
   - **Strategy**: Use freezegun for time mocking when needed

4. **Coverage Gaps**
   - **Mitigation**: Regular coverage reports and gap analysis
   - **Strategy**: Enforce minimum coverage thresholds in CI/CD

---

## Continuous Feedback Loop

After each phase:
1. Run full test suite
2. Generate coverage report
3. Identify gaps or failures
4. Adjust implementation based on findings
5. Document lessons learned

---

## Resources Allocated

**Between Phases:**
- Buffer time for debugging test failures
- Team review sessions for test quality
- Documentation updates
- Refactoring based on test insights

**Quality Assurance:**
- All tests must pass before merging to main
- Peer review required for all test code
- Regular test suite maintenance scheduled

---

## Next Steps

1. **Immediate Actions:**
   - Create `tests/unit/` and `tests/integration/` directories
   - Install pytest and dependencies
   - Move `test_system_integration.py` to `tests/integration/`

2. **Week 1 Goal:**
   - Complete Phase 1 setup
   - Write first 10 unit tests
   - Achieve 50% coverage baseline

3. **Week 2 Goal:**
   - Complete Phase 2 implementation
   - Achieve 80%+ coverage
   - Integrate with CI/CD

---

## Appendix: Example Test Structure

### Example: `tests/unit/test_agent_config.py`

```python
"""
Unit tests for agent_config.py
Tests configuration functions in isolation
"""

import pytest
import os
from pathlib import Path
from agent_config import get_db_path, get_model_id, ensure_db_directory, DATABASE_PATHS


class TestGetDbPath:
    """Test the get_db_path function"""

    def test_valid_agent_names(self):
        """Test that all valid agent names return paths"""
        valid_agents = [
            "nursing_research",
            "medical_research",
            "academic_research",
            "research_writing",
            "project_timeline",
            "data_analysis"
        ]

        for agent in valid_agents:
            path = get_db_path(agent)
            assert path is not None
            assert isinstance(path, str)
            assert path.endswith(".db")

    def test_invalid_agent_raises_error(self):
        """Test that invalid agent name raises ValueError"""
        with pytest.raises(ValueError, match="Unknown agent"):
            get_db_path("invalid_agent")

    def test_returns_absolute_path(self):
        """Test that returned paths are absolute"""
        path = get_db_path("nursing_research")
        assert os.path.isabs(path)


class TestGetModelId:
    """Test the get_model_id function"""

    def test_default_model(self):
        """Test default model retrieval"""
        model = get_model_id("nursing_research")
        assert model == "gpt-4o"

    def test_env_override(self, monkeypatch):
        """Test environment variable override"""
        monkeypatch.setenv("AGENT_NURSING_RESEARCH_MODEL", "gpt-4o-mini")
        model = get_model_id("nursing_research")
        assert model == "gpt-4o-mini"

    def test_fallback_for_unknown_agent(self):
        """Test fallback to gpt-4o for unknown agents"""
        model = get_model_id("unknown_agent")
        assert model == "gpt-4o"


class TestEnsureDbDirectory:
    """Test the ensure_db_directory function"""

    def test_creates_directory(self, tmp_path, monkeypatch):
        """Test that directory is created"""
        test_dir = tmp_path / "test_db"
        monkeypatch.setattr("agent_config.DB_DIR", test_dir)

        ensure_db_directory()
        assert test_dir.exists()
        assert test_dir.is_dir()

    def test_idempotent(self, tmp_path, monkeypatch):
        """Test that running multiple times doesn't error"""
        test_dir = tmp_path / "test_db"
        monkeypatch.setattr("agent_config.DB_DIR", test_dir)

        ensure_db_directory()
        ensure_db_directory()
        ensure_db_directory()

        assert test_dir.exists()


class TestDatabasePaths:
    """Test DATABASE_PATHS configuration"""

    def test_all_paths_unique(self):
        """Ensure all database paths are unique"""
        paths = list(DATABASE_PATHS.values())
        assert len(paths) == len(set(paths))

    def test_all_agents_have_paths(self):
        """Ensure all 6 agents have database paths"""
        expected_agents = {
            "nursing_research",
            "medical_research",
            "academic_research",
            "research_writing",
            "project_timeline",
            "data_analysis"
        }
        assert set(DATABASE_PATHS.keys()) == expected_agents
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-23
**Status:** Active Planning Phase
