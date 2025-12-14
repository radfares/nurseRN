
  Plan Status: Well-structured but requires refinements for production safety

  Major Findings:
  1. ✅ Addresses real architectural debt (dual-database problem confirmed)
  2. ⚠️ Missing explicit rollback mechanisms
  3. ⚠️ No cost ceiling for E2E tests (API bills risk)
  4. ⚠️ Phase gates need binary GO/NO-GO criteria
  5. ❌ No branch strategy defined

  ---
  ELEMENTAL DECOMPOSITION

  Phase 1: Foundation & Cleanup (18 Atomic Tasks)

  | ID    | Task
       | File(s)                            | Risk   | Reversibility  |
  |-------|-----------------------------------------------------------------------
  -----|------------------------------------|--------|----------------|
  | 1.1.1 | Create workflow_runs table DDL
       | project_manager.py                 | Low    | DROP TABLE     |
  | 1.1.2 | Create workflow_steps table DDL
       | project_manager.py                 | Low    | DROP TABLE     |
  | 1.1.3 | Create workflow_outputs table DDL
       | project_manager.py                 | Low    | DROP TABLE     |
  | 1.1.4 | Increment schema_version to 3
       | project_manager.py                 | Low    | Decrement      |
  | 1.1.5 | Write migration script
       | scripts/migrate_db.py              | Medium | Backup restore |
  | 1.1.6 | Migrate existing 6 project.db files
       | Each in data/projects/             | HIGH   | Backup restore |
  | 1.1.7 | Remove ad-hoc workflow_outputs from
  validated_research_workflow.py:140-152 | validated_research_workflow.py     |
  Low    | Git revert     |
  | 1.2.1 | Add _archived_* to .gitignore
       | .gitignore                         | None   | Remove line    |
  | 1.2.2 | Remove or archive context_manager.py
       | src/orchestration/                 | Medium | Git restore    |
  | 1.2.3 | Create src/workflows/registry.py
       | New file                           | Low    | Delete file    |
  | 1.2.4 | Update workflow imports to use registry
       | src/workflows/*.py                 | Medium | Git revert     |
  | 1.3.1 | Create src/orchestration/workflow_runner.py stub
       | New file                           | Low    | Delete file    |
  | 1.3.2 | Unit tests for new schema
       | tests/unit/test_project_manager.py | None   | N/A            |
  | 1.3.3 | Integration tests for migration
       | tests/integration/                 | None   | N/A            |
  | 1.4.1 | Update truth_file.md
       | Root                               | None   | Git revert     |
  | 1.4.2 | Verify foreign key integrity
       | All project.db                     | Low    | Manual fix     |
  | 1.4.3 | Backup all existing databases
       | data/projects/*/project.db         | None   | N/A            |
  | 1.4.4 | Remove workflow_probe.db and probe_test.db
       | Root                               | Low    | Re-create      |

  Phase 2: Reliability & Modularity (14 Atomic Tasks)

  | ID    | Task                                           | File(s)
   | Risk   | Reversibility |
  |-------|------------------------------------------------|----------------------
  -|--------|---------------|
  | 2.1.1 | Implement WorkflowRunner.__init__()            | workflow_runner.py
   | Low    | Git revert    |
  | 2.1.2 | Implement WorkflowRunner.execute()             | workflow_runner.py
   | Medium | Git revert    |
  | 2.1.3 | Implement WorkflowRunner._create_run_record()  | workflow_runner.py
   | Low    | Git revert    |
  | 2.1.4 | Implement WorkflowRunner._log_step_start()     | workflow_runner.py
   | Low    | Git revert    |
  | 2.1.5 | Implement WorkflowRunner._log_step_complete()  | workflow_runner.py
   | Low    | Git revert    |
  | 2.1.6 | Implement WorkflowRunner._save_outputs()       | workflow_runner.py
   | Low    | Git revert    |
  | 2.1.7 | Implement WorkflowRunner.resume()              | workflow_runner.py
   | Medium | Git revert    |
  | 2.1.8 | Implement WorkflowRunner.get_run_history()     | workflow_runner.py
   | Low    | Git revert    |
  | 2.2.1 | Add step callbacks to WorkflowTemplate         | src/workflows/base.py
   | Medium | Git revert    |
  | 2.2.2 | Implement _run_step() with callbacks           | src/workflows/base.py
   | Medium | Git revert    |
  | 2.3.1 | Implement retry logic with exponential backoff | workflow_runner.py
   | Low    | Git revert    |
  | 2.4.1 | Populate WORKFLOW_REGISTRY dict                | registry.py
   | Low    | Git revert    |
  | 2.4.2 | Implement get_workflow()                       | registry.py
   | Low    | Git revert    |
  | 2.4.3 | Implement list_workflows()                     | registry.py
   | Low    | Git revert    |

  Phase 3: Polish & Perfection (12 Atomic Tasks)

  | ID    | Task                                         | File(s)
                    | Risk   | Reversibility |
  |-------|----------------------------------------------|------------------------
  ------------------|--------|---------------|
  | 3.1.1 | Implement run_workflow_mode() menu           | run_nursing_project.py
                    | Low    | Git revert    |
  | 3.1.2 | Implement workflow picker UI                 | run_nursing_project.py
                    | Low    | Git revert    |
  | 3.1.3 | Implement run history display                | run_nursing_project.py
                    | Low    | Git revert    |
  | 3.1.4 | Implement resume failed workflow UI          | run_nursing_project.py
                    | Low    | Git revert    |
  | 3.2.1 | Create E2E test infrastructure               | tests/e2e/conftest.py
                    | Low    | Delete        |
  | 3.2.2 | Implement test_full_workflow_execution       |
  tests/e2e/test_validated_research_e2e.py | COST   | Delete        |
  | 3.2.3 | Implement test_workflow_resume_after_failure |
  tests/e2e/test_validated_research_e2e.py | COST   | Delete        |
  | 3.3.1 | Create docs/WORKFLOW_GUIDE.md                | New file
                    | None   | Delete        |
  | 3.4.1 | Remove context_manager.py                    | src/orchestration/
                    | Medium | Git restore   |
  | 3.4.2 | Remove verify_workflow_e2e.py                | Root
                    | Low    | Git restore   |
  | 3.4.3 | Remove workflow_probe.db                     | Root
                    | Low    | Re-create     |
  | 3.4.4 | Update CLAUDE.md                             | Root
                    | None   | Git revert    |

  ---
  CRITICAL ANALYSIS

  ✅ STRENGTHS

  1. Addresses Real Problem: Dual-database architecture is confirmed problematic
    - workflow_outputs table created ad-hoc in
  validated_research_workflow.py:140-152
    - Some project.db have 9 tables, others have 8 (inconsistent)
  2. Incremental Approach: Three phases allow checkpoint validation
  3. Registry Pattern: Enables plugin-style workflow addition without code changes
  4. Resume Capability: Critical for long-running workflows with API costs

  ⚠️ WEAKNESSES & GAPS

  Gap 1: No Database Backup Strategy

  Risk: Migration corrupts existing databases (6 project databases with real data)
  Mitigation Required:
  # Pre-migration backup (MUST be automated)
  for db in data/projects/*/project.db; do
    cp "$db" "${db}.backup.$(date +%Y%m%d_%H%M%S)"
  done

  Gap 2: No Explicit Rollback Script

  Risk: Failed migration leaves database in inconsistent state
  Mitigation Required:
  # scripts/rollback_migration.py
  def rollback_v3_to_v2(project_name: str):
      conn = get_connection(project_name)
      conn.execute("DROP TABLE IF EXISTS workflow_runs")
      conn.execute("DROP TABLE IF EXISTS workflow_steps")
      conn.execute("DROP TABLE IF EXISTS workflow_outputs")
      conn.execute("UPDATE schema_version SET version = 2 WHERE version = 3")
      conn.commit()

  Gap 3: No Cost Ceiling for E2E Tests

  Risk: E2E tests make real API calls ($$$)
  Mitigation Required:
  # tests/conftest.py
  @pytest.fixture(scope="session", autouse=True)
  def cost_guard():
      """Kill tests if cost threshold exceeded."""
      start_cost = get_openai_usage()
      yield
      end_cost = get_openai_usage()
      if (end_cost - start_cost) > MAX_TEST_BUDGET:
          pytest.exit("COST LIMIT EXCEEDED", returncode=99)

  Gap 4: No Branch Strategy

  Risk: Work collision, untested merges
  Missing:
  - Feature branch naming convention
  - PR requirements
  - Merge criteria

  Gap 5: Incomplete GO/NO-GO Criteria

  Current: "Must pass before Phase X"
  Problem: Doesn't specify what "pass" means quantitatively
  Need: Binary success criteria

  ---
  RISK MATRIX

  | Risk ID | Description                                  | Likelihood | Impact
   | Mitigation                                |
  |---------|----------------------------------------------|------------|---------
  -|-------------------------------------------|
  | R1      | Migration corrupts existing data             | Medium     | Critical
   | Automated backup + rollback script        |
  | R2      | E2E tests exceed API budget                  | High       | High
   | pytest markers + cost ceiling             |
  | R3      | context_manager removal breaks orchestrator  | Medium     | High
   | Deprecation period, not immediate removal |
  | R4      | Workflow resume logic has edge cases         | High       | Medium
   | Exhaustive state machine tests            |
  | R5      | Registry pattern introduces circular imports | Low        | Medium
   | Lazy imports, dependency injection        |
  | R6      | Schema migration misses one project.db       | Medium     | Medium
   | Migration validation script               |

  ---
  EXECUTION GUARDRAILS

  Branch Strategy (MISSING FROM PLAN)

  main (protected)
    └── develop (integration)
         ├── feature/phase1-schema-unification
         ├── feature/phase1-registry
         ├── feature/phase2-workflow-runner
         ├── feature/phase2-error-recovery
         └── feature/phase3-cli-enhancements

  Rules:
  1. All features branch from develop
  2. PR requires: passing CI + 1 review
  3. develop → main only after phase gate passes
  4. Squash merge to main for clean history

  Backup Protocol

  # MANDATORY before any Phase 1 work
  ./scripts/backup_all_dbs.sh

  # Content of backup_all_dbs.sh:
  #!/bin/bash
  BACKUP_DIR="data/backups/$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$BACKUP_DIR"
  cp data/projects/*/project.db "$BACKUP_DIR/"
  cp data/orchestration/workflow_context.db "$BACKUP_DIR/"
  echo "Backed up to $BACKUP_DIR"

  Rollback Protocol

  # If Phase 1 fails:
  ./scripts/rollback_migration.sh <backup_timestamp>

  # If Phase 2 fails:
  git checkout develop -- src/orchestration/workflow_runner.py
  git checkout develop -- src/workflows/base.py

  # If Phase 3 fails:
  git checkout develop -- run_nursing_project.py

  ---
  PYTEST MARKERS (Cost Control)

  # tests/conftest.py

  import pytest
  import os

  def pytest_configure(config):
      config.addinivalue_line("markers", "e2e: End-to-end tests (real API calls)")
      config.addinivalue_line("markers", "slow: Tests taking >30 seconds")
      config.addinivalue_line("markers", "costly: Tests that incur API costs")
      config.addinivalue_line("markers", "unit: Fast unit tests")
      config.addinivalue_line("markers", "integration: Integration tests")

  @pytest.fixture(scope="session")
  def api_budget_guard():
      """Enforce $5 max test budget per session."""
      # Only active when running costly tests
      if "costly" not in pytest.config.option.markexpr:
          yield
          return

      budget_file = "/tmp/test_api_budget.json"
      # Track and enforce budget...
      yield

  # pytest.ini
  [pytest]
  markers =
      e2e: End-to-end tests requiring API keys
      slow: Tests taking more than 30 seconds
      costly: Tests that incur API costs (use sparingly)
      unit: Fast isolated unit tests
      integration: Integration tests with real dependencies

  # Default: skip costly tests
  addopts = -m "not costly and not e2e"

  Usage:
  # Normal development (no API costs)
  pytest

  # CI pipeline (includes integration, skips costly)
  pytest -m "not costly"

  # Explicit E2E run (costs money)
  pytest -m e2e --run-costly

  # Full suite (pre-release only)
  pytest --run-all

  ---
  PHASE GATES (GO/NO-GO)

  Phase 1 Gate

  | Criterion        | Metric
          | Pass              | Fail           |
  |------------------|------------------------------------------------------------
  --------|-------------------|----------------|
  | Schema tests     | pytest tests/unit/test_project_manager.py
          | Exit 0, 100% pass | Any failure    |
  | Import check     | python -c "from src.workflows.registry import get_workflow"
          | Exit 0            | Import error   |
  | Schema exists    | sqlite3 data/projects/testing_1/project.db ".schema
  workflow_runs" | Returns DDL       | Empty or error |
  | All DBs migrated | 6/6 project.db have workflow_runs
          | 100%              | <100%          |
  | Backup exists    | ls data/backups/*/
          | At least 7 files  | Missing        |
  | No regressions   | pytest tests/unit/ tests/integration/ -m "not costly"
          | Exit 0, ≥95% pass | <95% pass      |

  GO Decision: ALL criteria PASS
  NO-GO Action: Rollback via ./scripts/rollback_migration.sh

  Phase 2 Gate

  | Criterion                | Metric
                                                | Pass                   | Fail
           |
  |--------------------------|----------------------------------------------------
  ----------------------------------------------|------------------------|--------
  ---------|
  | Runner tests             | pytest tests/integration/test_workflow_runner.py
                                                | Exit 0, 100% pass      | Any
  failure     |
  | Import check             | python -c "from src.orchestration.workflow_runner
  import WorkflowRunner"                         | Exit 0                 | Import
   error    |
  | Registry has 4 workflows | python -c "from src.workflows.registry import
  list_workflows; assert len(list_workflows()) >= 4" | Exit 0                 |
  AssertionError  |
  | Base class enhanced      | grep "on_step_start" src/workflows/base.py
                                                | Match found            | No
  match        |
  | Manual: Run workflow     | Execute via CLI, check DB
                                                | Row in workflow_runs   | No row
           |
  | Manual: Fail & resume    | Intentionally fail, resume
                                                | Resumes from last step | Fails
  to resume |

  GO Decision: ALL criteria PASS
  NO-GO Action: Git revert Phase 2 commits, fix, re-attempt

  Phase 3 Gate (Release Gate)

  | Criterion       | Metric
            | Pass                  | Fail             |
  |-----------------|-------------------------------------------------------------
  ----------|-----------------------|------------------|
  | Full test suite | pytest --cov=. --cov-fail-under=70
            | Exit 0, ≥70% coverage | <70% or failures |
  | E2E passes      | pytest tests/e2e/ -m e2e (ONE run, manual)
            | Exit 0                | Any failure      |
  | Docs complete   | ls docs/WORKFLOW_GUIDE.md
            | File exists           | Missing          |
  | No orphan files | context_manager.py, verify_workflow_e2e.py,
  workflow_probe.db removed | All removed           | Any present      |
  | CLI smoke test  | Manual: Run workflow → View history → Resume
            | All work              | Any fails        |

  GO Decision: ALL criteria PASS
  NO-GO Action: Do not merge to main, continue development on develop

  ---
  COST CONTROL STRATEGY

  API Cost Estimation

  | Test Type         | API Calls      | Estimated Cost | Frequency        |
  |-------------------|----------------|----------------|------------------|
  | Unit tests        | 0              | $0             | Every commit     |
  | Integration tests | 5-10 mocked    | $0             | Every PR         |
  | E2E (1 workflow)  | ~4 real calls  | ~$0.10-0.50    | Manual only      |
  | Full E2E suite    | ~20 real calls | ~$2-5          | Pre-release only |

  Budget Enforcement

  # tests/e2e/conftest.py

  import pytest
  import os

  MAX_E2E_BUDGET_USD = 5.00
  COST_FILE = "/tmp/e2e_test_costs.json"

  @pytest.fixture(scope="session", autouse=True)
  def enforce_budget():
      """Hard stop if E2E tests exceed $5."""
      if os.environ.get("BYPASS_BUDGET"):
          yield
          return

      # Check accumulated cost
      import json
      try:
          with open(COST_FILE) as f:
              data = json.load(f)
              if data.get("total_usd", 0) >= MAX_E2E_BUDGET_USD:
                  pytest.exit(f"E2E BUDGET EXCEEDED: ${data['total_usd']:.2f}",
  returncode=99)
      except FileNotFoundError:
          pass

      yield

      # Update cost tracking (requires OpenAI usage API or token counting)

  CI Configuration

  # .github/workflows/test.yml
  jobs:
    unit-integration:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - run: pip install -r requirements.txt
        - run: pytest -m "not costly and not e2e" --cov=.

    e2e-manual:
      runs-on: ubuntu-latest
      if: github.event_name == 'workflow_dispatch'  # Manual trigger only
      environment: e2e-tests  # Requires approval
      steps:
        - uses: actions/checkout@v4
        - run: pytest tests/e2e/ -m e2e

  ---
  SCOPE CREEP PREVENTION

  In-Scope (Allowed)

  - Schema changes for workflow persistence
  - WorkflowRunner implementation
  - Registry pattern
  - CLI enhancements for workflow mode
  - E2E tests for workflows

  Out-of-Scope (REJECT if proposed)

  - New agent implementations
  - Changes to agent prompts
  - New database tables beyond the 3 specified
  - UI beyond CLI (web, desktop)
  - Authentication/authorization
  - Cloud deployment
  - Performance optimizations not related to workflows

  Change Request Process

  Any scope change requires:
  1. Document in docs/SCOPE_CHANGE_REQUEST.md
  2. Impact analysis (files affected, risk)
  3. Explicit approval (comment in PR: "APPROVED: ")

  ---
  RECOMMENDED PLAN AMENDMENTS

  Amendment 1: Add Backup Task to Phase 1.1

  + 1.0 Pre-Phase: Create database backups
  +     - Run ./scripts/backup_all_dbs.sh
  +     - Verify 7 files in backup directory
  +     - Store backup timestamp for rollback

  Amendment 2: Add Rollback Script to Phase 1.3 Deliverables

    | Item                | File                     | Action |
  + | Rollback script     | scripts/rollback_migration.py | NEW |

  Amendment 3: Add Cost Markers to Phase 3.2

    @pytest.mark.e2e
    @pytest.mark.slow
  + @pytest.mark.costly  # Requires explicit --run-costly flag
    def test_full_workflow_execution(self, test_project):

  Amendment 4: Add Branch Strategy Section

  + ## Branch Strategy
  + - All work on feature branches from `develop`
  + - PR required for merge to `develop`
  + - Phase gates pass before `develop` → `main`
  + - Tag releases: v1.0.0-phase1, v1.0.0-phase2, v1.0.0

  Amendment 5: Explicit Deprecation for context_manager.py

  - | Remove context_manager.py dependency | src/workflows/*.py | Refactor |
  + | DEPRECATE context_manager.py        | src/workflows/*.py | Add deprecation
  warning, keep file |
  + | Remove context_manager.py           | Phase 3, Task 3.4.1 | Delete after
  2-week deprecation |

  ---
  FINAL VERDICT

  | Aspect                | Score | Notes                                        |
  |-----------------------|-------|----------------------------------------------|
  | Technical Feasibility | 9/10  | Addresses real issues, reasonable scope      |
  | Risk Management       | 5/10  | Missing backups, rollbacks, cost controls    |
  | Completeness          | 7/10  | Good detail but gaps in execution guardrails |
  | Phase Gates           | 6/10  | Present but need binary criteria             |
  | Cost Control          | 3/10  | E2E tests are unbounded cost risk            |

  Recommendation: APPROVE WITH AMENDMENTS

  The plan is fundamentally sound but requires the 5 amendments above before
  execution begins. The most critical gaps are:
  1. Database backup/rollback (data loss risk)
  2. E2E cost ceiling (budget overrun risk)
  3. Branch strategy (coordination risk)

  Would you like me to create the amended plan as a formal document, or implement
  the backup/rollback scripts first?