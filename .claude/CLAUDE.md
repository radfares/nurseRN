# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Last Updated**: 2025-11-28 (Schema Validation Tests Added)

---

## 🚀 Current Project Status (as of 2025-11-28)

### 📊 Current Metrics
- **Test Coverage**: 89% (Data Analysis Agent), 94% overall
- **Total Tests**: 173+ (30 for Data Analysis Agent)
- **Agents**: 6 specialized + 1 base class (all in `agents/` module)
- **Total Python Lines**: 3,699+
- **External Tools**: 4 integrated (PubMed, SerpAPI, ArXiv, Exa)

### 🏗️ Architecture Status
- **Project-Centric Database**: ✅ Complete (7 tables)
- **Circuit Breaker Protection**: ✅ All APIs protected
- **HTTP Caching**: ✅ 24hr TTL operational (`api_cache.sqlite`)
- **Agent Inheritance**: ✅ All agents use BaseAgent pattern
- **Schema Validation**: ✅ Pydantic models with comprehensive test coverage
- **Milestone Tools**: ✅ Database-driven timeline queries

---

## Overview

This is a **project-centric multi-agent AI system** designed to support nursing residents through healthcare improvement projects. Built with the **Agno framework** (vendored in `libs/agno/`), it provides 6 specialized AI agents for research, writing, planning, and statistical analysis.

**Key Architecture Principle**: Each nursing resident has their own project with its own SQLite database containing all research data (PICOT versions, literature findings, analysis plans, milestones, writing drafts, conversations, and documents).

**Project Status**: Production-ready with 94% test coverage, professional file organization, comprehensive documentation.

📝 **UPDATE NEEDED**: Confirm actual project timeline dates - documentation shows "Nov 2025 - June 2026" which appears to be a template. Actual timeline may be Nov 2024 - June 2025 or needs clarification.

---

## Quick Start

### First Time Setup

1. **Clone and Install**:
   ```bash
   cd nurseRN
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure API Keys**:
   ```bash
   cp .env.example .env
   # Edit .env and add OPENAI_API_KEY (required)
   # Optionally add: EXA_API_KEY, SERP_API_KEY, PUBMED_EMAIL
   ```

3. **Verify Setup**:
   ```bash
   python3 verify_setup.py
   ```

### Daily Development Workflow

**Start the System**:
```bash
./start_nursing_project.sh  # Recommended - sets PYTHONPATH automatically
```

**Run Tests** (before committing):
```bash
pytest --cov=. --cov-report=term-missing
```

**Test Individual Agent**:
```bash
python3 -m agents.nursing_research_agent
```

### Manual Start (if start script doesn't work)

```bash
source .venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno"
python3 run_nursing_project.py
```

---

## Environment Setup

The system requires:
- **OPENAI_API_KEY** (required for all agents)
- **EXA_API_KEY** (optional - for Nursing Research Agent web searches)
- **SERP_API_KEY** (optional - for Nursing Research Agent Google searches)
- **PUBMED_EMAIL** (optional - for Medical Research Agent identification)

All API keys must be in `.env` file (never committed to git - it's in `.gitignore`).

**Cost Estimates** (from README.md):
- Moderate monthly use: $10-20
- Per-query costs: $0.001-$0.04 depending on agent
- Timeline agent optimized with GPT-4o-mini for cost savings

---

## Architecture Deep Dive

### Project-Centric Database Model

**Central Concept**: Everything is organized by project, not by agent. Each project has:
- Location: `data/projects/{project_name}/`
- Database: `data/projects/{project_name}/project.db`
- Documents: `data/projects/{project_name}/documents/`

**Active Project Tracking**: `data/.active_project` file (7 bytes) stores the currently selected project name.
This persists across sessions, so when you restart `run_nursing_project.py`, it automatically loads your last active project.

**Example**:
```bash
$ cat data/.active_project
myproject
```

**Database Schema** (7 core tables):
1. **picot_versions** - PICOT question development and approval tracking
2. **literature_findings** - Articles, standards, guidelines from all research agents
3. **analysis_plans** - Statistical test selection, sample size calculations, data templates
4. **milestones** - Project timeline tracking (6 default milestones: PICOT Development → Final Presentation)
5. **writing_drafts** - PICOT questions, literature reviews, intervention plans
6. **conversations** - Tagged by agent_name with linking to created records
7. **documents** - File metadata with text extraction support

See `project_manager.py` constant `SCHEMA_DDL` (approximately lines 34-295) for complete schema DDL.

⚠️ **IMPROVEMENT NEEDED**: Line numbers are fragile and change with code updates. Reference constant name instead.

---

### Agent Architecture

**Inheritance Pattern** (established Phase 2):
```python
BaseAgent (agents/base_agent.py)
  ├── NursingResearchAgent (agents/nursing_research_agent.py)
  ├── MedicalResearchAgent (agents/medical_research_agent.py)
  ├── AcademicResearchAgent (agents/academic_research_agent.py)
  ├── ResearchWritingAgent (agents/research_writing_agent.py)
  ├── ProjectTimelineAgent (agents/nursing_project_timeline_agent.py)
  └── DataAnalysisAgent (agents/data_analysis_agent.py)
