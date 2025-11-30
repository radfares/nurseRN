# TECHNICAL ANALYSIS & V1.0 ROADMAP
## nurseRN Multi-Agent System - Floor Nurse QI Edition

**Generated**: 2025-11-29
**Target Audience**: Floor nurses conducting real QI projects for hospital approval
**Development Constraint**: Solo developer, 8 hours/week, maintainable codebase

---

## EXECUTIVE SUMMARY

**Biggest Problem**: **No cross-agent state coordination** - agents operate independently without shared context, causing silent data inconsistencies (PICOT from Agent 1 ≠ search terms in Agent 2 ≠ writing context in Agent 4).

**Recommended First Action**: Add `WorkflowOrchestrator` class (8 hours) that enforces PICOT → Search → Write state machine and links records via foreign keys.

**Overall Assessment**: **SALVAGEABLE** - excellent infrastructure (94% test coverage, circuit breakers, clean inheritance), but needs orchestration layer + validation middleware. Not a rebuild, just architectural enhancement.

---

## ARCHITECTURE HEALTH REPORT

### Complexity Analysis

| Component | LOC | Cyclomatic Complexity | Responsibilities | Grade | Action |
|-----------|-----|----------------------|------------------|-------|--------|
| `nursing_research_agent.py` | 482 | 8 (8 tools) | PICOT + Search + Safety + Standards | **C** | Split into 3 agents |
| `project_manager.py` | 698 | 5 | Schema + CRUD + CLI | **B** | Extract schema to SQL file |
| `data_analysis_agent.py` | 340 | 2 | Statistical planning | **A** | No changes needed |
| `run_nursing_project.py` | 324 | 3 | REPL loop | **B** | Add orchestrator mode |
| `circuit_breaker.py` | 322 | 4 | Resilience layer | **A** | No changes needed |

**Verdict**: 2/7 components need refactoring (NursingResearchAgent, ProjectManager).

### Missing Modules
- `src/orchestration/` - Workflow coordination ❌
- `src/validation/` - Clinical sanity checks ❌
- `src/export/` - Committee proposal generation ❌

---

## CRITICAL RISK MATRIX

### CRITICAL SEVERITY 🔴

| Risk ID | File/Function | Issue | Impact If Triggered | Recommended Fix | Effort (hrs) |
|---------|--------------|-------|---------------------|-----------------|--------------|
| **CR-1** | `run_nursing_project.py:232` | **No state passed between agents** | Nurse presents inconsistent project → Committee rejects | Add `WorkflowContext` object passed to all agents | 8 |
| **CR-2** | `data_analysis_agent.py:210-224` | **No sample size sanity checks** | Nurse proposes n=1000 for 20-bed unit → Impossible timeline | Add validation: `if n > 200: warn()` | 4 |
| **CR-3** | `project_manager.py:54-77` | **No `current_version` flag** | Multiple PICOTs, unclear which is active | Add column: `is_current BOOLEAN` | 2 |
| **CR-4** | `nursing_research_agent.py:144-153` | **No tool priority enforcement** | Agent uses preprints instead of peer-reviewed | Add tool ranking in prompt | 1 |

### HIGH SEVERITY 🟠

| Risk ID | File/Function | Issue | Impact If Triggered | Recommended Fix | Effort (hrs) |
|---------|--------------|-------|---------------------|-----------------|--------------|
| **HR-1** | `medical_research_agent.py:50-64` | **Silent PubMed failure** | Zero results, nurse doesn't realize API is down | Raise exception instead of silent failure | 0.5 |
| **HR-2** | `circuit_breaker.py:109-118` | **Circuit open notification only logs** | No user alert when API unavailable | Add user notification in print | 1 |
| **HR-3** | `project_manager.py:298-335` | **Hardcoded 2025-2026 dates** | Useless after June 2026 | Make milestones relative with offsets | 3 |
| **HR-4** | All agents | **No `save_to_project_db()` method** | Manual copy-paste of findings | Add persistence method to BaseAgent | 6 |
| **HR-5** | `run_nursing_project.py:273-280` | **Agent errors not logged to DB** | No audit trail to debug issues | Log errors to `conversations` table | 2 |
| **HR-6** | `safety_tools.py:40-86` | **No connectivity check enforcement** | False negative on FDA recalls | Call `verify_access()` in `__init__` | 1 |

