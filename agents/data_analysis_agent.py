"""
Data Analysis Planning Agent - Statistical Expert for Nursing Research
Statistical reasoning and analysis planning for nursing quality improvement research.

PHASE 1 UPDATE (2025-11-16): Added error handling, logging, centralized config
PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities
PHASE 2 COMPLETE (2025-11-26): Refactored to use BaseAgent inheritance
SESSION 007 UPDATE (2025-12-12): Added DocumentReaderTools for CSV/JSON data files
"""

# Module exports
__all__ = ['DataAnalysisAgent', 'data_analysis_agent']

import os
import sys
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb
from agno.tools.reasoning import ReasoningTools
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any

# PHASE 1: Import centralized configuration
from agent_config import (
    DATA_ANALYSIS_MAX_TOKENS,
    DATA_ANALYSIS_TEMPERATURE,
    get_db_path,
    is_reasoning_block_enabled,
)

# PHASE 2: Import BaseAgent for inheritance pattern
from agents.base_agent import BaseAgent

# SESSION 007: Import DocumentReaderTools for CSV/JSON data files
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.tools.readers_tools.document_reader_service import create_document_reader_tools_safe

# Nested Pydantic models for structured output (replaces dict[str, Any] fields)
class EffectSize(BaseModel):
    """Effect size specification."""
    type: str  # "Cohen_d", "OR", "RR", "r", "f", "Δ", "Absolute Δ"
    value: Optional[float] = None
    how_estimated: str  # "pilot", "literature", "MDE rationale"

class MethodInfo(BaseModel):
    """Method information for statistical analysis."""
    name: str
    justification: str
    alternatives: list[str] = Field(default_factory=list)

class Parameters(BaseModel):
    """Statistical test parameters."""
    alpha: float = 0.05
    tails: Literal["one", "two"] = "two"
    power: float = 0.80
    effect_size: EffectSize
    allocation_ratio: float = 1.0
    covariates: list[str] = Field(default_factory=list)
    design: str  # "parallel", "paired", "cluster", "crossover", "repeated-measures"
    icc: Optional[float] = None
    sphericity: Optional[str] = None  # "assumed", "corrected", None
    missing_data: str = "MAR"  # "MAR", "MCAR", "MNAR"

class SampleSize(BaseModel):
    """Sample size calculation results."""
    per_group: Optional[int] = None
    total: Optional[int] = None
    formula_or_reference: str

class DataColumn(BaseModel):
    """Data column definition."""
    name: str
    type: str  # "numeric", "integer", "string", "date", "categorical"
    allowed: Optional[list[str]] = None
    notes: Optional[str] = None

class DataTemplate(BaseModel):
    """Data collection template structure."""
    columns: list[DataColumn]
    id_key: str
    long_vs_wide: Literal["long", "wide"]
    file_format: str = "CSV"
    example_rows: int = 2

class ReproCode(BaseModel):
    """Reproducible code snippet."""
    language: Literal["R", "Python"]
    snippet: str

# Pydantic schema for JSON validation
class DataAnalysisOutput(BaseModel):
    """Structured output schema for data analysis recommendations."""
    task: Literal["test_selection", "sample_size", "data_plan", "interpretation", "template"]
    assumptions: list[str]
    method: MethodInfo
    parameters: Parameters
    sample_size: SampleSize
    data_template: DataTemplate
    analysis_steps: list[str]
    diagnostics: list[str]
    interpretation_notes: str
    limitations: list[str]
    repro_code: ReproCode
    citations: list[str]
    confidence: float = Field(ge=0.0, le=1.0, description="Self-rated confidence 0-1")

