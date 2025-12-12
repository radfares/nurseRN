# Integration of Options 7-9 into Conversational Interface

## Current Options 7-9

**7. Citation Validation Agent**
- Evidence level grading (Johns Hopkins I-VII)
- Retraction detection via PubMed
- Currency assessment (flags old articles)
- Quality scoring and recommendations

**8. Smart Mode (Auto-Routing)**
- Automatically routes your query to the best agent
- Detects intent (Research, Search, Planning)
- Best for: When you're not sure which agent to use

**9. Workflow Mode (Templates)**
- Run pre-defined multi-step workflows
- Validated Research (Search + Validate + Write) ⭐
- Basic Research (PICOT -> Search -> Writing)
- Parallel Search (Multiple databases)
- Timeline Planner

---

## How They're Integrated in New Design

### Option 7: Citation Validation Agent → **AUTOMATIC**

**Old Way (Manual):**
```
User: [Selects agent #2 - Medical Research]
User: "Search fall prevention"
Agent: [Returns PMIDs: 12345, 67890, 11111]
User: [Exits to menu]
User: [Selects agent #7 - Citation Validation]
User: "Validate PMIDs 12345, 67890, 11111"
Agent: [Validates articles]
```

**New Way (Automatic):**
```
User: "Research fall prevention"
System: [Automatically executes plan]
  ✓ PICOT generated
  ✓ PubMed search (found 8 articles)
  ✓ Citation validation (6 valid, 2 excluded) ← AUTOMATIC
  ✓ Synthesis complete
```

**Implementation:** The IntelligentOrchestrator's planning LLM automatically includes citation validation when articles are found:

```python
# In _create_execution_plan()
# LLM automatically generates:
[
  {agent: "medical", task: "search_pubmed"},
  {agent: "citation_validation", task: "validate", depends_on: ["search"]},  # AUTO
  {agent: "writing", task: "synthesize", depends_on: ["validate"]}
]
```

**User can still invoke explicitly:**
```
User: "Validate these articles: PMID 12345, PMID 67890"
System: [Runs citation validation agent directly]
```

---

### Option 8: Smart Mode → **DEFAULT BEHAVIOR**

**Old Way:**
- User must choose between 9 options
- Option 8 was a special "smart" mode
- Still required selecting mode first

**New Way:**
- **Smart mode IS the default interface**
- Every query is automatically routed
- No mode selection needed

**The entire conversational interface IS smart mode.** The IntelligentOrchestrator does what the old "Smart Mode" did, but better:

| Old Smart Mode | New Default Behavior |
|----------------|---------------------|
| Regex-based intent detection | LLM-based goal decomposition |
| Routes to 1 agent | Orchestrates multiple agents |
| Single-step execution | Multi-step workflows |
| No context retention | Full conversation context |

**Example:**
```
User: "What's my next deadline?"
System: [Detects timeline query, routes to timeline agent]
        📅 Next deadline: December 15 (IRB Submission)

User: "Help me prepare for that"
System: [Understands context, creates IRB prep plan]
        ✓ Data collection plan created
        ✓ Sample size calculated
        ✓ Consent form template generated
```

---

### Option 9: Workflow Mode → **INTELLIGENT WORKFLOWS**

**Old Way (Template-Based):**
```
User: [Selects option 9 - Workflow Mode]
System: "Choose workflow:"
        1. Validated Research
        2. Basic Research
        3. Parallel Search
        4. Timeline Planner
User: [Selects #1]
System: "Enter topic:"
User: "Fall prevention"
System: [Runs fixed 4-step workflow]
```

**New Way (Dynamic Workflows):**
```
User: "I need to do a complete research project on fall prevention"
System: [LLM detects comprehensive workflow needed]
        [Automatically executes validated research workflow]
        ✓ PICOT developed
        ✓ Parallel search (PubMed + ClinicalTrials + ArXiv)
        ✓ Citation validation
        ✓ Evidence synthesis
        ✓ Timeline created
```

**Key Difference:** Workflows are triggered **automatically based on query complexity**, not manually selected.

---

## Workflow Detection Logic

The IntelligentOrchestrator detects when to use pre-built workflows vs. custom plans:

```python
def _create_execution_plan(self, message: str, context: ConversationContext):
    """
    Detect if query matches a known workflow pattern.
    """
    # Check for comprehensive research queries
    if self._is_comprehensive_research_query(message):
        return self._load_validated_research_workflow()
    
    # Check for parallel search queries
    elif self._is_parallel_search_query(message):
        return self._load_parallel_search_workflow()
    
    # Check for timeline queries
    elif self._is_timeline_query(message):
        return self._load_timeline_workflow()
    
    # Otherwise, create custom plan with LLM
    else:
        return self._create_custom_plan(message, context)

def _is_comprehensive_research_query(self, message: str) -> bool:
    """
    Detect if user wants full research workflow.
    """
    keywords = [
        "complete research", "full project", "start to finish",
        "comprehensive", "entire workflow", "all steps"
    ]
    return any(kw in message.lower() for kw in keywords)
```

---

## Enhanced Workflow System

### Pre-Built Workflows (From Option 9)

**1. Validated Research Workflow**
```python
VALIDATED_RESEARCH_WORKFLOW = [
    {agent: "writing", task: "generate_picot"},
    {agent: "medical", task: "search_pubmed", depends_on: ["picot"]},
    {agent: "citation_validation", task: "validate", depends_on: ["search"]},
    {agent: "writing", task: "synthesize", depends_on: ["validate"]},
    {agent: "timeline", task: "create_milestones", depends_on: ["synthesize"]}
]
```

**Trigger phrases:**
- "Do a complete research project on [topic]"
- "Full validated research workflow for [topic]"
- "Start comprehensive project on [topic]"

**2. Parallel Search Workflow**
```python
PARALLEL_SEARCH_WORKFLOW = [
    {agent: "writing", task: "generate_picot"},
    {
        parallel: [
            {agent: "medical", task: "search_pubmed"},
            {agent: "academic", task: "search_arxiv"},
            {agent: "nursing", task: "search_clinical_trials"}
        ],
        depends_on: ["picot"]
    },
    {agent: "citation_validation", task: "validate_all", depends_on: ["parallel"]},
    {agent: "writing", task: "synthesize", depends_on: ["validate"]}
]
```

**Trigger phrases:**
- "Search all databases for [topic]"
- "Comprehensive literature search on [topic]"
- "Find everything about [topic]"

**3. Timeline Planner Workflow**
```python
TIMELINE_WORKFLOW = [
    {agent: "timeline", task: "get_current_phase"},
    {agent: "timeline", task: "get_upcoming_milestones"},
    {agent: "timeline", task: "suggest_next_steps", depends_on: ["phase", "milestones"]}
]
```

**Trigger phrases:**
- "Show my timeline"
- "What's my schedule?"
- "When are my deadlines?"

**4. Basic Research Workflow**
```python
BASIC_RESEARCH_WORKFLOW = [
    {agent: "writing", task: "generate_picot"},
    {agent: "medical", task: "search_pubmed", depends_on: ["picot"]},
    {agent: "writing", task: "synthesize", depends_on: ["search"]}
]
```

**Trigger phrases:**
- "Quick research on [topic]"
- "Basic literature search for [topic]"
- "Simple project on [topic]"

---

## User Control Over Workflows

Users can explicitly request workflows:

```
User: "Run the validated research workflow for CAUTI prevention"
System: [Recognizes explicit workflow request]
        Running Validated Research Workflow...
        
        Phase 1/5: PICOT Development
        ✓ Generated PICOT question
        
        Phase 2/5: Literature Search
        ✓ Searched PubMed (12 articles found)
        
        Phase 3/5: Citation Validation
        ✓ Validated articles (9 valid, 3 excluded)
        
        Phase 4/5: Evidence Synthesis
        ✓ Synthesized findings
        
        Phase 5/5: Timeline Creation
        ✓ Created 8-month timeline
        
        Workflow complete! (2 min 45 sec)
```

Or let the system decide:

```
User: "Help me with a CAUTI prevention project"
System: [Automatically selects validated research workflow]
        I'll run a complete research workflow for you...
        [Same output as above]
```

---

## Workflow Progress Tracking

The system shows progress for multi-step workflows:

```
User: "Start comprehensive fall prevention research"
System: Running Validated Research Workflow...
        
        [████████░░░░░░░░░░░░] 40% - Validating citations...
        
        Completed:
        ✓ PICOT Development (15 sec)
        ✓ Literature Search (45 sec)
        
        In Progress:
        ⏳ Citation Validation (30 sec elapsed)
        
        Remaining:
        ⏸ Evidence Synthesis
        ⏸ Timeline Creation
```

---

## Comparison: Old vs. New

| Feature | Old System (Options 7-9) | New System |
|---------|-------------------------|------------|
| **Citation Validation** | Manual selection (option 7) | Automatic in workflows |
| **Smart Routing** | Special mode (option 8) | Default behavior |
| **Workflows** | Manual template selection (option 9) | Automatic detection |
| **User Actions** | 5+ clicks to start workflow | 1 query |
| **Context** | Lost between steps | Maintained throughout |
| **Flexibility** | Fixed templates | Dynamic + templates |

---

## Implementation: Enhanced Orchestrator

```python
class IntelligentOrchestrator:
    """Enhanced with workflow detection."""
    
    def __init__(self):
        self.client = OpenAI()
        self.agent_registry = AgentRegistry()
        self.synthesizer = ResponseSynthesizer()
        self.suggestion_engine = SuggestionEngine()
        
        # Load pre-built workflows
        self.workflows = {
            "validated_research": self._load_validated_research_workflow(),
            "parallel_search": self._load_parallel_search_workflow(),
            "timeline_planner": self._load_timeline_workflow(),
            "basic_research": self._load_basic_research_workflow()
        }
    
    def _create_execution_plan(self, message: str, context: ConversationContext):
        """
        Create plan: check for workflow patterns first, then custom.
        """
        # 1. Check for explicit workflow request
        workflow_name = self._detect_explicit_workflow(message)
        if workflow_name:
            return self.workflows[workflow_name]
        
        # 2. Check for implicit workflow patterns
        workflow_name = self._detect_implicit_workflow(message)
        if workflow_name:
            return self.workflows[workflow_name]
        
        # 3. Create custom plan with LLM
        return self._create_custom_plan_with_llm(message, context)
    
    def _detect_explicit_workflow(self, message: str) -> str:
        """Detect explicit workflow requests."""
        message_lower = message.lower()
        
        if "validated research workflow" in message_lower:
            return "validated_research"
        elif "parallel search" in message_lower:
            return "parallel_search"
        elif "timeline" in message_lower or "schedule" in message_lower:
            return "timeline_planner"
        elif "basic research" in message_lower or "quick research" in message_lower:
            return "basic_research"
        
        return None
    
    def _detect_implicit_workflow(self, message: str) -> str:
        """Detect implicit workflow patterns."""
        message_lower = message.lower()
        
        # Comprehensive research indicators
        comprehensive_keywords = [
            "complete research", "full project", "comprehensive",
            "start to finish", "entire workflow", "all steps"
        ]
        if any(kw in message_lower for kw in comprehensive_keywords):
            return "validated_research"
        
        # Parallel search indicators
        parallel_keywords = [
            "search all databases", "comprehensive search",
            "find everything", "search everywhere"
        ]
        if any(kw in message_lower for kw in parallel_keywords):
            return "parallel_search"
        
        # Timeline indicators
        timeline_keywords = [
            "deadline", "timeline", "schedule", "milestone",
            "when is", "what's due", "next steps"
        ]
        if any(kw in message_lower for kw in timeline_keywords):
            return "timeline_planner"
        
        return None
    
    def _load_validated_research_workflow(self):
        """Load validated research workflow from existing code."""
        from src.workflows.validated_research_workflow import ValidatedResearchWorkflow
        workflow = ValidatedResearchWorkflow()
        return self._convert_workflow_to_plan(workflow)
    
    def _convert_workflow_to_plan(self, workflow):
        """Convert existing workflow to execution plan format."""
        # Convert workflow steps to AgentTask format
        # This bridges old workflow system with new orchestrator
        pass
```

---

## User Experience Examples

### Example 1: Implicit Workflow Detection

