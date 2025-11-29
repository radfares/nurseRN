# NEW SOURCES IMPLEMENTATION PLAN

**Created**: 2025-11-28
**Status**: Ready for Review
**Target**: Integrate 3 pending research databases

---

## 📊 CURRENT STATUS

**Already Integrated (9/12)**: ✅
1. PubMed (PRIMARY)
2. arXiv (Academic agent only)
3. Semantic Scholar
4. CORE
5. medRxiv
6. DOAJ
7. ClinicalTrials.gov
8. SerpAPI (optional, paid)
9. Exa (disabled for nursing, paid)

**Pending Integration (3/12)**: ❌
1. **CINAHL** - Highest priority, subscription required
2. **Cochrane Library** - High priority, free abstracts
3. **bioRxiv** - Medium priority, free

---

## 🎯 IMPLEMENTATION PLAN

### PHASE 1: Cochrane Library (RECOMMENDED START)

**Why First?**
- Free API access
- High relevance for nursing (evidence-based practice)
- No subscription blockers
- Similar complexity to existing integrations

**Implementation Steps:**

```text
PHASE 0 – REQUIREMENTS & CLARIFICATION
Goal: Integrate Cochrane Library API into Nursing Research Agent

Requirements:
- API Endpoint: https://api.cochrane.org/api-docs/
- Access: Free (abstracts always free, full text may require subscription)
- Output: Systematic reviews and evidence-based practice guidelines
- Agent: Nursing Research Agent (primary), possibly Medical Research Agent
- Integration Pattern: Follow existing safe wrapper pattern with circuit breaker
```

**File Structure:**
```
src/services/api_tools.py
  ├─ create_cochrane_tools_safe()  ← NEW FUNCTION
  └─ CochraneToolsWrapper          ← NEW CLASS (if needed)

agents/nursing_research_agent.py
  └─ Update _create_tools() to include Cochrane
```

**Code Template (Phase 2 - Pseudocode):**
```python
def create_cochrane_tools_safe(required=False, logger=None):
    """
    Create Cochrane Library tools with safe fallback.

    Args:
        required: If True, raise error when unavailable
        logger: Logger instance for status reporting

    Returns:
        CochraneTools instance or None if unavailable
    """
    # PSEUDOCODE:
    # 1. Try to import agno.tools.cochrane (or create custom wrapper)
    # 2. Check if API key needed (probably not for abstracts)
    # 3. Wrap with CircuitProtectedToolWrapper
    # 4. Log status (available/unavailable)
    # 5. Return tool or None
```

**Testing Checklist:**
- [ ] Can search for systematic reviews by keyword
- [ ] Returns properly formatted results (title, authors, abstract, URL)
- [ ] Handles API errors gracefully (circuit breaker activates)
- [ ] Works without API key (for free abstracts)
- [ ] Respects rate limits
- [ ] Edge case: No results found
- [ ] Edge case: Invalid query format
- [ ] Edge case: Network timeout

**Estimated Complexity**: Low-Medium
**Estimated Time**: 2-4 hours
**Dependencies**:
- Agno framework support for Cochrane (check if exists)
- If not: Create custom wrapper using `requests` library

**Success Criteria:**
✅ Nursing Research Agent can search Cochrane
✅ Results include systematic review metadata
✅ Circuit breaker protects against API failures
✅ Unit tests passing (10+ tests)
✅ Integration test with real API call
✅ Documentation updated in CLAUDE.md

---

### PHASE 2: bioRxiv (LOW-HANGING FRUIT)

**Why Second?**
- Uses same API as medRxiv (already integrated!)
- Very low implementation complexity
- Just need to filter for bioRxiv vs medRxiv
- Free, no subscription

**Implementation Steps:**

```text
PHASE 0 – REQUIREMENTS
Goal: Add bioRxiv support alongside existing medRxiv integration

Requirements:
- API: https://api.biorxiv.org/ (SAME as medRxiv)
- Access: Free
- Difference: Server parameter (bioRxiv vs medRxiv)
- Agent: Academic Research Agent (primary), possibly Nursing (for biological nursing topics)
```

