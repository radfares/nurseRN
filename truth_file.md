# TRUTH FILE - Complete Project Breakdown
**Generated**: 2025-12-08
**Total Python Lines**: 12,921
**Purpose**: Document every folder and file, what it does, and if it's being used

---

## ROOT FILES

| File | Lines | Purpose | Used? |
|------|-------|---------|-------|
| `run_nursing_project.py` | 643 | **Main entry point** - CLI interface, agent menu, project management commands | YES - Core |
| `project_manager.py` | 727 | **Project database management** - Creates/manages per-project SQLite DBs, schema DDL, CRUD operations | YES - Core |
| `agent_config.py` | 110 | **Centralized configuration** - Database paths, model IDs, environment variable handling | YES - Core |
| `start_nursing_project.sh` | ~20 | **Startup script** - Sets PYTHONPATH, activates venv, launches CLI | YES - Core |
| `data_template.xlsx` | N/A | **Excel template** - Data collection template for nursing projects | UNKNOWN - Needs verification |
| `diagnostic_tool_analysis.py` | ~100 | **Diagnostic utility** - Analyzes tool availability and configuration | NO - Utility only |
| `setup_gates.py` | ~50 | **Test gate setup** - Configures validation gates for testing | NO - Dev only |

---

## AGENTS FOLDER (`agents/`)

**Purpose**: Contains all 7 AI agents that do the actual work

| File | Lines | Purpose | Used? |
|------|-------|---------|-------|
| `__init__.py` | 10 | Package exports | YES |
| `base_agent.py` | 172 | **Abstract base class** - Logging, error handling, agent creation framework | YES - All agents inherit |
| `nursing_research_agent.py` | 335 | **Agent 1** - PICOT development, healthcare standards, uses PubMed/SerpAPI | YES |
| `medical_research_agent.py` | 208 | **Agent 2** - PubMed peer-reviewed clinical studies | YES |
| `academic_research_agent.py` | 188 | **Agent 3** - ArXiv statistical/theoretical research | YES |
| `research_writing_agent.py` | 219 | **Agent 4** - Literature synthesis, PICOT writing | YES |
| `nursing_project_timeline_agent.py` | 218 | **Agent 5** - Milestone tracking, timeline guidance | YES |
| `data_analysis_agent.py` | 253 | **Agent 6** - Statistical analysis, sample size calculations | YES |
| `citation_validation_agent.py` | ~200 | **Agent 7** - Citation verification, retraction checking | YES |

---

## SRC FOLDER (`src/`)

### `src/orchestration/` - Multi-Agent Coordination

| File | Lines | Purpose | Used? |
|------|-------|---------|-------|
| `__init__.py` | 10 | Package exports | YES |
| `orchestrator.py` | ~250 | **Main orchestrator** - Routes queries to agents, manages workflow execution | YES - Core |
| `query_router.py` | ~200 | **Query routing** - Regex-based routing to select appropriate agent | YES - Core |
| `context_manager.py` | ~200 | **Context management** - Tracks conversation context within session | YES |
| `workflow_context.py` | ~180 | **Workflow state** - Manages state during multi-step workflows | YES |
| `workflow_progress.py` | ~270 | **Progress tracking** - Tracks and displays workflow progress | YES |
| `api_validators.py` | ~100 | **API validation** - Validates API responses and inputs | YES |
| `log_sanitizer.py` | ~170 | **Log sanitization** - Removes sensitive data from logs | YES |
| `safe_accessors.py` | ~120 | **Safe data access** - Prevents null/undefined errors | YES |

### `src/services/` - Infrastructure Services

| File | Lines | Purpose | Used? |
|------|-------|---------|-------|
| `__init__.py` | 10 | Package exports | YES |
| `api_tools.py` | 398 | **Safe tool creation** - Creates API tools with fallbacks, circuit breaker wrapping | YES - Core |
| `circuit_breaker.py` | 322 | **Circuit breaker** - Protects against API failures, 5-failure threshold | YES - Core |
| `citation_apis.py` | ~150 | **Citation APIs** - Interfaces with citation verification services | YES |
| `agent_audit_logger.py` | ~100 | **Audit logging** - Logs agent actions for compliance | YES |
| `safety_tools.py` | ~80 | **Safety tools** - Input sanitization, output validation | YES |

### `src/tools/` - Agent Tools

| File | Lines | Purpose | Used? |
|------|-------|---------|-------|
| `__init__.py` | 10 | Package exports | YES |
| `milestone_tools.py` | 326 | **Milestone queries** - Database queries for project milestones | YES - Agent 5 |
| `literature_tools.py` | 480 | **Literature management** - Store/retrieve literature findings | YES |
| `writing_tools.py` | 287 | **Writing assistance** - Draft management, formatting | YES - Agent 4 |
| `statistics_tools.py` | 325 | **Statistical calculations** - Sample size, power analysis | YES - Agent 6 |
| `citation_validation_tools.py` | ~250 | **Citation tools** - Validate citations, check retractions | YES - Agent 7 |
| `validation_tools.py` | 400 | **Validation tools** - PICOT validation, clinical checks | YES |

### `src/validation/` - Data Validation

| File | Lines | Purpose | Used? |
|------|-------|---------|-------|
| `__init__.py` | 22 | Package exports | YES |
| `picot_scorer.py` | 196 | **PICOT scoring** - Grades PICOT questions for quality | YES |
| `clinical_checks.py` | 82 | **Clinical validation** - Validates clinical parameters | YES |
| `sample_size_validator.py` | 78 | **Sample size validation** - Validates statistical parameters | YES |
| `timeline_validator.py` | 98 | **Timeline validation** - Validates project timelines | YES |
| `budget_validator.py` | 99 | **Budget validation** - Validates budget constraints | YES |

