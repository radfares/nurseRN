# Repository Guidelines

## Repository & Branch Information
- **Main branch**: `main` (active development and production)
- **Local branches**: 3 total (main, claude/refactor-week1, show-current)
- **Remote branches**: 6 total on origin
- **Last updated**: 2025-11-29
- **Latest commit**: 9c4f6440 - Excel template generator and implementation updates

## Project Structure & Module Organization
- `agents/` — agent entry points and logic.
- `src/services/`, `src/tools/` — shared utilities (API tools, circuit breakers).
- `libs/agno/`, `libs/agno_infra/` — vendored frameworks; use provided scripts for formatting/validation.
- `tests/` — top‑level project tests; library tests live under `libs/**/tests/`.
- `scripts/` — dev helpers (`dev_setup.sh`, `format.sh`, `validate.sh`, `test.sh`).
- `data/projects/`, `tmp/` — runtime databases and session files.

## Build, Test, and Development Commands
- Setup env (uv-based): `./scripts/dev_setup.sh` then `source .venv/bin/activate`.
- Format: `./scripts/format.sh` (runs Ruff format + import fixes across libs).
- Validate: `./scripts/validate.sh` (Ruff checks + mypy for libs).
- Test (full, with coverage): `./scripts/test.sh` (combines reports from libs).
- Test project-only: `pytest -q tests`.
- Run app: `./start_nursing_project.sh` or `python3 run_nursing_project.py` (ensure `PYTHONPATH` includes `libs/agno`).

## Coding Style & Naming Conventions
- Python, 4‑space indent, line length 120 (Ruff config).
- Use type hints; prefer small, composable functions.
- Naming: modules/functions `snake_case`, classes `PascalCase`, constants `UPPER_SNAKE_CASE`.
- Keep agents one file per agent under `agents/`; shared code in `src/`.

## Testing Guidelines
- Framework: `pytest` with markers (`unit`, `integration`, `slow`, `requires_api`).
- File/class/function patterns: `tests/test_*.py`, classes `Test*`, functions `test_*`.
- Quick runs: `pytest -m "not slow"`.
- Coverage is reported via `./scripts/test.sh`; add tests for new code paths.

## Commit & Pull Request Guidelines
- PR titles: `[feat]`, `[fix]`, `[docs]`, `[test]`, `[refactor]`, `[build]`, `[ci]`, `[chore]`, `[perf]`, `[style]`, `[revert]` + short subject (e.g., `[feat] Add project switch menu`).
- Link issues: `fixes #123` / `closes #123`.
- PRs should include: clear description, test coverage, and screenshots/CLI output for user‑visible changes. Ensure formatting/validation/tests pass.

## Security & Configuration Tips
- Store secrets in `.env` (not committed). Required: `OPENAI_API_KEY`. Optional: `EXA_API_KEY`, `SERP_API_KEY`, `PUBMED_EMAIL`.
- Verify environment: `python3 verify_setup.py`.

## Agent‑Specific Notes
- Adding an agent: create `agents/my_agent.py`, register in `run_nursing_project.py`, and update paths/config in `agent_config.py`. Reuse utilities from `src/services/`.

## Recent Updates (Nov 2025)
- **Excel Template Generator**: New script `scripts/template_to_excel.py` for generating data templates
- **Circuit Breaker Enhancements**: Updated `src/services/circuit_breaker.py` with improved error handling
- **Implementation Plans**: Added `.claude/NEW_SOURCES_IMPLEMENTATION_PLAN.md` for source integration
- **Data Analysis Agent**: Enhanced query capabilities and schema validation
- **Agent6 Query Scripts**: Multiple test scripts for validating agent6 queries
- **CR3 Implementation**: Completed milestone tracking tools and API integration
- **DIY Folder**: Instructions and documentation stored in `DIY_folder/`

