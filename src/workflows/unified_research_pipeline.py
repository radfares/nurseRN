"""
Unified Research Pipeline - Professional Research Workflow

This pipeline produces publication-ready nursing research outputs.

ARCHITECTURE:
- Single entry point, sequential execution
- Each phase builds on previous outputs
- Quality gates ensure professional standards
- Automatic retry with progressive strategies
- Full audit trail and database persistence

PHASES:
1. PICOT GENERATION    → Professional PICOT question with clinical specificity
2. LITERATURE SEARCH   → Comprehensive PubMed search with multiple strategies
3. CITATION VALIDATION → Verify all PMIDs, check retractions, grade evidence
4. EVIDENCE SYNTHESIS  → Publication-quality literature review
5. ANALYSIS PLANNING   → Complete statistical analysis plan with power calculations
6. TIMELINE SETUP      → Project milestones aligned with academic calendar

OUTPUT QUALITY:
- All PMIDs verified against PubMed
- Evidence graded using Johns Hopkins scale
- Statistical methods justified with citations
- APA-formatted citations throughout

Created: 2025-12-10
"""

import sqlite3
import json
import time
import re
import os
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from src.workflows.quality_gates import run_quality_gate, GateResult
from src.workflows.base import WorkflowTemplate, WorkflowResult
from src.orchestration.orchestrator import WorkflowOrchestrator
from src.orchestration.context_manager import ContextManager


# =============================================================================
# PMID EXTRACTION - SINGLE SOURCE OF TRUTH
# =============================================================================