```

**BaseAgent Responsibilities**:
- Standardized logging setup
- Error handling with try/except patterns
- Agent creation framework
- Abstract methods: `_create_agent()`, `show_usage_examples()`

**Configuration Centralization** (`agent_config.py`):
- Database paths (agent session DBs in `tmp/`)
- Model configuration with environment variable overrides
- Logging configuration

**Code Metrics** (as of 2025-11-26):
- Total Python lines: 3,699
- Largest file: `project_manager.py` (698 lines)
- Average agent size: ~190-220 lines
- Test coverage: 94% (Phase 2 Enhanced)

---

### Resilience Architecture

**Circuit Breaker Pattern** (`src/services/circuit_breaker.py`):
- Protects against API failures
- 5 failure threshold → 60 second cooldown timeout
- Tracks failures over time windows
- Automatic recovery after success
- Logging listener for state changes

**Safe Tool Creation** (`src/services/api_tools.py`):
- Graceful fallback when API keys missing
- HTTP response caching (24hr TTL via requests-cache, SQLite backend: `api_cache.sqlite`)
- API status reporting
- Never crashes if optional tools unavailable
- CircuitProtectedToolWrapper class intercepts ALL tool method calls

**Critical Rule**: Agents work even with only OPENAI_API_KEY. Optional tools (Exa, SerpAPI, PubMed) fail gracefully.

**Tool Creation Pattern** (Week 1 Refactoring):
All agents use `create_{tool}_safe()` functions:
```python
def _create_tools(self) -> list:
    """Create tools with safe fallback."""
    exa_tool = create_exa_tools_safe(required=False)  # Returns None if key missing
    serp_tool = create_serp_tools_safe(required=False)
    tools = build_tools_list(exa_tool, serp_tool)  # Filters out None values
    # Agent logs which tools are available
    return tools
```

📝 **UPDATE NEEDED**: Add detailed documentation on HTTP cache location, cleanup strategy, and how to inspect cache.

---

### Agent-Specific Details

**Nursing Research Agent** (Agent 1):
- File: `agents/nursing_research_agent.py` (335+ lines)
- Tools: 
  - PubmedTools (PRIMARY - peer-reviewed clinical studies) - Free
  - ClinicalTrialsTools (clinical trial database) - Free
  - MedRxivTools (medical preprints) - Free
  - SemanticScholarTools (AI-powered paper discovery) - Free tier
  - CoreTools (open-access research) - Free
  - DoajTools (open-access journals) - Free
  - SerpApiTools (standards/guidelines) - Optional, requires SERP_API_KEY
  - ExaTools - DISABLED (not for healthcare)
  - ArxivTools - DISABLED (not for healthcare)
- Focus: PICOT development, healthcare standards, comprehensive literature search
- Database: `tmp/nursing_research_agent.db` (session) + project DB
- Model: GPT-4o

**Medical Research Agent** (Agent 2):
- File: `agents/medical_research_agent.py` (208 lines)
- Tools: PubmedTools (no API key required, uses PUBMED_EMAIL)
- Focus: Peer-reviewed clinical studies with full metadata
- Enhanced with DOI, URLs, MeSH terms, structured abstracts
- Database: `tmp/medical_research_agent.db` (session) + project DB
- Model: GPT-4o

**Academic Research Agent** (Agent 3):
- File: `agents/academic_research_agent.py` (188 lines)
- Tools: ArxivTools (free, no authentication)
- Focus: Statistical methods, theoretical research
- Database: `tmp/academic_research_agent.db` (session) + project DB
- Model: GPT-4o

**Research Writing Agent** (Agent 4):
- File: `agents/research_writing_agent.py` (219 lines)
- Tools: None (pure writing/organization)
- Focus: PICOT writing, literature synthesis, intervention planning
- Database: `tmp/research_writing_agent.db` (session) + project DB
- Model: GPT-4o

**Project Timeline Agent** (Agent 5):
- File: `agents/nursing_project_timeline_agent.py` (218 lines)
- Tools: MilestoneTools (database query tools for project milestones)
- Model: GPT-4o-mini (cost-effective for timeline queries)
- Focus: Database-driven milestone tracking and timeline guidance
- Database: `tmp/project_timeline_agent.db` (session) + project DB
- **Updated (2025-11-27)**: Now queries milestones table instead of using hardcoded dates

**Data Analysis Planner** (Agent 6):
- File: `agents/data_analysis_agent.py` (253 lines)
- Tools: None (pure statistical reasoning)
- Model: GPT-4o with temperature=0.2 for reliability
- Focus: Sample size, test selection, data templates, analysis plans
- Output: Structured JSON with confidence scores, reproducible R/Python code
- Database: `tmp/data_analysis_agent.db` (session) + project DB

---

## Claude Code Skills Integration

**Skills Directory**: `.claude/skills/` contains specialized sub-agents for specific refactoring and analysis tasks.

**Available Skills**:
- **legacy-code-reviewer** - Expert system for identifying deprecated patterns, suggesting refactoring to modern standards (e.g., ES2024), and checking test coverage
  - Location: `.claude/skills/legacy-code-reviewer/`
  - Allowed tools: Read, Grep, Glob
  - Use when: User asks to refactor, update, or analyze old codebase segments
  - Type: Project skill (project-specific)

**Invoking Skills**:
Skills are automatically available in Claude Code interface when `.claude/skills/` directory exists with properly formatted `SKILL.md` files.

---

## Testing & Quality Assurance

### Test Coverage

**Current Status**: 94% code coverage achieved (Phase 2 Enhanced - commit 2e413afd)

**Test Structure**:
```
tests/
├── unit/                      # Unit tests per agent/module
│   ├── test_base_agent.py     # BaseAgent functionality (26+ tests)
│   ├── test_nursing_research_agent.py  # Nursing Research Agent (15+ tests)
│   ├── test_medical_research_agent.py
│   ├── test_academic_research_agent.py
│   ├── test_research_writing_agent.py
│   ├── test_project_timeline_agent.py
│   ├── test_data_analysis_agent.py
│   ├── test_agent_config.py
│   └── __init__.py
├── integration/               # System integration tests
│   ├── test_system_integration.py
│   └── __init__.py
└── conftest.py                # Pytest configuration with PYTHONPATH setup
```

**Running Tests**:
```bash
# All tests
pytest

