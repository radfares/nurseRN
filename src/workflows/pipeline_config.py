"""
Pipeline Configuration - Instructions for Research Pipeline

This file contains ALL instructions the pipeline needs to coordinate agents.
Agents are NOT modified - this file tells the pipeline what to ask each agent
and how to validate their responses.

Created: 2025-12-10
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field


# =============================================================================
# PHASE DEFINITIONS
# =============================================================================

@dataclass
class PhaseConfig:
    """Configuration for a single phase in the pipeline."""
    name: str
    description: str
    agents_used: List[str]
    parallel: bool
    quality_gate: str
    retry_on_fail: bool
    max_retries: int


PHASES = {
    "planning": PhaseConfig(
        name="planning",
        description="Generate PICOT question from user topic",
        agents_used=["writing"],
        parallel=False,
        quality_gate="picot_quality",
        retry_on_fail=True,
        max_retries=2
    ),
    "search": PhaseConfig(
        name="search",
        description="Search literature databases in parallel",
        agents_used=["nursing", "medical"],
        parallel=True,
        quality_gate="search_quality",
        retry_on_fail=True,
        max_retries=1
    ),
    "validation": PhaseConfig(
        name="validation",
        description="Validate all citations for retraction status",
        agents_used=["citation"],
        parallel=False,
        quality_gate="validation_quality",
        retry_on_fail=False,
        max_retries=0
    ),
    "synthesis": PhaseConfig(
        name="synthesis",
        description="Write literature synthesis from validated articles",
        agents_used=["writing"],
        parallel=False,
        quality_gate="synthesis_quality",
        retry_on_fail=True,
        max_retries=1
    ),
    "analysis": PhaseConfig(
        name="analysis",
        description="Generate data analysis plan and template",
        agents_used=["data_analysis"],
        parallel=False,
        quality_gate="analysis_quality",
        retry_on_fail=True,
        max_retries=1
    )
}


# =============================================================================
# AGENT PROMPTS - What to ask each agent at each phase
# =============================================================================

AGENT_PROMPTS = {
    # -------------------------------------------------------------------------
    # PLANNING PHASE - Writing Agent generates PICOT
    # -------------------------------------------------------------------------
    "planning_picot": """
You are helping create a PICOT question for a nursing research project.

USER TOPIC: {topic}

Create a complete PICOT question with ALL 5 components clearly labeled:

P (Population): Describe the specific patient population
I (Intervention): Describe the nursing intervention being studied
C (Comparison): Describe what the intervention is compared against
O (Outcome): Describe the measurable outcomes
T (Time): Describe the timeframe for the study

Format your response EXACTLY like this:

**PICOT Components:**
- P (Population): [your population description]
- I (Intervention): [your intervention description]
- C (Comparison): [your comparison description]
- O (Outcome): [your outcome description]
- T (Time): [your timeframe]

**PICOT Question:**
"In [population], does [intervention] compared to [comparison] improve [outcome] over [time]?"

Make the PICOT specific enough to search in PubMed. Use proper medical terminology.
""",

    # -------------------------------------------------------------------------
    # SEARCH PHASE - Nursing Agent searches PubMed
    # -------------------------------------------------------------------------
    "search_nursing": """
Search PubMed for peer-reviewed research articles on this nursing topic.

PICOT QUESTION: {picot}

SEARCH STRATEGY (IMPORTANT):
1. Extract 2-3 KEY TERMS from the PICOT (e.g., "catheter", "CAUTI", "nursing")
2. Start with a BROAD search using these key terms
3. If too many results, add ONE more specific term
4. Use simple terms that PubMed understands

Example good searches:
- "Foley catheter CAUTI nursing" (simple, broad)
- "catheter associated urinary infection prevention"
- "nurse driven protocol catheter"

Example BAD searches (too specific, will return 0 results):
- "nurse-driven Foley catheter removal protocol CAUTI reduction acute care" ❌

Find 5-7 relevant peer-reviewed articles from the last 10 years.

For EACH article found, provide:
1. PMID (required - this is critical)
2. Title
3. Authors (first author et al.)
4. Journal name
5. Publication year
6. Brief summary of key findings (2-3 sentences)

Focus on:
- Randomized controlled trials (RCTs)
- Systematic reviews
- Quality improvement studies
- Meta-analyses

Return ONLY articles you actually find in PubMed with real PMIDs.
DO NOT fabricate or guess PMIDs.
""",

    # -------------------------------------------------------------------------
    # SEARCH PHASE - Medical Agent searches clinical trials
    # -------------------------------------------------------------------------
    "search_medical": """