**Code Changes Required (Minimal):**
```python
# OPTION 1: Modify existing medRxiv tool to support both
def create_medrxiv_tools_safe(server='medrxiv', required=False, logger=None):
    """
    Create medRxiv/bioRxiv tools.

    Args:
        server: 'medrxiv' or 'biorxiv'
        ...
    """
    # Just add server parameter, API is identical

# OPTION 2: Create separate wrapper (cleaner)
def create_biorxiv_tools_safe(required=False, logger=None):
    """
    Create bioRxiv tools (biological sciences preprints).

    Uses same API as medRxiv, different server parameter.
    """
    return create_medrxiv_tools_safe(server='biorxiv', required=required, logger=logger)
```

**Testing Checklist:**
- [ ] Can search bioRxiv separately from medRxiv
- [ ] Returns biological science papers (not medical)
- [ ] No interference with existing medRxiv searches
- [ ] Academic Research Agent can use both

**Estimated Complexity**: Very Low
**Estimated Time**: 30-60 minutes
**Dependencies**: None (uses existing medRxiv code)

**Success Criteria:**
✅ bioRxiv searches work independently
✅ No breaking changes to medRxiv
✅ Tests cover both bioRxiv and medRxiv
✅ Documentation updated

---

### PHASE 3: CINAHL (HIGHEST VALUE, BLOCKED)

**Why Last?**
- Requires institutional subscription
- Need API credentials from EBSCO/Ovid
- Highest value for nursing research
- Most complex integration

**Blockers:**
❌ **Institutional Access Required**
- Need to contact institution's library
- Request EBSCO API credentials
- May require approval process

**Pre-Implementation Checklist:**
- [ ] Confirm institutional CINAHL subscription exists
- [ ] Contact library for API access
- [ ] Obtain API key/credentials from EBSCO
- [ ] Review EBSCO API documentation
- [ ] Determine rate limits and usage restrictions
- [ ] Get approval for programmatic access

**Implementation Steps (AFTER credentials obtained):**

```text
PHASE 0 – REQUIREMENTS
Goal: Integrate CINAHL via EBSCO API

Requirements:
- API: EBSCOhost API (https://connect.ebsco.com/s/article/EBSCOhost-Integration-Toolkit-API)
- Access: Requires institutional subscription + API credentials
- Environment Variable: CINAHL_API_KEY (or EBSCO_API_KEY)
- Agent: Nursing Research Agent (PRIMARY tool for nursing literature)
```

**Code Template:**
```python
def create_cinahl_tools_safe(required=False, logger=None):
    """
    Create CINAHL tools with safe fallback.

    IMPORTANT: Requires institutional EBSCO subscription.
    Set CINAHL_API_KEY environment variable.

    Args:
        required: If True, raise error when unavailable
        logger: Logger instance

    Returns:
        CINAHLTools instance or None
    """
    # PSEUDOCODE:
    # 1. Check for CINAHL_API_KEY in environment
    # 2. If not found:
    #    - Log warning: "CINAHL requires institutional subscription"
    #    - Return None (graceful degradation)
    # 3. Create EBSCO API wrapper
    # 4. Wrap with CircuitProtectedToolWrapper
    # 5. Return tool
```

**Testing Checklist (when credentials available):**
- [ ] Authentication works with institutional credentials
- [ ] Can search nursing literature
- [ ] Returns full metadata (MeSH terms, full text links, etc.)
- [ ] Respects institutional rate limits
- [ ] Handles authentication errors gracefully
- [ ] Works alongside PubMed without conflicts

**Estimated Complexity**: High
**Estimated Time**: 4-8 hours (after credentials obtained)
**Dependencies**:
- Institutional CINAHL subscription
- EBSCO API credentials
- Possible: Python EBSCO SDK or custom wrapper

**Success Criteria (DEFERRED until credentials available):**
⏸️ Institutional subscription confirmed
⏸️ API credentials obtained
⏸️ Authentication tested
⏸️ Integration working
⏸️ Tests passing

---

## 🗓️ RECOMMENDED IMPLEMENTATION ORDER

### Week 1: Cochrane Library
- **Days 1-2**: API research, design, pseudocode
- **Days 3-4**: Implementation, testing
- **Day 5**: Documentation, review

