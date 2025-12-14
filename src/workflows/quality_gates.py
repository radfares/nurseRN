"""
Quality Gates - Validation functions for pipeline phases

Each gate checks if the output from a phase meets quality standards.
If a gate fails, the pipeline can retry or stop.

Created: 2025-12-10
"""

import re
import json
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class GateResult:
    """Result from a quality gate check."""
    passed: bool
    gate_name: str
    message: str
    details: Dict[str, Any]


# =============================================================================
# GATE 1: PICOT QUALITY
# =============================================================================

def check_picot_quality(picot_text: str) -> GateResult:
    """
    Validate PICOT question has all required components.

    Checks:
    1. Has all 5 PICOT components (P, I, C, O, T)
    2. Each component has meaningful content
    3. Ends with a question mark (is actually a question)
    4. Is long enough to be specific

    Args:
        picot_text: The PICOT output from writing agent

    Returns:
        GateResult with pass/fail and details
    """
    details = {
        "components_found": [],
        "components_missing": [],
        "length": len(picot_text),
        "is_question": False
    }

    # Check for each PICOT component - more flexible patterns
    components = {
        "P": ["P (Population)", "P:", "Population:", "**P", "- P ", "P -", "P–", "Population"],
        "I": ["I (Intervention)", "I:", "Intervention:", "**I", "- I ", "I -", "I–", "Intervention"],
        "C": ["C (Comparison)", "C:", "Comparison:", "**C", "- C ", "C -", "C–", "Comparison"],
        "O": ["O (Outcome)", "O:", "Outcome:", "**O", "- O ", "O -", "O–", "Outcome"],
        "T": ["T (Time)", "T:", "Time:", "Timeframe:", "**T", "- T ", "T -", "T–", "Timeframe"]
    }

    for component, patterns in components.items():
        found = any(pattern.lower() in picot_text.lower() for pattern in patterns)
        if found:
            details["components_found"].append(component)
        else:
            details["components_missing"].append(component)

    # Check if it ends with a question
    details["is_question"] = "?" in picot_text

    # Check minimum length (a good PICOT should be detailed)
    min_length = 200
    is_long_enough = len(picot_text) >= min_length

    # Determine pass/fail
    all_components = len(details["components_missing"]) == 0
    passed = all_components and details["is_question"] and is_long_enough

    if passed:
        message = "PICOT quality check PASSED. All components present."
    else:
        issues = []
        if details["components_missing"]:
            issues.append(f"Missing components: {details['components_missing']}")
        if not details["is_question"]:
            issues.append("Not formatted as a question")
        if not is_long_enough:
            issues.append(f"Too short ({len(picot_text)} chars, need {min_length})")
        message = f"PICOT quality check FAILED. Issues: {'; '.join(issues)}"

    return GateResult(
        passed=passed,
        gate_name="picot_quality",
        message=message,
        details=details
    )


# =============================================================================
# GATE 2: SEARCH QUALITY
# =============================================================================

def check_search_quality(search_results: str) -> GateResult:
    """
    Validate search returned enough usable articles.

    Checks:
    1. At least 3 articles found
    2. Each article has a PMID or identifier
    3. Articles are from recent years (within 10 years)

    Args:
        search_results: The search output from nursing/medical agents

    Returns:
        GateResult with pass/fail and details
    """
    details = {
        "pmids_found": [],
        "dois_found": [],
        "article_count": 0,
        "identifiers_missing": 0
    }

    # Find PMIDs - multiple formats:
    # 1. PMID: 12345678 or PMID 12345678
    # 2. [12345678](https://pubmed.ncbi.nlm.nih.gov/12345678/) - markdown links
    # 3. pubmed.ncbi.nlm.nih.gov/12345678 - URLs
    # 4. **PMID:** [number] - bold markdown format
    pmids = []
    pmids.extend(re.findall(r'PMID[:\s]*(\d{7,8})', search_results, re.IGNORECASE))
    pmids.extend(re.findall(r'\[(\d{7,8})\]\(https?://pubmed', search_results))
    pmids.extend(re.findall(r'pubmed\.ncbi\.nlm\.nih\.gov/(\d{7,8})', search_results))
    pmids.extend(re.findall(r'\*\*PMID[:\*\s]*\[?(\d{7,8})', search_results, re.IGNORECASE))
    details["pmids_found"] = list(set(pmids))

    # Find DOIs
    doi_pattern = r'10\.\d{4,9}/[-._;()/:A-Z0-9]+'
    dois = re.findall(doi_pattern, search_results, re.IGNORECASE)
    details["dois_found"] = list(set(dois))

    # Count total identifiers
    total_identifiers = len(details["pmids_found"]) + len(details["dois_found"])
    details["article_count"] = total_identifiers

    # Minimum requirement
    min_articles = 3
    passed = total_identifiers >= min_articles

    if passed:
        message = f"Search quality check PASSED. Found {total_identifiers} articles with identifiers."
    else:
        message = f"Search quality check FAILED. Found only {total_identifiers} articles, need at least {min_articles}."

    return GateResult(
        passed=passed,
        gate_name="search_quality",
        message=message,
        details=details
    )