### `src/workflows/` - Multi-Step Workflows

| File | Lines | Purpose | Used? |
|------|-------|---------|-------|
| `base.py` | 139 | **Base workflow class** - Abstract workflow implementation | YES |
| `research_workflow.py` | 133 | **Research workflow** - Multi-agent research execution | YES |
| `parallel_search.py` | 88 | **Parallel search** - Runs multiple agents in parallel | YES |
| `timeline_planner.py` | 102 | **Timeline planning** - Creates project timelines | YES |
| `validated_research_workflow.py` | 217 | **Validated research** - Research with validation gates | YES |

### `src/adapters/` - External Service Adapters

| File | Lines | Purpose | Used? |
|------|-------|---------|-------|
| `__init__.py` | 10 | Package exports | YES |
| `base.py` | ~50 | **Base adapter** - Abstract adapter interface | YES |
| `pubmed_adapter.py` | ~80 | **PubMed adapter** - Wraps PubmedTools from agno | YES |

### `src/models/` - Data Models

| File | Lines | Purpose | Used? |
|------|-------|---------|-------|
| `__init__.py` | 10 | Package exports | YES |
| `agent_handoff.py` | ~100 | **Handoff models** - Data structures for agent handoffs | YES |
| `evidence_types.py` | ~80 | **Evidence types** - Enums and types for evidence classification | YES |

---

## TESTS FOLDER (`tests/`)

| Folder/File | Purpose | Count |
|-------------|---------|-------|
| `tests/unit/` | Unit tests for individual components | 25 files |
| `tests/integration/` | Integration tests for system components | 5 files |
| `tests/gates/` | Validation gate tests | 2 files |
| `conftest.py` | Pytest configuration and fixtures | 1 file |

---

## DATA FOLDER (`data/`)

| Path | Purpose |
|------|---------|
| `data/projects/{name}/` | Per-project directories |
| `data/projects/{name}/project.db` | SQLite database (7 tables) |
| `data/projects/{name}/documents/` | Uploaded project documents |
| `data/.active_project` | Tracks currently active project (7 bytes) |

**Database Tables** (in project.db):
1. `picot_versions` - PICOT question versions and approval status
2. `literature_findings` - Research articles from all agents
3. `analysis_plans` - Statistical analysis plans
4. `milestones` - Project timeline milestones
5. `writing_drafts` - Document drafts
6. `conversations` - Chat history per agent
7. `documents` - Uploaded file metadata

---

## SCRIPTS FOLDER (`scripts/`)

| File | Purpose | Used? |
|------|---------|-------|
| `_utils.sh` | Shared shell utilities | YES |
| `validate.sh` | Run validation checks (mypy removed) | YES |
| `test.sh` | Run pytest | YES |
| `format.sh` | Code formatting | Dev only |
| `dev_setup.sh` | Development setup | Dev only |
| `cookbook_setup.sh` | Cookbook setup | NO |
| `perf_setup.sh` | Performance setup | NO |
| `run_model_tests.sh` | Model testing | Dev only |
| `run_agent6_query.py` | Test Agent 6 | Dev only |
| `run_medical_agent_safe.py` | Test Medical Agent | Dev only |
| `smoke_test_research_tools.py` | Smoke test tools | Dev only |
| `template_to_excel.py` | Excel template generation | UNKNOWN |

---

## .CLAUDE FOLDER (`.claude/`)

| File | Purpose | Keep? |
|------|---------|-------|
| `CLAUDE.md` | Instructions for this project | YES - Core |
| `agent_mistral.py` | Mistral agent configuration | UNKNOWN |
| `settings.local.json` | Local Claude settings | YES |
| `skills/` | Claude skills (legacy-code-reviewer) | YES |
| `archive/` | Old planning documents | NO - Can delete |

---

## EXTERNAL DEPENDENCIES

| Folder | Purpose | Notes |
|--------|---------|-------|
| `libs/agno/` | Vendored Agno framework | Core dependency, pip installed |
| `libs/agno_infra/` | Agno infrastructure | May not be used |
| `.venv/` | Python virtual environment | Local only |

---

## CRITICAL PATH (Files that matter most)

```
run_nursing_project.py      ← Entry point
       │
       ├── project_manager.py    ← Database management
       ├── agent_config.py       ← Configuration
       │
       └── agents/               ← THE AGENTS
           ├── nursing_research_agent.py
           ├── medical_research_agent.py
           ├── academic_research_agent.py
           ├── research_writing_agent.py
           ├── nursing_project_timeline_agent.py
           ├── data_analysis_agent.py
           └── citation_validation_agent.py
                    │
                    └── src/services/api_tools.py  ← Tool creation
                              │
                              └── libs/agno/       ← Framework
```

---

## FILES THAT CAN BE DELETED

1. `.claude/archive/` - Old planning docs (18 files)
2. `tests/unit/backup/` - Backup test files (3 files)
3. `.mypy_cache/` - mypy removed, cache useless
4. `diagnostic_tool_analysis.py` - One-time diagnostic
5. `setup_gates.py` - Dev setup only

---

## UNKNOWN STATUS (Need Verification)

1. `data_template.xlsx` - Is this used by any agent?
2. `.claude/agent_mistral.py` - Is Mistral being used?
3. `scripts/template_to_excel.py` - Is this used?
4. `libs/agno_infra/` - Is this used?

---

**END OF TRUTH FILE**