### Week 2: bioRxiv
- **Day 1**: Quick implementation (modify existing code)
- **Day 2**: Testing, documentation

### Week 3+: CINAHL (when ready)
- **Pending**: Institutional credential acquisition
- **Implementation**: 1 week after credentials obtained

---

## 📋 RESOURCE REQUIREMENTS

### For Cochrane (Phase 1):
- [ ] Review Cochrane API docs: https://api.cochrane.org/api-docs/
- [ ] Check if agno framework has Cochrane support
- [ ] If not: Install `requests` library (already have it)
- [ ] Create test Cochrane account (if needed)

### For bioRxiv (Phase 2):
- [ ] None (uses existing medRxiv API)

### For CINAHL (Phase 3 - BLOCKED):
- [ ] Contact institution library
- [ ] Request EBSCO API access
- [ ] Obtain credentials
- [ ] Review EBSCO integration toolkit

---

## 🧪 TESTING STRATEGY

### Unit Tests (for each source):
```python
# tests/unit/test_cochrane_tools.py (example)
def test_cochrane_tools_creation():
    """Test Cochrane tools can be created."""
    tool = create_cochrane_tools_safe()
    assert tool is not None or tool is None  # Graceful degradation

def test_cochrane_search():
    """Test searching Cochrane Library."""
    # Mock API response
    # Test result parsing
    pass

def test_cochrane_circuit_breaker():
    """Test circuit breaker activates on failures."""
    # Simulate 5 consecutive failures
    # Verify circuit opens
    pass
```

### Integration Tests:
```python
# tests/integration/test_new_sources.py
@pytest.mark.integration
def test_cochrane_real_api():
    """Test real Cochrane API call."""
    # Only run if API available
    # Real search query
    # Verify response format
    pass
```

---

## 📚 DOCUMENTATION UPDATES REQUIRED

### Files to Update:
1. **CLAUDE.md** - Add to "Agent-Specific Details" section
2. **README.md** - Update tool list
3. **AGENT_STATUS.md** - Update capabilities matrix
4. **.env.example** - Add new API key variables (if needed)
5. **IMPLMENTATION_SOURCES.md** - Mark as integrated

### Example Documentation:
```markdown
**Nursing Research Agent** (Agent 1):
- Tools:
  ...
  - CochraneTools (systematic reviews, evidence-based practice) - Free abstracts
  - bioRxivTools (biological sciences preprints) - Free
  - CINAHL Tools (nursing literature) - Requires institutional subscription
```

---

## 🎯 SUCCESS METRICS

**Phase 1 Complete (Cochrane):**
- [ ] Nursing agent can search Cochrane Library
- [ ] Returns systematic review results
- [ ] Test coverage >85%
- [ ] Zero production errors in first week
- [ ] Documented in CLAUDE.md

**Phase 2 Complete (bioRxiv):**
- [ ] Academic agent can search bioRxiv
- [ ] Separate from medRxiv queries
- [ ] Test coverage >85%
- [ ] Documentation updated

**Phase 3 Complete (CINAHL) - FUTURE:**
- [ ] Institutional credentials obtained
- [ ] CINAHL searches working
- [ ] Primary nursing literature tool
- [ ] Test coverage >85%

---

## 🚨 RISK ASSESSMENT

### Cochrane Library:
- **Risk**: API changes or rate limits
- **Mitigation**: Circuit breaker, graceful degradation
- **Severity**: Low

### bioRxiv:
- **Risk**: Conflicts with medRxiv
- **Mitigation**: Separate tool creation, thorough testing
- **Severity**: Very Low

### CINAHL:
- **Risk**: Can't obtain institutional credentials
- **Mitigation**: Continue using PubMed as primary (still excellent)
- **Severity**: Medium (high value but not critical)

---

## 📞 NEXT STEPS - ACTION ITEMS

**For User:**
1. **Review this plan** - Approve implementation order
2. **Decide on Cochrane** - Proceed with Phase 1?
3. **CINAHL Research** - Contact institution library about API access

**For Implementation (after approval):**
1. Start Phase 0 for Cochrane Library
2. Research Cochrane API documentation
3. Design integration following existing patterns
4. Get user approval before Phase 3 (implementation)

---

**END OF PLAN** - Awaiting your review and approval!
