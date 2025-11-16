# PHASE 2 PLAN: Architecture, Reuse & Streaming

**Project**: Nursing Research Agents - Beta 1
**Phase**: 2 of 3
**Branch**: `claude/nursing-research-agents-beta_1-011CV5AKAeg3JoNYWtMnnrwg`
**Plan Created**: 2025-11-16 16:45 UTC
**Estimated Duration**: 4-6 hours
**Status**: 📋 PLANNING

---

## PHASE 1 COMPLETION STATUS ✅

**Completed**: 2025-11-16 07:20 UTC
**Duration**: 63 minutes
**Results**: All 6 agents passed with 0 errors

**Achievements**:
- ✅ Error handling (all 6 agents)
- ✅ Logging framework (all 6 agents)
- ✅ Centralized configuration (agent_config.py)
- ✅ API key security fix (Agent 1)
- ✅ Absolute database paths (all 6 agents)

---

## PHASE 2 OBJECTIVES

### Goal: Improve Architecture, Enable Reuse & Add Streaming

**Focus Areas**:
1. **Architecture**: Create base agent class for code reuse
2. **Streaming**: Enable real-time responses for all agents
3. **Optimization**: Add caching and rate limiting for API-based agents
4. **Configuration**: Move remaining hardcoded values to config

**Timeline**:
- **Start**: TBD (pending user approval)
- **Estimated End**: Start + 4-6 hours
- **Method**: 3-Part Loop for each improvement

---

## PHASE 2 TASKS

### Task Group 1: Base Agent Class (Priority: HIGH)
**Estimated Time**: 90 minutes
**Timestamp**: TBD

#### Task 1.1: Design Base Agent Class
**Duration**: 30 minutes
**Description**: Create `base_agent.py` with shared functionality

**Requirements**:
- [ ] Common initialization logic
- [ ] Shared error handling patterns
- [ ] Shared logging setup
- [ ] Database configuration
- [ ] Model configuration
- [ ] Streaming support built-in

**Deliverable**: `base_agent.py` (estimated 150-200 lines)

**Validation**:
- [ ] Base class can be imported
- [ ] No errors when instantiated
- [ ] All shared methods work

---

#### Task 1.2: Refactor Agent 6 (Data Analysis) to Use Base Class
**Duration**: 20 minutes
**Description**: First agent to inherit from base class

**Changes**:
- [ ] Import BaseAgent
- [ ] Inherit from BaseAgent
- [ ] Remove duplicate code
- [ ] Test functionality

**Validation**:
- [ ] Agent 6 works identically to before
- [ ] Code is shorter (reduced duplication)
- [ ] Error count: 0

---

#### Task 1.3: Refactor Remaining Agents (2, 4, 1, 5, 3)
**Duration**: 40 minutes (8 min per agent)
**Description**: Apply base class pattern to all agents

**Sequence**:
1. [ ] Agent 2 (Medical Research) - 8 min
2. [ ] Agent 4 (Research Writing) - 8 min
3. [ ] Agent 1 (Nursing Research) - 8 min
4. [ ] Agent 5 (Project Timeline) - 8 min
5. [ ] Agent 3 (Academic Research) - 8 min

**Validation** (each agent):
- [ ] Works identically to before
- [ ] Code reduction achieved
- [ ] Error count: 0

---

### Task Group 2: Enable Streaming (Priority: HIGH)
**Estimated Time**: 90 minutes
**Timestamp**: TBD

#### Task 2.1: Update Base Agent Class for Streaming
**Duration**: 20 minutes
**Description**: Add streaming support to BaseAgent

**Changes**:
- [ ] Add `enable_streaming=True` to agent creation
- [ ] Add streaming configuration
- [ ] Test streaming output

**Deliverable**: BaseAgent with streaming enabled

---

#### Task 2.2: Enable Streaming for All Agents
**Duration**: 30 minutes (5 min per agent)
**Description**: Turn on streaming for all 6 agents

**Sequence**:
1. [ ] Agent 6 - 5 min
2. [ ] Agent 2 - 5 min
3. [ ] Agent 4 - 5 min
4. [ ] Agent 1 - 5 min
5. [ ] Agent 5 - 5 min
6. [ ] Agent 3 - 5 min

**Validation**:
- [ ] Each agent streams responses
- [ ] No errors during streaming
- [ ] User experience improved

---

#### Task 2.3: Test Streaming Integration
**Duration**: 40 minutes
**Description**: Comprehensive streaming tests

**Tests**:
- [ ] Short queries stream correctly
- [ ] Long queries stream correctly
- [ ] Error handling works during streaming
- [ ] Interruption (Ctrl+C) works during streaming