# With coverage report (terminal)
pytest --cov=. --cov-report=term-missing

# With HTML coverage report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# Specific test file
pytest tests/unit/test_base_agent.py -v

# Async tests (supported via pytest-asyncio)
pytest tests/integration/test_system_integration.py
```

**Test Utilities**:
- `verify_setup.py` (190 lines) - Setup verification script
- `test_resilience.py` (259 lines) - Resilience testing
- `test_schema_spike.py` (706 lines) - Database schema spike testing

### Test Patterns

#### Schema Validation Testing Pattern

**Purpose**: Validate Pydantic schemas with Literal type constraints and Field validators

**Example** (from `test_data_analysis_agent.py`):

```python
from agents.data_analysis_agent import (
    DataAnalysisOutput, EffectSize, MethodInfo,
    Parameters, SampleSize, DataColumn, DataTemplate, ReproCode
)
from pydantic import ValidationError

class TestStructuredOutputValidation:
    """Test structured output schema validation"""

    def test_valid_output_schema_parsing(self):
        """Test that a valid response conforms to schema"""
        # Create nested models
        effect_size = EffectSize(
            type="Cohen_d",
            value=0.7,
            how_estimated="literature review"
        )

        method = MethodInfo(
            name="Two-proportion z-test",
            justification="Comparing CAUTI rates pre/post intervention"
        )

        params = Parameters(
            effect_size=effect_size,
            design="parallel groups",
            alpha=0.05,
            power=0.80
        )

        # ... build complete output ...

        output = DataAnalysisOutput(
            task="sample_size",  # Literal type validation
            confidence=0.90,  # Field(ge=0.0, le=1.0) validation
            # ... other fields ...
        )

        assert output.task == "sample_size"
        assert output.confidence == 0.90

    def test_confidence_boundary_values(self):
        """Test Field constraints enforce 0.0-1.0 range"""
        with pytest.raises(ValidationError):
            DataAnalysisOutput(
                confidence=1.5,  # Invalid: exceeds max
                # ... other required fields ...
            )

    def test_repro_code_language_validation(self):
        """Test Literal type constraints (R or Python only)"""
        with pytest.raises(ValidationError):
            ReproCode(
                language="JavaScript",  # Invalid: not in Literal["R", "Python"]
                snippet="console.log('test')"
            )
```

**Key Patterns**:
1. **Nested Model Validation**: Build complete object graphs to test complex schemas
2. **Boundary Testing**: Test Field constraints (ge/le values)
3. **Literal Type Testing**: Verify only allowed values accepted
4. **Required Field Testing**: Ensure ValidationError on missing required fields
5. **Full Schema Testing**: Create complete valid instances to verify schema design

**Coverage Results** (Data Analysis Agent):
- 30 tests, 100% pass rate
- 89% code coverage (94 statements, 10 missed)
- Runtime: 0.13s (4.3ms/test average)
- Zero skipped tests

---

## Agno Framework Integration

**Vendored Library**: The Agno framework is included in `libs/agno/` (not installed via pip to avoid dependency conflicts).

**PYTHONPATH Setup**: Must add `libs/agno` to PYTHONPATH before running:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno"
```

This is automatically handled by `start_nursing_project.sh`.

**Key Agno Patterns** (from `.cursorrules` file in project root):
- **NEVER create agents in loops** - reuse them for performance
- Always use `output_schema` for structured responses
- PostgreSQL for production, SQLite for dev
- Use `search_knowledge=True` with knowledge bases
- Agent creation is expensive - create once, call `.run()` multiple times

**Common Agno Imports**:
```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.tools.pubmed import PubmedTools
from agno.tools.arxiv import ArxivTools
from agno.tools.exa import ExaTools
from agno.tools.serp_api import SerpApiTools
```

---

## Critical Development Rules

### From `.cursorrules` - MUST FOLLOW