### MEDIUM SEVERITY 🟡

| Risk ID | File/Function | Issue | Recommended Fix | Effort (hrs) |
|---------|--------------|-------|-----------------|--------------|
| **MR-1** | `project_manager.py:573-576` | **No connection pooling** | Add singleton connection pool with thread-safe locking | 4 |
| **MR-2** | `project_manager.py:578-597` | **Path traversal vulnerability** | Block `..` in project names | 0.5 |
| **MR-3** | `data_analysis_agent.py:78-94` | **No effect size range validation** | Add Field validator: `ge=-3, le=3` | 1 |
| **MR-4** | `run_nursing_project.py:100-109` | **No duplicate name check** | Add fuzzy match warning | 2 |
| **MR-5** | `nursing_research_agent.py:233-314` | **8000+ char prompt** | Split into base + tool-specific addendums | 3 |

---

## FEATURE GAP ANALYSIS

### What's Missing for Hospital Approval

| Missing Capability | Clinical Impact | Implementation Complexity | v1.0? |
|-------------------|-----------------|---------------------------|-------|
| **PICOT quality scorecard** | **HIGH** - Vague PICOT → Committee rejects | **MEDIUM** - GPT-4 scoring with rubric | **YES** |
| **Deduplication across sources** | **MEDIUM** - Wastes time reviewing duplicates | **LOW** - Hash DOI/PMID | **YES** |
| **Inclusion/exclusion criteria checker** | **HIGH** - Weak evidence base | **MEDIUM** - GPT-4 PICO extraction | **YES** |
| **PICO extraction table** | **VERY HIGH** - Required, takes 2-3 hours manually | **MEDIUM** - Structured extraction | **YES** |
| **Evidence synthesis table** | **VERY HIGH** - Committee packet requirement | **MEDIUM** - Markdown table generator | **YES** |
| **Stakeholder analysis** | **CRITICAL** - Missed stakeholder → Shutdown | **MEDIUM** - Knowledge base of approvals | **YES** |
| **Data validation rules** | **HIGH** - Bad data → Analysis fails | **LOW** - Pydantic schemas | **YES** |
| **Budget estimation** | **CRITICAL** - Committee question #1 | **MEDIUM** - Cost library | **YES** |
| **Timeline feasibility check** | **CRITICAL** - Unrealistic n → Abandonment | **LOW** - Math formula | **YES** |
| **ROI calculator** | **HIGH** - Justifies funding | **MEDIUM** - Cost avoidance formulas | **YES** |
| **Committee proposal PDF export** | **VERY HIGH** - Saves 3-5 hours | **MEDIUM** - Template + PDF gen | **YES** |
| **IRB vs. QI decision tree** | **CRITICAL** - Wrong choice → 6-month delay | **LOW** - Decision tree logic | **YES** |
| **Citation export** | **LOW** - Needed only if publishing | **MEDIUM** - BibTeX export | **NO** (v2.0) |
| **Poster template integration** | **MEDIUM** - Nice-to-have | **HIGH** - PowerPoint API | **NO** (v2.0) |
| **R/Python code runner** | **MEDIUM** - Planning is valuable | **HIGH** - Security risk | **NO** (v2.0) |

---

## PROPOSED ARCHITECTURE

### Current vs. Proposed

**CURRENT (Disconnected Agents)**:
```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Agent 1     │  │  Agent 2     │  │  Agent 4     │
│  (PICOT)     │  │  (PubMed)    │  │  (Writing)   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
               ┌──────────────────┐
               │  project.db      │
               │  (No links)      │
               └──────────────────┘
```
❌ **Problem**: No enforcement of relationships.