Search PubMed for clinical trials and medical research on this topic.

PICOT QUESTION: {picot}

SEARCH STRATEGY (IMPORTANT):
1. Use 2-3 SIMPLE key terms from the PICOT
2. Keep your search query SHORT (3-5 words max)
3. Use common medical terms

Example good searches:
- "catheter CAUTI prevention RCT"
- "urinary infection hospital nursing"
- "catheter removal protocol"

Find 3-5 relevant clinical trials or medical research studies.

For EACH study found, provide:
1. Identifier (PMID required, NCT number if available)
2. Title
3. Study type (RCT, cohort, etc.)
4. Publication year
5. Key findings or objectives

Focus on:
- Completed trials with results
- High-quality medical evidence
- Studies relevant to the intervention

Return ONLY real studies with verifiable identifiers.
DO NOT fabricate or guess PMIDs or NCT numbers.
""",

    # -------------------------------------------------------------------------
    # VALIDATION PHASE - Citation Agent validates PMIDs
    # -------------------------------------------------------------------------
    "validate_citations": """
Validate the following citations for retraction status and quality.

CITATIONS TO VALIDATE:
{citations}

For EACH citation:
1. Check if the PMID exists in PubMed
2. Check if the article has been retracted
3. Check if there are any corrections or concerns
4. Verify the journal is peer-reviewed

Return a validation report:
- PMID: [number]
- Status: VALID / RETRACTED / NOT_FOUND / CONCERNS
- Notes: [any issues found]

Flag any citations that should NOT be used.
""",

    # -------------------------------------------------------------------------
    # SYNTHESIS PHASE - Writing Agent writes literature review
    # -------------------------------------------------------------------------
    "synthesis_literature": """
Write a literature synthesis based on the validated research articles.

PICOT QUESTION: {picot}

VALIDATED ARTICLES:
{articles}

Write a professional literature synthesis that includes:

1. **Introduction** (2-3 sentences)
   - State the clinical problem
   - Why this research matters

2. **Evidence Summary** (main body)
   - Organize by theme or finding type
   - Cite each article with (Author, Year)
   - Compare and contrast findings
   - Note consistency or conflicts in evidence

3. **Strength of Evidence**
   - Level of evidence (I, II, III, etc.)
   - Quality of included studies
   - Limitations noted

4. **Implications for Practice**
   - What does the evidence support?
   - Recommendations based on findings

5. **Gaps in Literature**
   - What questions remain unanswered?

Use professional academic tone. Do NOT invent citations - only use the articles provided.
""",

    # -------------------------------------------------------------------------
    # ANALYSIS PHASE - Data Agent creates analysis plan
    # -------------------------------------------------------------------------
    "analysis_plan": """
Create a data analysis plan for this nursing research project.

PICOT QUESTION: {picot}

STUDY DESIGN: Pre/post intervention quality improvement project

Create a complete analysis plan:

1. **Variables**
   List all variables to collect:
   - Primary outcome variable
   - Secondary outcome variables
   - Demographic variables
   - Potential confounders

2. **Data Collection Template**
   Define columns for data spreadsheet:
   | Variable Name | Data Type | Valid Values | Collection Method |

3. **Statistical Tests**
   - Primary analysis: [test name] for [outcome]
   - Secondary analyses
   - Justification for each test

4. **Sample Size**
   - Estimated N needed
   - Power calculation assumptions
   - Practical considerations

5. **Analysis Code**
   Provide R or Python code snippet for primary analysis