**Location**: `.cursorrules` file in project root directory

**Execution Rules (TOP PRIORITY)**:
- NEVER execute code that makes API calls without explicit "EXECUTE NOW" or "RUN THIS" command
- NEVER create files without showing content first and getting explicit approval
- NEVER use API keys automatically - having a key is NOT permission to use it
- API calls cost money - treat them like financial transactions requiring authorization

**Agent Reuse**:
```python
# WRONG - Creates agent every time (huge overhead, 10x slower)
for query in queries:
    agent = Agent(...)  # DON'T DO THIS

# CORRECT - Create once, reuse
agent = Agent(...)
for query in queries:
    agent.run(query)  # Much faster
```

---

### Adding a New Agent

**Step-by-Step Guide**:

1. **Create file**: `agents/{agent_name}_agent.py`

2. **Inherit from `BaseAgent`**:
```python
from agents.base_agent import BaseAgent
from agent_config import get_db_path, get_model_id

class MyAgent(BaseAgent):
    def __init__(self):
        tools = self._create_tools() if self._needs_tools() else []
        super().__init__(
            agent_name="My Agent Name",
            agent_key="my_agent",  # for database path
            tools=tools
        )

    def _create_tools(self) -> list:
        """Create tools with safe fallback."""
        from src.services.api_tools import create_safe_tool_instance

        tool = create_safe_tool_instance(
            tool_class_name="SomeToolClass",
            api_key_env_var="SOME_API_KEY",
            import_path="agno.tools.sometool",
            logger=self.logger
        )
        return [tool] if tool else []

    def _create_agent(self):
        from agno.agent import Agent
        from agno.models.openai import OpenAIChat
        from agno.db.sqlite import SqliteDb

        return Agent(
            model=OpenAIChat(id=get_model_id("my_agent")),
            tools=self.tools,
            db=SqliteDb(db_file=get_db_path("my_agent")),
            instructions="...",
            add_history_to_context=True,
            num_history_runs=3,
            markdown=True,
        )

    def show_usage_examples(self):
        print("Agent ready!")
        print("\nExample queries:")
        print("  - Query 1")

# Create global instance for backward compatibility
_my_agent_instance = MyAgent()
my_agent = _my_agent_instance.agent
```

3. **Add to `agent_config.py`** - Add database path (around line 26):
```python
DATABASE_PATHS = {
    # ... existing ...
    "my_agent": str(DB_DIR / "my_agent.db"),
}
```

4. **Add to `agent_config.py`** - Add default model (around line 40):
```python
DEFAULT_MODELS = {
    # ... existing ...
    "my_agent": "gpt-4o",  # or "gpt-4o-mini" for cost savings
}
```

5. **Import in `run_nursing_project.py`** (around line 34):
```python
from my_agent import my_agent
```

6. **Add to agent menu in `run_nursing_project.py`** (around line 204):
```python
agent_map = {
    # ... existing ...
    '7': (my_agent, "My Agent Name"),
}
```

⚠️ **IMPROVEMENT NEEDED**: Line numbers are approximate and change with updates. Consider using function/class names instead.

📝 **UPDATE NEEDED**: Add guide for integrating new agent with project database (not just session DB).

---

### Testing Patterns

**Creating Unit Tests**:

1. Create `tests/unit/test_my_agent.py`
2. Use pytest fixtures from `conftest.py`
3. Mock external API calls
4. Test both success and failure cases

**Example Test**:
```python
import pytest
from unittest.mock import Mock, patch
from my_agent import MyAgent

def test_agent_initialization():
    """Test that agent initializes correctly."""
    agent = MyAgent()
    assert agent.agent_name == "My Agent Name"
    assert agent.agent_key == "my_agent"

@patch('os.getenv')
def test_agent_with_missing_api_key(mock_getenv):
    """Test graceful degradation when API key missing."""
    mock_getenv.return_value = None
    agent = MyAgent()
    assert agent.tools == []  # Should have no tools but not crash
```

**Test Execution**:
```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=term-missing

# Specific file
pytest tests/unit/test_my_agent.py -v
```

---

### Error Handling Pattern

**Level 1: BaseAgent Built-in** (all agents inherit this):
```python
try:
    # Agent logic
    self.logger.info("Starting operation")
    agent.print_response(query, stream=True)
except KeyboardInterrupt:
    self.logger.info("Interrupted by user")
except Exception as e:
    self.logger.error(f"Error: {e}", exc_info=True)
    raise
```

**Level 2: Circuit Breaker Protection** (for API tools):
API tools are automatically wrapped with circuit breakers via `CircuitProtectedToolWrapper`:
```python
from src.services.circuit_breaker import call_with_breaker, EXA_BREAKER

result = call_with_breaker(
    EXA_BREAKER,
    exa_api.search,
    "Exa search temporarily unavailable. Wait 60 seconds and try again.",
    query="healthcare"
)
# Returns dict with error info if circuit is open
```

**Level 3: Manual Circuit Breaker** (for custom functions):
```python
from src.services.circuit_breaker import with_circuit_breaker, OPENAI_BREAKER

@with_circuit_breaker(OPENAI_BREAKER, "OpenAI temporarily unavailable")
def call_custom_api():
    # Your API call
    return response
```

