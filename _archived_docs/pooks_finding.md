# Pooks Finding: Complete Agents Folder Analysis

**Analysis Date**: 2025-12-07
**Analyst**: Claude Opus 4.5
**Scope**: Complete decomposition of `/Users/hdz/nurseRN/agents/` folder and its external connections

---

## Executive Summary

The `agents/` folder contains a **7-agent multi-agent system** for nursing research support, built on a **BaseAgent inheritance pattern** with the **Agno framework**. All agents share common infrastructure for logging, error handling, and audit trails, while each specializes in specific research tasks.

**Key Finding**: The system is designed with **strict grounding policies** to prevent AI hallucination of citations - every agent has validation hooks that verify tool outputs before presenting to users.

---

## 1. Agents Folder Structure

```
agents/
├── __init__.py                        (38 lines) - Package exports
├── base_agent.py                      (360 lines) - Abstract base class
├── nursing_research_agent.py          (732 lines) - Primary healthcare research
├── medical_research_agent.py          (578 lines) - PubMed specialist
├── academic_research_agent.py         (283 lines) - ArXiv specialist
├── research_writing_agent.py          (333 lines) - Writing/synthesis
├── nursing_project_timeline_agent.py  (296 lines) - Milestone tracking
├── data_analysis_agent.py             (444 lines) - Statistical planning
└── citation_validation_agent.py       (331 lines) - Evidence grading
```

**Total**: ~3,395 lines of Python across 9 files

---

## 2. Agent Inheritance Hierarchy

```
                    ┌─────────────────────────────────────────┐
                    │            BaseAgent (ABC)              │
                    │  agents/base_agent.py:97-337            │
                    │                                         │
                    │  Abstract Methods:                      │
                    │  - _create_agent() → Agent              │
                    │  - show_usage_examples()                │
                    │                                         │
                    │  Provided Features:                     │
                    │  - Logging (setup_agent_logging)        │
                    │  - Error handling                       │
                    │  - Audit logging (AuditLogger)          │
                    │  - Pre/Post hooks for validation        │
                    │  - print_response() adapter             │
                    │  - print_watermark() clinical disclaimer│
                    └───────────────────┬─────────────────────┘
                                        │
            ┌───────────────────────────┼───────────────────────────┐
            │                           │                           │
            ▼                           ▼                           ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│ NursingResearchAgent  │  │ MedicalResearchAgent  │  │ AcademicResearchAgent │
│ (Primary Research)    │  │ (PubMed)              │  │ (ArXiv)               │
│                       │  │                       │  │                       │
│ Tools: 9+             │  │ Tools: 2              │  │ Tools: 2              │
│ - PubMed (PRIMARY)    │  │ - PubMed              │  │ - ArXiv               │
│ - ClinicalTrials      │  │ - LiteratureTools     │  │ - LiteratureTools     │
│ - medRxiv             │  │                       │  │                       │
│ - Semantic Scholar    │  │ Grounding: STRICT     │  │ Grounding: STRICT     │
│ - CORE                │  │ (blocks direct run()) │  │                       │
│ - DOAJ                │  │                       │  │                       │
│ - SafetyTools         │  │                       │  │                       │
│ - SerpAPI             │  │                       │  │                       │
│ - LiteratureTools     │  │                       │  │                       │
└───────────────────────┘  └───────────────────────┘  └───────────────────────┘
            │                           │                           │
            │         ┌─────────────────┼─────────────────┐         │
            │         │                 │                 │         │
            ▼         ▼                 ▼                 ▼         ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│ ResearchWritingAgent  │  │ ProjectTimelineAgent  │  │ DataAnalysisAgent     │
│ (No tools)            │  │                       │  │ (No tools)            │
│                       │  │ Tools: 1              │  │                       │
│ Pure GPT-4o writing   │  │ - MilestoneTools      │  │ Pure GPT-4o stats     │
│                       │  │                       │  │ Pydantic output schema│
│                       │  │ Model: GPT-4o-mini    │  │ Temperature: 0        │
│                       │  │ (cost-optimized)      │  │                       │
└───────────────────────┘  └───────────────────────┘  └───────────────────────┘
                                        │
                                        ▼
                            ┌───────────────────────┐
                            │CitationValidationAgent│
                            │                       │
                            │ Tools: 1              │
                            │ - ValidationTools     │
                            │                       │
                            │ Evidence grading      │
                            │ Retraction detection  │
                            │ Quality scoring       │
                            └───────────────────────┘
```