**PROPOSED (Orchestrated Workflow)**:
```
┌───────────────────────────────────────────────────────────┐
│              WORKFLOW ORCHESTRATOR                         │
│  • Enforces state machine: PICOT → Search → Synthesize    │
│  • Passes context between agents                          │
│  • Validates outputs before next step                     │
└─────────────────┬─────────────────────────────────────────┘
                  │
      ┌───────────┼───────────┬───────────────┐
      ▼           ▼           ▼               ▼
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐
│ Agent 1  │ │ Agent 2  │ │ Agent 4  │ │ Agent 6+7    │
│ PICOT    │ │ PubMed   │ │ Writing  │ │ Planning     │
│ (GPT-4)  │ │ (PubMed) │ │ +Export  │ │ +Budget+IRB  │
└────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘
     │            │            │               │
     └────────────┴────────────┴───────────────┘
                         ▼
               ┌──────────────────────────────┐
               │  project.db (LINKED RECORDS) │
               │  • picot_id → finding_ids    │
               │  • finding_ids → draft_id    │
               └──────────────────────────────┘
```
✅ **Solution**: Orchestrator passes `WorkflowContext`, enforces foreign key links.

### Agent Responsibility Matrix (v1.0)

| Agent | Role | v1.0 Status |
|-------|------|-------------|
| **Agent 1: PICOT Developer** | Guide PICOT formulation | ✅ KEEP (simplify: remove external tools) |
| **Agent 2: Evidence Searcher** | Search PubMed for studies | ✅ KEEP (PubMed only, disable others) |
| **Agent 4: Research Writer** | Synthesize evidence, draft review | ✅ ENHANCE (add table export) |
| **Agent 6: Sample Size Planner** | Calculate n, create data template | ✅ ENHANCE (add budget, timeline checks) |
| **Agent 7: QI Project Advisor** 🆕 | Budget, stakeholders, IRB, feasibility | ✅ **NEW** (critical for approval) |
| **Orchestrator** 🆕 | Coordinate workflow, validate state | ✅ **NEW** (prevents inconsistencies) |

**Removed from v1.0**:
- ❌ **Agent 3 (Academic/ArXiv)** - Not critical for clinical QI (defer to v2.0)
- ❌ **Agent 5 (Timeline)** - Merge into Agent 7 with relative dates

---

## MIGRATION PLAN (44 hours total)

### Phase 1: Add Orchestration Layer (12 hours)
1. ✅ Create `src/orchestration/workflow_context.py` (2 hours)
2. ✅ Create `src/orchestration/workflow_orchestrator.py` (6 hours)
3. ✅ Add "Guided Mode" to `run_nursing_project.py` (2 hours)
4. ✅ Write integration tests (2 hours)

### Phase 2: Enhance Existing Agents (10 hours)
5. ✅ Simplify Agent 1 (Nursing Research) (2 hours)
6. ✅ Add `save_finding()` to Agent 2 (2 hours)
7. ✅ Add evidence table export to Agent 4 (3 hours)
8. ✅ Add timeline feasibility to Agent 6 (2 hours)
9. ✅ Add budget estimation to Agent 6 (1 hour)

### Phase 3: Add New Agent 7 (QI Planner) (8 hours)
10. ✅ Create `agents/qi_planner_agent.py` (4 hours)
11. ✅ Add Henry Ford-specific knowledge base (2 hours)
12. ✅ Wire Agent 7 to orchestrator (1 hour)
13. ✅ Write unit tests for Agent 7 (1 hour)

### Phase 4: Committee Proposal Export (8 hours)
14. ✅ Create `src/export/committee_proposal.py` (4 hours)
15. ✅ Add Markdown template (2 hours)
16. ✅ Add export to orchestrator workflow (1 hour)
17. ✅ Test export with real project data (1 hour)

