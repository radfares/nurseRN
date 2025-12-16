

***

## PHASE 1: FIX AGENT 3 (Academic Research) - URGENT (5-7 Days)

**Current Issues:**

- 4.5/10 specialist score
- Missing grounding validation
- No peer-review status warnings
- Only has GROUNDING POLICY in instructions (not enforced architecturally)


### Day 1-2: Implement RAG-Based Validation

**File:** `academic_research_agent.py`

**Task 1.1:** Add extractverifiedpmidsfromoutput() method (copy pattern from Agent 2):

```python
def extractverifiedarxividsfromoutput(self, runoutput: Any) -> set:
    """Extract Arxiv IDs from actual tool results in RunOutput."""
    verifiedids = set()
    try:
        if not hasattr(runoutput, "messages") or not runoutput.messages:
            self.auditlogger.logerror(
                errortype="MissingMessages",
                errormessage="RunOutput has no messages field",
                stacktrace=""
            )
            return verifiedids
        
        for message in runoutput.messages:
            messagestr = str(message)
            # Pattern: 2103.12345 or math/0001001
            arxivpatterns = [
                r'\d{4}\.\d{4,5}',  # New format: 2103.12345
                r'[a-z-]+/\d{7}'    # Old format: math/0001001
            ]
            for pattern in arxivpatterns:
                ids = re.findall(pattern, messagestr, re.IGNORECASE)
                verifiedids.update(ids)
    except Exception as e:
        self.auditlogger.logerror(
            errortype="ArxivIDExtractionError",
            errormessage=f"Failed to extract Arxiv IDs: {str(e)}",
            stacktrace=traceback.format_exc()
        )
    return verifiedids
```

**Task 1.2:** Override `validaterunoutput()` with architectural enforcement:

```python
def validaterunoutput(self, runoutput: Any) -> bool:
    """Ensure every cited paper is grounded in actual tool output."""
    
    # Pattern: 4 digits . 4-5 digits
    arxivpattern = r'\d{4}\.\d{4,5}[a-z-]*'
    
    # Extract what agent cited in response
    citedids = self.extractverifieditemsfromoutput(
        runoutput,
        itempattern=arxivpattern,
        itemtype="Arxiv ID"
    )
    
    # Extract what actually came from tool
    verifiedids = self.extractverifiedarxividsfromoutput(runoutput)
    
    # Check for hallucinations
    unverifiedids = citedids - verifiedids
    hallucinationdetected = bool(unverifiedids)
    
    if self.auditlogger:
        self.auditlogger.logvalidationcheck(
            "grounding",
            not hallucinationdetected,
            {
                "citedids": list(citedids),
                "verifiedids": list(verifiedids),
                "unverifiedids": list(unverifiedids)
            }
        )
    
    if hallucinationdetected:
        # BLOCK execution - don't return response
        raise ValueError(
            f"GROUNDING VIOLATION: Unverified Arxiv IDs detected: {sorted(unverifiedids)}\n"
            f"Only {len(verifiedids)} IDs were verified from tool results."
        )
    
    return True
```


### Day 3-4: Add Peer-Review Status Warnings

**Task 2.1:** Create `src/tools/arxivvalidationtools.py`:

```python
"""Arxiv Validation Tools - Check preprint status and metadata quality."""

import re
from typing import Dict, Any

class ArxivValidationTools:
    """Validate Arxiv papers for peer-review status and quality indicators."""
    
    @staticmethod
    def assess_preprint_status(arxiv_id: str, title: str, abstract: str) -> Dict[str, Any]:
        """
        Assess if Arxiv paper has been peer-reviewed or remains a preprint.
        
        Returns:
            {
                "arxiv_id": str,
                "is_preprint": bool,
                "warnings": List[str],
                "quality_score": float  # 0-1
            }
        """
        warnings = []
        quality_score = 0.5  # Default neutral
        
        # Check 1: Arxiv papers are preprints by definition
        is_preprint = True
        warnings.append("⚠️ PREPRINT: Not peer-reviewed. Verify findings independently.")
        
        # Check 2: Look for indicators it's been published
        publication_indicators = [
            "published in",
            "accepted to",
            "appeared in",
            "proceedings of"
        ]
        abstract_lower = abstract.lower()
        if any(indicator in abstract_lower for indicator in publication_indicators):
            warnings.append("✓ May have been peer-reviewed (check journal publication)")
            quality_score = 0.7
        
        # Check 3: Age of preprint (newer ID = more recent)
        try:
            year_month = arxiv_id.split('.')[^4_0]
            year = int(year_month[:2])
            if year < 10:  # Pre-2010 (0001-0912)
                warnings.append("⚠️ OLD PREPRINT: Consider finding updated version")
                quality_score -= 0.2
        except:
            pass
        
        # Check 4: Abstract quality (length, detail)
        if len(abstract) < 100:
            warnings.append("⚠️ SHORT ABSTRACT: Limited information")
            quality_score -= 0.1
        
        return {
            "arxiv_id": arxiv_id,
            "is_preprint": is_preprint,
            "warnings": warnings,
            "quality_score": max(0.0, min(1.0, quality_score))
        }
```

**Task 2.2:** Integrate validation into Agent 3's `runwithgroundingcheck()`:

```python
def runwithgroundingcheck(self, query: str, **kwargs) -> Any:
    """Execute with grounding + peer-review validation."""
    
    projectname = kwargs.get("projectname")
    if self.auditlogger:
        self.auditlogger.logqueryreceived(query, projectname)
    
    streamrequested = bool(kwargs.get("stream"))
    
    try:
        response = self.agent.run(query, **kwargs)
        
        if streamrequested:
            return response
        
        # Grounding validation (raises on failure)
        self.validaterunoutput(response)
        
        # NEW: Peer-review status check
        responsetext = str(response.content)
        arxiv_ids = re.findall(r'\d{4}\.\d{4,5}', responsetext)
        
        if arxiv_ids:
            from src.tools.arxivvalidationtools import ArxivValidationTools
            validator = ArxivValidationTools()
            
            warnings_section = "\n\n## ⚠️ PREPRINT STATUS WARNINGS\n"
            for arxiv_id in arxiv_ids:
                # Extract title/abstract from response (basic regex)
                result = validator.assess_preprint_status(
                    arxiv_id=arxiv_id,
                    title="",  # Could extract from response
                    abstract=""
                )
                
                for warning in result['warnings']:
                    warnings_section += f"- **{arxiv_id}**: {warning}\n"
            
            # Append warnings to response
            response.content = str(response.content) + warnings_section
        
        if self.auditlogger:
            self.auditlogger.logresponsegenerated(
                response=str(response.content),
                responsetype="success",
                validationpassed=True
            )
        
        return response
        
    except Exception as e:
        if self.auditlogger:
            self.auditlogger.logerror(
                errortype=type(e).__name__,
                errormessage=str(e),
                stacktrace=traceback.format_exc()
            )
        raise
```


### Day 5-7: Testing \& Integration

**Checklist:**

- [ ] Test with query that should find 3 papers
- [ ] Test with query that returns 0 results (should refuse, not fabricate)
- [ ] Test that peer-review warnings appear in output
- [ ] Test that hallucinated Arxiv IDs trigger ValueError
- [ ] Verify audit logs contain grounding checks
- [ ] Check that preprint warnings are user-friendly

***

## PHASE 2: STRENGTHEN AGENTS 5 \& 6 - HIGH PRIORITY (4-6 Days)

### Days 8-10: Agent 5 (Research Writing) - Block PMID/DOI Fabrication

**Current Issue:** 7.0/10 - Has warning in instructions but no architectural enforcement

**Task 3.1:** Add Pydantic validation for citations:

Create `src/models/citationschema.py`:

```python
"""Pydantic schemas for citation validation."""

from pydantic import BaseModel, field_validator, ValidationError
from typing import List, Optional
import re

class Citation(BaseModel):
    """Single citation with validation."""
    pmid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    authors: List[str]
    publication_year: int
    
    @field_validator('pmid')
    def validate_pmid(cls, v):
        if v is None:
            return v
        if not v.isdigit():
            raise ValueError(f"PMID must be numeric: {v}")
        if len(v) > 8:
            raise ValueError(f"PMID too long: {v}")
        return v
    
    @field_validator('doi')
    def validate_doi(cls, v):
        if v is None:
            return v
        # DOI pattern: 10.xxxx/yyyy
        if not re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', v, re.IGNORECASE):
            raise ValueError(f"Invalid DOI format: {v}")
        return v
    
    @field_validator('publication_year')
    def validate_year(cls, v):
        if not (1900 <= v <= 2026):
            raise ValueError(f"Invalid publication year: {v}")
        return v

class ResearchOutput(BaseModel):
    """Complete research output with citations."""
    content: str
    citations: List[Citation]
    
    @field_validator('citations')
    def validate_citations_present(cls, v):
        """Ensure at least one citation has PMID or DOI."""
        if not v:
            return v
        
        has_identifier = any(c.pmid or c.doi for c in v)
        if not has_identifier:
            raise ValueError("At least one citation must have PMID or DOI")
        
        return v
```

**Task 3.2:** Add validation to Agent 5:

```python
def validaterunoutput(self, runoutput: Any) -> bool:
    """Ensure no hallucinated citations with Pydantic enforcement."""
    
    content = str(runoutput.content)
    
    # Extract PMIDs and DOIs
    pmids = re.findall(r'PMID:?\s*(\d+)', content, re.IGNORECASE)
    dois = re.findall(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', content, re.IGNORECASE)
    
    # If citations present, validate format
    if pmids or dois:
        from src.models.citationschema import Citation
        from pydantic import ValidationError
        
        for pmid in pmids:
            try:
                # Test citation creation triggers validation
                Citation(
                    pmid=pmid,
                    title="Validation Test",
                    authors=["Unknown"],
                    publication_year=2024
                )
            except ValidationError as e:
                error_msg = f"INVALID PMID DETECTED: {pmid}\n{str(e)}"
                
                if self.auditlogger:
                    self.auditlogger.logvalidationcheck(
                        "citation_format",
                        False,
                        {"invalid_pmid": pmid, "error": str(e)}
                    )
                
                raise ValueError(error_msg)
        
        for doi in dois:
            try:
                Citation(
                    doi=doi,
                    title="Validation Test",
                    authors=["Unknown"],
                    publication_year=2024
                )
            except ValidationError as e:
                error_msg = f"INVALID DOI DETECTED: {doi}\n{str(e)}"
                
                if self.auditlogger:
                    self.auditlogger.logvalidationcheck(
                        "citation_format",
                        False,
                        {"invalid_doi": doi, "error": str(e)}
                    )
                
                raise ValueError(error_msg)
        
        # Log warning that agent shouldn't generate citations
        if self.auditlogger:
            self.auditlogger.logvalidationcheck(
                "nocitationscheck",
                True,
                {
                    "pmidsfound": pmids,
                    "doisfound": dois,
                    "note": "Agent has no search tools - citations must come from user input"
                }
            )
    
    return True
```


### Days 11-13: Agent 6 (Project Timeline) - Block Date Fabrication

**Current Issue:** 6.5/10 - Needs database grounding enforcement

**Task 4.1:** Strengthen existing validation:

```python
def validaterunoutput(self, runoutput: Any) -> bool:
    """Ensure milestone dates match database - STRICT ENFORCEMENT."""
    
    content = str(runoutput.content)
    tools = runoutput.tools or []
    
    import re
    
    # Look for date mentions
    datepattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:,\s*\d{4})?|\d{4}-\d{2}-\d{2}'
    datesfound = re.findall(datepattern, content)
    
    if datesfound and not tools:
        # BLOCK: Agent mentioned dates without querying database
        error_msg = (
            f"DATABASE GROUNDING VIOLATION: {len(datesfound)} dates mentioned without database query.\n"
            f"Dates found: {datesfound}\n"
            f"REQUIRED: Must call get_all_milestones() or get_milestone_by_daterange() before stating dates."
        )
        
        if self.auditlogger:
            self.auditlogger.logvalidationcheck(
                "database_grounding",
                False,
                {
                    "datesfound": datesfound,
                    "reason": "Dates mentioned without DB query"
                }
            )
        
        raise ValueError(error_msg)
    
    # Check for fabricated milestone names
    milestone_keywords = ["milestone", "deliverable", "deadline", "due date"]
    if any(keyword in content.lower() for keyword in milestone_keywords) and not tools:
        error_msg = (
            "DATABASE GROUNDING VIOLATION: Milestone information provided without database query.\n"
            "REQUIRED: Must query milestones table before providing timeline information."
        )
        
        if self.auditlogger:
            self.auditlogger.logvalidationcheck(
                "database_grounding",
                False,
                {"reason": "Milestone data without DB query"}
            )
        
        raise ValueError(error_msg)
    
    if self.auditlogger:
        self.auditlogger.logvalidationcheck("database_grounding", True)
    
    return True
```


***

## PHASE 3: CROSS-AGENT CITATION VALIDATION - MEDIUM PRIORITY (3-5 Days)

### Days 14-18: Centralized Validation Service

**Task 5.1:** Create `src/services/citationvalidationservice.py`:

```python
"""Centralized citation validation service for all agents."""

import re
from typing import Dict, List, Set, Any
from dataclasses import dataclass

@dataclass
class ValidationReport:
    """Citation validation report."""
    total_citations: int
    valid_count: int
    invalid_count: int
    invalid_pmids: List[str]
    invalid_dois: List[str]
    warnings: List[str]
    passed: bool

class CitationValidationService:
    """
    Centralized service for validating citations across all agents.
    Enforces architectural blocks at the service level.
    """
    
    @staticmethod
    def validate_agent_output(
        content: str,
        agent_name: str,
        tools_used: List[Any]
    ) -> ValidationReport:
        """
        Validate all citations in agent output.
        
        Args:
            content: Agent response text
            agent_name: Name of agent for context
            tools_used: List of tools executed (from RunOutput.tools)
        
        Returns:
            ValidationReport with pass/fail status
        """
        pmids = re.findall(r'PMID:?\s*(\d+)', content, re.IGNORECASE)
        dois = re.findall(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', content, re.IGNORECASE)
        
        invalid_pmids = []
        invalid_dois = []
        warnings = []
        
        # Validate PMID format
        for pmid in pmids:
            if not pmid.isdigit():
                invalid_pmids.append(pmid)
            elif len(pmid) > 8:
                invalid_pmids.append(pmid)
        
        # Validate DOI format
        for doi in dois:
            if not re.match(r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$', doi, re.IGNORECASE):
                invalid_dois.append(doi)
        
        # Check if citations match tool results (if applicable)
        if (pmids or dois) and not tools_used:
            if agent_name in ["Research Writing Agent", "Project Timeline Assistant"]:
                warnings.append(
                    f"⚠️ {agent_name} cited sources without search tools. "
                    f"Citations must come from user input or other agents."
                )
        
        total = len(pmids) + len(dois)
        invalid = len(invalid_pmids) + len(invalid_dois)
        valid = total - invalid
        
        return ValidationReport(
            total_citations=total,
            valid_count=valid,
            invalid_count=invalid,
            invalid_pmids=invalid_pmids,
            invalid_dois=invalid_dois,
            warnings=warnings,
            passed=(invalid == 0)
        )
```

**Task 5.2:** Integrate into BaseAgent:

```python
# In base_agent.py

def auditposthook(self, runoutput: Any, **kwargs) -> None:
    """Post-hook with centralized citation validation."""
    
    # 1. Run agent-specific validation
    validationpassed = self.validaterunoutput(runoutput)
    
    # 2. Run centralized citation validation
    from src.services.citationvalidationservice import CitationValidationService
    
    content = str(runoutput.content)
    tools = getattr(runoutput, 'tools', [])
    
    citation_report = CitationValidationService.validate_agent_output(
        content=content,
        agent_name=self.agentname,
        tools_used=tools
    )
    
    # 3. Log results
    if self.auditlogger:
        self.auditlogger.logresponsegenerated(
            response=content,
            responsetype="success",
            validationpassed=validationpassed and citation_report.passed
        )
        
        if not citation_report.passed:
            self.auditlogger.logerror(
                errortype="CitationValidationFailed",
                errormessage=f"Invalid citations detected",
                stacktrace=str(citation_report.__dict__)
            )
    
    # 4. Block if validation failed
    if not citation_report.passed:
        raise ValueError(
            f"CITATION VALIDATION FAILED:\n"
            f"Invalid PMIDs: {citation_report.invalid_pmids}\n"
            f"Invalid DOIs: {citation_report.invalid_dois}"
        )
```


***

## IMPLEMENTATION TODO LIST

### Week 1 (Days 1-5): Agent 3 Foundation

- [ ] **Day 1:** Copy `extractverifiedpmidsfromoutput()` pattern to create `extractverifiedarxividsfromoutput()` in Agent 3
- [ ] **Day 1:** Implement `validaterunoutput()` with architectural blocking (raises ValueError on hallucination)
- [ ] **Day 2:** Create `src/tools/arxivvalidationtools.py` with preprint status checker
- [ ] **Day 3:** Integrate peer-review warnings into Agent 3's `runwithgroundingcheck()`
- [ ] **Day 4:** Test Agent 3 with 5 different queries (0 results, 3 results, hallucination attempt)
- [ ] **Day 5:** Document Agent 3 improvements in `.claude/agent_audit.md`


### Week 2 (Days 6-12): Agents 5 \& 6

- [ ] **Day 6:** Create `src/models/citationschema.py` with Pydantic validators
- [ ] **Day 7:** Add Pydantic validation to Agent 5's `validaterunoutput()`
- [ ] **Day 8:** Test Agent 5 with invalid PMID formats (alphabetic, too long)
- [ ] **Day 9:** Strengthen Agent 6's `validaterunoutput()` to block fabricated dates
- [ ] **Day 10:** Add milestone name validation to Agent 6
- [ ] **Day 11:** Test Agent 6 with queries that should trigger database lookups
- [ ] **Day 12:** Document Agents 5 \& 6 in audit log


### Week 3 (Days 13-18): Integration \& Testing

