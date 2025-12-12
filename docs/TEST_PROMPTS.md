# Comprehensive Agent Test Prompts

## Purpose

These prompts test the full agent system to ensure:
1. ✅ LLM-based planning (not fallback rules)
2. ✅ Context awareness (remembers conversation)
3. ✅ All agents work correctly
4. ✅ Outputs are relevant and high-quality

---

## Quick Diagnostic (Run This First)

### Step 1: Run Diagnostic Script

```bash
cd /Users/hdz/nurseRN
.venv/bin/python3 test_orchestrator_full.py
```

**This will test:**
- OpenAI API key configuration
- Orchestrator initialization
- All 7 agents availability
- LLM-based planning
- Context awareness
- End-to-end query processing

**Expected output:**
```
✅ PASS: api_key
✅ PASS: orchestrator_init
✅ PASS: agent_registry
✅ PASS: llm_planning
✅ PASS: context_awareness
✅ PASS: end_to_end

RESULT: 6/6 tests passed
🎉 ALL TESTS PASSED!
```

---

## Manual Test Prompts (If Diagnostic Passes)

### Test 1: Context Awareness

**Purpose:** Verify system remembers conversation context

```
Start application:
.venv/bin/python3 run_nursing_project.py

Then run this conversation:
```

**Prompt 1:**
```
How does communication between nurses and nursing aides improve workflow efficiency in hospital settings?
```

**Expected:** System searches for articles, provides research findings

**Prompt 2:**
```
generate a picot question
```

**Expected:** Generates PICOT about nurse-aide communication (NOT random topic)

**✅ PASS if:** PICOT mentions nurses, aides, communication, or workflow  
**❌ FAIL if:** PICOT is about random topic (nursing students, etc.)

---

### Test 2: Multi-Step Research Workflow

**Purpose:** Verify full research workflow with validation

**Prompt:**
```
Research fall prevention interventions in elderly hospitalized patients. Find validated evidence and synthesize the findings.
```

**Expected:**
1. Creates 4-5 tasks
2. Generates PICOT about fall prevention
3. Searches PubMed for articles
4. Validates article quality
5. Synthesizes findings

**✅ PASS if:**
- Response includes PICOT question
- Lists 3+ research articles with PMIDs
- Includes evidence levels (I-VII)
- Provides synthesis of findings

**❌ FAIL if:**
- Generic response without articles
- No evidence grading
- Random topic (not fall prevention)

---

### Test 3: Follow-Up Questions

**Purpose:** Verify system maintains context across multiple turns

**Prompt 1:**
```
I'm interested in CAUTI prevention strategies
```

**Expected:** System discusses CAUTI prevention

**Prompt 2:**
```
search for recent studies
```

**Expected:** Searches for CAUTI prevention studies (NOT generic "recent studies")

**Prompt 3:**
```
what's the evidence level?
```

**Expected:** Grades evidence for the CAUTI articles found in Prompt 2

**✅ PASS if:** Each follow-up uses context from previous messages  
**❌ FAIL if:** System asks "what studies?" or searches generic topics

---

### Test 4: Conversational Queries

**Purpose:** Verify system understands natural language

**Prompt 1:**
```
what do you recommend for my project?
```

**Expected:** Shows next milestone or suggests next steps

**Prompt 2:**
```
what are some promising research topics in nursing?
```

**Expected:** Searches for trending nursing research topics

**Prompt 3:**
```
how can I improve patient satisfaction scores?
```

**Expected:** Researches patient satisfaction interventions

**✅ PASS if:** System creates plans (not 0 tasks) for all queries  
**❌ FAIL if:** System says "I'm not sure what you'd like to do"

---

### Test 5: Agent-Specific Tasks

**Purpose:** Verify each agent works correctly

**Timeline Agent:**
```
What's my next deadline?
```
**Expected:** Shows upcoming milestone

**Data Analysis Agent:**
```
Calculate sample size for a study with 30% reduction in falls, 80% power, 0.05 alpha
```
**Expected:** Provides sample size calculation

**Citation Validation Agent:**
```
Validate these articles: PMID 12345678, PMID 23456789
```
**Expected:** Grades evidence levels, checks for retractions

**Research Writing Agent:**
```
Generate a PICOT question for pressure ulcer prevention in ICU patients
```
**Expected:** Generates structured PICOT

**Medical Research Agent:**
```
Search PubMed for systematic reviews on hand hygiene compliance
```
**Expected:** Returns PubMed articles with PMIDs

**✅ PASS if:** Each agent returns relevant, specific output  
**❌ FAIL if:** Generic responses or errors

---

## Interpreting Results

### All Tests Pass ✅