### Phase 5: Validation & Testing (6 hours)
18. ✅ Add clinical sanity checks (3 hours)
19. ✅ Add PICOT quality scorecard (2 hours)
20. ✅ Nurse peer review (3 reviewers) (1 hour)

---

## SAFETY & VALIDATION STRATEGY

### Tier 1: Automated Tests (CI/CD)

| Test Type | Pass Criteria | Automated? |
|-----------|---------------|------------|
| **Smoke Test** | Guided workflow completes without exceptions | ✅ YES |
| **Output Accuracy Test** | Sample size n < 500; budget < $50k; timeline < 12mo | ✅ YES |
| **Consistency Test** | Same PICOT → Same PubMed query | ✅ YES |
| **Adversarial Test** | Project name `"; DROP TABLE;` doesn't execute SQL | ✅ YES |
| **Regression Test** | All 173 unit tests + 10 integration tests pass | ✅ YES |
| **Foreign Key Integrity** | `finding_id` exists before linking to `draft_id` | ✅ YES |

### Tier 2: Human Review (Nurse Peer Validation)

| Validation Task | Reviewer | Pass Criteria |
|----------------|----------|---------------|
| **PICOT Quality** | Experienced QI nurse | 8/10 PICOTs are "good quality" |
| **Literature Search Accuracy** | Medical librarian | ≥3 relevant articles for 9/10 queries |
| **Budget Estimate Accuracy** | Nurse manager | Within ±20% of actual unit costs |
| **Stakeholder Map Completeness** | QI director | Identifies all required approvals |
| **IRB Decision Accuracy** | IRB coordinator | Correctly classifies 10/10 test cases |

### Tier 3: Clinical Expert Audit (Quarterly)

| Expert | What They Review |
|--------|-----------------|
| **Medical Librarian** | PubMed search strategies |
| **Biostatistician** | Sample size calculations |
| **QI Director** | Budget estimates, stakeholder maps |
| **IRB Coordinator** | IRB decision logic |

### Liability Protection (Four Layers)

1. **Startup Modal**: Cannot bypass disclaimer acknowledgment
2. **Output Watermarking**: Every agent response has disclaimer footer
3. **Audit Trail**: Database logging of all queries, exports, disclaimer acceptance
4. **Export Watermark**: PDF footer on committee proposals

### Audit Trail Requirements

| Event | Data Captured | Retention |
|-------|--------------|-----------|
| **Disclaimer Acceptance** | Timestamp | Permanent |
| **Agent Query** | Agent name, query length, response length | Permanent |
| **PICOT Created** | Full text, version, approval status | Permanent |
| **Literature Search** | Query, # results, source, timestamp | Permanent |
| **Budget Estimate** | Intervention, sample size, cost | Permanent |
| **PDF Export** | File hash, timestamp, linked records | Permanent |
| **API Calls** | API name, success/failure, response time | 90 days |
| **Errors** | Exception type, stack trace | 90 days |

---

## IMMEDIATE ACTION PLAN (6 Weeks @ 8 hrs/week)

### Phase 1 (Week 1 - 8 hours)
**Priority: Fix Critical Risks + Add Highest-Value Features**

1. ✅ Add WorkflowContext class (2 hours)
   - File: `src/orchestration/workflow_context.py`

2. ✅ Add sample size validation to Agent 6 (1 hour)
   - File: `agents/data_analysis_agent.py:305`

3. ✅ Add `is_current` flag to picot_versions (0.5 hours)
   - File: `project_manager.py:54`

4. ✅ Add clinical disclaimer modal (1.5 hours)
   - File: `run_nursing_project.py:37`

5. ✅ Add output watermarking to BaseAgent (1 hour)
   - File: `agents/base_agent.py:145`

6. ✅ Fix PubMed silent failure (0.5 hours)
   - File: `agents/medical_research_agent.py:62`

7. ✅ Add path traversal protection (0.5 hours)
   - File: `project_manager.py:591`

8. ✅ Add budget estimation stub to Agent 6 (1 hour)
   - File: `agents/data_analysis_agent.py:318`