📝 **UPDATE NEEDED**: Add examples of how to debug circuit breaker states and reset them manually.

---

## Project Management Commands

### Python API

**Creating Projects**:
```python
from project_manager import get_project_manager

pm = get_project_manager()
pm.create_project("fall_prevention", add_default_milestones=True)
# ✅ Created project: fall_prevention
# ✨ This is now your active project
```

**Switching Projects**:
```python
pm.set_active_project("fall_prevention")
active = pm.get_active_project()  # Returns "fall_prevention"
```

**Accessing Project Database**:
```python
db_path = pm.get_project_db_path()  # Uses active project
conn = pm.get_project_connection()  # Returns sqlite3.Connection

# Always close connections when done
conn.close()
```

### CLI Commands

Available in `run_nursing_project.py` interactive menu:
- `new <project_name>` - Create new project
- `list` - List all projects with statistics
- `switch <project_name>` - Switch to project
- `archive <project_name>` - Archive project (moves to `data/archives/`)
- `agents` - Launch agent menu (requires active project)
- `exit` - Exit program

**Example Session**:
```bash
$ ./start_nursing_project.sh

> new fall_prevention
✅ Created project: fall_prevention

> new cauti_reduction
✅ Created project: cauti_reduction

> list
Projects:
  - fall_prevention (active)
  - cauti_reduction

> switch fall_prevention
✅ Switched to: fall_prevention

> agents
[Agent selection menu appears]

> exit
Goodbye!
```

---

## Git Workflow

**Branch Strategy**:
- **Working Branch**: `main-nurseRN` - Active development branch
- **PR Target**: `claude/refactor-week1-019tf9ApiyUDheGnY3Z396k5` - Main integration branch
- **Feature Branches**: Follow pattern `feature/description` or `test/description`

**Note**: This project uses non-standard branch naming to track refactoring progress. When creating pull requests, always target `claude/refactor-week1-019tf9ApiyUDheGnY3Z396k5`.

**Current Git Status** (as of 2025-11-26):
```
Modified: AGENT_STATUS.md, README.md, requirements.txt
Staged: run_nursing_project.py
Untracked: .claude/ directory, verify_setup.py
Recent commits:
  - 97464623 docs: Add Day 1 delivery report
  - ed573e10 feat: Day 1 - Project-centric database architecture foundation
  - 2e413afd test: Phase 2 Enhanced - comprehensive test expansion (94% coverage)
```

⚠️ **IMPROVEMENT NEEDED**: Normalize branch naming for easier contribution and maintenance.

---

## File Organization

```
nurseRN/                                  (Root: 3,699 total lines of Python)
├── Agents Module (7 files organized in agents/)
│   └── agents/
│       ├── __init__.py                   Package definition
│       ├── base_agent.py                 172 lines - Abstract base class
│       ├── nursing_research_agent.py     219 lines - PICOT & standards
│       ├── medical_research_agent.py     208 lines - PubMed searches
│       ├── academic_research_agent.py    188 lines - ArXiv searches
│       ├── research_writing_agent.py     219 lines - Literature synthesis
│       ├── nursing_project_timeline_agent.py  156 lines - Milestone tracking
│       └── data_analysis_agent.py        253 lines - Statistical analysis
│
├── Core Infrastructure
│   ├── agent_config.py                   108 lines - Centralized config
│   ├── project_manager.py                698 lines - Project management (largest file)
│   ├── run_nursing_project.py            323 lines - Main entry point
│   └── start_nursing_project.sh          Shell script for quick start
│
├── Services (Resilience layer)
│   └── src/services/
│       ├── api_tools.py                  398 lines - Safe tool creation
│       └── circuit_breaker.py            322 lines - Circuit breaker pattern
│
├── Data Directories
│   ├── data/
│   │   ├── .active_project              File-based state tracking (7 bytes)
│   │   ├── projects/{name}/             Project databases
│   │   │   ├── project.db              SQLite with 7 tables
│   │   │   └── documents/              Uploaded files
│   │   └── archives/                    Archived projects
│   └── tmp/                             Agent session databases (6 files)
│
├── Vendored Framework
│   └── libs/agno/                       Agno framework (not pip installed)
│
├── Testing
│   └── tests/
│       ├── unit/                        8 test files
│       ├── integration/                 System integration tests
│       └── conftest.py                  pytest configuration
│
├── Claude Code Integration
│   └── .claude/
│       ├── CLAUDE.md                    This file
│       └── skills/
│           └── legacy-code-reviewer/    Code analysis skill
│
├── Documentation (Active)
│   ├── README.md                        Main documentation (400 lines)
│   ├── AGENT_STATUS.md                  Agent capabilities (354 lines)
│   ├── NURSING_PROJECT_GUIDE.md        Usage guide
│   ├── NEW_AGENTS_GUIDE.md             PubMed/ArXiv guide
│   ├── SETUP.md                        Setup instructions
│   ├── GITHUB_SETUP_GUIDE.md           GitHub setup guide
│   ├── PORTABLE.md                     Portability guide
│   ├── CONTRIBUTING.md                 Contribution guidelines
│   └── CODE_OF_CONDUCT.md              Community standards
│
├── Archived Documentation
│   └── archived/
│       ├── historical-reports/         Historical reports & assessments
│       │   ├── DAY1_DELIVERY_REPORT.md
│       │   ├── WEEK1_COMPLETION_REPORT.md
│       │   ├── WEEK1_ASSESSMENT.md
│       │   ├── WEEK1_PROGRESS.md
│       │   ├── QA_REPORT.md
│       │   ├── INTEGRATION_TEST_SUMMARY.md
│       │   ├── INTEGRATION_TEST_RESULTS.txt
│       │   └── BRANCH_COMPARISON.md
│       └── [legacy agent files and test code]
│
├── Configuration
│   ├── .env                            API keys (gitignored)
│   ├── .env.example                    Template
│   ├── requirements.txt                43 dependencies
│   ├── pytest.ini                      Test configuration
│   ├── .cursorrules                    AI coding rules (critical!)
│   └── .gitignore                      Security protection
│
└── Utilities
    ├── verify_setup.py                 190 lines - Setup verification
    ├── test_resilience.py              259 lines - Resilience testing
    └── test_schema_spike.py            706 lines - Database spike test
```