---

### Task Group 3: API Optimization (Priority: MEDIUM)
**Estimated Time**: 120 minutes
**Timestamp**: TBD

#### Task 3.1: Add Rate Limiting
**Duration**: 40 minutes
**Description**: Prevent API rate limit errors

**Agents Affected**:
- [ ] Agent 1 (Nursing Research) - Exa + SerpAPI
- [ ] Agent 2 (Medical Research) - PubMed
- [ ] Agent 3 (Academic Research) - ArXiv

**Implementation**:
- [ ] Add rate limiting to agent_config.py
- [ ] Configure per-API limits
- [ ] Test with rapid queries

**Validation**:
- [ ] No rate limit errors
- [ ] Queries still work
- [ ] Performance acceptable

---

#### Task 3.2: Add Response Caching
**Duration**: 40 minutes
**Description**: Cache API responses to reduce costs

**Agents Affected**:
- [ ] Agent 1 (Nursing Research)
- [ ] Agent 2 (Medical Research)
- [ ] Agent 3 (Academic Research)

**Implementation**:
- [ ] Add caching layer to BaseAgent
- [ ] Configure cache TTL (time-to-live)
- [ ] Test cache hit/miss

**Validation**:
- [ ] Duplicate queries use cache
- [ ] Cache doesn't serve stale data
- [ ] Cache size is manageable

---

#### Task 3.3: Add API Usage Logging
**Duration**: 40 minutes
**Description**: Track API usage for cost monitoring

**Implementation**:
- [ ] Log all API calls
- [ ] Track API costs (estimate)
- [ ] Create usage report

**Validation**:
- [ ] All API calls are logged
- [ ] Cost estimates are accurate
- [ ] Usage report is useful

---

### Task Group 4: Configuration Improvements (Priority: LOW)
**Estimated Time**: 60 minutes
**Timestamp**: TBD

#### Task 4.1: Move Timeline Dates to Configuration (Agent 5)
**Duration**: 30 minutes
**Description**: Make timeline configurable for multiple cohorts

**Changes**:
- [ ] Create timeline_config.py
- [ ] Move dates from instructions to config
- [ ] Update Agent 5 to use config

**Validation**:
- [ ] Agent 5 works with new config
- [ ] Timeline is easily updatable
- [ ] Error count: 0

---

#### Task 4.2: Environment Variable Documentation
**Duration**: 30 minutes
**Description**: Document all required environment variables

**Deliverable**: `.env.example` file

**Contents**:
- [ ] OPENAI_API_KEY
- [ ] EXA_API_KEY
- [ ] SERP_API_KEY
- [ ] AGENT_LOG_LEVEL
- [ ] Other configuration options

**Validation**:
- [ ] .env.example is complete
- [ ] Instructions are clear
- [ ] Users can set up easily

---

## PHASE 2 TIMELINE (ESTIMATED)

```
Hour 0:00 - 1:30  │ Task Group 1: Base Agent Class
                  │ ├─ 0:00-0:30: Design base class
                  │ ├─ 0:30-0:50: Refactor Agent 6
                  │ └─ 0:50-1:30: Refactor Agents 2,4,1,5,3
                  │
Hour 1:30 - 3:00  │ Task Group 2: Enable Streaming
                  │ ├─ 1:30-1:50: Update BaseAgent
                  │ ├─ 1:50-2:20: Enable for all agents
                  │ └─ 2:20-3:00: Test streaming
                  │
Hour 3:00 - 5:00  │ Task Group 3: API Optimization
                  │ ├─ 3:00-3:40: Rate limiting
                  │ ├─ 3:40-4:20: Response caching
                  │ └─ 4:20-5:00: Usage logging
                  │
Hour 5:00 - 6:00  │ Task Group 4: Configuration
                  │ ├─ 5:00-5:30: Timeline config
                  │ └─ 5:30-6:00: .env documentation
```

**Total Estimated Time**: 6 hours (max estimate)
**Optimistic Time**: 4 hours (if tasks go quickly)

---

## 3-PART LOOP FOR EACH TASK GROUP

### Part 1: Baseline Analysis (15 min per group)
- [ ] Document current state
- [ ] Identify specific changes needed
- [ ] Create implementation checklist

### Part 2: Implementation (varies per group)
- [ ] Make changes according to checklist
- [ ] Add comments and documentation
- [ ] Test as you go

### Part 3: Validation (15 min per group)
- [ ] Run all agents
- [ ] Verify no regressions
- [ ] Check error count = 0
- [ ] Document results