```
💬 You: I need to do a comprehensive research project on catheter infections

🤖 Assistant: I'll run a complete validated research workflow for you. This will:
   • Develop a PICOT question
   • Search PubMed for evidence
   • Validate article quality
   • Synthesize findings
   • Create project timeline
   
   This will take about 2-3 minutes. Proceed?

💬 You: Yes

🤖 Assistant: [Working on your project...]
   
   ✓ PICOT Question Developed
     "In hospitalized adults with urinary catheters (P)..."
   
   ✓ Literature Search Complete
     Found 12 articles from PubMed
   
   ✓ Citation Validation Complete
     9 articles validated (3 excluded: 1 retracted, 2 outdated)
   
   ✓ Evidence Synthesis Complete
     Key findings: Catheter bundles reduce CAUTI by 50-70%
   
   ✓ Timeline Created
     8 milestones from Nov 2025 - June 2026
   
   📊 COMPLETE RESEARCH PACKAGE READY
   
   What would you like to do next?
   • Review detailed findings
   • Export to Word document
   • Plan data collection
```

### Example 2: Explicit Workflow Request

```
💬 You: Run parallel search workflow for pressure ulcer prevention

🤖 Assistant: Running Parallel Search Workflow...
   
   Searching 3 databases simultaneously:
   • PubMed (clinical studies)
   • ArXiv (statistical methods)
   • ClinicalTrials.gov (ongoing trials)
   
   [████████████████████] 100%
   
   ✓ PubMed: 15 articles found
   ✓ ArXiv: 3 methodology papers found
   ✓ ClinicalTrials: 5 active trials found
   
   ✓ Validation: 18 valid sources (5 excluded)
   ✓ Synthesis: Combined findings from all sources
   
   📚 RESULTS:
   • 18 validated sources across 3 databases
   • Evidence levels: 12 Level I, 4 Level II, 2 Level III
   • Most effective interventions: repositioning protocols, 
     specialized surfaces, nutrition optimization
   
   What would you like to do next?
   • Review detailed findings by database
   • Grade evidence quality
   • Create intervention plan
```

### Example 3: Citation Validation (Automatic)

```
💬 You: Search for fall prevention studies

🤖 Assistant: [Working...]
   
   ✓ Found 8 relevant studies from PubMed
   ✓ Automatically validated all articles ← AUTOMATIC
   
   📊 VALIDATION RESULTS:
   • 6 articles validated (high quality)
   • 2 articles excluded:
     - PMID 11111: Retracted in 2020
     - PMID 22222: Published 2005 (outdated)
   
   📚 TOP 3 VALIDATED ARTICLES:
   1. Cameron et al. (2018) - Level I - PMID: 30191554
   2. Miake-Lye et al. (2013) - Level I - PMID: 23552949
   3. Dykes et al. (2010) - Level I - PMID: 20048269
```

### Example 4: Timeline Workflow (Automatic)

```
💬 You: What should I be working on right now?

🤖 Assistant: [Analyzing your timeline...]
   
   📅 CURRENT STATUS:
   • Phase: Literature Review (on track)
   • Next deadline: November 30 (in 5 days)
   
   ⚠️ URGENT:
   • Complete PICOT question (not started)
   • Find 3 research articles (not started)
   
   ✅ COMPLETED:
   • Project setup
   • Topic selection
   
   📋 RECOMMENDED NEXT STEPS:
   1. Develop PICOT question (30 min)
   2. Search PubMed for articles (1 hour)
   3. Validate article quality (30 min)
   
   Would you like me to help with step 1 (PICOT development)?
```

---

## Summary

### How Options 7-9 Are Integrated

1. **Option 7 (Citation Validation)** → **Automatic** in all research workflows
2. **Option 8 (Smart Mode)** → **Default behavior** of new interface
3. **Option 9 (Workflow Mode)** → **Intelligent detection** + explicit requests

### Key Improvements

| Old System | New System |
|------------|------------|
| User selects citation validation | System validates automatically |
| User enables smart mode | Smart mode is always on |
| User selects workflow template | System detects workflow needs |
| 9 menu options | 1 conversation interface |
| Manual orchestration | Automatic orchestration |

### Result

**All the power of options 7-9, with none of the complexity.**

Users get:
- Automatic citation validation (no manual selection)
- Smart routing by default (no mode switching)
- Intelligent workflows (no template selection)
- One simple conversation interface

The system handles all the complexity internally.