### Phase 2 (Week 2 - 8 hours)
**Priority: Build Orchestrator + Agent 7 Skeleton**

9. ✅ Create WorkflowOrchestrator skeleton (4 hours)
   - File: `src/orchestration/workflow_orchestrator.py`

10. ✅ Create QI Planner Agent skeleton (3 hours)
    - File: `agents/qi_planner_agent.py`

11. ✅ Write integration test for orchestrator (1 hour)
    - File: `tests/integration/test_workflow_orchestration.py`

### Phase 3 (Week 3 - 8 hours)
**Priority: Export Feature + Evidence Table**

12. ✅ Implement evidence synthesis table (3 hours)
    - File: `agents/research_writing_agent.py`

13. ✅ Create committee proposal export (4 hours)
    - File: `src/export/committee_proposal.py`

14. ✅ Add export to orchestrator (1 hour)
    - File: `src/orchestration/workflow_orchestrator.py`

### Phase 4 (Week 4 - 8 hours)
**Priority: Validation + Testing**

15. ✅ Implement ClinicalValidator class (3 hours)
    - File: `src/validation/clinical_checks.py`

16. ✅ Add validator calls to agents (2 hours)
    - Files: `agents/data_analysis_agent.py`, `agents/qi_planner_agent.py`

17. ✅ Conduct nurse peer review (2 hours)
    - Recruit 3 nurse colleagues, distribute checklist

18. ✅ Fix critical bugs from peer review (1 hour)

### Phase 5 (Week 5 - 8 hours)
**Priority: Polish + Documentation**

19. ✅ Write user guide (3 hours)
    - File: `docs/USER_GUIDE.md`

20. ✅ Add cost tracking (2 hours)
    - File: `project_manager.py:232`

21. ✅ Enhance timeline feasibility checker (2 hours)
    - File: `agents/data_analysis_agent.py`

22. ✅ Create demo project (1 hour)
    - Script: `scripts/create_demo_project.py`

### Phase 6 (Week 6 - 8 hours)
**Priority: Final Testing + Release Prep**

23. ✅ Run full regression suite (2 hours)
24. ✅ Add logging for audit trail (2 hours)
25. ✅ Test on fresh machine (2 hours)
26. ✅ Write v1.0 release notes (1 hour)
27. ✅ Create installer script (1 hour)

---

## MINIMUM VIABLE v1.0 SCOPE

**Must-Have Features**:
1. ✅ **Guided Workflow Mode** - Orchestrator enforces PICOT → Search → Write
2. ✅ **PICOT Quality Scorecard** - Validates Specific, Measurable, Feasible, Relevant, Time-bound
3. ✅ **PubMed Literature Search** - Agent 2 only (disable ArXiv/Exa)
4. ✅ **Evidence Synthesis Table** - Auto-generate from `literature_findings`
5. ✅ **Sample Size Calculator + Validation** - Agent 6 with n<500 sanity check
6. ✅ **Budget Estimator** - Cost library for CAUTI/falls/med safety
7. ✅ **Timeline Feasibility Checker** - Validates n vs. shifts/week × duration
8. ✅ **Stakeholder Mapper** - Identifies required approvals
9. ✅ **IRB Decision Tree** - Classifies as Research vs. QI
10. ✅ **Committee Proposal Export** - 1-page PDF
11. ✅ **Clinical Disclaimer + Watermarking** - Liability protection
12. ✅ **Audit Trail** - Log all queries, exports, disclaimer acceptance

**Deferred to v2.0**:
- ❌ Agent 3 (ArXiv)
- ❌ Agent 5 (Timeline with hardcoded dates)
- ❌ Citation export (Zotero/EndNote)
- ❌ Poster template integration
- ❌ Data analysis execution (R/Python)
- ❌ Multi-site rollout features

**Estimated Total Hours**: **48 hours** (6 weeks @ 8 hrs/week)