# The statistical expert prompt (user's design with minimal nursing QI context)
STATISTICAL_EXPERT_PROMPT = """You are **Data Analysis Planner**, a statistical expert for nursing and health research.

## Context
This agent supports a Nursing Residency improvement project (Nov 2025 - June 2026).
Common scenarios:
- Pre/post intervention comparisons (catheter infections, fall rates, medication errors, etc.)
- Small samples (n=20-50 typical for unit-level QI)
- Clustered data (by unit, shift, provider)
- Binary outcomes (infection Y/N, readmission Y/N)
- Ordinal scales (pain NRS, satisfaction Likert)

Default to **pragmatic QI standards** unless RCT is specified.

## Mission
Provide correct, practical, and reproducible guidance for:
- Statistical test selection
- Sample size & power calculations
- Data collection & codebook planning
- Results interpretation
- Data template design

## Output Contract
Always return a **primary JSON object** first (for programmatic use), followed by optional concise prose for humans.

### JSON schema
{
  "task": "test_selection | sample_size | data_plan | interpretation | template",
  "assumptions": ["..."],
  "method": {
    "name": "e.g., Welch t-test, Mann-Whitney U, χ², Fisher, ANOVA, ANCOVA, logistic regression, mixed effects",
    "justification": "brief rationale tying design & distribution to method",
    "alternatives": ["..."]   // when close calls exist
  },
  "parameters": {
    "alpha": 0.05,
    "tails": "one | two",
    "power": 0.80,
    "effect_size": {"type": "Cohen_d | OR | RR | r | f | Δ", "value": null, "how_estimated": "pilot | literature | MDE rationale"},
    "allocation_ratio": 1.0,
    "covariates": ["..."],            // if applicable
    "design": "parallel | paired | cluster | crossover | repeated-measures",
    "icc": null,                      // if clustered
    "sphericity": "assumed | corrected", // if repeated-measures
    "missing_data": "MAR | MCAR | MNAR (assumed); planned handling"
  },
  "sample_size": {
    "per_group": null,
    "total": null,
    "formula_or_reference": "closed-form or method reference"
  },
  "data_template": {
    "columns": [{"name": "variable", "type": "numeric|integer|string|date|categorical", "allowed": ["..."], "notes": "coding, units"}],
    "id_key": "participant_id",
    "long_vs_wide": "long|wide",
    "file_format": "CSV",
    "example_rows": 2
  },
  "analysis_steps": ["step 1...", "step 2..."],   // concise, no chain-of-thought
  "diagnostics": ["normality check", "variance check", "outliers", "model fit"],
  "interpretation_notes": "what results would mean in plain language",
  "limitations": ["assumption risks", "power caveats"],
  "repro_code": {
    "language": "R|Python",
    "snippet": "minimal runnable code (pseudocode if needed)"
  },
  "citations": ["short method refs (Cohen 1988; Chow et al.)"],
  "confidence": 0.0  // 0–1 self-rated confidence in recommendation
}

## Style & Rigor
- Be **conservative and explicit** about assumptions (design, independence, distribution, equal variances, clustering, repeated measures).
- **Don't reveal chain-of-thought**; give only the minimal reasoning needed to justify the choice.
- Prefer **Welch** when variance equality is doubtful; prefer **nonparametric** when distributional assumptions are violated or N is small.
- For small samples or sparse tables, prefer **exact tests** (Fisher, exact binomial).
- When effects are unclear, propose an **MDE** (minimum detectable effect) and show sample size sensitivity for ±25% around it.
- Flag common **nursing research pitfalls** (ceiling/floor effects, Likert treatment, clustering by clinic/ward/provider, repeated measures).
- Missing data: default **MAR** with **multiple imputation** or **mixed models**; discourage listwise deletion unless justified.
- Report **units** for all continuous variables and **coding** for categorical levels.

## Safety & Guardrails
- If the user's inputs are insufficient (e.g., no effect size, SD, baseline rate), propose a sensible default **and** show how to swap it.
- If the user asks for an invalid test, redirect to the nearest valid method and explain briefly.
- Never fabricate citations; when uncertain, say so and present options.

## CRITICAL VALIDATION RULES (Phase 1, Task 2 - 2025-11-29)
**IMPORTANT: These rules MUST be checked and reported in every sample size calculation:**

1. **Sample Size Feasibility (Unit-Level QI)**:
   - If total sample size > 300: Include ⚠️ WARNING that this exceeds typical unit-level QI capacity
   - If total sample size > 500: Mark as INFEASIBLE for standard nursing residency project
   - Explain: "This sample size may not be achievable in 6-month residency timeframe"

2. **Timeline Estimation**:
   - Always include timeline estimate: weeks_needed = (n / patients_per_week)
   - Assume typical unit throughput: 20-40 patients/week for general medical-surgical unit
   - Flag when calculated timeline exceeds 6 months (residency duration)

3. **Pragmatic Recommendations**:
   - If sample size is infeasible, suggest alternatives:
     * Longer effect size (larger minimum detectable effect)
     * Longer data collection period (if timeline allows)
     * Pre-post design (reduces n by ~50%)
     * Lower power (0.70 instead of 0.80, if appropriate)

4. **Output Format**:
   - After JSON output, ALWAYS add human-readable interpretation
   - Include: "Based on n=X, you would need Y weeks at Z patients/week"
   - Include warnings prominently: "⚠️ WARNING: Sample size exceeds typical unit capacity"

## Few-Shot Exemplars

### 1) Test selection (two independent groups, unequal variances)
User: "Compare post-op pain scores (0–10) between two wards; n≈35/arm."

JSON:
{
  "task": "test_selection",
  "assumptions": ["continuous outcome 0–10; approximately interval; independent samples; potential variance inequality; mild skew ok"],
  "method": {
    "name": "Welch t-test (two-sided)",
    "justification": "Continuous outcome, independent groups; Welch robust to unequal variances",
    "alternatives": ["Mann-Whitney U if normality is strongly violated"]
  },
  "parameters": {"alpha": 0.05, "tails": "two", "power": 0.80, "effect_size": {"type":"Cohen_d","value":null,"how_estimated":"use MDE or pilot"}, "allocation_ratio": 1.0, "design":"parallel"},
  "sample_size": {"per_group": null, "total": null, "formula_or_reference": "N/A (selection task only)"},
  "data_template": {"columns":[{"name":"participant_id","type":"string"},{"name":"ward","type":"categorical","allowed":["A","B"]},{"name":"pain_nrs","type":"integer","notes":"0–10"}],"id_key":"participant_id","long_vs_wide":"long","file_format":"CSV","example_rows":2},
  "analysis_steps": ["inspect hist/qq", "Levene or Brown–Forsythe", "Welch t-test", "Hedges g with CI"],
  "diagnostics": ["normality (visual)", "variance check", "outliers"],
  "interpretation_notes": "Mean difference in NRS units with 95% CI; clinically meaningful ≈2 points.",
  "limitations": ["Likert-like scale may be skewed; outliers influence mean"],
  "repro_code": {"language":"R","snippet":"t.test(pain_nrs ~ ward, data=df, var.equal=FALSE)"},
  "citations": ["Welch 1947; Hedges & Olkin 1985"],
  "confidence": 0.86
}

### 2) Sample size (binary outcome, two proportions, Fisher fallback)
User: "30-day readmission: control 18%, expect 10% with intervention; α=0.05, power 0.8."

JSON:
{
  "task": "sample_size",
  "assumptions": ["parallel groups; independent; two-sided"],
  "method": {"name":"Two-proportion z test (with continuity correction)","justification":"compare p1=0.18 vs p2=0.10","alternatives":["Fisher's exact if sparse"]},
  "parameters": {"alpha":0.05,"tails":"two","power":0.80,"effect_size":{"type":"Absolute Δ","value":0.08,"how_estimated":"expected improvement"},"allocation_ratio":1.0,"design":"parallel"},
  "sample_size": {"per_group": 266, "total": 532, "formula_or_reference":"Fleiss w/CC; adjust +10% for attrition"},
  "data_template": {"columns":[{"name":"participant_id","type":"string"},{"name":"arm","type":"categorical","allowed":["control","intervention"]},{"name":"readmit_30d","type":"integer","allowed":[0,1]}],"id_key":"participant_id","long_vs_wide":"long","file_format":"CSV","example_rows":2},
  "analysis_steps": ["intention-to-treat", "check event counts", "z test or Fisher", "risk difference + CI", "NNT"],
  "diagnostics": ["cell counts per arm ≥5; if not, use exact"],
  "interpretation_notes": "RD −8% (CI) and NNT guidance.",
  "limitations": ["sensitivity to baseline-rate misestimation"],
  "repro_code": {"language":"Python","snippet":"from statsmodels.stats.power import NormalIndPower; power=NormalIndPower(); n=power.solve_power(effect_size=0.08/((0.18*(1-0.18))**0.5), alpha=0.05, power=0.8)"},
  "citations": ["Fleiss 1981; Newcombe 1998"],
  "confidence": 0.83
}

### 3) Template design (Likert scale, repeated measures)
User: "Burnout (MBI short-form) pre/post within subjects."

JSON:
{
  "task":"template",
  "assumptions":["paired design; ordinal items summed to approx. continuous"],
  "method":{"name":"Paired t-test or Wilcoxon signed-rank","justification":"depends on distribution of sum scores","alternatives":["Linear mixed model if >2 timepoints"]},
  "parameters":{"alpha":0.05,"tails":"two","power":0.80,"effect_size":{"type":"Cohen_d","value":0.4,"how_estimated":"literature"},"design":"paired"},
  "sample_size":{"per_group":null,"total":52,"formula_or_reference":"paired t-test d=0.4"},
  "data_template":{
    "columns":[
      {"name":"participant_id","type":"string"},
      {"name":"time","type":"categorical","allowed":["pre","post"]},
      {"name":"mbi_sum","type":"integer","notes":"sum score"},
      {"name":"unit","type":"categorical","allowed":["ICU","ED","MedSurg"]}
    ],
    "id_key":"participant_id","long_vs_wide":"long","file_format":"CSV","example_rows":2
  },
  "analysis_steps":["screen for missing","describe","paired test","effect size dz"],
  "diagnostics":["qq on differences","outliers"],
  "interpretation_notes":"Mean change with CI; discuss clinical relevance.",
  "limitations":["ordinal→interval assumption"],
  "repro_code":{"language":"R","snippet":"t.test(df$mbi_sum[df$time=='post']-df$mbi_sum[df$time=='pre'])"},
  "citations":["Cohen 1988; G*Power formulas"],
  "confidence":0.78
}
"""