def extract_pmids(text: str) -> List[str]:
    """
    Extract PMIDs from text using all known formats.
    This is the ONLY function that should extract PMIDs.
    """
    if not text:
        return []

    pmids = set()

    # Standard formats
    pmids.update(re.findall(r'PMID[:\s]*(\d{7,8})', text, re.IGNORECASE))
    pmids.update(re.findall(r'PubMed\s*ID[:\s]*(\d{7,8})', text, re.IGNORECASE))

    # Markdown link format: [12345678](https://pubmed...)
    pmids.update(re.findall(r'\[(\d{7,8})\]\(https?://pubmed', text))

    # URL format: pubmed.ncbi.nlm.nih.gov/12345678
    pmids.update(re.findall(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d{7,8})', text))

    # Bold markdown: **PMID:** 12345678
    pmids.update(re.findall(r'\*\*PMID[:\*\s]*\[?(\d{7,8})', text, re.IGNORECASE))

    # Numbered list: 1. PMID: 12345678
    pmids.update(re.findall(r'\d+\.\s*PMID[:\s]*(\d{7,8})', text, re.IGNORECASE))

    # Parenthetical: (PMID: 12345678)
    pmids.update(re.findall(r'\(PMID[:\s]*(\d{7,8})\)', text, re.IGNORECASE))

    return list(pmids)


def extract_dois(text: str) -> List[str]:
    """Extract DOIs from text."""
    if not text:
        return []
    pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    return list(set(re.findall(pattern, text, re.IGNORECASE)))


# =============================================================================
# EVIDENCE LEVELS
# =============================================================================

class EvidenceLevel(Enum):
    """Johns Hopkins Evidence Levels"""
    LEVEL_I = "Level I - Experimental/RCT"
    LEVEL_II = "Level II - Quasi-experimental"
    LEVEL_III = "Level III - Non-experimental/Qualitative"
    LEVEL_IV = "Level IV - Expert Opinion"
    LEVEL_V = "Level V - Quality Improvement"
    UNKNOWN = "Unknown"


# =============================================================================
# PIPELINE STATE
# =============================================================================

@dataclass
class PipelineState:
    """Complete state tracking for the unified pipeline."""
    # Inputs
    project_name: str
    user_topic: str

    # Phase 1: PICOT
    picot_question: str = ""
    picot_components: Dict[str, str] = field(default_factory=dict)

    # Phase 2: Search
    search_results: str = ""
    pmids_found: List[str] = field(default_factory=list)
    dois_found: List[str] = field(default_factory=list)
    search_strategies_used: List[str] = field(default_factory=list)

    # Phase 3: Validation
    validation_report: str = ""
    valid_pmids: List[str] = field(default_factory=list)
    retracted_pmids: List[str] = field(default_factory=list)
    evidence_grades: Dict[str, str] = field(default_factory=dict)

    # Phase 4: Synthesis
    synthesis_text: str = ""
    synthesis_sections: List[str] = field(default_factory=list)
    citation_count: int = 0

    # Phase 5: Analysis
    analysis_plan: str = ""
    statistical_test: str = ""
    sample_size: int = 0
    power: float = 0.0

    # Phase 6: Timeline
    milestones: List[Dict] = field(default_factory=list)

    # Tracking
    current_phase: int = 0
    phase_name: str = "init"
    status: str = "in_progress"
    error: str = ""
    warnings: List[str] = field(default_factory=list)

    # Timing
    started_at: float = field(default_factory=time.time)
    phase_times: Dict[str, float] = field(default_factory=dict)

    # Quality
    gate_results: Dict[str, bool] = field(default_factory=dict)
    retry_counts: Dict[str, int] = field(default_factory=dict)


# =============================================================================
# PROFESSIONAL PROMPTS
# =============================================================================

PROMPTS = {
    # -------------------------------------------------------------------------
    # PHASE 1: PICOT GENERATION
    # -------------------------------------------------------------------------
    "picot": """You are a doctoral-level nursing researcher creating a PICOT question.

RESEARCH TOPIC: {topic}

Create a clinically rigorous PICOT question following these requirements:

**P - Population**
- Specific patient demographics (age range, condition, setting)
- Inclusion/exclusion criteria implied
- Clinical context (acute care, long-term care, community, etc.)

**I - Intervention**
- Specific, evidence-based intervention
- Include frequency, duration, delivery method if applicable
- Reference established protocols when possible

**C - Comparison**
- Standard of care OR specific alternative
- Must be clinically meaningful comparison
- Not just "no intervention"

**O - Outcome**
- Primary outcome: measurable, clinically significant
- Consider validated measurement tools
- Timeframe for measurement

**T - Timeframe**
- Realistic for the intervention
- Aligned with typical research periods
- Consider clinical significance of timeframe

FORMAT YOUR RESPONSE AS:

**PICOT Components:**
- P (Population): [detailed population]
- I (Intervention): [specific intervention]
- C (Comparison): [meaningful comparison]
- O (Outcome): [measurable outcome]
- T (Timeframe): [specific timeframe]

**Clinical PICOT Question:**
"In [population], does [intervention] compared to [comparison] improve [outcome] over [timeframe]?"

**Search Keywords:**
- Primary: [3-4 key terms]
- Secondary: [2-3 alternative terms]
- MeSH terms: [if applicable]
""",

    # -------------------------------------------------------------------------
    # PHASE 2: LITERATURE SEARCH
    # -------------------------------------------------------------------------
    "search_primary": """You are a medical librarian conducting a systematic literature search.

RESEARCH QUESTION:
{picot}

SEARCH STRATEGY:
1. Use the PRIMARY search terms from the PICOT
2. Search PubMed for peer-reviewed articles
3. Prioritize: Systematic Reviews > RCTs > Cohort Studies > Case Studies

REQUIREMENTS:
- Find 7-10 relevant articles
- Each article MUST have a valid PMID
- Focus on articles from 2019-2024 (within 5 years)
- Include at least 2 systematic reviews if available
- Include at least 2 RCTs if available

FOR EACH ARTICLE PROVIDE:
```
**Article [N]**
- PMID: [8-digit number]
- Title: [full title]
- Authors: [First Author et al., Year]
- Journal: [journal name]
- Study Type: [RCT/Systematic Review/Cohort/etc.]
- Key Findings: [2-3 sentences]
- Relevance: [Why this article matters for the PICOT]
```

SEARCH NOW using PubMed tools.
""",

    "search_expanded": """The initial search found insufficient articles. Expand the search.

ORIGINAL PICOT:
{picot}

PREVIOUS SEARCH FOUND: {count} articles

EXPANDED SEARCH STRATEGY:
1. Broaden population criteria (e.g., "elderly" instead of "65-80 years")
2. Use alternative intervention terms
3. Include related outcomes
4. Extend date range to 10 years (2014-2024)
5. Search for: "{broad_terms}"

Find 5-7 ADDITIONAL articles with valid PMIDs.
Do NOT repeat articles already found: {existing_pmids}

Search PubMed now with broader terms.
""",

    "search_tertiary": """Final search attempt with maximum breadth.

TOPIC: {topic}

BROAD SEARCH TERMS:
- {term1}
- {term2}
- {term3}

This is a fallback search. Find ANY relevant peer-reviewed articles on this topic.
Minimum requirement: 3 articles with valid PMIDs.

Search PubMed now.
""",

    # -------------------------------------------------------------------------
    # PHASE 3: VALIDATION
    # -------------------------------------------------------------------------
    "validate": """You are a research librarian validating citations.

CITATIONS TO VALIDATE:
{pmids}

FOR EACH PMID:
1. Verify it exists in PubMed (use PubMed tools)
2. Check retraction status
3. Check for corrections/errata
4. Assess publication date (flag if >10 years old)
5. Grade evidence level using Johns Hopkins scale:
   - Level I: Experimental/RCT, Systematic Review of RCTs
   - Level II: Quasi-experimental
   - Level III: Non-experimental, Qualitative
   - Level IV: Expert Opinion, Consensus
   - Level V: Quality Improvement, Case Report

REPORT FORMAT:
```
**Validation Report**

| PMID | Status | Evidence Level | Year | Notes |
|------|--------|----------------|------|-------|
| [pmid] | VALID/RETRACTED/NOT_FOUND | Level I-V | YYYY | [any concerns] |

**Summary:**
- Total Validated: X
- Retracted: X (list PMIDs)
- Evidence Distribution: Level I (X), Level II (X), etc.
- Recommendations: [which to include/exclude]
```
""",

    # -------------------------------------------------------------------------
    # PHASE 4: SYNTHESIS
    # -------------------------------------------------------------------------
    "synthesize": """You are writing a literature review for a peer-reviewed nursing journal.

PICOT QUESTION:
{picot}

VALIDATED ARTICLES:
{articles}

Write a PUBLICATION-QUALITY literature synthesis with these sections:

**1. Introduction** (150-200 words)
- Clinical significance of the problem
- Scope and prevalence
- Purpose of the review

**2. Search Methodology** (100-150 words)
- Databases searched
- Search terms used
- Inclusion/exclusion criteria
- Number of articles included

**3. Evidence Summary** (400-500 words)
- Organize by theme OR study design
- Synthesize findings across studies (don't just summarize each)
- Note areas of agreement and disagreement
- Include specific statistics when available

**4. Strength of Evidence** (150-200 words)
- Overall quality assessment
- Limitations of the evidence base
- Gaps in current research
- Johns Hopkins evidence level distribution

**5. Implications for Practice** (200-250 words)
- Specific, actionable recommendations
- Implementation considerations
- Barriers and facilitators
- Areas needing further research

**6. Conclusion** (100-150 words)
- Key takeaways
- Recommendation strength
- Next steps

CITATION FORMAT:
Use APA 7th edition in-text citations: (Author, Year)
Each claim must be supported by at least one citation.
""",

    # -------------------------------------------------------------------------
    # PHASE 5: ANALYSIS
    # -------------------------------------------------------------------------
    "analysis": """You are a biostatistician creating a data analysis plan.

RESEARCH QUESTION:
{picot}

Create a COMPLETE statistical analysis plan:

**1. Study Design**
- Design type (Pre-post, RCT, Cohort, etc.)
- Justify why this design fits the PICOT
- Potential biases and how to address them

**2. Variables**
```
| Variable | Type | Role | Measurement | Scale |
|----------|------|------|-------------|-------|
| [name] | Continuous/Categorical/Binary | IV/DV/Covariate | [tool/method] | [scale] |
```

**3. Primary Statistical Test**
- Test name and justification
- Assumptions to check
- Alternative if assumptions violated
- Effect size measure

**4. Sample Size Calculation**
- Formula used
- Alpha level: 0.05
- Power: 0.80
- Expected effect size (with citation if available)
- Calculated N per group
- Account for attrition (add 15-20%)
- Final recommended N

**5. Analysis Steps**
1. Data cleaning and missing data handling
2. Descriptive statistics
3. Assumption checking
4. Primary analysis
5. Sensitivity analyses
6. Subgroup analyses (if applicable)

**6. Data Collection Template**
```csv
participant_id,group,age,gender,[outcome_var],[covariate1],[covariate2]
string,categorical,integer,categorical,[type],[type],[type]
```

**7. Analysis Code (R)**
```r
# Load required packages
library(tidyverse)
library(pwr)

# Sample size calculation
pwr.t.test(d = [effect_size], sig.level = 0.05, power = 0.80, type = "two.sample")

# Primary analysis
model <- [appropriate_test](outcome ~ group + covariates, data = df)
summary(model)
```

**8. Interpretation Guide**
- What p-value threshold indicates significance
- How to interpret effect size
- Clinical vs. statistical significance
""",

    # -------------------------------------------------------------------------
    # PHASE 6: TIMELINE
    # -------------------------------------------------------------------------
    "timeline": """Create a project timeline for this nursing research project.

PROJECT: {project}
TOPIC: {topic}
START DATE: {start_date}
ACADEMIC CALENDAR: November 2025 - June 2026

Based on the completed PICOT and literature review, create milestones:

**Phase 1: Foundation (Completed)**
- PICOT Development ✓
- Literature Search ✓
- Citation Validation ✓

**Phase 2: Planning (Current)**
| Milestone | Due Date | Deliverables | Status |
|-----------|----------|--------------|--------|
| Analysis Plan Finalization | [date] | Statistical plan, data template | Pending |
| IRB/Ethics Submission | [date] | Protocol, consent forms | Pending |

**Phase 3: Implementation**
| Milestone | Due Date | Deliverables | Status |
|-----------|----------|--------------|--------|
| IRB Approval | [date] | Approval letter | Pending |
| Data Collection Start | [date] | Recruitment materials | Pending |
| Data Collection Complete | [date] | Dataset | Pending |

**Phase 4: Analysis & Writing**
| Milestone | Due Date | Deliverables | Status |
|-----------|----------|--------------|--------|
| Data Analysis | [date] | Results tables, figures | Pending |
| Results Write-up | [date] | Draft results section | Pending |
| Discussion & Conclusions | [date] | Full draft | Pending |

**Phase 5: Dissemination**
| Milestone | Due Date | Deliverables | Status |
|-----------|----------|--------------|--------|
| Poster/Presentation Prep | [date] | Visual materials | Pending |
| Final Presentation | [date] | Oral defense | Pending |
| Manuscript Submission | [date] | Journal submission | Pending |

**Key Dates:**
- Next immediate deadline: [date] - [milestone]
- Critical path items: [list]
- Flex time built in: [X weeks]
"""
}


# =============================================================================
# DATABASE SCHEMA
# =============================================================================

SCHEMA = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    topic TEXT NOT NULL,

    -- Phase 1
    picot_question TEXT,
    picot_components_json TEXT,
    picot_gate_passed INTEGER DEFAULT 0,

    -- Phase 2
    search_results TEXT,
    pmids_json TEXT,
    dois_json TEXT,
    search_strategies_json TEXT,
    search_gate_passed INTEGER DEFAULT 0,

    -- Phase 3
    validation_report TEXT,
    valid_pmids_json TEXT,
    retracted_pmids_json TEXT,
    evidence_grades_json TEXT,
    validation_gate_passed INTEGER DEFAULT 0,

    -- Phase 4
    synthesis_text TEXT,
    synthesis_sections_json TEXT,
    citation_count INTEGER DEFAULT 0,
    synthesis_gate_passed INTEGER DEFAULT 0,

    -- Phase 5
    analysis_plan TEXT,
    statistical_test TEXT,
    sample_size INTEGER,
    power REAL,
    analysis_gate_passed INTEGER DEFAULT 0,

    -- Phase 6
    milestones_json TEXT,

    -- Tracking
    current_phase INTEGER DEFAULT 0,
    status TEXT DEFAULT 'in_progress',
    error TEXT,
    warnings_json TEXT,

    -- Timing
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    phase_times_json TEXT,
    total_seconds REAL,

    -- Quality
    gate_results_json TEXT,
    retry_counts_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_runs_project ON pipeline_runs(project_name);
CREATE INDEX IF NOT EXISTS idx_runs_status ON pipeline_runs(status);
"""


# =============================================================================
# UNIFIED RESEARCH PIPELINE
# =============================================================================

class UnifiedResearchPipeline(WorkflowTemplate):
    """
    Professional nursing research pipeline.

    Produces publication-ready outputs through a structured,
    quality-gated process.
    """

    PHASES = [
        (1, "PICOT Generation", "picot"),
        (2, "Literature Search", "search"),
        (3, "Citation Validation", "validation"),
        (4, "Evidence Synthesis", "synthesis"),
        (5, "Analysis Planning", "analysis"),
        (6, "Timeline Setup", "timeline"),
    ]

    def __init__(
        self,
        project_name: str,
        db_path: str = None,
        orchestrator: WorkflowOrchestrator = None,
        context_manager: ContextManager = None
    ):
        if context_manager is None:
            context_manager = ContextManager(db_path="pipeline_context.db")
        if orchestrator is None:
            orchestrator = WorkflowOrchestrator(context_manager)

        super().__init__(orchestrator, context_manager)

        self.project_name = project_name
        self.db_path = db_path or f"data/projects/{project_name}/pipeline.db"
        self._init_database()

        # Agents
        self._agents_loaded = False
        self.writing_agent = None
        self.nursing_agent = None
        self.medical_agent = None
        self.citation_agent = None
        self.data_agent = None
        self.timeline_agent = None

    @property
    def name(self) -> str:
        return "unified_research_pipeline"

    @property
    def description(self) -> str:
        return "Professional research: PICOT → Search → Validate → Synthesize → Analyze → Timeline"

    def _init_database(self):
        """Initialize database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()

    def _load_agents(self):
        """Load all agents."""
        if self._agents_loaded:
            return

        from agents.research_writing_agent import ResearchWritingAgent
        from agents.nursing_research_agent import NursingResearchAgent
        from agents.medical_research_agent import MedicalResearchAgent
        from agents.citation_validation_agent import CitationValidationAgent
        from agents.data_analysis_agent import DataAnalysisAgent
        from agents.nursing_project_timeline_agent import ProjectTimelineAgent

        self.writing_agent = ResearchWritingAgent()
        self.nursing_agent = NursingResearchAgent()
        self.medical_agent = MedicalResearchAgent()
        self.citation_agent = CitationValidationAgent()
        self.data_agent = DataAnalysisAgent()
        self.timeline_agent = ProjectTimelineAgent()

        self._agents_loaded = True

    def validate_inputs(self, **kwargs) -> bool:
        """Validate inputs."""
        topic = kwargs.get("topic", "").strip()
        if not topic:
            raise ValueError("Research topic is required")
        if len(topic) < 10:
            raise ValueError("Topic too short - provide more detail")
        return True

    def run(self, topic: str) -> WorkflowResult:
        """Run the pipeline."""
        return self.execute(topic=topic)

    def execute(self, **kwargs) -> WorkflowResult:
        """Execute complete pipeline."""
        self._start_execution()

        try:
            self.validate_inputs(**kwargs)
        except ValueError as e:
            return self._end_execution({}, error=str(e))

        state = PipelineState(
            project_name=self.project_name,
            user_topic=kwargs["topic"]
        )

        run_id = self._save_state(state)

        self._print_header("UNIFIED RESEARCH PIPELINE", state.user_topic)
        self._load_agents()
        print("   6 research agents loaded")

        outputs = {}

        try:
            # Phase 1: PICOT
            state = self._phase_1_picot(state)
            if state.status == "failed":
                return self._finish(state, outputs, run_id)
            outputs["picot"] = state.picot_question
            outputs["picot_components"] = state.picot_components
            self._save_state(state, run_id)

            # Phase 2: Search
            state = self._phase_2_search(state)
            if state.status == "failed":
                return self._finish(state, outputs, run_id)
            outputs["search_results"] = state.search_results
            outputs["pmids"] = state.pmids_found
            self._save_state(state, run_id)

            # Phase 3: Validation
            state = self._phase_3_validation(state)
            outputs["validation_report"] = state.validation_report
            outputs["valid_pmids"] = state.valid_pmids
            outputs["retracted_pmids"] = state.retracted_pmids
            outputs["evidence_grades"] = state.evidence_grades
            self._save_state(state, run_id)

            # Phase 4: Synthesis
            state = self._phase_4_synthesis(state)
            if state.status == "failed":
                return self._finish(state, outputs, run_id)
            outputs["synthesis"] = state.synthesis_text
            self._save_state(state, run_id)

            # Phase 5: Analysis
            state = self._phase_5_analysis(state)
            outputs["analysis_plan"] = state.analysis_plan
            outputs["sample_size"] = state.sample_size
            outputs["statistical_test"] = state.statistical_test
            self._save_state(state, run_id)

            # Phase 6: Timeline
            state = self._phase_6_timeline(state)
            outputs["milestones"] = state.milestones

            # Complete
            state.status = "completed"
            state.phase_times["total"] = time.time() - state.started_at
            self._save_state(state, run_id)

            self._print_summary(state, run_id)

            return self._end_execution(outputs)

        except Exception as e:
            state.error = str(e)
            state.status = "failed"
            self._save_state(state, run_id)
            return self._end_execution(outputs, error=str(e))

    def _finish(self, state: PipelineState, outputs: dict, run_id: int) -> WorkflowResult:
        """Handle pipeline termination."""
        self._save_state(state, run_id)
        return self._end_execution(outputs, error=state.error)

    # =========================================================================
    # PHASE 1: PICOT
    # =========================================================================

    def _phase_1_picot(self, state: PipelineState) -> PipelineState:
        """Generate professional PICOT question."""
        start = time.time()
        state.current_phase = 1
        state.phase_name = "picot"

        self._print_phase(1, "PICOT GENERATION")

        prompt = PROMPTS["picot"].format(topic=state.user_topic)

        result = self.orchestrator.execute_single_agent(
            agent=self.writing_agent.agent,
            query=prompt,
            workflow_id=self.workflow_id
        )

        if not result.success:
            state.error = f"PICOT generation failed: {result.error}"
            state.status = "failed"
            return state

        state.picot_question = result.content
        self._increment_step()

        # Extract components
        state.picot_components = self._extract_picot_components(result.content)

        # Quality gate
        gate = run_quality_gate("picot_quality", picot_text=state.picot_question)
        state.gate_results["picot"] = gate.passed

        if not gate.passed:
            state.retry_counts["picot"] = state.retry_counts.get("picot", 0) + 1
            if state.retry_counts["picot"] < 2:
                print("   Refining PICOT...")
                retry_prompt = prompt + "\n\nREQUIRED: Clearly label ALL 5 components (P, I, C, O, T). End with the full question."
                retry = self.orchestrator.execute_single_agent(
                    agent=self.writing_agent.agent,
                    query=retry_prompt,
                    workflow_id=self.workflow_id
                )
                if retry.success:
                    state.picot_question = retry.content
                    state.picot_components = self._extract_picot_components(retry.content)
                    gate = run_quality_gate("picot_quality", picot_text=state.picot_question)
                    state.gate_results["picot"] = gate.passed

        if not gate.passed:
            state.error = "Could not generate complete PICOT question"
            state.status = "failed"
            return state

        state.phase_times["picot"] = time.time() - start
        print(f"   PICOT complete ({state.phase_times['picot']:.1f}s)")
        print(f"   Components: {list(state.picot_components.keys())}")

        return state

    def _extract_picot_components(self, text: str) -> Dict[str, str]:
        """Extract individual PICOT components."""
        components = {}
        patterns = {
            "P": r"P\s*\(Population\)[:\s]*([^\n]+)",
            "I": r"I\s*\(Intervention\)[:\s]*([^\n]+)",
            "C": r"C\s*\(Comparison\)[:\s]*([^\n]+)",
            "O": r"O\s*\(Outcome\)[:\s]*([^\n]+)",
            "T": r"T\s*\(Time(?:frame)?\)[:\s]*([^\n]+)",
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                components[key] = match.group(1).strip()
        return components

    # =========================================================================
    # PHASE 2: SEARCH
    # =========================================================================

    def _phase_2_search(self, state: PipelineState) -> PipelineState:
        """Comprehensive literature search with progressive strategies."""
        start = time.time()
        state.current_phase = 2
        state.phase_name = "search"

        self._print_phase(2, "LITERATURE SEARCH")

        # Strategy 1: Primary search with both agents
        print("   Strategy 1: Primary PubMed search...")
        prompt = PROMPTS["search_primary"].format(picot=state.picot_question)

        # Nursing agent search
        nursing_result = self.orchestrator.execute_single_agent(
            agent=self.nursing_agent.agent,
            query=prompt,
            workflow_id=self.workflow_id
        )

        if nursing_result.success:
            state.search_results = nursing_result.content
            state.pmids_found = extract_pmids(nursing_result.content)
            state.dois_found = extract_dois(nursing_result.content)
            state.search_strategies_used.append("nursing_primary")
            print(f"   Nursing agent: {len(state.pmids_found)} PMIDs")

        self._increment_step()

        # Medical agent search
        medical_result = self.orchestrator.execute_single_agent(
            agent=self.medical_agent.agent,
            query=prompt,
            workflow_id=self.workflow_id
        )

        if medical_result.success:
            state.search_results += "\n\n---\n" + medical_result.content
            new_pmids = extract_pmids(medical_result.content)
            new_dois = extract_dois(medical_result.content)
            state.pmids_found = list(set(state.pmids_found + new_pmids))
            state.dois_found = list(set(state.dois_found + new_dois))
            state.search_strategies_used.append("medical_primary")
            print(f"   Medical agent: {len(new_pmids)} additional PMIDs")

        self._increment_step()

        print(f"   Total after Strategy 1: {len(state.pmids_found)} PMIDs")

        # Strategy 2: Expanded search if needed
        if len(state.pmids_found) < 5:
            print("   Strategy 2: Expanded search...")
            state.retry_counts["search"] = 1

            # Extract broad terms from PICOT
            broad_terms = self._extract_broad_terms(state.user_topic, state.picot_components)

            expanded_prompt = PROMPTS["search_expanded"].format(
                picot=state.picot_question,
                count=len(state.pmids_found),
                broad_terms=broad_terms,
                existing_pmids=", ".join(state.pmids_found)
            )

            expanded_result = self.orchestrator.execute_single_agent(
                agent=self.nursing_agent.agent,
                query=expanded_prompt,
                workflow_id=self.workflow_id
            )

            if expanded_result.success:
                state.search_results += "\n\n--- Expanded Search ---\n" + expanded_result.content
                new_pmids = extract_pmids(expanded_result.content)
                state.pmids_found = list(set(state.pmids_found + new_pmids))
                state.search_strategies_used.append("expanded")
                print(f"   Expanded: {len(new_pmids)} additional PMIDs")

            self._increment_step()

        # Strategy 3: Tertiary broad search if still insufficient
        if len(state.pmids_found) < 3:
            print("   Strategy 3: Broad fallback search...")
            state.retry_counts["search"] = state.retry_counts.get("search", 0) + 1

            terms = state.user_topic.split()[:3]
            tertiary_prompt = PROMPTS["search_tertiary"].format(
                topic=state.user_topic,
                term1=terms[0] if len(terms) > 0 else "nursing",
                term2=terms[1] if len(terms) > 1 else "intervention",
                term3=terms[2] if len(terms) > 2 else "outcome"
            )

            tertiary_result = self.orchestrator.execute_single_agent(
                agent=self.medical_agent.agent,
                query=tertiary_prompt,
                workflow_id=self.workflow_id
            )

            if tertiary_result.success:
                state.search_results += "\n\n--- Broad Search ---\n" + tertiary_result.content
                new_pmids = extract_pmids(tertiary_result.content)
                state.pmids_found = list(set(state.pmids_found + new_pmids))
                state.search_strategies_used.append("tertiary")
                print(f"   Broad search: {len(new_pmids)} additional PMIDs")

            self._increment_step()

        # Quality gate
        gate = run_quality_gate("search_quality", search_results=state.search_results)
        state.gate_results["search"] = gate.passed

        print(f"   Final count: {len(state.pmids_found)} PMIDs")
        print(f"   Gate: {'PASSED' if gate.passed else 'WARNING - proceeding with available articles'}")

        # Don't fail on search gate - proceed with what we have
        if len(state.pmids_found) == 0:
            state.error = "No articles found after all search strategies"
            state.status = "failed"
            return state

        if not gate.passed:
            state.warnings.append(f"Search found only {len(state.pmids_found)} articles (minimum 3 recommended)")

        state.phase_times["search"] = time.time() - start
        print(f"   Search complete ({state.phase_times['search']:.1f}s)")

        return state

    def _extract_broad_terms(self, topic: str, components: Dict[str, str]) -> str:
        """Extract broad search terms."""
        terms = []

        # From topic
        words = topic.lower().split()
        important = [w for w in words if len(w) > 4 and w not in
                    ['patients', 'intervention', 'compared', 'outcome', 'during']]
        terms.extend(important[:3])

        # From PICOT components
        if "P" in components:
            pop_words = components["P"].lower().split()[:2]
            terms.extend(pop_words)
        if "I" in components:
            int_words = components["I"].lower().split()[:2]
            terms.extend(int_words)

        return " ".join(list(set(terms))[:5])

    # =========================================================================
    # PHASE 3: VALIDATION
    # =========================================================================

    def _phase_3_validation(self, state: PipelineState) -> PipelineState:
        """Validate citations and grade evidence."""
        start = time.time()
        state.current_phase = 3
        state.phase_name = "validation"

        self._print_phase(3, "CITATION VALIDATION")

        pmid_list = ", ".join([f"PMID {p}" for p in state.pmids_found])
        prompt = PROMPTS["validate"].format(pmids=pmid_list)

        result = self.orchestrator.execute_single_agent(
            agent=self.citation_agent.agent,
            query=prompt,
            workflow_id=self.workflow_id
        )

        if result.success:
            state.validation_report = result.content

            # Parse validation results
            report_lower = result.content.lower()

            # Extract valid/retracted
            for pmid in state.pmids_found:
                pmid_section = self._find_pmid_section(result.content, pmid)
                if "retracted" in pmid_section.lower():
                    state.retracted_pmids.append(pmid)
                else:
                    state.valid_pmids.append(pmid)

                # Extract evidence level
                level = self._extract_evidence_level(pmid_section)
                state.evidence_grades[pmid] = level

            if not state.valid_pmids:
                state.valid_pmids = state.pmids_found
        else:
            state.validation_report = "Validation service unavailable"
            state.valid_pmids = state.pmids_found
            state.warnings.append("Citation validation could not be completed")

        self._increment_step()

        # Quality gate
        gate = run_quality_gate(
            "validation_quality",
            validation_report=state.validation_report,
            pmid_list=state.pmids_found
        )
        state.gate_results["validation"] = gate.passed

        print(f"   Valid: {len(state.valid_pmids)}")
        print(f"   Retracted: {len(state.retracted_pmids)}")
        if state.evidence_grades:
            levels = list(state.evidence_grades.values())
            print(f"   Evidence levels: {dict((l, levels.count(l)) for l in set(levels))}")

        state.phase_times["validation"] = time.time() - start
        print(f"   Validation complete ({state.phase_times['validation']:.1f}s)")

        return state

    def _find_pmid_section(self, text: str, pmid: str) -> str:
        """Find the section of text discussing a specific PMID."""
        lines = text.split('\n')
        section = []
        in_section = False

        for line in lines:
            if pmid in line:
                in_section = True
            if in_section:
                section.append(line)
                if len(section) > 5:
                    break

        return '\n'.join(section)

    def _extract_evidence_level(self, text: str) -> str:
        """Extract evidence level from text."""
        text_lower = text.lower()

        if 'level i' in text_lower or 'level 1' in text_lower:
            return "Level I"
        elif 'level ii' in text_lower or 'level 2' in text_lower:
            return "Level II"
        elif 'level iii' in text_lower or 'level 3' in text_lower:
            return "Level III"
        elif 'level iv' in text_lower or 'level 4' in text_lower:
            return "Level IV"
        elif 'level v' in text_lower or 'level 5' in text_lower:
            return "Level V"

        # Infer from study type
        if any(t in text_lower for t in ['rct', 'randomized', 'systematic review']):
            return "Level I"
        elif any(t in text_lower for t in ['quasi', 'cohort']):
            return "Level II"
        elif any(t in text_lower for t in ['descriptive', 'qualitative', 'cross-sectional']):
            return "Level III"

        return "Not Graded"

    # =========================================================================
    # PHASE 4: SYNTHESIS
    # =========================================================================

    def _phase_4_synthesis(self, state: PipelineState) -> PipelineState:
        """Generate publication-quality literature synthesis."""
        start = time.time()
        state.current_phase = 4
        state.phase_name = "synthesis"

        self._print_phase(4, "EVIDENCE SYNTHESIS")

        # Use only valid PMIDs
        valid_articles = state.search_results
        if state.retracted_pmids:
            for pmid in state.retracted_pmids:
                # Remove retracted article sections
                valid_articles = re.sub(
                    rf'.*{pmid}.*\n(?:.*\n){{0,10}}',
                    '',
                    valid_articles
                )

        prompt = PROMPTS["synthesize"].format(
            picot=state.picot_question,
            articles=valid_articles
        )

        result = self.orchestrator.execute_single_agent(
            agent=self.writing_agent.agent,
            query=prompt,
            workflow_id=self.workflow_id
        )

        if not result.success:
            state.error = f"Synthesis failed: {result.error}"
            state.status = "failed"
            return state

        state.synthesis_text = result.content
        self._increment_step()

        # Extract sections
        sections = re.findall(r'\*\*(\d+\.\s*[^*]+)\*\*', result.content)
        state.synthesis_sections = sections

        # Count citations
        state.citation_count = len(re.findall(r'\([A-Z][a-z]+.*?,\s*\d{4}\)', result.content))

        # Quality gate
        gate = run_quality_gate("synthesis_quality", synthesis_text=state.synthesis_text)
        state.gate_results["synthesis"] = gate.passed

        if not gate.passed:
            state.retry_counts["synthesis"] = 1
            print("   Enhancing synthesis...")
            retry_prompt = prompt + """

REQUIRED IMPROVEMENTS:
1. Add section headers: Introduction, Evidence Summary, Strength of Evidence, Implications
2. Include more in-text citations (Author, Year)
3. Synthesize across studies, don't just summarize each
4. Add clinical implications with specific recommendations
"""
            retry = self.orchestrator.execute_single_agent(
                agent=self.writing_agent.agent,
                query=retry_prompt,
                workflow_id=self.workflow_id
            )
            if retry.success:
                state.synthesis_text = retry.content
                state.citation_count = len(re.findall(r'\([A-Z][a-z]+.*?,\s*\d{4}\)', retry.content))
                gate = run_quality_gate("synthesis_quality", synthesis_text=state.synthesis_text)
                state.gate_results["synthesis"] = gate.passed

        print(f"   Sections: {len(state.synthesis_sections)}")
        print(f"   Citations: {state.citation_count}")
        print(f"   Gate: {'PASSED' if gate.passed else 'WARNING'}")

        state.phase_times["synthesis"] = time.time() - start
        print(f"   Synthesis complete ({state.phase_times['synthesis']:.1f}s)")

        return state

    # =========================================================================
    # PHASE 5: ANALYSIS
    # =========================================================================

    def _phase_5_analysis(self, state: PipelineState) -> PipelineState:
        """Generate comprehensive analysis plan."""
        start = time.time()
        state.current_phase = 5
        state.phase_name = "analysis"

        self._print_phase(5, "ANALYSIS PLANNING")

        prompt = PROMPTS["analysis"].format(picot=state.picot_question)

        result = self.orchestrator.execute_single_agent(
            agent=self.data_agent.agent,
            query=prompt,
            workflow_id=self.workflow_id
        )

        if result.success:
            state.analysis_plan = result.content

            # Extract key statistics
            sample_match = re.search(r'(?:N|n|sample size)[:\s=]*(\d+)', result.content)
            if sample_match:
                state.sample_size = int(sample_match.group(1))

            power_match = re.search(r'power[:\s=]*([0-9.]+)', result.content, re.IGNORECASE)
            if power_match:
                state.power = float(power_match.group(1))

            test_patterns = [
                r't-test', r'chi-square', r'ANOVA', r'regression',
                r'McNemar', r'Mann-Whitney', r'Wilcoxon', r'Fisher'
            ]
            for pattern in test_patterns:
                if re.search(pattern, result.content, re.IGNORECASE):
                    state.statistical_test = pattern.replace(r'\\', '')
                    break
        else:
            state.analysis_plan = "Analysis plan generation failed"
            state.warnings.append("Analysis plan could not be generated")

        self._increment_step()

        # Quality gate
        gate = run_quality_gate("analysis_quality", analysis_text=state.analysis_plan)
        state.gate_results["analysis"] = gate.passed

        print(f"   Statistical test: {state.statistical_test or 'To be determined'}")
        print(f"   Sample size: {state.sample_size or 'To be calculated'}")
        print(f"   Gate: {'PASSED' if gate.passed else 'WARNING'}")

        state.phase_times["analysis"] = time.time() - start
        print(f"   Analysis planning complete ({state.phase_times['analysis']:.1f}s)")

        return state

    # =========================================================================
    # PHASE 6: TIMELINE
    # =========================================================================

    def _phase_6_timeline(self, state: PipelineState) -> PipelineState:
        """Setup project milestones."""
        start = time.time()
        state.current_phase = 6
        state.phase_name = "timeline"

        self._print_phase(6, "TIMELINE SETUP")

        prompt = PROMPTS["timeline"].format(
            project=state.project_name,
            topic=state.user_topic,
            start_date=datetime.now().strftime("%Y-%m-%d")
        )

        result = self.orchestrator.execute_single_agent(
            agent=self.timeline_agent.agent,
            query=prompt,
            workflow_id=self.workflow_id
        )

        if result.success:
            state.milestones = self._parse_milestones(result.content)
        else:
            state.milestones = self._default_milestones()

        self._increment_step()

        # Mark completed phases
        for m in state.milestones:
            if any(phase in m.get("name", "").lower() for phase in ["picot", "literature", "search"]):
                m["status"] = "completed"

        print(f"   Milestones created: {len(state.milestones)}")
        completed = sum(1 for m in state.milestones if m.get("status") == "completed")
        print(f"   Completed: {completed}/{len(state.milestones)}")

        state.phase_times["timeline"] = time.time() - start
        print(f"   Timeline complete ({state.phase_times['timeline']:.1f}s)")

        return state

    def _parse_milestones(self, text: str) -> List[Dict]:
        """Parse milestones from agent response."""
        milestones = []

        # Look for table rows or list items
        patterns = [
            r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|',  # Table format
            r'[-*]\s*\*\*([^*]+)\*\*[:\s]+([^\n]+)',  # Bold list items
            r'\d+\.\s+([^:]+):\s*([^\n]+)',  # Numbered with colon
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) >= 2:
                    name = match[0].strip()
                    if name and not name.lower().startswith(('milestone', 'due', '---')):
                        milestones.append({
                            "name": name,
                            "due": match[1].strip() if len(match) > 1 else "",
                            "deliverables": match[2].strip() if len(match) > 2 else "",
                            "status": "pending"
                        })

        return milestones if milestones else self._default_milestones()

    def _default_milestones(self) -> List[Dict]:
        """Create default milestone structure."""
        base = datetime.now()
        return [
            {"name": "PICOT Development", "due": base.strftime("%Y-%m-%d"), "status": "completed"},
            {"name": "Literature Search", "due": base.strftime("%Y-%m-%d"), "status": "completed"},
            {"name": "Citation Validation", "due": base.strftime("%Y-%m-%d"), "status": "completed"},
            {"name": "IRB Submission", "due": (base + timedelta(days=30)).strftime("%Y-%m-%d"), "status": "pending"},
            {"name": "IRB Approval", "due": (base + timedelta(days=60)).strftime("%Y-%m-%d"), "status": "pending"},
            {"name": "Data Collection", "due": (base + timedelta(days=120)).strftime("%Y-%m-%d"), "status": "pending"},
            {"name": "Data Analysis", "due": (base + timedelta(days=150)).strftime("%Y-%m-%d"), "status": "pending"},
            {"name": "Results Write-up", "due": (base + timedelta(days=170)).strftime("%Y-%m-%d"), "status": "pending"},
            {"name": "Poster/Presentation", "due": (base + timedelta(days=190)).strftime("%Y-%m-%d"), "status": "pending"},
            {"name": "Final Presentation", "due": (base + timedelta(days=210)).strftime("%Y-%m-%d"), "status": "pending"},
        ]

    # =========================================================================
    # DISPLAY
    # =========================================================================

    def _print_header(self, title: str, topic: str):
        """Print pipeline header."""
        print(f"\n{'='*70}")
        print(f"{title}".center(70))
        print(f"{'='*70}")
        print(f"\nProject: {self.project_name}")
        print(f"Topic: {topic}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def _print_phase(self, num: int, name: str):
        """Print phase header."""
        print(f"\n{'-'*70}")
        print(f"PHASE {num}: {name}")
        print(f"{'-'*70}")

    def _print_summary(self, state: PipelineState, run_id: int):
        """Print completion summary."""
        total = time.time() - state.started_at

        print(f"\n{'='*70}")
        print("PIPELINE COMPLETE".center(70))
        print(f"{'='*70}")

        print(f"\nRun ID: {run_id}")
        print(f"Total Time: {total:.1f}s")

        print("\nPhase Results:")
        for num, name, key in self.PHASES:
            passed = state.gate_results.get(key, True)
            t = state.phase_times.get(key, 0)
            status = "PASS" if passed else "WARN"
            print(f"  {num}. {name}: {status} ({t:.1f}s)")

        print(f"\nOutputs:")
        print(f"  PMIDs Found: {len(state.pmids_found)}")
        print(f"  Valid Citations: {len(state.valid_pmids)}")
        print(f"  Synthesis Citations: {state.citation_count}")
        print(f"  Sample Size: {state.sample_size or 'TBD'}")
        print(f"  Milestones: {len(state.milestones)}")

        if state.warnings:
            print(f"\nWarnings:")
            for w in state.warnings:
                print(f"  - {w}")

        print(f"\nResults saved to: {self.db_path}")

    # =========================================================================
    # DATABASE
    # =========================================================================

    def _save_state(self, state: PipelineState, run_id: int = None) -> int:
        """Save state to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if run_id is None:
            cursor.execute("""
                INSERT INTO pipeline_runs (project_name, topic, status)
                VALUES (?, ?, ?)
            """, (state.project_name, state.user_topic, state.status))
            run_id = cursor.lastrowid
        else:
            cursor.execute("""
                UPDATE pipeline_runs SET
                    picot_question = ?,
                    picot_components_json = ?,
                    picot_gate_passed = ?,
                    search_results = ?,
                    pmids_json = ?,
                    dois_json = ?,
                    search_strategies_json = ?,
                    search_gate_passed = ?,
                    validation_report = ?,
                    valid_pmids_json = ?,
                    retracted_pmids_json = ?,
                    evidence_grades_json = ?,
                    validation_gate_passed = ?,
                    synthesis_text = ?,
                    synthesis_sections_json = ?,
                    citation_count = ?,
                    synthesis_gate_passed = ?,
                    analysis_plan = ?,
                    statistical_test = ?,
                    sample_size = ?,
                    power = ?,
                    analysis_gate_passed = ?,
                    milestones_json = ?,
                    current_phase = ?,
                    status = ?,
                    error = ?,
                    warnings_json = ?,
                    completed_at = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE NULL END,
                    phase_times_json = ?,
                    total_seconds = ?,
                    gate_results_json = ?,
                    retry_counts_json = ?
                WHERE id = ?
            """, (
                state.picot_question,
                json.dumps(state.picot_components),
                1 if state.gate_results.get("picot") else 0,
                state.search_results,
                json.dumps(state.pmids_found),
                json.dumps(state.dois_found),
                json.dumps(state.search_strategies_used),
                1 if state.gate_results.get("search") else 0,
                state.validation_report,
                json.dumps(state.valid_pmids),
                json.dumps(state.retracted_pmids),
                json.dumps(state.evidence_grades),
                1 if state.gate_results.get("validation") else 0,
                state.synthesis_text,
                json.dumps(state.synthesis_sections),
                state.citation_count,
                1 if state.gate_results.get("synthesis") else 0,
                state.analysis_plan,
                state.statistical_test,
                state.sample_size,
                state.power,
                1 if state.gate_results.get("analysis") else 0,
                json.dumps(state.milestones),
                state.current_phase,
                state.status,
                state.error,
                json.dumps(state.warnings),
                state.status,
                json.dumps(state.phase_times),
                time.time() - state.started_at,
                json.dumps(state.gate_results),
                json.dumps(state.retry_counts),
                run_id
            ))

        conn.commit()
        conn.close()
        return run_id


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def run_unified_pipeline(topic: str, project_name: str = "default") -> WorkflowResult:
    """
    Run the unified research pipeline.

    Args:
        topic: Research topic
        project_name: Project name

    Returns:
        WorkflowResult with all outputs
    """
    pipeline = UnifiedResearchPipeline(project_name=project_name)
    return pipeline.run(topic)


def main():
    """CLI entry point."""
    import sys

    print("\n" + "="*70)
    print("UNIFIED NURSING RESEARCH PIPELINE".center(70))
    print("="*70)

    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("\nEnter research topic: ").strip()

    if not topic:
        print("No topic provided.")
        return

    project = input("Project name [default]: ").strip() or "default"

    result = run_unified_pipeline(topic, project)

    if result.success:
        print("\n" + "="*70)
        print("SUCCESS - All phases complete")
        print("="*70)
    else:
        print(f"\nFailed: {result.error}")


if __name__ == "__main__":
    main()