---

## Common Development Tasks

### Debugging Agent Behavior

1. **Enable detailed logging**:
   ```bash
   export AGENT_LOG_LEVEL=DEBUG
   ```

2. **Run agent standalone**:
   ```bash
   python3 -m agents.nursing_research_agent
   ```

3. **Check session database**:
   ```bash
   sqlite3 tmp/nursing_research_agent.db
   .tables
   SELECT * FROM conversations;
   ```

4. **Check circuit breaker status**:
   ```python
   from src.services.circuit_breaker import print_breaker_status, get_all_breaker_status

   # Print status to console
   print_breaker_status()

   # Get programmatic status
   status = get_all_breaker_status()
   print(status['exa'])  # {'available': True, 'state': 'closed', ...}
   ```

5. **Test API tools independently**:
   ```bash
   python3 src/services/api_tools.py
   # Shows which tools can be created based on available API keys
   ```

6. **View HTTP cache**:
   ```bash
   sqlite3 api_cache.sqlite
   .tables
   SELECT * FROM cache LIMIT 5;
   ```

---

### Working with Project Databases

```python
from project_manager import get_project_manager

pm = get_project_manager()
conn = pm.get_project_connection("fall_prevention")

# Query literature findings
cursor = conn.execute("""
    SELECT title, authors, agent_source
    FROM literature_findings
    WHERE selected_for_project = 1
""")

for row in cursor.fetchall():
    print(dict(row))

# Always close when done
conn.close()
```

---

### Modifying Database Schema

**IMPORTANT**: Schema is defined in `project_manager.py` constant `SCHEMA_DDL`. When updating:

1. Update `SCHEMA_DDL` string
2. Increment version in `schema_version` table insert
3. Consider migration path for existing projects
4. Test with fresh project creation
5. Update this documentation

📝 **UPDATE NEEDED**: Create schema migration guide for upgrading existing project databases.

---

### Adding New Tools to Agents

**Using Safe Tool Creation** (Week 1 Pattern):
```python
# In agent's __init__ or _create_tools method
from src.services.api_tools import create_safe_tool_instance

tools = []
exa_tool = create_safe_tool_instance(
    tool_class_name="ExaTools",
    api_key_env_var="EXA_API_KEY",
    import_path="agno.tools.exa",
    logger=self.logger
)
if exa_tool:
    tools.append(exa_tool)

super().__init__(
    agent_name="My Agent",
    agent_key="my_agent",
    tools=tools
)
```

---

## Security & Best Practices

### Threat Model

**Protected Against**:
- ✅ **API Key Exposure**: Keys in `.env` (gitignored), never in code
- ✅ **Runaway Costs**: Circuit breakers stop repeated failed API calls
- ✅ **SQL Injection**: Parameterized queries with sqlite3 `execute(?, values)`
- ✅ **Cascade Failures**: Circuit breakers isolate failing services
- ✅ **Data Loss**: SQLite WAL mode for crash recovery

**NOT Protected Against** (user responsibility):
- ❌ Malicious prompt injection (OpenAI handles this at model level)
- ❌ File system access control (relies on OS permissions)
- ❌ Network sniffing (HTTPS is provider responsibility)
- ❌ API key theft from memory (Python runtime limitation)

**API Key Management**:
- All keys in `.env` file (never committed)
- `.env` is in `.gitignore`
- No hardcoded credentials anywhere
- Use `os.getenv()` with defaults
- Rotate keys quarterly

**Circuit Breakers**:
- All external API calls protected
- Prevents cascade failures
- Automatic recovery after cooldown
- Manual reset available for testing

**Database Safety**:
- Foreign keys enabled: `PRAGMA foreign_keys = ON`
- WAL mode for concurrency: `PRAGMA journal_mode = WAL`
- All dates use ISO 8601 format
- Parameterized queries prevent SQL injection