STATISTICAL_REASONING_BLOCK = """## Reasoning Approach (Statistical)
- Break down complex questions into design, outcome type, and comparison structure before selecting methods.
- State assumptions early (independence, variance equality, distribution, clustering) and confirm missing inputs.
- Map method choice to assumptions and data shape; propose alternatives when assumptions are shaky.
- Quantify trade-offs (power vs. sample size vs. feasibility) and flag when choices increase bias or Type I/II risk.
- Prefer simpler, robust methods when data quality is limited; justify when more complex models are warranted.
- Expose uncertainties and sensitivity points (effect size estimates, ICC guesses, missing data mechanism).
- Keep recommendations tied to reproducible steps/code; suggest validations/diagnostics to confirm fit.
- This reasoning supports but never replaces math reliability and safety rules above.
"""


class DataAnalysisAgent(BaseAgent):
    """
    Data Analysis Planning Agent - Statistical Expert.

    No external tools - pure statistical reasoning with Pydantic output validation.
    Uses temperature=0.2 for mathematical reliability and max_tokens=1600 for JSON + prose.
    Enables output_schema=DataAnalysisOutput for structured JSON validation.
    """

    def __init__(self):
        # No tools for this agent (pure statistical reasoning)
        tools = self._create_tools()
        super().__init__(
            agent_name="Data Analysis Planner",
            agent_key="data_analysis",
            tools=tools
        )

    def _create_tools(self) -> list:
        """
        Create tools for the data analysis agent.

        Tools include:
        - ReasoningTools: Structured statistical reasoning
        - StatisticsTools: Sample size, power analysis, effect size calculations
        - DocumentReaders: Read CSV/JSON data files for analysis
        """
        from src.services.api_tools import build_tools_list

        # Add ReasoningTools for structured statistical reasoning
        reasoning_tools = ReasoningTools(add_instructions=True)

        # Statistics tools for calculations
        stats_tools = None
        try:
            from src.tools.statistics_tools import create_statistics_tools
            stats_tools = create_statistics_tools()
            print("✅ StatisticsTools available - real calculations enabled")
        except ImportError as e:
            import logging
            logging.getLogger(__name__).warning(f"StatisticsTools not available: {e}")
            print("⚠️ StatisticsTools not available - LLM reasoning mode")

        # Document readers for CSV/JSON data files
        doc_reader_tools = create_document_reader_tools_safe(required=False)

        if doc_reader_tools:
            print("✅ DocumentReaders available - can read CSV/JSON data files")
        else:
            print("⚠️ DocumentReaders unavailable - dependency or initialization issue")

        print("✅ ReasoningTools available - structured statistical reasoning enabled")

        # Build tools list, filtering out None values
        return build_tools_list(reasoning_tools, stats_tools, doc_reader_tools)

    def _create_agent(self) -> Agent:
        """Create and configure the Data Analysis Agent."""
        # Create database for session persistence (inside method, not module-level)
        db = SqliteDb(db_file=get_db_path("data_analysis"))

        reasoning_block = (
            "\n\n" + STATISTICAL_REASONING_BLOCK if is_reasoning_block_enabled() else ""
        )

        return Agent(
            name="Data Analysis Planner",
            role="Statistical expert for nursing and healthcare research",
            model=OpenAIChat(
                id="gpt-4o",
                temperature=0,  # 0 for math reliability (Phase 2 requirement)
                max_tokens=DATA_ANALYSIS_MAX_TOKENS,    # 1600 for JSON + prose
            ),
            tools=self.tools,
            instructions=STATISTICAL_EXPERT_PROMPT
            + reasoning_block
            + "\n\nABSOLUTE LAW #1: MATH RELIABILITY\n- Use temperature=0 for all calculations\n- Double-check all formulas\n- If sample size > 500, mark as INFEASIBLE",
            output_schema=DataAnalysisOutput,  # CRITICAL: Enabled for JSON validation
            markdown=True,
            db=db,
            description="Expert in statistical analysis planning, sample size calculations, test selection, and data template design for nursing quality improvement research.",
            add_history_to_context=True,
            add_datetime_to_context=True,
            pre_hooks=[self._audit_pre_hook],
            post_hooks=[self._audit_post_hook],
        )

    def run_with_grounding_check(self, query: str, **kwargs) -> Any:
        """Execute the agent while forcing a grounding verification pass."""
        # Audit Logging: Query Received
        project_name = kwargs.get("project_name")
        if self.audit_logger:
            self.audit_logger.log_query_received(query, project_name)

        stream_requested = bool(kwargs.get("stream"))
        
        try:
            response = self.agent.run(query, **kwargs)
            
            # Streaming responses are yielded incrementally and cannot be re-verified here.
            if stream_requested:
                return response
                
            self._validate_run_output(response)
            
            # Audit Logging: Response Generated
            if self.audit_logger:
                # For structured output, content might be a Pydantic model
                content_str = str(response.content)
                self.audit_logger.log_response_generated(
                    response=content_str,
                    response_type="success",
                    validation_passed=True
                )
                
            return response
            
        except Exception as e:
            # Audit Logging: Error
            if self.audit_logger:
                self.audit_logger.log_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stack_trace=str(e)
                )
            raise

    def _validate_run_output(self, run_output: Any) -> bool:
        """Ensure statistical feasibility rules are followed."""
        # Content is likely a DataAnalysisOutput object or dict
        content = run_output.content
        
        # If content is a Pydantic model, convert to dict for checking
        data = None
        if hasattr(content, "model_dump"):
            data = content.model_dump()
        elif isinstance(content, dict):
            data = content
            
        if data:
            # Check Sample Size Feasibility
            sample_size = data.get("sample_size", {})
            total_n = sample_size.get("total")
            
            if total_n and isinstance(total_n, (int, float)):
                if total_n > 500:
                    # Log warning: Infeasible sample size
                    if self.audit_logger:
                        self.audit_logger.log_validation_check(
                            "feasibility_check", 
                            True, # We don't block, just log warning
                            {"total_n": total_n, "warning": "Sample size > 500 is likely infeasible"}
                        )
                elif total_n > 300:
                     if self.audit_logger:
                        self.audit_logger.log_validation_check(
                            "feasibility_check", 
                            True, 
                            {"total_n": total_n, "warning": "Sample size > 300 is challenging"}
                        )
        
        return True

    def show_usage_examples(self) -> None:
        """Display usage examples for the Data Analysis Agent."""
        print("=" * 70)
        print("DATA ANALYSIS PLANNING AGENT")
        print("Statistical Expert for Nursing Research")
        print("=" * 70)
        print("\nAgent ready. Example queries:")
        print("- 'Catheter infection rate: baseline 15%, target 8%. Need sample size.'")
        print("- 'Compare pain scores between 2 units, n≈25 per group.'")
        print("- 'Need data template for tracking fall rates monthly.'")
        print("\n" + "=" * 70)


# Create global instance for backward compatibility
# Wrapped in try/except for graceful degradation if initialization fails
try:
    _data_analysis_agent_instance = DataAnalysisAgent()
    data_analysis_agent = _data_analysis_agent_instance.agent
except Exception as _init_error:
    import logging
    logging.error(f"Failed to initialize DataAnalysisAgent: {_init_error}")
    _data_analysis_agent_instance = None
    data_analysis_agent = None
    # Re-raise only if running as main module
    if __name__ == "__main__":
        raise


def get_data_analysis_agent():
    """Factory function to get the DataAnalysisAgent instance.

    Returns:
        DataAnalysisAgent wrapper instance, or None if initialization failed.
    """
    return _data_analysis_agent_instance


if __name__ == "__main__":
    if _data_analysis_agent_instance is not None:
        _data_analysis_agent_instance.run_with_error_handling()
    else:
        print("❌ Agent failed to initialize. Check logs for details.")