---

## 3. Agent-to-Agent Connections

### 3.1 Direct Connections (None at runtime)

**Key Finding**: Agents do NOT directly call each other at runtime. They are designed as **independent microservices** that communicate through:
1. **Shared project database** (`project.db`)
2. **Orchestration layer** (`run_nursing_project.py`)
3. **Workflow templates** (`src/workflows/`)

### 3.2 Indirect Connections via Shared Resources

```
                    ┌──────────────────────────────────────┐
                    │         PROJECT DATABASE             │
                    │   data/projects/{name}/project.db    │
                    │                                      │
                    │   Tables:                            │
                    │   - literature_findings              │
                    │   - milestones                       │
                    │   - picot_versions                   │
                    │   - analysis_plans                   │
                    │   - writing_drafts                   │
                    │   - conversations                    │
                    │   - documents                        │
                    └─────────────────┬────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
         ▼                            ▼                            ▼
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│ Research Agents │        │ Timeline Agent  │        │ Citation Agent  │
│ Write to:       │        │ Reads/Writes:   │        │ Reads:          │
│ literature_     │        │ milestones      │        │ literature_     │
│ findings        │        │                 │        │ findings        │
└─────────────────┘        └─────────────────┘        └─────────────────┘
         │                            │                            │
         └────────────────────────────┴────────────────────────────┘
                                      │
                          ┌───────────▼───────────┐
                          │   Writing Agent       │
                          │   Reads:              │
                          │   - literature_findings│
                          │   - picot_versions    │
                          │   Writes:             │
                          │   - writing_drafts    │
                          └───────────────────────┘
```

### 3.3 Workflow-Level Connections

The **ValidatedResearchWorkflow** demonstrates multi-agent collaboration:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VALIDATED RESEARCH WORKFLOW                               │
│                    src/workflows/validated_research_workflow.py              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
    Step 1                Step 2              Step 3              Step 4
    ┌───────────┐         ┌───────────┐       ┌───────────┐       ┌───────────┐
    │ Nursing   │ ──────▶ │ Medical   │ ────▶ │ Citation  │ ────▶ │ Research  │
    │ Research  │ PICOT   │ Research  │ Search│ Validation│ Filter│ Writing   │
    │ Agent     │ output  │ Agent     │ results│ Agent    │ valid │ Agent     │
    └───────────┘         └───────────┘       └───────────┘ only  └───────────┘
                                                                        │
                                                                        ▼
                                                               Final Literature
                                                               Review Output
```

---

## 4. External Dependencies Map

### 4.1 Configuration Layer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           agent_config.py                                   │
│                           (111 lines)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   DATABASE_PATHS = {                                                        │
│     "nursing_research": "tmp/nursing_research_agent.db",                    │
│     "medical_research": "tmp/medical_research_agent.db",                    │
│     "academic_research": "tmp/academic_research_agent.db",                  │
│     "research_writing": "tmp/research_writing_agent.db",                    │
│     "project_timeline": "tmp/project_timeline_agent.db",                    │
│     "data_analysis": "tmp/data_analysis_agent.db",                          │
│     "citation_validation": "tmp/citation_validation_agent.db"               │
│   }                                                                         │
│                                                                             │
│   DEFAULT_MODELS = {                                                        │
│     Most agents: "gpt-4o"                                                   │
│     project_timeline: "gpt-4o-mini" (cost optimization)                     │
│   }                                                                         │
│                                                                             │
│   Helper Functions:                                                         │
│   - get_db_path(agent_name) → str                                           │
│   - get_model_id(agent_name) → str                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ Used by ALL agents
                                      ▼
                         ┌─────────────────────────┐
                         │    BaseAgent.__init__   │
                         │    get_db_path(key)     │
                         └─────────────────────────┘
```

