# CR-3 Implementation Plan: Refactor Agent 6 (DataAnalysisAgent) to BaseAgent

**Target File:** `agents/data_analysis_agent.py` (254 lines)
**Reference Pattern:** `agents/nursing_project_timeline_agent.py` (CR-2 completed)
**Status:** Ready for implementation
**Special Requirements:** Pydantic output schema, custom temperature/tokens, module-level constants

---

## File Analysis

### Current Structure (OLD Pattern)
```
Lines 1-7:    Module docstring
Lines 9-14:   Standard imports (agno, pydantic)
Lines 16-17:  Import agent_config
Lines 19-20:  ❌ OLD: Import setup_agent_logging, run_agent_with_error_handling
Line 23:      ❌ OLD: Module-level logger
Lines 26-41:  ✅ KEEP: DataAnalysisOutput Pydantic class (module level)
Lines 43-45:  ❌ MOVE: Module-level db variable → into _create_agent()
Lines 48-205: ✅ KEEP: STATISTICAL_EXPERT_PROMPT constant (module level)
Lines 207-223: ❌ OLD: Direct Agent() instantiation
Line 219:     🔴 CRITICAL: Commented output_schema (MUST UNCOMMENT)
Line 225:     ❌ OLD: Module-level logger.info
Lines 227-243: ❌ OLD: show_usage_examples function
Lines 246-252: ❌ OLD: __main__ block using run_agent_with_error_handling
```

### Target Structure (NEW Pattern - BaseAgent)
```
Lines 1-7:    ✅ Module docstring (update to PHASE 2 COMPLETE)
Lines 9-14:   ✅ Module exports __all__
Lines 15-20:  ✅ Standard imports
Lines 21-22:  ✅ Import agent_config
Lines 23-24:  ✅ Import BaseAgent (not utilities)
Lines 26-41:  ✅ KEEP: DataAnalysisOutput Pydantic class
Lines 43-205: ✅ KEEP: STATISTICAL_EXPERT_PROMPT constant
Lines 207-230: ✅ NEW: DataAnalysisAgent class with __init__
Lines 232-240: ✅ NEW: _create_tools() method
Lines 242-270: ✅ NEW: _create_agent() method (db created here)
Lines 272-300: ✅ NEW: show_usage_examples() instance method
Lines 302-315: ✅ NEW: Global instance with try/except
Lines 317-322: ✅ NEW: __main__ block using instance.run_with_error_handling()
```

---

## Step-by-Step Implementation Checklist

### Phase 1: Module Setup (Lines 1-24)

- [ ] **Step 1.1** - Update docstring (line 7)
  - Change: `PHASE 2 UPDATE (2025-11-16): Refactored to use base_agent utilities`
  - To: `PHASE 2 COMPLETE (2025-11-26): Refactored to use BaseAgent inheritance`

- [ ] **Step 1.2** - Add module exports (after line 7, before imports)
  ```python
  # Module exports
  __all__ = ['DataAnalysisAgent', 'data_analysis_agent']
  ```

- [ ] **Step 1.3** - Update base_agent import (line 20)
  - Change: `from .base_agent import setup_agent_logging, run_agent_with_error_handling`
  - To: `from .base_agent import BaseAgent`

- [ ] **Step 1.4** - Remove module-level logger (line 23)
  - Delete: `logger = setup_agent_logging("Data Analysis Agent")`

- [ ] **Step 1.5** - VERIFY: DataAnalysisOutput class stays at module level (lines 26-41)
  - ✅ Do NOT move this class
  - ✅ Do NOT modify this class

- [ ] **Step 1.6** - Remove module-level db variable (lines 43-45)
  - Delete 3 lines:
    ```python
    db = SqliteDb(db_file=get_db_path("data_analysis"))
    logger.info(f"Database initialized: {get_db_path('data_analysis')}")
    ```
  - NOTE: Will recreate db inside _create_agent() method

- [ ] **Step 1.7** - VERIFY: STATISTICAL_EXPERT_PROMPT stays at module level (lines 48-205)
  - ✅ Do NOT move this constant
  - ✅ Do NOT modify this constant

---

### Phase 2: Create Class Structure (Lines 207-240)

- [ ] **Step 2.1** - Delete old agent instantiation (lines 207-225)
  - Delete from `data_analysis_agent = Agent(` through `logger.info("Data Analysis Agent initialized successfully")`
  - Total: ~19 lines to delete

- [ ] **Step 2.2** - Create DataAnalysisAgent class
  ```python
  class DataAnalysisAgent(BaseAgent):
      """
      Data Analysis Planning Agent - Statistical Expert.

      No external tools - pure statistical reasoning with Pydantic output validation.
      Uses temperature=0.2 for mathematical reliability.
      """

      def __init__(self):
          # No tools for this agent (pure statistical reasoning)
          tools = self._create_tools()
          super().__init__(
              agent_name="Data Analysis Planner",
              agent_key="data_analysis",
              tools=tools
          )
  ```

- [ ] **Step 2.3** - Implement _create_tools() method
  ```python
  def _create_tools(self) -> list:
      """
      Create tools for the data analysis agent.

      This agent has no external tools - it relies on GPT-4o statistical
      reasoning capabilities with temperature=0.2 for reliability.
      """
      # No tools needed for data analysis agent
      return []
  ```

---

### Phase 3: Implement _create_agent() Method (Lines 242-270)

- [ ] **Step 3.1** - Create _create_agent() method header
  ```python
  def _create_agent(self) -> Agent:
      """Create and configure the Data Analysis Agent."""
  ```

- [ ] **Step 3.2** - Create db variable inside method (not module-level)
  ```python
      # Create database for session persistence
      from agno.db.sqlite import SqliteDb
      db = SqliteDb(db_file=get_db_path("data_analysis"))
  ```

