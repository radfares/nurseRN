# Phase 5 Hardening Audit Report
**Date**: 2025-12-08 12:51:44

## 📊 Summary Statistics
- **Total Files Scanned**: 40
- **Total Functions**: 222
- **Total Classes**: 46

### Compliance Rates
- **Function Docstrings**: 84.7% (188/222)
- **Function Type Hints**: 85.6% (190/222)
- **Class Docstrings**:    97.8% (45/46)

## ❌ Compliance Issues
### `src/adapters/base.py`
- Function `__init__` missing docstring

### `src/models/agent_handoff.py`
- Function `to_dict` missing docstring

### `src/models/evidence_types.py`
- Function `__str__` missing docstring

### `src/orchestration/context_manager.py`
- Function `_initialize_schema` missing types: return value

### `src/orchestration/orchestrator.py`
- Function `__post_init__` missing docstring
- Function `__post_init__` missing types: return value

### `src/services/api_tools.py`
- Function `call_with_breaker` missing docstring
- Function `call_with_breaker` missing types: arg `breaker`, arg `func`, arg `fallback_message`, return value
- Function `_get_exa_breaker` missing docstring
- Function `_get_exa_breaker` missing types: return value
- Function `_get_serp_breaker` missing docstring
- Function `_get_serp_breaker` missing types: return value
- Function `_get_pubmed_breaker` missing docstring
- Function `_get_pubmed_breaker` missing types: return value
- Function `_get_arxiv_breaker` missing docstring
- Function `_get_arxiv_breaker` missing types: return value
- Function `_get_clinicaltrials_breaker` missing docstring
- Function `_get_clinicaltrials_breaker` missing types: return value
- Function `_get_medrxiv_breaker` missing docstring
- Function `_get_medrxiv_breaker` missing types: return value
- Function `_get_semantic_scholar_breaker` missing docstring
- Function `_get_semantic_scholar_breaker` missing types: return value
- Function `_get_core_breaker` missing docstring
- Function `_get_core_breaker` missing types: return value
- Function `_get_doaj_breaker` missing docstring
- Function `_get_doaj_breaker` missing types: return value
- Function `_custom_getstate` missing types: return value
- Function `_custom_setstate` missing types: arg `state`, return value
- Function `_make_bound_wrapper` missing types: arg `method_name`, arg `orig_func`, return value
- Function `_wrapper` missing docstring
- Function `_wrapper` missing types: return value
- Function `_unwrap_tool_method` missing types: arg `tool`, arg `method_name`, return value
- Function `print_api_status` missing types: return value

### `src/services/circuit_breaker.py`
- Function `__init__` missing docstring
- Function `success` missing docstring
- Function `success` missing types: arg `cb`, return value
- Function `failure` missing docstring
- Function `failure` missing types: arg `cb`, arg `exc`, return value
- Function `state_change` missing docstring
- Function `state_change` missing types: arg `cb`, arg `old_state`, arg `new_state`, return value
- Function `create_circuit_breaker` missing types: return value
- Function `with_circuit_breaker` missing types: return value
- Function `decorator` missing docstring
- Function `wrapper` missing docstring
- Function `print_breaker_status` missing types: return value
- Function `failing_api_call` missing docstring
- Function `failing_api_call` missing types: return value

### `src/services/citation_apis.py`
- Function `_rate_limit` missing types: return value
- Function `do_search` missing docstring
- Function `do_search` missing types: return value

### `src/services/safety_tools.py`
- Class `SafetyTools` missing docstring
- Function `__init__` missing docstring

### `src/tools/statistics_tools.py`
- Function `__init__` missing docstring

### `src/tools/writing_tools.py`
- Function `__init__` missing docstring

### `src/validation/clinical_checks.py`
- Function `__post_init__` missing types: return value

### `src/validation/picot_scorer.py`
- Function `__post_init__` missing types: return value

### `src/workflows/base.py`
- Function `_start_execution` missing types: return value
- Function `_increment_step` missing types: return value
- Function `clear_context` missing types: return value

### `src/workflows/parallel_search.py`
- Function `name` missing docstring
- Function `description` missing docstring

### `src/workflows/research_workflow.py`
- Function `name` missing docstring
- Function `description` missing docstring

### `src/workflows/timeline_planner.py`
- Function `name` missing docstring
- Function `description` missing docstring

### `src/workflows/validated_research_workflow.py`
- Function `name` missing docstring
- Function `description` missing docstring