### 4.2 API Tools Layer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       src/services/api_tools.py                             │
│                       (862 lines)                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Safe Tool Creation Functions:                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ create_pubmed_tools_safe()      → PubmedTools + CircuitBreaker      │   │
│   │ create_arxiv_tools_safe()       → ArxivTools + CircuitBreaker       │   │
│   │ create_serp_tools_safe()        → SerpApiTools + CircuitBreaker     │   │
│   │ create_exa_tools_safe()         → ExaTools + CircuitBreaker         │   │
│   │ create_clinicaltrials_tools_safe() → ClinicalTrialsTools            │   │
│   │ create_medrxiv_tools_safe()     → MedRxivTools                      │   │
│   │ create_semantic_scholar_tools_safe() → SemanticScholarTools         │   │
│   │ create_core_tools_safe()        → CoreTools                         │   │
│   │ create_doaj_tools_safe()        → DoajTools                         │   │
│   │ create_milestone_tools_safe()   → MilestoneTools                    │   │
│   │ create_safety_tools_safe()      → SafetyTools                       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Utility Functions:                                                        │
│   - build_tools_list(*tools) → filters None values                          │
│   - get_api_status() → dict of API availability                             │
│   - apply_in_place_wrapper() → circuit breaker wrapping                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.3 Audit Logging Layer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    src/services/agent_audit_logger.py                       │
│                    (473 lines)                                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   class AuditLogger:                                                        │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ Log Methods:                                                        │   │
│   │ - log_query_received(query)                                         │   │
│   │ - log_tool_call(tool_name, method, params)                          │   │
│   │ - log_tool_result(tool_name, result)                                │   │
│   │ - log_validation_check(check_type, passed, details)                 │   │
│   │ - log_grounding_check(pmids_cited, pmids_verified, hallucination)   │   │
│   │ - log_response_generated(response, type, validation_passed)         │   │
│   │ - log_error(type, message, stack_trace)                             │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   Output: .claude/agent_audit_logs/{agent_key}_audit.jsonl                  │
│   Features:                                                                 │
│   - Thread-safe writes                                                      │
│   - API key redaction (_sanitize_entry)                                     │
│   - Log rotation at 10MB                                                    │
│   - Response hashing for verification                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.4 Custom Tools Layer

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CUSTOM TOOLS (src/tools/)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ LiteratureTools (src/tools/literature_tools.py)                     │   │
│   │ ─────────────────────────────────────────────────────────────────   │   │
│   │ Used by: NursingResearchAgent, MedicalResearchAgent,                │   │
│   │          AcademicResearchAgent                                      │   │
│   │                                                                     │   │
│   │ Methods:                                                            │   │
│   │ - save_finding(agent_source, title, pmid, doi, abstract, ...)       │   │
│   │ - get_saved_findings(agent_source, selected_only, limit)            │   │
│   │ - mark_finding_selected(finding_id, selected, notes)                │   │
│   │ - search_findings(query, limit)                                     │   │
│   │ - delete_finding(finding_id)                                        │   │
│   │ - get_finding_count()                                               │   │
│   │                                                                     │   │
│   │ Target Table: literature_findings                                   │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ MilestoneTools (src/tools/milestone_tools.py)                       │   │
│   │ ─────────────────────────────────────────────────────────────────   │   │
│   │ Used by: ProjectTimelineAgent                                       │   │
│   │                                                                     │   │
│   │ Methods:                                                            │   │
│   │ - get_all_milestones()                                              │   │
│   │ - get_next_milestone()                                              │   │
│   │ - get_milestones_by_date_range(start, end)                          │   │
│   │ - update_milestone_status(id, status)                               │   │
│   │ - add_milestone(name, date, description, deliverables)              │   │
│   │                                                                     │   │
│   │ Target Table: milestones                                            │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │ CitationValidationTools (src/tools/citation_validation_tools.py)    │   │
│   │ ─────────────────────────────────────────────────────────────────   │   │
│   │ Used by: CitationValidationAgent                                    │   │
│   │                                                                     │   │
│   │ Methods:                                                            │   │
│   │ - grade_evidence_level(abstract, publication_type)                  │   │
│   │ - check_retraction_status(pmid)                                     │   │
│   │ - assess_currency(publication_date, max_age_years)                  │   │
│   │ - validate_single_article(pmid, title, abstract, date, type)        │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Complete Connection Diagram

