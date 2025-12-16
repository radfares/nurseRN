# 🔒 CLAUDE.md - Agent Configuration & Rules

> **Last Updated:** 2025-12-15

---

## ⚠️ MANDATORY AGENT ACKNOWLEDGMENT

**Before starting ANY work on this project, you MUST:**

1. Read this entire `CLAUDE.md` file
2. Confirm by stating: **"I have read and acknowledge CLAUDE.md (updated 2025-12-15)"**
3. Wait for user confirmation before proceeding

> [!CAUTION]
> Failure to acknowledge this file before starting work is a violation of project protocol.

---

## 🚫 CRITICAL RULE: PHASE APPROVAL REQUIRED

**DO NOT PROCEED TO THE NEXT PHASE WITHOUT EXPLICIT USER APPROVAL.**

| Rule | Description |
|------|-------------|
| **Wait for Approval** | After completing ANY phase, STOP and WAIT for user to say "ok to phase X" or give explicit approval |
| **Applies To** | ALL phased work: implementation, testing, cleanup, etc. |
| **No Auto-Continue** | Even if all validation gates pass, DO NOT automatically continue |
| **Reason** | Violating this rule wastes user time and removes their control |

### ✅ CORRECT Behavior
```
Phase 1 complete. All validation gates passed.
Waiting for your approval to proceed to Phase 2.
```

### ❌ WRONG Behavior
```
Phase 1 complete. Moving to Phase 2...
[VIOLATION - did not wait for approval]
```

---

## 📋 Validation Gate Requirements

1. **Never mark a task** from `AGENTS_PLANS.md` as complete until it passes its VALIDATION GATES

2. **For every change:**
   - Locate the relevant file(s) mentioned in the plan
   - Confirm new functions/methods exist with exact names specified
   - Confirm they are **actually called** in runtime path (`run()`, `runwithgroundingcheck()`, or `auditposthook()`)
   - Run or simulate described tests (sample queries, error-path tests)

3. **If a validation gate fails:**
   - Do **NOT** move on to the next task/day
   - Fix the issue and re-run the gate
   - Log what failed and how it was fixed in `.claude/agent_audit.md`

4. **If code cannot be statically verified** (missing file, import error):
   - STOP and report a **BLOCKER**
   - Do NOT guess or assume

---

## 📁 Documentation Requirements

- Everything is **timestamped and dated** each visit and after project completion
- All work logged to `.claude/agent_audit.md`

---

## 📝 Pending Tasks (User Notes)

> [!NOTE]
> The following are user-defined tasks to be completed:

- [ ] **Folder Cleanup**
  - [ ] Organize files
  - [ ] Move non-essential files to nested folder structure
  - [ ] Create `truth_file.md` with full breakdown of:
    - Each folder's purpose
    - Each file's function (e.g., `data_template.xlsx` - what is it, what does it do, is it being used?)

- [ ] **Agent Code Review** (5 passes per agent)
  - [ ] Analyze each agent's code file-by-file
  - [ ] Identify optimization opportunities to avoid basic outputs
  - [ ] If agents cannot be specialized → project evaluation needed
  - [ ] Consider cost implications for any changes
  - [ ] **Note:** No changes to be made yet - analysis only

---

## 🧪 Testing Reference Guide

### 1. Proof of Concept (PoC) Testing

| Test Type | Category | Description |
|-----------|----------|-------------|
| Smoke Testing | Coding | Basic "does it turn on" test |
| Feasibility/Spike Testing | Coding | Quick throwaway code to verify technical challenges |
| Benchmark Testing | Coding | Performance metrics validation |
| Requirements Validation | Non-Coding | Review logic with stakeholders |
| Market/User Viability | Non-Coding | Show wireframes/concepts to potential users |

### 2. Implementation Testing

| Test Type | Category | Description |
|-----------|----------|-------------|
| Unit Testing | Coding | Test individual functions/modules |
| Static Code Analysis | Coding/Automated | Scan for errors, vulnerabilities |
| Integration Testing | Coding | Test module interactions |
| Code Reviews | Non-Coding | Manual code inspection |
| Usability Testing | Non-Coding | UX observation and feedback |

### 3. Verification of Integration (System Testing)

| Test Type | Category | Description |
|-----------|----------|-------------|
| System Integration Testing (SIT) | Coding/Config | End-to-end data flow verification |
| Regression Testing | Coding/Automated | Re-run previous tests after changes |
| Performance/Load Testing | Coding | Simulate high user load |
| User Acceptance Testing (UAT) | Non-Coding | Real-world user validation |
| Compliance/Audit Review | Non-Coding | Legal/regulatory verification |