**ERROR RULE**: If error count > 0, STOP, fix once, re-run once, document if still errors

---

## SUCCESS CRITERIA FOR PHASE 2

### Must Have (Required):
- [ ] BaseAgent class created and working
- [ ] All 6 agents inherit from BaseAgent
- [ ] Streaming enabled for all 6 agents
- [ ] No functionality regressions
- [ ] Error count: 0 for all agents

### Should Have (High Priority):
- [ ] Rate limiting implemented
- [ ] Response caching implemented
- [ ] API usage logging implemented

### Nice to Have (Optional):
- [ ] Timeline dates in config (Agent 5)
- [ ] .env.example created

---

## DELIVERABLES

### Code Files:
1. **base_agent.py** (NEW) - Base class for all agents
2. **agent_config.py** (UPDATED) - Add rate limiting, caching config
3. **All 6 agent files** (UPDATED) - Inherit from BaseAgent, enable streaming
4. **timeline_config.py** (NEW - optional) - Timeline configuration
5. **.env.example** (NEW - optional) - Environment variable template

### Documentation:
1. **PHASE_2_BASELINE.md** - Pre-implementation state
2. **PHASE_2_POST_IMPLEMENTATION.md** - Results and validation
3. **PHASE_2_COMPLETE.md** - Final summary
4. **change_log.md** (UPDATED) - Add Phase 2 changes

---

## RISKS & MITIGATION

### Risk 1: Breaking Changes During Refactoring
**Impact**: High
**Probability**: Medium
**Mitigation**:
- Test each agent after refactoring
- Use 3-part loop validation
- Keep error count = 0 rule

### Risk 2: Streaming Introduces New Bugs
**Impact**: Medium
**Probability**: Low
**Mitigation**:
- Test streaming thoroughly
- Add error handling for streaming
- Allow fallback to non-streaming

### Risk 3: Caching Serves Stale Data
**Impact**: Medium
**Probability**: Medium
**Mitigation**:
- Use short cache TTL (5-10 minutes)
- Clear cache option
- Cache per query, not per agent

### Risk 4: Phase 2 Takes Longer Than Expected
**Impact**: Low
**Probability**: Medium
**Mitigation**:
- Prioritize Must Have features
- Make Should Have optional
- Can defer Nice to Have to Phase 3

---

## DEPENDENCIES

**External Dependencies**:
- Agno framework (already installed)
- OpenAI API (working)
- Python 3.x (available)

**Internal Dependencies**:
- Phase 1 must be complete ✅
- All agents working ✅
- agent_config.py exists ✅

**User Dependencies**:
- Environment variables set (for Agent 1) ⚠️
- API keys rotated (recommended) ⚠️

---

## PHASE 2 vs PHASE 1 COMPARISON

| Aspect | Phase 1 | Phase 2 (Planned) |
|--------|---------|-------------------|
| Focus | Safety, Security | Architecture, Performance |
| Duration | 63 min | 4-6 hours |
| Agents Modified | 6 | 6 + 1 new base class |
| New Files | 1 (agent_config) | 2-4 (base, timeline, .env) |
| Code Added | +525 lines | +300-400 lines |
| Code Removed | -166 lines | -200-300 lines (dedup) |
| Complexity | Low-Medium | Medium-High |
| Risk | Low | Medium |

---

## NEXT STEPS AFTER PHASE 2

**Phase 3**: Testing, Monitoring & Production Readiness
- Unit tests for all agents
- Integration tests
- Performance monitoring
- Cost tracking
- Production deployment guide

**Estimated Start**: After Phase 2 complete
**Estimated Duration**: 6-8 hours

---

## APPROVAL CHECKLIST

Before starting Phase 2, confirm:
- [ ] User has reviewed this plan
- [ ] User approves the timeline
- [ ] User approves the scope
- [ ] Environment variables are set (Agent 1)
- [ ] API keys have been rotated (recommended)
- [ ] Phase 1 is committed and pushed ✅
- [ ] Branch is renamed ✅

---

## TIMESTAMPS (To Be Filled During Execution)

**Planning Complete**: 2025-11-16 16:45 UTC
**Approval Received**: _TBD_
**Phase 2 Start**: _TBD_
**Task Group 1 Complete**: _TBD_
**Task Group 2 Complete**: _TBD_
**Task Group 3 Complete**: _TBD_
**Task Group 4 Complete**: _TBD_
**Phase 2 Complete**: _TBD_

---

**END OF PHASE 2 PLAN**

**Status**: ⏸️ Awaiting User Approval
**Next Action**: User reviews and approves plan
**Then**: Begin Task Group 1 (Base Agent Class)
