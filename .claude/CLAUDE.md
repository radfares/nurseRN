## GLOBAL IMPLEMENTATION RULES

---
## **CRITICAL RULE - PHASE APPROVAL REQUIRED**

**DO NOT PROCEED TO THE NEXT PHASE WITHOUT EXPLICIT USER APPROVAL.**

- After completing ANY phase, STOP and WAIT for the user to say "ok to phase X" or give explicit approval.
- This applies to ALL phased work: implementation phases, testing phases, cleanup phases, etc.
- Even if all validation gates pass, DO NOT automatically continue.
- Violating this rule wastes user time and removes their control over the project.

**Example of CORRECT behavior:**
```
Phase 1 complete. All validation gates passed.
Waiting for your approval to proceed to Phase 2.
```

**Example of WRONG behavior:**
```
Phase 1 complete. Moving to Phase 2...
[VIOLATION - did not wait for approval]
```

---

1. Never mark a task from `AGENTS_PLANS.md` as complete until it passes its VALIDATION GATES below.
2. For every change:
   - Locate the relevant file(s) mentioned in the plan.
   - Confirm the new functions/methods exist with the exact names specified.
   - Confirm they are **actually called** in the runtime path (`run()`, `runwithgroundingcheck()`, or `auditposthook()`).
   - Run or simulate the described tests (sample queries, error-path tests).
3. If a validation gate fails:
   - Do **not** move on to the next task/day.
   - Fix the issue and re-run the gate.
   - Log what failed and how it was fixed in `.claude/agent_audit.md`.
4. If code cannot be statically verified (e.g., missing file, import error), stop and report a **BLOCKER** instead of guessing.



No code in this file
everything is time stamped and dated each single visit and after project completion
task and todo list
  a-clean up the folder
    b-organize the files
      c-put not esstinal files in a folder nested with folders in order
      e-create a file ONE call it the truth_file.md and there I want a full breakdown of what each folder and files within those folders do. For example data_template.xlsx is a file what is it what does it do and is it being used. The same for the rest.
Then I want you go through each agents code file by file 5 times each one and find how We can optimize them not to  produce basic outputs and if can not be speiclized then the whole project is trashed no excusess no other solutions. You are allowed to change the agents around but consider cost. I do not want anyting to change for now.