**Cost Optimization**:
- GPT-4o-mini for Timeline Agent (10x cheaper than GPT-4o)
- HTTP response caching (24hr TTL, SQLite backend)
- Retry logic with exponential backoff
- Circuit breakers prevent runaway costs

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'agno'"
**Cause**: PYTHONPATH not set
**Fix**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/libs/agno"
```
Or use the start script: `./start_nursing_project.sh`

---

### "Circuit breaker OPEN" errors
**Cause**: Too many API failures (5 in a row)
**Fix**: Wait 60 seconds for automatic reset, check API key validity, check network connection
```python
# Manual reset for testing
from src.services.circuit_breaker import reset_breaker, EXA_BREAKER
reset_breaker(EXA_BREAKER)
```

---

### "No active project" error
**Cause**: Haven't created or selected a project
**Fix**:
```bash
# In run_nursing_project.py CLI:
new my_project
# or
switch existing_project
```

---

### SQLite "database locked" error
**Cause**: Multiple processes accessing same database
**Fix**: Close other connections, WAL mode should prevent this
```python
conn.close()  # Always close connections when done
```

---

### Import errors when running tests
**Cause**: `conftest.py` PYTHONPATH setup not working
**Fix**: Run pytest from project root directory

📝 **UPDATE NEEDED**: Add more common error scenarios and solutions based on actual usage.

---

## Performance Tuning

### Cost Optimization

1. **Use GPT-4o-mini** for simple agents:
   ```bash
   export AGENT_PROJECT_TIMELINE_MODEL=gpt-4o-mini
   ```

2. **Reduce History Context**:
   ```python
   Agent(..., num_history_runs=1)  # Default is 3
   ```

3. **Disable Streaming** for batch processing:
   ```python
   agent.run(query)  # No stream=True
   ```

### Speed Optimization

1. **Enable HTTP Caching** (enabled by default):
   - Saves ~2-5s on repeated queries
   - Check cache: `ls -lh api_cache.sqlite`

2. **Reuse Agent Instances** (critical!):
   ```python
   # SLOW - Creates new agent each time
   for query in queries:
       agent = Agent(...)
       agent.run(query)

   # FAST - Reuse agent (10x faster!)
   agent = Agent(...)
   for query in queries:
       agent.run(query)
   ```

3. **Reduce Model Size**:
   - GPT-4o-mini is ~10x faster than GPT-4o
   - Use for simple, non-critical tasks

⚠️ **IMPROVEMENT NEEDED**: Add benchmarks and actual performance measurements.

---

## What's New

### 2025-11-28 - Schema Validation Test Expansion
- ✅ **Comprehensive Schema Validation Tests** - Added 6 new test classes for Data Analysis Agent
  - Added `TestStructuredOutputValidation` class with 6 tests validating Pydantic schemas
  - Test Literal type constraints (`task`, `language`, `tails`, `long_vs_wide`)
  - Test Field validators (`confidence` Field(ge=0.0, le=1.0))
  - Test nested model validation (EffectSize, MethodInfo, Parameters, etc.)
  - Test boundary values and required field enforcement
  - **Coverage**: 89% (94 statements, 10 missed) for Data Analysis Agent
  - **Performance**: 30 tests passing in 0.13s (100% pass rate)
  - **File**: `tests/unit/test_data_analysis_agent.py` (+284 lines)
- ✅ **Documentation Updates** - Added schema validation test pattern to CLAUDE.md
- ✅ **Cleanup** - Removed outdated QEF framework, old test reports, and implementation roadmap (635 lines removed)

### Week 1 Day 3 (2025-11-27) - Agent 5 Database Integration
- ✅ **Agent 5 Database Integration Complete** - Timeline agent now queries database instead of hardcoded dates
  - Created `src/tools/milestone_tools.py` (327 lines) - MilestoneTools class with 5 database query methods
  - Updated `src/services/api_tools.py` - Added `create_milestone_tools_safe()` function
  - Refactored `agents/nursing_project_timeline_agent.py` - Replaced 74 lines of hardcoded dates with database-driven instructions
  - Agent now queries milestones table for: get_all_milestones, get_next_milestone, get_milestones_by_date_range, update_milestone_status, add_milestone
  - Added module-level wrappers (`logger`, `show_usage_examples()`) for backward compatibility
- ✅ **Comprehensive Test Coverage** - 22 new tests added
  - Created `tests/unit/test_milestone_tools.py` (299 lines) - 11 tests for MilestoneTools
  - Updated `tests/unit/test_project_timeline_agent.py` - 11 tests updated/passing (100% pass rate)
  - All tests validate database-driven behavior instead of hardcoded dates
- ✅ **Documentation Updates** - CLAUDE.md, AGENT_STATUS.md updated to reflect database integration

### Week 1 Day 2 (2025-11-26) - Major Reorganization
- ✅ **Agent Folder Reorganization** - All 7 agent files moved to `agents/` module
  - Created `agents/` package with `__init__.py`
  - Moved all `*_agent.py` files including `base_agent.py`
  - Root directory cleaned: 13 → 6 Python files (54% reduction)
  - Updated all imports across 8 files (main + tests + utilities)
  - Updated patch decorators in test files for new module structure
  - Verified test suite still passes (26 tests)
- ✅ **Documentation Synchronization** - All docs updated to reflect new structure
  - README.md: Updated file structure diagram + examples
  - AGENT_STATUS.md: Updated directory tree + commands
  - NURSING_PROJECT_GUIDE.md: Updated agent file paths
  - SETUP.md: Updated commands + structure diagram
  - CLAUDE.md: Updated all references, examples, and file organization
- ✅ **Archive Cleanup** - Historical reports organized
  - Created `archived/historical-reports/` directory
  - Moved 8 files: Week 1 reports, QA report, Day 1 delivery, test results
  - Total archived: 88KB of historical documentation
- ✅ Quality Engineering Framework (QEF) added - 8 specialized review agents
- ✅ QEF-1 through QEF-8: Requirements, Prompts, Testing, Workflow, Integration, Resilience, Code Quality, Architecture
- ✅ Cross-cutting code quality standards with complexity metrics
- ✅ Architectural decision framework with trade-off analysis
- ✅ Agent-driven analysis workflow for systematic reviews
- ✅ **Comprehensive Agent Testing System executed - ALL 6 AGENTS PASSED**
- ✅ Agent Testing Report: 100% pass rate, 98.7% quality score
- ✅ Live API validation completed with real OpenAI queries
- ✅ **Nursing Research Agent multi-tool update:**
  - Added PubMed (PRIMARY), SerpAPI, ArXiv, Exa tools
  - ArXiv & Exa RESTRICTED (not for healthcare research)
  - Tool priority: PubMed > SerpAPI > ArXiv > Exa
  - Installed: exa_py, arxiv, pypdf, google-search-results
- ✅ PubMed tool verified returning real results (PMID 41176611)
- ✅ Deep code scan completed - error handling, exports, documentation updated

### Week 1 Day 1 (2025-11-26)
- ✅ Claude Code Skills integration (legacy-code-reviewer)
- ✅ Testing framework: 94% coverage achieved
- ✅ Integration test suite completed
- ✅ QA report and assessment documentation
- ✅ Updated CLAUDE.md with current state analysis

### Week 1 Refactoring (2025-11-22)
- ✅ Circuit breaker protection for all APIs
- ✅ HTTP response caching (24hr TTL)
- ✅ Safe tool creation patterns
- ✅ Enhanced error handling

### Phase 2 Complete (2025-11-23)
- ✅ BaseAgent inheritance pattern
- ✅ Project-centric database architecture
- ✅ Centralized configuration
- ✅ Enhanced PubMed metadata support

---

## FAQ

**Q: Why do I need OPENAI_API_KEY even for PubMed searches?**
A: The AI agent needs OpenAI to understand your query and synthesize results, even though PubMed API itself is free.

**Q: Can I use this without any API keys?**
A: No. OPENAI_API_KEY is required for all agents. Other keys (Exa, SerpAPI) are optional.

**Q: How much does this cost to run?**
A: See "Cost Optimization" section. Typical usage: $10-20/month for moderate use.

**Q: Can I run multiple projects simultaneously?**
A: Yes, but only one is "active" at a time in the CLI. You can programmatically access any project database.

**Q: Where is the HTTP cache stored?**
A: `api_cache.sqlite` in the project root directory. It expires automatically after 24 hours.

**Q: How do I reset a circuit breaker?**
A: Wait 60 seconds for automatic reset, or manually: `reset_breaker(BREAKER_NAME)`

**Q: What happens to archived projects?**
A: They're moved to `data/archives/{project_name}_archived_{timestamp}/` and can be restored by moving back.

📝 **UPDATE NEEDED**: Add more FAQs based on actual user questions.

---

## Version Information

- **Version**: 1.0.0 (Week 1 Day 1 Complete)
- **Python**: 3.8+ required (tested with 3.13.0)
- **Agno Framework**: Vendored in `libs/agno/` (as of 2025-11-23)
- **OpenAI Models**: GPT-4o (primary), GPT-4o-mini (timeline)
- **Architecture Phase**: Week 1 Day 1 Complete (2025-11-26)
- **Test Coverage**: 94% (Phase 2 Enhanced)
- **Total Codebase**: 3,699 lines of Python

⚠️ **IMPROVEMENT NEEDED**: Create `agent_config.__version__` as single source of truth for version info.

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for full guidelines (if exists).

**Quick Checklist**:
- [ ] Run `pytest --cov=.` (maintain >90% coverage)
- [ ] Update CLAUDE.md if adding new features
- [ ] Add docstrings to all new functions
- [ ] Follow agent reuse patterns (never create in loops)
- [ ] Test with minimal API keys (OPENAI_API_KEY only)
- [ ] Update version info
- [ ] Follow `.cursorrules` execution rules

**PR Targeting**:
Always create PRs against `claude/refactor-week1-019tf9ApiyUDheGnY3Z396k5`, not `main`.

📝 **UPDATE NEEDED**: Create CONTRIBUTING.md if it doesn't exist.

---


**End of CLAUDE.md** - Last updated: 2025-11-28