```
                                    EXTERNAL APIS
                    ┌─────────────────────────────────────────────┐
                    │  PubMed  │  ArXiv  │  SerpAPI  │  OpenFDA   │
                    │  (Free)  │ (Free)  │  (Paid)   │  (Free)    │
                    └────┬────────┬────────┬────────────┬─────────┘
                         │        │        │            │
                         ▼        ▼        ▼            ▼
                    ┌─────────────────────────────────────────────┐
                    │           CIRCUIT BREAKERS                  │
                    │      src/services/circuit_breaker.py        │
                    │  (5 failure threshold, 60s cooldown)        │
                    └────┬────────┬────────┬────────────┬─────────┘
                         │        │        │            │
                         ▼        ▼        ▼            ▼
                    ┌─────────────────────────────────────────────┐
                    │            API TOOLS LAYER                  │
                    │         src/services/api_tools.py           │
                    │    (Safe wrappers + HTTP caching 24hr)      │
                    └────────────────────┬────────────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────┐
              │                          │                          │
              ▼                          ▼                          ▼
    ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
    │  Agno Tools     │      │  Custom Tools   │      │  Safety Tools   │
    │  ────────────   │      │  ────────────   │      │  ────────────   │
    │  PubmedTools    │      │  LiteratureTools│      │  SafetyTools    │
    │  ArxivTools     │      │  MilestoneTools │      │  (OpenFDA)      │
    │  SerpApiTools   │      │  ValidationTools│      │                 │
    │  ExaTools       │      │                 │      │                 │
    └────────┬────────┘      └────────┬────────┘      └────────┬────────┘
             │                        │                        │
             └────────────────────────┼────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────────────┐
                    │              AGENT LAYER                    │
                    │                                             │
                    │   BaseAgent (Inheritance)                   │
                    │   ├── NursingResearchAgent (9 tools)        │
                    │   ├── MedicalResearchAgent (2 tools)        │
                    │   ├── AcademicResearchAgent (2 tools)       │
                    │   ├── ResearchWritingAgent (0 tools)        │
                    │   ├── ProjectTimelineAgent (1 tool)         │
                    │   ├── DataAnalysisAgent (0 tools)           │
                    │   └── CitationValidationAgent (1 tool)      │
                    │                                             │
                    │   Features from BaseAgent:                  │
                    │   - Logging via setup_agent_logging()       │
                    │   - Audit via AuditLogger                   │
                    │   - Pre/Post hooks (_audit_pre_hook, etc.)  │
                    │   - Error handling (run_with_error_handling)│
                    │   - Clinical watermark                      │
                    └────────────────────┬────────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         │                               │                               │
         ▼                               ▼                               ▼
┌─────────────────┐          ┌─────────────────────┐          ┌─────────────────┐
│  AUDIT LOGGING  │          │   PROJECT DATABASE  │          │  AGENT SESSIONS │
│  ────────────   │          │   ─────────────     │          │  ────────────   │
│  .claude/agent_ │          │   data/projects/    │          │  tmp/*.db       │
│  audit_logs/    │          │   {name}/project.db │          │  (per-agent)    │
│  *.jsonl        │          │                     │          │                 │
│                 │          │  Tables:            │          │  Stores:        │
│  Stores:        │          │  - literature_      │          │  - Conversation │
│  - Queries      │          │    findings         │          │    history      │
│  - Tool calls   │          │  - milestones       │          │  - Context      │
│  - Validations  │          │  - picot_versions   │          │                 │
│  - Responses    │          │  - analysis_plans   │          │                 │
│  - Errors       │          │  - writing_drafts   │          │                 │
│                 │          │  - conversations    │          │                 │
└─────────────────┘          │  - documents        │          └─────────────────┘
                             └──────────┬──────────┘
                                        │
                                        │ project_manager.py
                                        ▼
                    ┌─────────────────────────────────────────────┐
                    │           PROJECT MANAGER                   │
                    │         project_manager.py (698 lines)      │
                    │                                             │
                    │   Functions:                                │
                    │   - get_project_manager() (singleton)       │
                    │   - create_project(name, add_milestones)    │
                    │   - list_projects()                         │
                    │   - set_active_project(name)                │
                    │   - get_active_project()                    │
                    │   - get_project_connection(name)            │
                    │   - archive_project(name)                   │
                    │                                             │
                    │   Active project tracked in:                │
                    │   data/.active_project (7 bytes file)       │
                    └────────────────────┬────────────────────────┘
                                         │
                                         ▼
                    ┌─────────────────────────────────────────────┐
                    │           MAIN ENTRY POINT                  │
                    │       run_nursing_project.py (644 lines)    │
                    │                                             │
                    │   User Interface:                           │
                    │   - show_welcome()                          │
                    │   - show_clinical_disclaimer() ← REQUIRED   │
                    │   - project_management_loop()               │
                    │   - agent_selection_loop()                  │
                    │   - run_agent_interaction()                 │
                    │   - run_smart_mode() (auto-routing)         │
                    │   - run_workflow_mode() (templates)         │
                    │                                             │
                    │   Imports ALL agents:                       │
                    │   - nursing_research_agent                  │
                    │   - get_medical_research_agent()            │
                    │   - academic_research_agent                 │
                    │   - research_writing_agent                  │
                    │   - project_timeline_agent                  │
                    │   - data_analysis_agent                     │
                    │   - get_citation_validation_agent()         │
                    └─────────────────────────────────────────────┘
```

