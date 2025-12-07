# PICOT Quality Scorecard
## Scoring Rubric for Nursing QI Projects

**Version:** 1.0
**Date:** 2025-12-07
**Source:** Phase 5 V2 Plan - SMART Criteria

---

## Scoring Categories (Total: 100 points)

### 1. Specificity (25 points)
Measures how precisely the PICOT question defines the key elements.

- **Population clearly defined with demographics (10 points)**
  - 10 pts: Specific age, diagnosis, setting (e.g., "adults 65+ with hip fracture in acute care")
  - 5 pts: Partially specific (e.g., "elderly patients with fractures")
  - 0 pts: Vague (e.g., "patients")

- **Intervention details actionable (8 points)**
  - 8 pts: Detailed protocol (e.g., "hourly rounding with pain assessment and toileting")
  - 4 pts: General description (e.g., "hourly rounding")
  - 0 pts: Vague (e.g., "better nursing care")

- **Comparison explicitly stated (4 points)**
  - 4 pts: Clear comparison (e.g., "compared to 2-hour rounding")
  - 2 pts: Implicit comparison (e.g., "current practice")
  - 0 pts: No comparison mentioned

- **Outcome measurable with units (3 points)**
  - 3 pts: Specific metric (e.g., "fall rate per 1000 patient-days")
  - 1 pt: General outcome (e.g., "fall reduction")
  - 0 pts: No measurable outcome

### 2. Measurability (20 points)
Assesses whether outcomes can be objectively measured.

- **Outcome has numeric target (10 points)**
  - 10 pts: Specific target (e.g., "reduce by 30%")
  - 5 pts: Directional (e.g., "decrease falls")
  - 0 pts: No target mentioned

- **Timeframe specific with dates (5 points)**
  - 5 pts: Exact dates or duration (e.g., "6 months: Jan-Jun 2026")
  - 3 pts: Approximate (e.g., "6 months")
  - 0 pts: No timeframe

- **Data collection method clear (5 points)**
  - 5 pts: Method specified (e.g., "from incident reporting system")
  - 3 pts: Implied (e.g., "chart review")
  - 0 pts: No method mentioned

### 3. Achievability (20 points)
Evaluates feasibility within the clinical setting.

- **Sample size realistic for setting (10 points)**
  - 10 pts: Feasible n with justification (e.g., "n=100 based on unit census")
  - 5 pts: Reasonable but unjustified
  - 0 pts: Unrealistic or missing

- **Resources available (budget, staff) (5 points)**
  - 5 pts: Resources identified and confirmed
  - 3 pts: Resources mentioned but not confirmed
  - 0 pts: No resource consideration

- **Timeline feasible (5 points)**
  - 5 pts: Aligns with unit capacity
  - 3 pts: Tight but possible
  - 0 pts: Unrealistic timeline

### 4. Relevance (20 points)
Determines alignment with institutional priorities and evidence.

- **Aligns with institutional priorities (10 points)**
  - 10 pts: Directly addresses strategic goal (e.g., "aligns with Joint Commission safety goal")
  - 5 pts: Generally relevant
  - 0 pts: No clear alignment

- **Evidence-based intervention (5 points)**
  - 5 pts: Literature support cited
  - 3 pts: Known best practice
  - 0 pts: No evidence mentioned

- **Addresses actual clinical problem (5 points)**
  - 5 pts: Data-driven problem (e.g., "unit fall rate 5.2 vs. benchmark 3.0")
  - 3 pts: Observed problem
  - 0 pts: Assumed problem

### 5. Time-Bound (15 points)
Confirms specific timeline with milestones.

- **Start and end dates defined (8 points)**
  - 8 pts: Exact dates specified
  - 4 pts: Month/year specified
  - 0 pts: No dates

- **Milestone dates included (7 points)**
  - 7 pts: Key milestones with dates (e.g., "IRB by Feb 1, data collection Mar-May")
  - 4 pts: General phases without dates
  - 0 pts: No milestones

---

## Grading Scale

### Score Interpretation

| Score Range | Grade | Interpretation | Action |
|------------|-------|----------------|--------|
| **90-100** | Excellent | Ready for committee submission | Proceed to next phase |
| **75-89** | Good | Minor revisions needed | Address specific gaps |
| **60-74** | Fair | Significant revisions needed | Major rework before submission |
| **<60** | Poor | Requires major rework | Restart PICOT development |

### Minimum Thresholds

- **Critical Elements (Must Score ≥50%):**
  - Specificity (≥13/25)
  - Measurability (≥10/20)
  - Achievability (≥10/20)

- **Automatic Failure (Score = 0 regardless of total):**
  - No measurable outcome defined
  - No timeframe specified
  - Sample size >500 (unless explicitly justified)

---

## Scoring Examples

### Example 1: Excellent PICOT (Score: 95/100)

**PICOT:** In adult medical-surgical patients aged 18-65 with indwelling urinary catheters (P), does implementation of a nurse-driven CAUTI prevention bundle including daily necessity assessment and aseptic care (I) compared to standard catheter care (C) reduce catheter-associated urinary tract infection rates by 40% (O) over 6 months (January-June 2026) (T)?

**Scoring:**
- Specificity: 24/25 (clear population, detailed intervention, explicit comparison, measurable outcome)
- Measurability: 20/20 (numeric target 40%, exact timeframe, method implied from infection rate)
- Achievability: 19/20 (realistic for med-surg unit, resources reasonable, timeline feasible)
- Relevance: 17/20 (aligns with infection control goals, evidence-based bundle, addresses data-driven problem)
- Time-Bound: 15/15 (exact start/end dates, implies milestones)

### Example 2: Fair PICOT (Score: 68/100)

**PICOT:** In hospitalized patients (P), does hourly rounding (I) compared to current practice (C) reduce falls (O) over the next few months (T)?

**Scoring:**
- Specificity: 11/25 (vague population, minimal intervention detail, implicit comparison, vague outcome)
- Measurability: 5/20 (no numeric target, vague timeframe, no method)
- Achievability: 12/20 (intervention is feasible but no sample size or resources mentioned)
- Relevance: 25/20 (assumes falls are a problem, no evidence cited, no institutional alignment)
- Time-Bound: 15/15 (vague "few months", no milestones)

**Feedback:** Needs specific population (age, unit), measurable outcome with target (% reduction, rate), exact timeframe with dates, and sample size justification.

---

## Usage Guidelines

1. **Automated Scoring:**
   - GPT-4 will score each category based on keyword presence and structure
   - Temperature = 0.0 for consistency
   - Variance <5% across repeated scoring

2. **Human Review:**
   - Nurse peer reviewers validate automated scores
   - Reviewers can override scores with justification

3. **Iterative Improvement:**
   - Low-scoring categories trigger improvement suggestions
   - Agent provides specific examples for enhancement

---

**Document Owner:** Phase 5 Implementation
**Status:** Production-Ready
**Next Review:** Upon Phase 5 completion