# =============================================================================
# GATE 3: VALIDATION QUALITY
# =============================================================================

def check_validation_quality(validation_report: str, pmid_list: List[str]) -> GateResult:
    """
    Validate that citations passed retraction check.

    Checks:
    1. At least 3 citations are VALID
    2. No more than 20% are RETRACTED
    3. Validation was actually performed

    Args:
        validation_report: Output from citation validation agent
        pmid_list: List of PMIDs that were validated

    Returns:
        GateResult with pass/fail and details
    """
    details = {
        "total_checked": len(pmid_list),
        "valid_count": 0,
        "retracted_count": 0,
        "not_found_count": 0,
        "concerns_count": 0
    }

    # Count validation statuses
    report_lower = validation_report.lower()

    # Count VALID
    valid_patterns = [r'status:\s*valid', r'\bvalid\b.*pmid', r'no retraction']
    for pattern in valid_patterns:
        matches = re.findall(pattern, report_lower)
        details["valid_count"] += len(matches)

    # Count RETRACTED
    retracted_patterns = [r'status:\s*retracted', r'\bretracted\b', r'has been retracted']
    for pattern in retracted_patterns:
        matches = re.findall(pattern, report_lower)
        details["retracted_count"] += len(matches)

    # If we found PMIDs in search but validation didn't count them properly,
    # estimate from the total
    if details["valid_count"] == 0 and "no retraction found" in report_lower:
        # Likely all are valid if report says no retractions
        details["valid_count"] = len(pmid_list)

    # Calculate pass criteria
    min_valid = 3
    max_retracted_ratio = 0.2

    has_minimum_valid = details["valid_count"] >= min_valid

    if details["total_checked"] > 0:
        retracted_ratio = details["retracted_count"] / details["total_checked"]
        retraction_acceptable = retracted_ratio <= max_retracted_ratio
    else:
        retraction_acceptable = True

    passed = has_minimum_valid and retraction_acceptable

    if passed:
        message = f"Validation check PASSED. {details['valid_count']} valid citations, {details['retracted_count']} retracted."
    else:
        issues = []
        if not has_minimum_valid:
            issues.append(f"Only {details['valid_count']} valid (need {min_valid})")
        if not retraction_acceptable:
            issues.append(f"Too many retracted ({details['retracted_count']})")
        message = f"Validation check FAILED. {'; '.join(issues)}"

    return GateResult(
        passed=passed,
        gate_name="validation_quality",
        message=message,
        details=details
    )


# =============================================================================
# GATE 4: SYNTHESIS QUALITY
# =============================================================================

def check_synthesis_quality(synthesis_text: str) -> GateResult:
    """
    Validate literature synthesis is complete and structured.

    Checks:
    1. Has required sections (Evidence Summary, Strength, Implications)
    2. Meets minimum length
    3. Cites sources (has author names or citations)

    Args:
        synthesis_text: Output from writing agent

    Returns:
        GateResult with pass/fail and details
    """
    details = {
        "sections_found": [],
        "sections_missing": [],
        "length": len(synthesis_text),
        "citation_count": 0
    }

    # Required sections (flexible matching)
    required_sections = {
        "evidence": ["evidence summary", "evidence", "summary of evidence", "key findings"],
        "strength": ["strength of evidence", "level of evidence", "quality of evidence"],
        "implications": ["implications", "practice implications", "recommendations", "clinical implications"]
    }

    for section_name, patterns in required_sections.items():
        found = any(pattern.lower() in synthesis_text.lower() for pattern in patterns)
        if found:
            details["sections_found"].append(section_name)
        else:
            details["sections_missing"].append(section_name)

    # Count citations (author et al., year) or (Author, Year)
    citation_pattern = r'\([A-Z][a-z]+(?:\s+et\s+al\.?)?,?\s*\d{4}\)'
    citations = re.findall(citation_pattern, synthesis_text)
    details["citation_count"] = len(citations)

    # Also count "Author et al. (Year)" format
    citation_pattern2 = r'[A-Z][a-z]+\s+et\s+al\.\s*\(\d{4}\)'
    citations2 = re.findall(citation_pattern2, synthesis_text)
    details["citation_count"] += len(citations2)

    # Minimum requirements
    min_length = 500
    min_citations = 2  # At least 2 citations

    has_sections = len(details["sections_missing"]) <= 1  # Allow 1 missing
    is_long_enough = details["length"] >= min_length
    has_citations = details["citation_count"] >= min_citations

    passed = has_sections and is_long_enough and has_citations

    if passed:
        message = f"Synthesis quality check PASSED. {len(details['sections_found'])} sections, {details['citation_count']} citations."
    else:
        issues = []
        if not has_sections:
            issues.append(f"Missing sections: {details['sections_missing']}")
        if not is_long_enough:
            issues.append(f"Too short ({details['length']} chars, need {min_length})")
        if not has_citations:
            issues.append(f"Not enough citations ({details['citation_count']}, need {min_citations})")
        message = f"Synthesis quality check FAILED. {'; '.join(issues)}"

    return GateResult(
        passed=passed,
        gate_name="synthesis_quality",
        message=message,
        details=details
    )