- [ ] **Step 3.3** - Return Agent with all configuration
  ```python
      return Agent(
          name="Data Analysis Planner",
          role="Statistical expert for nursing and healthcare research",
          model=OpenAIChat(
              id="gpt-4o",
              temperature=DATA_ANALYSIS_TEMPERATURE,  # 0.2 for math reliability
              max_tokens=DATA_ANALYSIS_MAX_TOKENS,    # 1600 for JSON + prose
          ),
          tools=self.tools,
          instructions=STATISTICAL_EXPERT_PROMPT,
          output_schema=DataAnalysisOutput,  # 🔴 CRITICAL: UNCOMMENT THIS LINE
          markdown=True,
          db=db,
          description="Expert in statistical analysis planning, sample size calculations, test selection, and data template design for nursing quality improvement research.",
          add_history_to_context=True,
          add_datetime_to_context=True,
      )
  ```

- [ ] **Step 3.4** - VERIFY output_schema is ENABLED
  - ✅ Line must be: `output_schema=DataAnalysisOutput,` (NO # comment)
  - ✅ This enables JSON validation via Pydantic

---

### Phase 4: Convert show_usage_examples (Lines 272-300)

- [ ] **Step 4.1** - Delete old function definition (lines 227-243)
  - Delete from `def show_usage_examples():` through the entire function

- [ ] **Step 4.2** - Create new instance method
  ```python
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
  ```

- [ ] **Step 4.3** - VERIFY: Added `self` parameter
- [ ] **Step 4.4** - VERIFY: Added return type `-> None`

---

### Phase 5: Global Instance Creation (Lines 302-315)

- [ ] **Step 5.1** - Create global instance with error handling
  ```python
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
  ```

- [ ] **Step 5.2** - VERIFY: Instance variable is `_data_analysis_agent_instance`
- [ ] **Step 5.3** - VERIFY: Global variable is `data_analysis_agent` (matches exports)

---

### Phase 6: Update __main__ Block (Lines 317-322)

- [ ] **Step 6.1** - Delete old __main__ block (lines 246-252)

- [ ] **Step 6.2** - Create new __main__ block
  ```python
  if __name__ == "__main__":
      if _data_analysis_agent_instance is not None:
          _data_analysis_agent_instance.run_with_error_handling()
      else:
          print("❌ Agent failed to initialize. Check logs for details.")
  ```

- [ ] **Step 6.3** - VERIFY: Uses instance method `run_with_error_handling()`
- [ ] **Step 6.4** - VERIFY: Shows error message if initialization failed

---

## Verification Checklist

### Syntax & Import Verification
- [ ] **V1** - Check syntax: `python3 -m py_compile agents/data_analysis_agent.py`
- [ ] **V2** - Test class import: `python3 -c "from agents.data_analysis_agent import DataAnalysisAgent"`
- [ ] **V3** - Test global import: `python3 -c "from agents.data_analysis_agent import data_analysis_agent"`

### Instantiation & Functionality
- [ ] **V4** - Test instantiation:
  ```bash
  python3 -c "from agents.data_analysis_agent import DataAnalysisAgent; agent = DataAnalysisAgent(); print(agent.agent_name)"
  ```
  Expected: "Data Analysis Planner"

- [ ] **V5** - Test global instance type:
  ```bash
  python3 -c "from agents.data_analysis_agent import data_analysis_agent; print(type(data_analysis_agent))"
  ```
  Expected: `<class 'agno.agent.agent.Agent'>`

- [ ] **V6** - Verify output_schema enabled:
  ```bash
  python3 -c "from agents.data_analysis_agent import data_analysis_agent; print(hasattr(data_analysis_agent, 'output_model'))"
  ```
  Expected: True

### Integration Testing
- [ ] **V7** - Run unit tests: `pytest tests/unit/test_data_analysis_agent.py -v`
- [ ] **V8** - Run main module: `python3 -m agents.data_analysis_agent` (Ctrl+C after verification)

---

## Expected Test Results

**Unit Tests:** Expect same pattern as CR-1 and CR-2
- ✅ 3-4 passing (agent_exists, database_configuration, markdown_enabled)
- ⚠️ 8-10 failing (pattern mismatch - tests expect old module-level functions)

**Integration:** Agent should work in run_nursing_project.py

---

## Critical Success Criteria

1. ✅ Class inherits from BaseAgent
2. ✅ output_schema=DataAnalysisOutput is UNCOMMENTED (line 219 in _create_agent)
3. ✅ temperature=0.2 preserved (DATA_ANALYSIS_TEMPERATURE)
4. ✅ max_tokens=1600 preserved (DATA_ANALYSIS_MAX_TOKENS)
5. ✅ DataAnalysisOutput class stays at module level (not moved into class)
6. ✅ STATISTICAL_EXPERT_PROMPT stays at module level (not moved into class)
7. ✅ db variable created inside _create_agent() (not module-level)
8. ✅ Global instance `data_analysis_agent` works for backward compatibility

---

## Post-Implementation Notes

**Files Modified:** 1
- `agents/data_analysis_agent.py` (254 → ~280 lines estimated)

**Files NOT Modified:**
- `tests/unit/test_data_analysis_agent.py` (will update after all agents refactored)
- `agent_config.py` (already has data_analysis configuration)
- `run_nursing_project.py` (already imports from agents.data_analysis_agent)

**Known Issues:**
- Unit test failures expected (same pattern as CR-1, CR-2)
- Tests will be updated after CR-3 complete

**Next Steps After CR-3:**
1. CR-4: Git staging cleanup
2. Update test suite for new BaseAgent pattern
3. BF-1: Agent 5 milestone database integration
4. FW-1: Knowledge base implementation
