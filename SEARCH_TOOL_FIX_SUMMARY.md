# Search Tool Query Validation Fix

## Issue
The PubMed tool (and potentially other search tools) was being called with `query=None`, causing the error:
```
Could not run function search_pubmed(query=None…)
Input should be a valid string
```

## Root Cause
While the function signatures correctly defined `query: str` (non-nullable), the LLM model was still producing tool calls without a query parameter or with `query=None`. The tools had no defensive validation to catch this error early.

## Solution Implemented

### 1. Added Defensive Guards
Added validation at the start of each search function to ensure query is:
- Not None
- Not empty string
- Is an instance of string

Example:
```python
# Defensive guard: validate query parameter
if not query or not isinstance(query, str):
    raise ValueError("search_pubmed requires a non-empty string query")
```

### 2. Updated Docstrings
Updated the docstrings to explicitly mark query as REQUIRED:
```python
Args:
    query (str): The search query. REQUIRED - must be a non-empty string.
```

## Files Modified

### Medical Research Tools (Primary)
1. **libs/agno/agno/tools/pubmed.py** - `search_pubmed()` at line 142
2. **libs/agno/agno/tools/clinicaltrials.py** - `search_clinicaltrials()` at line 27
3. **libs/agno/agno/tools/arxiv.py** - `search_arxiv_and_return_articles()` at line 39
4. **libs/agno/agno/tools/medrxiv.py** - `search_medrxiv()` at line 30
5. **libs/agno/agno/tools/semantic_scholar.py** - `search_semantic_scholar()` at line 30
6. **libs/agno/agno/tools/core.py** - `search_core()` at line 30
7. **libs/agno/agno/tools/doaj.py** - `search_doaj()` at line 27

## Testing

Created `test_search_tool_validation.py` to verify:
- ✅ Tools reject `query=None`
- ✅ Tools reject empty string `query=""`
- ✅ Tools raise clear, descriptive error messages

All tests passed (4/4).

## Benefits

1. **Early Error Detection**: Catches invalid queries immediately with clear error messages
2. **Better Debugging**: Clear error messages indicate exactly what went wrong
3. **Type Safety**: Runtime validation ensures query parameter integrity
4. **Consistent Behavior**: All search tools now have uniform validation
5. **Prevents Crashes**: Stops execution before making API calls with invalid parameters

## Schema Generation

The agno framework automatically generates tool schemas based on:
- Function signatures (line 264-280 in `libs/agno/agno/tools/function.py`)
- Parameters without default values are marked as "required"
- Type hints are used to generate the JSON schema

The schema should already correctly mark `query` as required since it has no default value. However, defensive guards provide an additional layer of safety against LLM errors or schema misinterpretation.

## Next Steps

If the issue persists:
1. Check the actual tool schema being sent to the LLM (log the parameters dict)
2. Verify the LLM model is correctly interpreting the schema
3. Consider adding schema validation at the agent level before tool calls
4. Review the prompt instructions to ensure the LLM understands query is required

## Related Files

- `src/services/api_tools.py` - Safe tool creation functions (lines 422-460 for PubMed)
- `agents/medical_research_agent.py` - Uses PubMed tool (line 86)
- `libs/agno/agno/tools/function.py` - Schema generation logic (lines 183-293)
