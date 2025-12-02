# NurseRN Repository Refactoring Plan
**Date:** 2025-12-02  
**Status:** PENDING USER APPROVAL  

---

## Executive Summary

After scanning the repository, I've identified **significant redundancy and cleanup opportunities**. The repo currently contains:
- **~1.4GB total** (including `.venv`)
- **25MB** of vendored `libs/` (agno framework)
- **9.3MB** of `cookbook/` (demo/example code)
- **1.2MB** of archived files
- **50MB** of `.git` history

### Key Issues Found:
1. **Cookbook folder (9.3MB)** - Demo/example code not used by main app
2. **Duplicate documentation** - Same info in multiple locations
3. **Historical reports scattered** - Should be consolidated
4. **Root-level clutter** - Files that belong in subdirectories
5. **Missing DIY_folder** - Not created per your preference

---

## TIER 1: REMOVE (Safe to Delete)

### Files with `❌` - Recommended for Deletion

| Path | Size | Reason |
|------|------|--------|
| `/cookbook/` | 9.3MB | Demo/example code from agno - not used by nursing project |
| `/.pytest_cache/` | - | Auto-generated, can be recreated |
| `/.mypy_cache/` | - | Auto-generated cache |
| `/.ruff_cache/` | - | Auto-generated cache |
| `/__pycache__/` | - | Python bytecode cache |
| `/pytest_full_output.txt` | 564B | Old test output |
| `/api_cache.sqlite` | 24KB | Should be in tmp/ or data/ |
| `/diagnostic_tool_analysis.py` | 7KB | One-time diagnostic script |
| `/.coverage` | 53KB | Coverage data (regenerated on test) |

### Cookbook Analysis (9.3MB)
```
/cookbook/
├── demo/           # Generic agno demos - NOT nursing specific
├── evals/          # Performance evaluations - NOT needed
├── tools/          # ~150 tool examples - NOT used
└── README.md       # Documentation for unused code
```
**Verdict:** Delete entire folder - it's reference code from agno framework

---

## TIER 2: CONSOLIDATE ARCHIVES

### Move to `/archived/` (organized subfolders)

| Current Location | New Location | Reason |
|------------------|--------------|--------|
| `/archived/root_cleanup_2025_12_02/` | Keep as-is | Already archived |
| `/archived/historical-reports/` | Keep as-is | Already organized |
| `/.claude/archive/` | `/archived/claude_plans/` | Consolidate all archives |
| `/docs/phase_planning/` | `/archived/phase_planning/` | Historical - phases completed |

### Files to Archive from Root

| File | New Location | Reason |
|------|--------------|--------|
| `/ARCHITECTURAL_DESIGN.md` | `/archived/` | Reference doc, not active |
| `/CODE_OF_CONDUCT.md` | `/docs/` | Standard location |
| `/CONTRIBUTING.md` | `/docs/` | Standard location |
| `/GEMINI.md` | `/archived/` | Alternative model notes |
| `/NEW_AGENTS_GUIDE.md` | `/docs/guides/` | Active documentation |
| `/NURSING_PROJECT_GUIDE.md` | `/docs/guides/` | Active documentation |
| `/SETUP.md` | `/docs/guides/` | Active documentation |

---

## TIER 3: REORGANIZE (Keep but Move)

### Proposed New Structure

```
nurseRN/
├── agents/                    # ✅ KEEP - Core agents (7 files)
├── src/                       # ✅ KEEP - Core services
│   ├── services/              
│   ├── tools/                 
│   └── orchestration/         
├── libs/                      # ✅ KEEP - Vendored agno (25MB required)
│   ├── agno/
│   └── agno_infra/
├── data/                      # ✅ KEEP - Project data
│   ├── projects/
│   └── archives/
├── tmp/                       # ✅ KEEP - Session databases
├── tests/                     # ✅ KEEP - Test suite
├── scripts/                   # ⚠️ CLEANUP NEEDED
├── docs/                      # ⚠️ REORGANIZE
│   ├── guides/                # Move user guides here
│   └── reference/             # Technical reference
├── archived/                  # Consolidated archives
├── New_Grad_project/          # ✅ KEEP - User project data
├── DIY_folder/                # ✅ CREATE - Per your preference
├── .claude/                   # ⚠️ SLIM DOWN
├── .github/                   # ✅ KEEP
└── [root files]               # ⚠️ REDUCE CLUTTER
```

---

## TIER 4: ROOT FILE CLEANUP

### Files to KEEP at Root (Essential)
```
✅ agent_config.py              # Core config
✅ run_nursing_project.py       # Main entry point
✅ project_manager.py           # Project management
✅ start_nursing_project.sh     # Launch script
✅ setup_venv.sh                # Setup script
✅ requirements.txt             # Dependencies
✅ README.md                    # Project documentation
✅ LICENSE                      # Legal
✅ pytest.ini                   # Test config
✅ CODEOWNERS                   # Git config
✅ .env / .env.example          # Environment config
✅ .gitignore                   # Git config
✅ .editorconfig                # Editor config
✅ .cursorrules                 # Cursor AI config
✅ AGENTS.md                    # Your custom rules
```

