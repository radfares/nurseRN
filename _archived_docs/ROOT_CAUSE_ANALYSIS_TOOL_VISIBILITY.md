# Root Cause Analysis: Tool Visibility & Execution Failure

**Date:** December 2, 2025
**Incident:** Agents failed to execute tools, resulting in "Planning Only" behavior and hallucinations.
**Severity:** Critical (Functional Failure)
**Status:** Resolved

## 1. Problem Description
The Medical Research Agent (and potentially others) would state its intent to search (e.g., `search_pubmed("query")`) or hallucinate a search result, but never actually executed the Python code to call the API.

## 2. Technical Root Cause
The failure stemmed from the **Circuit Breaker implementation pattern** used in `src/services/api_tools.py`.

### The Flawed Pattern: Proxy Class (`CircuitProtectedToolWrapper`)
We initially wrapped tool instances in a proxy class to intercept method calls:

```python
class CircuitProtectedToolWrapper:
    def __init__(self, tool, ...):
        self._tool = tool
    
    def __getattr__(self, name):
        # Intercept access and wrap in circuit breaker
        attr = getattr(self._tool, name)
        if callable(attr):
            return wrap_with_breaker(attr)
        return attr
```

### Why It Failed
The `agno` framework (and Python's `inspect` module) relies on standard introspection to discover tool capabilities.

1.  **Hidden Methods:** The proxy class did not implement `__dir__`. When `agno` inspected the object to find methods like `search_pubmed`, `dir(wrapper)` returned only the wrapper's own methods (which were none), not the underlying tool's methods.
2.  **Type Mismatch:** The wrapper changed the object type from `PubmedTools` to `CircuitProtectedToolWrapper`. If `agno` performed any type checks or looked for specific base classes, these failed.
3.  **Inspection Failure:** `inspect.getmembers()` and similar functions do not trigger `__getattr__`. They look at the object's `__dict__` and class attributes. Since the methods didn't exist on the wrapper class, they were invisible to inspection.

### The Chain of Events
1.  `run_nursing_project.py` initialized the agent.
2.  `MedicalResearchAgent` called `create_pubmed_tools_safe()`.
3.  The function returned a `CircuitProtectedToolWrapper` instance.
4.  `agno.Agent` inspected the tools list.
5.  **CRITICAL FAILURE:** `agno` saw an object with **zero** discoverable methods.
6.  The Agent was initialized with **no tools**.
7.  The LLM, instructed to use tools but given none, either:
    *   Hallucinated the tool call text (e.g., `search_pubmed(...)`) as part of its response.
    *   Refused to act (Planning Only).

## 3. The Fix: In-Place Wrapping
We replaced the Proxy Pattern with a **Decorator/Monkey-Patch Pattern** (`wrap_tool_with_circuit_breaker`).

```python
def wrap_tool_with_circuit_breaker(tool, breaker, ...):
    # Iterate over existing methods
    for name in dir(tool):
        if callable(getattr(tool, name)):
            # Wrap the method
            wrapped_method = wrap_with_breaker(getattr(tool, name))
            # Replace it ON THE INSTANCE
            setattr(tool, name, wrapped_method)
    return tool
```

### Why This Works
1.  **Identity Preservation:** The object remains an instance of `PubmedTools`. `isinstance(tool, PubmedTools)` is True.
2.  **Discovery:** `dir(tool)` still lists all original methods.
3.  **Inspection:** `inspect.getmembers()` finds the methods because they exist on the instance (shadowing the class methods).
4.  **Functionality:** When called, the methods still execute through the circuit breaker logic.

## 4. Verification
- **Debug Script:** Confirmed `dir(tool)` now lists `search_pubmed`.
- **Functional Test:** `test_medical_agent_fix.py` confirmed the agent now executes the tool and returns real data (verified by presence of DOIs/URLs).

## 5. Lessons Learned
- **Avoid Proxy Wrappers for Libraries:** When working with 3rd-party frameworks (`agno`) that rely on introspection, avoid wrapping objects in proxies. Modify them in-place or use inheritance.
- **Check `dir()`:** When creating wrappers, always implement `__dir__` to expose the underlying attributes.
- **Verify Tool Registration:** Don't just verify the tool object exists; verify the framework *sees* its methods.