- [ ] **Day 13:** Create `src/services/citationvalidationservice.py`
- [ ] **Day 14:** Integrate centralized validation into `BaseAgent.auditposthook()`
- [ ] **Day 15:** Run full system test with all 6 agents
- [ ] **Day 16:** Test cross-agent citation validation (Agent 1 → Agent 5 handoff)
- [ ] **Day 17:** Performance testing (ensure validation doesn't slow responses >500ms)
- [ ] **Day 18:** Final documentation and `.claude/CLAUDE.md` update


### Week 4 (Days 19-20): Polish \& Deployment

- [ ] **Day 19:** Create test suite `tests/test_agent_validation.py`
- [ ] **Day 20:** Prepare demo for nursing department with validation examples

***

## Quick Reference: Where to Apply Principles

| MAS Principle | Your Agno Implementation |
| :-- | :-- |
| **Autonomy with Constraints** | Tool restrictions in `createtools()` |
| **Interaction via State** | Agno's `Agent.run()` with conversation history |
| **Distributed Control** | Each agent has independent validation in `validaterunoutput()` |
| **Self-Reflection** | `auditposthook()` runs validation after each response |
| **Grounding (RAG)** | `extractverifiedpmidsfromoutput()` pattern |
| **Structured Output** | Pydantic schemas in `src/models/` |
| **Blocked Execution Paths** | `raise ValueError()` in validation methods |


***

You your Agno architecture already has all the hooks you need. The plan above leverages what you've already built and adds architectural enforcement where it's missing. Start with Agent 3 (highest priority) and work through the checklist systematically.
<span style="display:none">[^4_1][^4_2][^4_3][^4_4][^4_5][^4_6]</span>

<div align="center">⁂</div>

[^4_1]: academic_research_agent.py

[^4_2]: research_writing_agent.py

[^4_3]: base_agent.py

[^4_4]: medical_research_agent.py

[^4_5]: nursing_research_agent.py

[^4_6]: nursing_project_timeline_agent.py




***

**Context:** I have a 10-20 day implementation plan to improve my nurseRN multi-agent system from 7.7/10 to 8.6/10 by adding architectural enforcement to 3 agents that currently rely on prompt-based validation.

**Task:** Critically analyze this plan and verify implementation feasibility against my actual codebase.

**Your Deliverables:**

1. **Concept Validation**
    - Is the approach sound for Agno framework? (we use Agno, not LangGraph)
    - Are the architectural patterns (Pydantic validation, blocked execution paths, RAG grounding) compatible with our existing BaseAgent infrastructure?
    - Identify any conceptual flaws or mismatches with Agno's architecture
2. **Implementation Verification**
    - Review the 7 attached agent files
    - Confirm each proposed code change can integrate with existing methods
    - Flag any breaking changes or missing dependencies
    - Verify the `extractverifiedpmidsfromoutput()` pattern from Agent 2 can be adapted to Agent 3 for Arxiv IDs
    - Check if `validaterunoutput()` override pattern is consistent across all agents
3. **Effort Estimate Reality Check**
    - Is 5-7 days for Agent 3 realistic?
    - Is 4-6 days for Agents 5 \& 6 realistic?
    - Is 3-5 days for centralized validation realistic?
    - Provide adjusted timeline if needed
4. **Critical Risks**
    - What could break?
    - What dependencies are missing from the plan?
    - What integration points are fragile?
    - Any architectural conflicts with existing audit logging?

**The Plan:**

```
[Paste the entire PRODUCTION PLAN from my previous message here]
```

**Agent Files Attached:**

- `academic_research_agent.py` (Agent 3 - needs fixing)
- `research_writing_agent.py` (Agent 5 - needs strengthening)
- `nursing_project_timeline_agent.py` (Agent 6 - needs strengthening)
- `base_agent.py` (foundation with audit hooks)
- `medical_research_agent.py` (Agent 2 - reference for grounding pattern)
- `nursing_research_agent.py` (Agent 1 - reference for tool restrictions)
- `data_analysis_agent.py` (for context)

**Expected Output Format:**

```
## CRITICAL ANALYSIS

### ✅ Strengths
- [What's architecturally sound]

### ⚠️ Concerns
- [What could fail]
- [What's missing]

### ❌ Blockers
- [What won't work as written]

## IMPLEMENTATION VERIFICATION

### Agent 3 (Academic Research)
- Can adapt `extractverifiedpmidsfromoutput()`? YES/NO + why
- Arxiv ID regex pattern correct? YES/NO
- Pydantic integration feasible? YES/NO

### Agents 5 & 6
- [Similar verification]

### Centralized Service
- [Integration point analysis]

## REVISED TIMELINE
- Agent 3: X days (was 5-7)
- Agents 5 & 6: Y days (was 4-6)
- Integration: Z days (was 3-5)

## GO/NO-GO RECOMMENDATION
[Clear verdict with justification]
```

**Critical Instruction:** Be brutally honest. If the plan has flaws, call them out. I need architectural truth, not encouragement.