Your system is working correctly:
- LLM-based planning active
- Context awareness working
- All agents functional
- Outputs are relevant

**Action:** No fixes needed, system is production-ready

---

### Context Awareness Fails ❌

**Symptom:** System generates content about random topics instead of conversation topic

**Fix:** Deploy the context-aware orchestrator:

```bash
cd /Users/hdz/nurseRN
cp intelligent_orchestrator_FINAL_FIX.py src/orchestration/intelligent_orchestrator.py
git add src/orchestration/intelligent_orchestrator.py
git commit -m "Fix: Add conversation history for context awareness"
git push origin main
```

---

### Planning Creates 0 Tasks ❌

**Symptom:** System says "I'm not sure what you'd like to do" for valid queries

**Fix:** Update planner prompt to be more helpful:

```bash
cd /Users/hdz/nurseRN
cp intelligent_orchestrator_FINAL_FIX.py src/orchestration/intelligent_orchestrator.py
```

---

### API Key Not Configured ❌

**Symptom:** Tests fail at step 1 (API key check)

**Fix:**

```bash
cd /Users/hdz/nurseRN

# Create/edit .env file
echo "OPENAI_API_KEY=your-actual-key-here" >> .env

# Verify
cat .env | grep OPENAI_API_KEY
```

---

### Agents Not Available ❌

**Symptom:** Agent registry test fails

**Fix:** Check agent imports in `agent_registry.py`:

```python
# Verify all agents are imported correctly
from agents.nursing_research_agent import nursing_research_agent
from agents.medical_research_agent import get_medical_research_agent
# ... etc
```

---

### Fallback Mode Active ❌

**Symptom:** Orchestrator uses rule-based planning instead of LLM

**Check:**
```python
# In intelligent_orchestrator.py __init__
if hasattr(self, 'client') and self.client:
    print("✅ LLM mode")
else:
    print("❌ Fallback mode")
```

**Fix:** Ensure OpenAI client is initialized:

```python
def __init__(self):
    self.client = OpenAI()  # This should NOT be None
    # ... rest of init
```

---

## Expected Behavior Summary

| Test | Expected Behavior | Pass Criteria |
|------|-------------------|---------------|
| Context Awareness | Remembers previous topic | PICOT about discussed topic |
| Multi-Step Workflow | Runs 4-5 tasks automatically | Articles + validation + synthesis |
| Follow-Up Questions | Uses context from previous messages | Relevant to conversation |
| Conversational Queries | Understands natural language | Creates plans (not 0 tasks) |
| Agent-Specific | Each agent returns relevant output | Specific, not generic |

---

## Quick Validation Commands

### Check API Key
```bash
echo $OPENAI_API_KEY
```

### Check Orchestrator Version
```bash
cd /Users/hdz/nurseRN
head -20 src/orchestration/intelligent_orchestrator.py | grep -E "FIXED|Created"
```

### Check Recent Commits
```bash
git log --oneline -5 src/orchestration/intelligent_orchestrator.py
```

### Run Diagnostic
```bash
.venv/bin/python3 test_orchestrator_full.py 2>&1 | tee diagnostic_results.txt
```

---

## Success Criteria

**System is working correctly if:**

1. ✅ Diagnostic script: 6/6 tests pass
2. ✅ Context test: PICOT about discussed topic
3. ✅ Workflow test: 4-5 tasks executed
4. ✅ Follow-up test: Uses conversation context
5. ✅ Conversational test: No "I'm not sure" responses
6. ✅ Agent test: All 7 agents return relevant output

**If all pass → System is production-ready! 🎉**

---

## Troubleshooting

### Issue: "I'm not sure what you'd like to do"

**Cause:** Planner is too conservative or using fallback rules

**Fix:** Deploy context-aware orchestrator with improved prompt

### Issue: Generic/random topics in responses

**Cause:** Context not passed to planner

**Fix:** Deploy orchestrator with conversation history

### Issue: 0 tasks created

**Cause:** Planner prompt too strict or API failure

**Fix:** Check API key, deploy improved planner prompt

### Issue: Agents return errors

**Cause:** Agent initialization failure or missing dependencies

**Fix:** Check agent imports, verify dependencies installed

---

## Final Validation

After deploying fixes, run this complete test:

```bash
cd /Users/hdz/nurseRN
.venv/bin/python3 run_nursing_project.py
```

**Test conversation:**
```
You: How does nurse-aide communication improve workflow?
[Wait for response]

You: generate a picot question
[Should generate PICOT about nurse-aide communication]

You: search for recent articles
[Should search about nurse-aide communication]

You: validate the evidence quality
[Should validate the articles found]
```

**✅ If all work correctly → SYSTEM FIXED!**