**Success Criteria**:
- Nurse can go from "QI idea" → "Committee-ready proposal PDF" in <2 hours
- ≥80% of generated proposals approved on first submission
- Budget estimates within ±20% of actual costs
- ≥2/3 nurse reviewers rate system as "Ready for use"

---

## CODE EXAMPLES

### WorkflowContext Implementation

```python
# src/orchestration/workflow_context.py
from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class WorkflowContext:
    """Shared state passed between agents in guided workflow."""
    project_name: str
    picot_id: Optional[int] = None
    finding_ids: List[int] = field(default_factory=list)
    draft_id: Optional[int] = None
    plan_id: Optional[int] = None

    def validate_for_search(self):
        """Ensure PICOT exists before searching."""
        if not self.picot_id:
            raise WorkflowError("Cannot search - PICOT not created yet")

    def validate_for_writing(self):
        """Ensure literature findings exist before writing."""
        if not self.finding_ids:
            raise WorkflowError("Cannot write - no literature found")

class WorkflowError(Exception):
    """Raised when workflow state is invalid."""
    pass
```

### Clinical Validator Implementation

```python
# src/validation/clinical_checks.py
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ValidationIssue:
    severity: str  # 'error' | 'warning'
    message: str
    suggestion: str

@dataclass
class ValidationResult:
    valid: bool
    issues: List[ValidationIssue]

class ClinicalValidator:
    """Validates agent outputs for clinical plausibility."""

    @staticmethod
    def validate_sample_size(n: int, context: Dict) -> ValidationResult:
        """Check if sample size is realistic for nursing QI project."""
        issues = []

        if n > 500:
            issues.append(ValidationIssue(
                severity='error',
                message=f'Sample size {n} is unrealistic for unit-level QI',
                suggestion='Consider pre/post design or longer timeframe'
            ))

        beds = context.get('unit_beds', 30)
        duration = context.get('duration_months', 6)
        max_possible = beds * 2 * duration  # 2 patients/bed/month

        if n > max_possible:
            issues.append(ValidationIssue(
                severity='error',
                message=f'Sample size {n} exceeds unit capacity ({max_possible} max)',
                suggestion='Reduce sample size or extend timeline'
            ))

        return ValidationResult(
            valid=len([i for i in issues if i.severity=='error']) == 0,
            issues=issues
        )
```

### Disclaimer Implementation

```python
# run_nursing_project.py
def show_clinical_disclaimer() -> bool:
    """Display disclaimer and require acknowledgment."""
    print("=" * 80)
    print("⚠️  CLINICAL DISCLAIMER ⚠️")
    print("=" * 80)
    print("""
This system is a QUALITY IMPROVEMENT PLANNING TOOL for nursing professionals.

IT IS NOT:
❌ A substitute for clinical judgment
❌ A replacement for institutional approvals
❌ Medical advice or clinical decision support

ALL OUTPUTS MUST BE REVIEWED BY:
- Nurse Manager (workflow feasibility)
- Clinical experts (Infection Control, Safety, Quality Dept)
- Statistician (if using sample size calculations)

BY USING THIS TOOL YOU ACKNOWLEDGE:
1. You are a licensed healthcare professional
2. You will obtain appropriate institutional approvals
3. You will validate all recommendations with experts
4. You are solely responsible for project outcomes
    """)
    print("=" * 80)

    response = input("\nType 'I UNDERSTAND AND AGREE' to continue: ")
    return response.strip().upper() == "I UNDERSTAND AND AGREE"
```

---

## NEXT STEPS

1. **This Week**: Implement Phase 1 (8 hours) - Critical fixes + disclaimer
2. **Beta Test**: Recruit 1 nurse colleague to test guided workflow
3. **Iterate**: Based on feedback, adjust Phase 2 priorities
4. **Documentation**: Create screencasts of guided workflow for user guide
5. **Release**: v1.0 launch after Phase 6 completion (Week 6)

---

**Document Owner**: Claude (Sonnet 4.5)
**Last Updated**: 2025-11-29
**Status**: Ready for implementation