### Files to MOVE from Root
```
→ /docs/
  - CODE_OF_CONDUCT.md
  - CONTRIBUTING.md

→ /docs/guides/
  - NEW_AGENTS_GUIDE.md
  - NURSING_PROJECT_GUIDE.md
  - SETUP.md

→ /archived/
  - ARCHITECTURAL_DESIGN.md
  - GEMINI.md

→ /tmp/ or DELETE
  - api_cache.sqlite
  - pytest_full_output.txt
  - diagnostic_tool_analysis.py
  - data_template.xlsx (move to data/)
```

---

## TIER 5: SCRIPTS CLEANUP

### Scripts to KEEP
```
✅ dev_setup.sh          # Essential
✅ format.sh             # Essential
✅ validate.sh           # Essential
✅ test.sh               # Essential
✅ _utils.sh             # Dependency
✅ template_to_excel.py  # Useful tool
```

### Scripts to ARCHIVE or REMOVE
```
❌ _utils.bat             # Windows - not used on Mac
❌ dev_setup.bat          # Windows version
❌ format.bat             # Windows version
❌ test.bat               # Windows version
❌ validate.bat           # Windows version
→ ARCHIVE:
  - run_agent6_query.py   # Test script
  - run_medical_agent_safe.py
  - smoke_test_research_tools.py
  - run_model_tests.sh
  - cookbook_setup.sh     # For deleted cookbook
  - perf_setup.sh         # Performance testing
```

---

## TIER 6: .CLAUDE FOLDER CLEANUP

### Current Size: 304KB

| File/Folder | Action | Reason |
|-------------|--------|--------|
| `CLAUDE.md` | ✅ KEEP | Active Claude context |
| `QUICK_REFERENCE.md` | ✅ KEEP | Active reference |
| `settings.local.json` | ✅ KEEP | Local settings |
| `skills/` | ✅ KEEP | Custom skills |
| `archive/` | → `/archived/claude_plans/` | Move to main archive |
| `agent_audit_logs/` | ✅ KEEP | Important logs |
| `agent_mistral.py` | ❌ REMOVE | Unused |
| `DOCUMENT_ACCESS_PLAN.md` | → Archive | Completed plan |
| `PHASE_2_HALLUCINATION_PREVENTION_COMPLETED.md` | → Archive | Historical |
| `ROOT_CAUSE_ANALYSIS_TOOL_VISIBILITY.md` | → Archive | Historical |
| `TECHNICAL_ANALYSIS_AND_V1_ROADMAP.md` | → Archive | Reference only |

---

## ESTIMATED SAVINGS

| Category | Current | After Cleanup |
|----------|---------|---------------|
| Cookbook | 9.3MB | 0 |
| Caches | ~5MB | 0 (regenerated as needed) |
| Scripts (Windows) | ~10KB | 0 |
| Scattered archives | ~1MB | Consolidated |
| **Total Savings** | **~15MB** | |

---

## ACTION CHECKLIST

### Phase 1: Create Structure (Do First)
- [ ] Create `/DIY_folder/` directory
- [ ] Create `/archived/claude_plans/` directory
- [ ] Create `/docs/reference/` directory

### Phase 2: Safe Deletions
- [ ] Delete `/cookbook/` folder entirely
- [ ] Delete cache folders (`__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`)
- [ ] Delete `/pytest_full_output.txt`
- [ ] Delete `/.coverage`
- [ ] Delete `/diagnostic_tool_analysis.py`

### Phase 3: Move Files
- [ ] Move `.claude/archive/*` → `/archived/claude_plans/`
- [ ] Move `/docs/phase_planning/*` → `/archived/phase_planning/`
- [ ] Move root docs to appropriate locations
- [ ] Move `/api_cache.sqlite` → `/tmp/`
- [ ] Move `/data_template.xlsx` → `/data/`

### Phase 4: Scripts Cleanup
- [ ] Delete Windows .bat files from `/scripts/`
- [ ] Archive test scripts to `/archived/scripts/`

### Phase 5: Final Cleanup
- [ ] Clean up `.claude/` folder
- [ ] Update `.gitignore` if needed
- [ ] Run `git status` to verify changes
- [ ] Test that app still runs

---

## RISK ASSESSMENT

| Action | Risk Level | Mitigation |
|--------|------------|------------|
| Delete cookbook | LOW | Not imported by any agent |
| Delete caches | NONE | Auto-regenerated |
| Move archives | LOW | No code references them |
| Delete Windows scripts | NONE | Mac-only environment |
| Move root docs | LOW | Update any hardcoded paths |

---

## AWAITING YOUR APPROVAL

**Please review this plan and let me know:**
1. ✅ Approve all recommendations
2. ⚠️ Approve with modifications (specify)
3. ❌ Do not proceed

I will NOT make any changes until you explicitly approve.