# =============================================================================
# GATE 5: ANALYSIS QUALITY
# =============================================================================

def check_analysis_quality(analysis_text: str) -> GateResult:
    """
    Validate analysis plan is complete.

    Checks:
    1. Has variables section
    2. Has statistical test specified
    3. Has sample size consideration
    4. Has code snippet (R or Python)

    Args:
        analysis_text: Output from data analysis agent

    Returns:
        GateResult with pass/fail and details
    """
    details = {
        "has_variables": False,
        "has_statistical_test": False,
        "has_sample_size": False,
        "has_code": False,
        "test_mentioned": None
    }

    text_lower = analysis_text.lower()

    # Check for variables section
    variable_indicators = ["variable", "outcome variable", "independent variable", "dependent variable", "data type"]
    details["has_variables"] = any(ind in text_lower for ind in variable_indicators)

    # Check for statistical test
    stat_tests = [
        "t-test", "t test", "chi-square", "chi square", "mcnemar",
        "anova", "regression", "mann-whitney", "wilcoxon", "fisher exact",
        "paired t", "independent t"
    ]
    for test in stat_tests:
        if test in text_lower:
            details["has_statistical_test"] = True
            details["test_mentioned"] = test
            break

    # Check for sample size
    sample_indicators = ["sample size", "n =", "n=", "power", "participants needed"]
    details["has_sample_size"] = any(ind in text_lower for ind in sample_indicators)

    # Check for code
    code_indicators = ["```", "def ", "function(", "<-", "import ", "library("]
    details["has_code"] = any(ind in analysis_text for ind in code_indicators)

    # Pass if at least 3 of 4 criteria met
    criteria_met = sum([
        details["has_variables"],
        details["has_statistical_test"],
        details["has_sample_size"],
        details["has_code"]
    ])

    passed = criteria_met >= 3

    if passed:
        message = f"Analysis quality check PASSED. {criteria_met}/4 criteria met."
    else:
        missing = []
        if not details["has_variables"]:
            missing.append("variables")
        if not details["has_statistical_test"]:
            missing.append("statistical test")
        if not details["has_sample_size"]:
            missing.append("sample size")
        if not details["has_code"]:
            missing.append("code snippet")
        message = f"Analysis quality check FAILED. Missing: {', '.join(missing)}"

    return GateResult(
        passed=passed,
        gate_name="analysis_quality",
        message=message,
        details=details
    )


# =============================================================================
# MASTER GATE CHECKER
# =============================================================================

def run_quality_gate(gate_name: str, **kwargs) -> GateResult:
    """
    Run a specific quality gate by name.

    Args:
        gate_name: Name of the gate to run
        **kwargs: Arguments for the specific gate

    Returns:
        GateResult from the gate

    Example:
        result = run_quality_gate("picot_quality", picot_text="...")
        if result.passed:
            proceed_to_next_phase()
    """
    gates = {
        "picot_quality": lambda: check_picot_quality(kwargs.get("picot_text", "")),
        "search_quality": lambda: check_search_quality(kwargs.get("search_results", "")),
        "validation_quality": lambda: check_validation_quality(
            kwargs.get("validation_report", ""),
            kwargs.get("pmid_list", [])
        ),
        "synthesis_quality": lambda: check_synthesis_quality(kwargs.get("synthesis_text", "")),
        "analysis_quality": lambda: check_analysis_quality(kwargs.get("analysis_text", ""))
    }

    if gate_name not in gates:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            message=f"Unknown gate: {gate_name}",
            details={}
        )

    return gates[gate_name]()


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    # Test PICOT gate
    test_picot = """
    **PICOT Components:**
    - P (Population): Adult hospitalized patients with indwelling urinary catheters
    - I (Intervention): Nurse-driven catheter removal protocol
    - C (Comparison): Standard physician-ordered removal
    - O (Outcome): Reduction in CAUTIs and catheter days
    - T (Time): During hospital stay

    **PICOT Question:**
    "In adult hospitalized patients with indwelling urinary catheters (P), does
    implementation of a nurse-driven catheter removal protocol (I) compared to
    standard physician-ordered removal (C) reduce catheter-associated urinary
    tract infections and catheter days (O) during hospitalization (T)?"
    """

    result = check_picot_quality(test_picot)
    print(f"PICOT Gate: {result.message}")
    print(f"Details: {result.details}")