Be specific to nursing QI projects. Use appropriate tests for the data types.
"""
}


# =============================================================================
# QUALITY GATE DEFINITIONS - How to validate each phase output
# =============================================================================

QUALITY_GATES = {
    "picot_quality": {
        "description": "Verify PICOT has all 5 components and is searchable",
        "required_elements": ["P (Population)", "I (Intervention)", "C (Comparison)", "O (Outcome)", "T (Time)"],
        "min_length": 200,
        "must_contain": ["?"],  # Must be a question
        "checks": [
            "has_all_components",
            "is_specific",
            "is_searchable"
        ]
    },

    "search_quality": {
        "description": "Verify search returned enough usable results",
        "min_articles": 3,
        "required_fields": ["PMID", "Title", "Year"],
        "max_age_years": 10,
        "checks": [
            "has_minimum_articles",
            "has_identifiers",
            "articles_are_recent"
        ]
    },

    "validation_quality": {
        "description": "Verify citations are valid and not retracted",
        "min_valid": 3,
        "max_retracted_ratio": 0.2,  # No more than 20% retracted
        "checks": [
            "has_minimum_valid",
            "retraction_ratio_acceptable"
        ]
    },

    "synthesis_quality": {
        "description": "Verify synthesis is complete and properly structured",
        "required_sections": ["Evidence Summary", "Strength of Evidence", "Implications"],
        "min_length": 500,
        "min_citations": 3,
        "checks": [
            "has_required_sections",
            "meets_length",
            "cites_sources"
        ]
    },

    "analysis_quality": {
        "description": "Verify analysis plan is complete and appropriate",
        "required_sections": ["Variables", "Statistical Tests", "Sample Size"],
        "must_have_code": True,
        "checks": [
            "has_required_sections",
            "has_statistical_test",
            "has_code_snippet"
        ]
    }
}


# =============================================================================
# PIPELINE EXECUTION ORDER
# =============================================================================

PIPELINE_ORDER = [
    "planning",
    "search",
    "validation",
    "synthesis",
    "analysis"
]


# =============================================================================
# ERROR MESSAGES
# =============================================================================

ERROR_MESSAGES = {
    "picot_incomplete": "PICOT question is missing required components. Need P, I, C, O, and T clearly labeled.",
    "search_insufficient": "Search returned fewer than 3 usable articles. Try broader search terms.",
    "validation_failed": "Too many citations are retracted or invalid. Cannot proceed with synthesis.",
    "synthesis_incomplete": "Literature synthesis is missing required sections.",
    "analysis_incomplete": "Analysis plan is missing required components.",
    "agent_error": "Agent failed to respond. Check agent status and retry.",
    "timeout": "Operation timed out. The database may be slow or unavailable."
}


# =============================================================================
# DATABASE TABLE FOR PIPELINE RESULTS
# =============================================================================

RESULTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS pipeline_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- User input
    user_topic TEXT NOT NULL,

    -- Phase 1: Planning
    picot_question TEXT,
    picot_status TEXT DEFAULT 'pending',

    -- Phase 2: Search
    search_results_json TEXT,
    search_count INTEGER DEFAULT 0,
    search_status TEXT DEFAULT 'pending',

    -- Phase 3: Validation
    validation_report TEXT,
    valid_count INTEGER DEFAULT 0,
    retracted_count INTEGER DEFAULT 0,
    validation_status TEXT DEFAULT 'pending',

    -- Phase 4: Synthesis
    literature_synthesis TEXT,
    synthesis_status TEXT DEFAULT 'pending',

    -- Phase 5: Analysis
    analysis_plan TEXT,
    data_template_json TEXT,
    analysis_status TEXT DEFAULT 'pending',

    -- Metadata
    overall_status TEXT DEFAULT 'in_progress',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,

    -- Execution tracking
    total_cost REAL DEFAULT 0.0,
    total_time_seconds REAL DEFAULT 0.0
);
"""


# =============================================================================
# HELPER FUNCTION TO GET PROMPT
# =============================================================================

def get_prompt(prompt_key: str, **kwargs) -> str:
    """
    Get a prompt template and fill in variables.

    Args:
        prompt_key: Key from AGENT_PROMPTS
        **kwargs: Variables to substitute in the prompt

    Returns:
        Formatted prompt string

    Example:
        prompt = get_prompt("planning_picot", topic="fall prevention")
    """
    if prompt_key not in AGENT_PROMPTS:
        raise ValueError(f"Unknown prompt key: {prompt_key}")

    template = AGENT_PROMPTS[prompt_key]
    return template.format(**kwargs)


def get_phase_config(phase_name: str) -> PhaseConfig:
    """
    Get configuration for a pipeline phase.

    Args:
        phase_name: Name of the phase

    Returns:
        PhaseConfig object
    """
    if phase_name not in PHASES:
        raise ValueError(f"Unknown phase: {phase_name}")

    return PHASES[phase_name]


def get_quality_gate(gate_name: str) -> dict:
    """
    Get quality gate configuration.

    Args:
        gate_name: Name of the quality gate

    Returns:
        Quality gate configuration dict
    """
    if gate_name not in QUALITY_GATES:
        raise ValueError(f"Unknown quality gate: {gate_name}")

    return QUALITY_GATES[gate_name]