---

## 6. Agent Feature Matrix

| Agent | Tools | Model | Temperature | DB Access | Grounding | Validation |
|-------|-------|-------|-------------|-----------|-----------|------------|
| NursingResearchAgent | 9 (PubMed, ClinicalTrials, medRxiv, SemanticScholar, CORE, DOAJ, Safety, SerpAPI, Literature) | gpt-4o | 0 | Literature | PMID verification | `_validate_run_output()` |
| MedicalResearchAgent | 2 (PubMed, Literature) | gpt-4o | 0 | Literature | PMID verification, blocks run() | `run_with_grounding_check()` |
| AcademicResearchAgent | 2 (ArXiv, Literature) | gpt-4o | 0 | Literature | ArXiv ID verification | `_validate_run_output()` |
| ResearchWritingAgent | 0 | gpt-4o | 0 | None | No citation generation | `_validate_run_output()` |
| ProjectTimelineAgent | 1 (Milestone) | gpt-4o-mini | 0 | Milestones | Database grounding | `_validate_run_output()` |
| DataAnalysisAgent | 0 | gpt-4o | 0 | None | Sample size feasibility | `_validate_run_output()` |
| CitationValidationAgent | 1 (Validation) | gpt-4o | 0 | Literature | Evidence grading | `validate_articles()` |

---

## 7. Key Design Patterns

### 7.1 Anti-Hallucination Pattern (Critical)

Every research agent implements grounding checks:

```python
# MedicalResearchAgent (most strict)
def run(self, *args, **kwargs):
    raise RuntimeError("Direct run() is disabled. Use run_with_grounding_check()")

def run_with_grounding_check(self, query: str, ...):
    response = self.agent.run(query)
    cited_pmids = extract_pmids(response)           # From response text
    verified_pmids = extract_pmids_from_tools(...)  # From tool outputs

    unverified = cited_pmids - verified_pmids
    if unverified:
        return {"content": "SAFETY SYSTEM ACTIVATED", "hallucination_detected": True}
```

### 7.2 Lazy Initialization Pattern

```python
# Global instance with lazy init (citation_validation_agent.py:300-319)
_citation_validation_agent_instance = None

def get_citation_validation_agent():
    global _citation_validation_agent_instance
    if _citation_validation_agent_instance is None:
        _citation_validation_agent_instance = CitationValidationAgent()
    return _citation_validation_agent_instance
```

### 7.3 Safe Tool Creation Pattern

```python
# All tools wrapped with try/except + circuit breaker
def _create_tools(self) -> list:
    pubmed_tool = create_pubmed_tools_safe(required=False)  # Returns None if fail
    tools = build_tools_list(pubmed_tool, ...)              # Filters None
    return tools
```

### 7.4 Audit Hook Pattern

```python
# BaseAgent pre/post hooks (base_agent.py:186-218)
return Agent(
    ...
    pre_hooks=[self._audit_pre_hook],   # Logs query received
    post_hooks=[self._audit_post_hook],  # Logs response + validation
)
```

---

## 8. Data Flow Summary

```
USER QUERY
    │
    ▼
run_nursing_project.py (CLI Interface)
    │
    ├──▶ Smart Mode → QueryRouter → Intent Detection → Agent Selection
    │
    └──▶ Direct Selection → Agent from agent_map
                │
                ▼
           BaseAgent.print_response()
                │
                ▼
        Agent._audit_pre_hook() → logs query
                │
                ▼
        Agent.agent.run(query) → OpenAI API
                │
                ▼
        Tools execute (PubMed, ArXiv, etc.)
                │
                ▼
        Agent._validate_run_output() → grounding check
                │
                ├── PASS → Agent._audit_post_hook() → logs response
                │
                └── FAIL → Response replaced with refusal message
                        │
                        ▼
                BaseAgent.print_watermark() → clinical disclaimer
                        │
                        ▼
                   OUTPUT TO USER
```

---

## 9. File Import Graph

```
run_nursing_project.py
├── agents/base_agent.py
│   ├── agno.agent.Agent
│   ├── agno.db.sqlite.SqliteDb
│   ├── agno.models.openai.OpenAIChat
│   └── agent_config.py
│       └── pathlib.Path
│
├── agents/nursing_research_agent.py
│   ├── agents/base_agent.py (BaseAgent)
│   ├── agent_config.py (get_db_path)
│   ├── src/services/api_tools.py (create_*_tools_safe)
│   └── src/tools/literature_tools.py (LiteratureTools)
│
├── agents/medical_research_agent.py
│   ├── agents/base_agent.py (BaseAgent)
│   ├── agent_config.py (get_db_path)
│   ├── src/services/api_tools.py
│   ├── src/services/agent_audit_logger.py (get_audit_logger)
│   └── src/tools/literature_tools.py (LiteratureTools)
│
├── agents/academic_research_agent.py
│   ├── agents/base_agent.py (BaseAgent)
│   ├── agent_config.py (get_db_path)
│   ├── src/services/api_tools.py
│   └── src/tools/literature_tools.py (LiteratureTools)
│
├── agents/research_writing_agent.py
│   ├── agents/base_agent.py (BaseAgent)
│   └── agent_config.py (get_db_path)
│
├── agents/nursing_project_timeline_agent.py
│   ├── agents/base_agent.py (BaseAgent)
│   ├── agent_config.py (get_db_path)
│   └── src/services/api_tools.py (create_milestone_tools_safe)
│
├── agents/data_analysis_agent.py
│   ├── agents/base_agent.py (BaseAgent)
│   ├── agent_config.py (get_db_path, DATA_ANALYSIS_*)
│   └── pydantic (BaseModel, Field, Literal)
│
├── agents/citation_validation_agent.py
│   ├── agents/base_agent.py (BaseAgent)
│   ├── agent_config.py (get_db_path)
│   ├── src/models/evidence_types.py (EvidenceLevel, ValidationResult)
│   ├── src/services/agent_audit_logger.py (get_audit_logger)
│   └── src/tools/citation_validation_tools.py
│
└── project_manager.py
    ├── pathlib.Path
    └── sqlite3
```

---

## 10. Summary of Findings

### Strengths
1. **Clean inheritance hierarchy** - All agents inherit from BaseAgent with consistent interfaces
2. **Strong anti-hallucination measures** - PMID/DOI verification, grounding checks, mandatory refusals
3. **Complete audit trail** - Every action logged to JSONL with timestamps and hashes
4. **Graceful degradation** - Optional tools fail safely without crashing agents
5. **Cost optimization** - Timeline agent uses cheaper gpt-4o-mini model
6. **Separation of concerns** - Agents don't directly call each other; orchestration is external

### Potential Improvements
1. No direct agent-to-agent communication protocol
2. Each agent has own session database (potential for consolidation)
3. Citation validation is called separately, not automatically integrated into search agents

### Critical Integration Points
- **agent_config.py** - Central configuration for all agents
- **src/services/api_tools.py** - All external API access flows through here
- **src/services/agent_audit_logger.py** - All agents log here for compliance
- **project_manager.py** - Shared database access for all agents
- **run_nursing_project.py** - Orchestrates agent selection and workflow execution

---

*End of Analysis*
