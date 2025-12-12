# Implementation Code for Agentic UX Redesign

## File 1: `src/orchestration/intelligent_orchestrator.py`

```python
"""
Intelligent Orchestrator - LLM-powered agent coordination
Decomposes user goals into agent tasks and synthesizes results.
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from openai import OpenAI

from src.orchestration.conversation_context import ConversationContext
from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.response_synthesizer import ResponseSynthesizer
from src.orchestration.suggestion_engine import SuggestionEngine

logger = logging.getLogger(__name__)


@dataclass
class AgentTask:
    """Represents a single agent task in execution plan."""
    task_id: str
    agent_name: str
    action: str
    params: Dict[str, Any]
    depends_on: List[str] = None
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


class IntelligentOrchestrator:
    """
    Orchestrates multiple agents based on user goals.
    Uses LLM to decompose goals, execute tasks, and synthesize results.
    """
    
    def __init__(self):
        self.client = OpenAI()  # Uses OPENAI_API_KEY from env
        self.agent_registry = AgentRegistry()
        self.synthesizer = ResponseSynthesizer()
        self.suggestion_engine = SuggestionEngine()
        
        # Model for planning (cheaper, faster)
        self.planner_model = "gpt-4o-mini"
        
        # Model for synthesis (better quality)
        self.synthesis_model = "gpt-4o"
    
    def process_user_message(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Tuple[str, List[str]]:
        """
        Main entry point: process user message and return response + suggestions.
        
        Args:
            message: User's natural language input
            context: Current conversation context
            
        Returns:
            Tuple of (response_text, suggestions_list)
        """
        try:
            # Step 1: Create execution plan
            logger.info(f"Creating execution plan for: {message}")
            plan = self._create_execution_plan(message, context)
            
            if not plan:
                return self._handle_unclear_intent(message, context)
            
            # Step 2: Execute plan
            logger.info(f"Executing plan with {len(plan)} tasks")
            results = self._execute_plan(plan, context)
            
            # Step 3: Synthesize results into coherent response
            logger.info("Synthesizing results")
            response = self.synthesizer.synthesize(
                user_message=message,
                plan=plan,
                results=results,
                context=context
            )
            
            # Step 4: Generate suggestions for next steps
            suggestions = self.suggestion_engine.generate_suggestions(context)
            
            return response, suggestions
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return self._handle_error(e, context)
    
    def _create_execution_plan(
        self, 
        message: str, 
        context: ConversationContext
    ) -> List[AgentTask]:
        """
        Use LLM to decompose user message into agent tasks.
        """
        system_prompt = """You are an execution planner for a nursing research assistant system.

Your job is to decompose user goals into a sequence of agent tasks.

Available agents and their capabilities:
- nursing_research: PICOT development, web search, healthcare standards, Joint Commission guidelines
- medical_research: PubMed search, clinical studies, systematic reviews, peer-reviewed articles
- academic_research: ArXiv search, statistical methods, research methodologies
- writing: Literature synthesis, PICOT refinement, drafting sections, citation formatting
- timeline: Milestone tracking, deadline reminders, project phase management
- data_analysis: Sample size calculation, statistical test selection, power analysis
- citation_validation: Evidence grading (Johns Hopkins), retraction detection, quality scoring

Common workflows:
1. Research topic → [writing: generate_picot] → [medical_research: search_pubmed] → [citation_validation: validate] → [writing: synthesize]
2. Timeline query → [timeline: get_milestones]
3. Statistical question → [data_analysis: calculate_sample_size]
4. Validate articles → [citation_validation: grade_evidence]

Return JSON array of tasks with this structure:
[
  {
    "task_id": "task_1",
    "agent_name": "writing",
    "action": "generate_picot",
    "params": {"topic": "fall prevention", "population": "elderly"},
    "depends_on": []
  },
  {
    "task_id": "task_2",
    "agent_name": "medical_research",
    "action": "search_pubmed",
    "params": {"picot": "<task_1.picot>"},
    "depends_on": ["task_1"]
  }
]

Use "<task_id.field>" syntax for dependencies.
"""
        
        user_prompt = f"""User message: "{message}"

Conversation context:
- Project: {context.project_name}
- Phase: {context.current_phase}
- Completed tasks: {', '.join(context.completed_tasks) if context.completed_tasks else 'None'}
- Available artifacts: {', '.join(context.artifacts.keys()) if context.artifacts else 'None'}

Create an execution plan."""

        try:
            response = self.client.chat.completions.create(
                model=self.planner_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for consistent planning
                response_format={"type": "json_object"}
            )
            
            plan_json = json.loads(response.choices[0].message.content)
            
            # Convert to AgentTask objects
            tasks = []
            for task_dict in plan_json.get("tasks", []):
                tasks.append(AgentTask(
                    task_id=task_dict["task_id"],
                    agent_name=task_dict["agent_name"],
                    action=task_dict["action"],
                    params=task_dict.get("params", {}),
                    depends_on=task_dict.get("depends_on", [])
                ))
            
            logger.info(f"Created plan with {len(tasks)} tasks")
            return tasks
            
        except Exception as e:
            logger.error(f"Error creating execution plan: {e}", exc_info=True)
            return []
    
    def _execute_plan(
        self, 
        plan: List[AgentTask], 
        context: ConversationContext
    ) -> Dict[str, Any]:
        """
        Execute plan with dependency resolution.
        """
        results = {}
        
        for task in plan:
            try:
                logger.info(f"Executing task {task.task_id}: {task.agent_name}.{task.action}")
                
                # Resolve dependencies
                resolved_params = self._resolve_dependencies(task.params, results)
                
                # Get agent
                agent = self.agent_registry.get_agent(task.agent_name)
                
                # Execute task
                result = self._execute_agent_task(
                    agent=agent,
                    action=task.action,
                    params=resolved_params,
                    context=context
                )
                
                # Store result
                results[task.task_id] = {
                    "agent": task.agent_name,
                    "action": task.action,
                    "output": result,
                    "success": True
                }
                
                # Mark task as completed
                context.completed_tasks.add(f"{task.agent_name}:{task.action}")
                
            except Exception as e:
                logger.error(f"Error executing task {task.task_id}: {e}", exc_info=True)
                results[task.task_id] = {
                    "agent": task.agent_name,
                    "action": task.action,
                    "error": str(e),
                    "success": False
                }
        
        return results
    
    def _resolve_dependencies(
        self, 
        params: Dict[str, Any], 
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Replace dependency placeholders with actual results.
        
        Example:
            params = {"picot": "<task_1.picot>"}
            results = {"task_1": {"output": {"picot": "In elderly..."}}}
            → {"picot": "In elderly..."}
        """
        resolved = {}
        
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("<") and value.endswith(">"):
                # Dependency reference: <task_id.field>
                ref = value[1:-1]  # Remove < >
                task_id, field = ref.split(".", 1)
                
                if task_id in results and "output" in results[task_id]:
                    # Navigate nested dict
                    resolved[key] = self._get_nested_value(
                        results[task_id]["output"], 
                        field
                    )
                else:
                    logger.warning(f"Dependency not found: {ref}")
                    resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved
    
    def _get_nested_value(self, data: Any, path: str) -> Any:
        """
        Get value from nested dict using dot notation.
        Example: "picot.full_question" → data["picot"]["full_question"]
        """
        keys = path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
    
    def _execute_agent_task(
        self,
        agent: Any,
        action: str,
        params: Dict[str, Any],
        context: ConversationContext
    ) -> Any:
        """
        Execute a specific action on an agent.
        """
        # Build query for agent based on action and params
        query = self._build_agent_query(action, params)
        
        # Run agent
        response = agent.run(query)
        
        # Extract structured output
        output = self._extract_agent_output(response, action)
        
        # Store in context if it's an artifact
        if action in ["generate_picot", "search_pubmed", "synthesize"]:
            context.add_artifact(action, output)
        
        return output
    
    def _build_agent_query(self, action: str, params: Dict[str, Any]) -> str:
        """
        Build natural language query for agent based on action and params.
        """
        query_templates = {
            "generate_picot": "Generate a PICOT question for {topic} in {population}",
            "search_pubmed": "Search PubMed for articles about: {picot}",
            "validate": "Validate these articles and grade evidence: {pmids}",
            "synthesize": "Synthesize these research findings: {articles}",
            "calculate_sample_size": "Calculate sample size for {design} with {effect_size} effect",
            "get_milestones": "Show upcoming milestones and deadlines",
        }
        
        template = query_templates.get(action, "{params}")
        
        try:
            return template.format(**params)
        except KeyError:
            # Fallback: just stringify params
            return f"{action}: {json.dumps(params)}"
    
    def _extract_agent_output(self, response: Any, action: str) -> Any:
        """
        Extract structured output from agent response.
        """
        # Try to parse as JSON first
        try:
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # Look for JSON in response
            if "{" in content and "}" in content:
                start = content.index("{")
                end = content.rindex("}") + 1
                json_str = content[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError, AttributeError):
            pass
        
        # Fallback: return raw content
        if hasattr(response, 'content'):
            return {"text": response.content}
        return {"text": str(response)}
    
    def _handle_unclear_intent(
        self, 
        message: str, 
        context: ConversationContext
    ) -> Tuple[str, List[str]]:
        """
        Handle cases where intent is unclear.
        """
        response = f"""I'm not sure I understand what you'd like to do. 

Could you clarify? For example:
• "Research fall prevention in elderly patients"
• "What's my next deadline?"
• "Calculate sample size for my study"
• "Validate these articles: PMID 12345, PMID 67890"

Or type 'help' to see what I can do."""
        
        suggestions = [
            "Start a new research topic",
            "Check project timeline",
            "Review completed work",
            "Get help"
        ]
        
        return response, suggestions
    
    def _handle_error(
        self, 
        error: Exception, 
        context: ConversationContext
    ) -> Tuple[str, List[str]]:
        """
        Handle errors gracefully.
        """
        response = f"""I encountered an error while processing your request:

{str(error)}

Please try rephrasing your request or type 'help' for assistance."""
        
        suggestions = ["Try again", "Get help", "Report issue"]
        
        return response, suggestions
```

## File 2: `src/orchestration/conversation_context.py`

```python
"""
Conversation Context - Maintains state across agent interactions
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set
from dataclasses import dataclass, field


@dataclass
class ConversationContext:
    """
    Tracks conversation state across multiple agent interactions.
    """
    project_name: str
    project_db_path: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    artifacts: Dict[str, Any] = field(default_factory=dict)
    current_phase: str = "planning"
    completed_tasks: Set[str] = field(default_factory=set)
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add message to conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        })
    
    def add_artifact(self, artifact_type: str, content: Any):
        """Store generated artifact (PICOT, articles, synthesis, etc.)."""
        self.artifacts[artifact_type] = content
        self._update_phase_based_on_artifacts()
    
    def get_artifact(self, artifact_type: str) -> Any:
        """Retrieve artifact by type."""
        return self.artifacts.get(artifact_type)
    
    def has_artifact(self, artifact_type: str) -> bool:
        """Check if artifact exists."""
        return artifact_type in self.artifacts
    
    def _update_phase_based_on_artifacts(self):
        """Automatically update project phase based on completed artifacts."""
        if "synthesize" in self.artifacts:
            self.current_phase = "writing"
        elif "validate" in self.artifacts:
            self.current_phase = "analyzing"
        elif "search_pubmed" in self.artifacts:
            self.current_phase = "searching"
        elif "generate_picot" in self.artifacts:
            self.current_phase = "planning"
    
    def get_summary(self) -> str:
        """Generate summary of conversation for LLM context."""
        recent_messages = self.messages[-5:] if len(self.messages) > 5 else self.messages
        
        return f"""Project: {self.project_name}
Phase: {self.current_phase}
Completed tasks: {', '.join(self.completed_tasks) if self.completed_tasks else 'None'}
Artifacts: {', '.join(self.artifacts.keys()) if self.artifacts else 'None'}
Recent messages: {len(recent_messages)} messages
Last message: {recent_messages[-1]['content'][:100] if recent_messages else 'None'}"""
    
    def save_to_db(self):
        """Persist conversation to project database."""
        try:
            conn = sqlite3.connect(self.project_db_path)
            cursor = conn.cursor()
            
            # Save each new message
            for msg in self.messages:
                cursor.execute("""
                    INSERT INTO conversations (
                        agent_name, user_query, agent_response, 
                        importance_level, created_at
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    "orchestrator",
                    msg['content'] if msg['role'] == 'user' else "",
                    msg['content'] if msg['role'] == 'assistant' else "",
                    "normal",
                    msg['timestamp']
                ))
            
            conn.commit()
            conn.close()
            
            # Clear messages after saving (keep only in DB)
            self.messages.clear()
            
        except Exception as e:
            print(f"Warning: Could not save conversation to database: {e}")
    
    def load_from_db(self):
        """Load recent conversation history from database."""
        try:
            conn = sqlite3.connect(self.project_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT user_query, agent_response, created_at
                FROM conversations
                WHERE agent_name = 'orchestrator'
                ORDER BY created_at DESC
                LIMIT 10
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            # Load in reverse order (oldest first)
            for row in reversed(rows):
                user_query, agent_response, timestamp = row
                if user_query:
                    self.messages.append({
                        "role": "user",
                        "content": user_query,
                        "timestamp": timestamp
                    })
                if agent_response:
                    self.messages.append({
                        "role": "assistant",
                        "content": agent_response,
                        "timestamp": timestamp
                    })
                    
        except Exception as e:
            print(f"Warning: Could not load conversation from database: {e}")
```

## File 3: `src/orchestration/agent_registry.py`

```python
"""
Agent Registry - Centralized agent access
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Centralized registry for all agents.
    Provides consistent interface for agent access.
    """
    
    def __init__(self):
        self._agents = {}
        self._initialized = False
    
    def _initialize(self):
        """Lazy initialization of agents."""
        if self._initialized:
            return
        
        try:
            # Import all agents
            from agents.nursing_research_agent import nursing_research_agent
            from agents.medical_research_agent import get_medical_research_agent
            from agents.academic_research_agent import academic_research_agent
            from agents.research_writing_agent import research_writing_agent
            from agents.nursing_project_timeline_agent import project_timeline_agent
            from agents.data_analysis_agent import data_analysis_agent
            from agents.citation_validation_agent import get_citation_validation_agent
            
            # Register agents
            self._agents = {
                "nursing_research": nursing_research_agent,
                "medical_research": get_medical_research_agent(),
                "academic_research": academic_research_agent,
                "writing": research_writing_agent,
                "timeline": project_timeline_agent,
                "data_analysis": data_analysis_agent,
                "citation_validation": get_citation_validation_agent()
            }
            
            self._initialized = True
            logger.info(f"Initialized {len(self._agents)} agents")
            
        except Exception as e:
            logger.error(f"Error initializing agents: {e}", exc_info=True)
            raise
    
    def get_agent(self, agent_name: str) -> Any:
        """
        Get agent by name.
        
        Args:
            agent_name: One of: nursing_research, medical_research, academic_research,
                       writing, timeline, data_analysis, citation_validation
        
        Returns:
            Agent instance
        
        Raises:
            ValueError: If agent_name is not recognized
        """
        if not self._initialized:
            self._initialize()
        
        if agent_name not in self._agents:
            raise ValueError(
                f"Unknown agent: {agent_name}. "
                f"Available agents: {', '.join(self._agents.keys())}"
            )
        
        return self._agents[agent_name]
    
    def list_agents(self) -> Dict[str, str]:
        """
        List all available agents with descriptions.
        
        Returns:
            Dict mapping agent names to descriptions
        """
        return {
            "nursing_research": "PICOT development, web search, healthcare standards",
            "medical_research": "PubMed search, clinical studies, systematic reviews",
            "academic_research": "ArXiv search, statistical methods, research methodologies",
            "writing": "Literature synthesis, PICOT refinement, drafting sections",
            "timeline": "Milestone tracking, deadline reminders, project management",
            "data_analysis": "Sample size calculation, statistical test selection",
            "citation_validation": "Evidence grading, retraction detection, quality scoring"
        }
```

## File 4: `src/orchestration/response_synthesizer.py`

```python
"""
Response Synthesizer - Combines agent outputs into coherent responses
"""

import json
import logging
from typing import Dict, List, Any
from openai import OpenAI

from src.orchestration.conversation_context import ConversationContext

logger = logging.getLogger(__name__)


class ResponseSynthesizer:
    """
    Synthesizes multiple agent outputs into a single coherent response.
    """
    
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4o"
    
    def synthesize(
        self,
        user_message: str,
        plan: List[Any],
        results: Dict[str, Any],
        context: ConversationContext
    ) -> str:
        """
        Synthesize agent results into coherent response.
        
        Args:
            user_message: Original user message
            plan: Execution plan that was run
            results: Results from each agent task
            context: Conversation context
        
        Returns:
            Synthesized response text
        """
        system_prompt = """You are a nursing research assistant synthesizing results from multiple specialized agents.

Your job is to create a single, coherent response that:
1. Directly addresses the user's request
2. Presents information in logical order
3. Uses checkmarks (✓) for completed steps
4. Highlights key findings with bullet points
5. Includes specific citations (PMIDs, DOIs) when available
6. Ends with actionable next steps

Tone: Professional but friendly, first person ("I found...", "I've created...")
Format: Use markdown for structure (headers, lists, bold)
Length: Comprehensive but concise (aim for 200-400 words)

DO NOT:
- Mention agent names or technical details
- Say "Agent X found..." - just present the findings
- Include raw JSON or technical output
- Be verbose or repetitive"""

        # Format results for LLM
        results_summary = self._format_results(results)
        
        user_prompt = f"""User asked: "{user_message}"

Results from execution:
{results_summary}

Context:
- Project: {context.project_name}
- Phase: {context.current_phase}

Synthesize these results into a single coherent response."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error synthesizing response: {e}", exc_info=True)
            # Fallback: concatenate results
            return self._fallback_synthesis(results)
    
    def _format_results(self, results: Dict[str, Any]) -> str:
        """Format results dict into readable text for LLM."""
        formatted = []
        
        for task_id, result in results.items():
            if result.get("success"):
                agent = result.get("agent", "unknown")
                action = result.get("action", "unknown")
                output = result.get("output", {})
                
                formatted.append(f"Task: {agent}.{action}")
                formatted.append(f"Output: {json.dumps(output, indent=2)}")
                formatted.append("")
        
        return "\n".join(formatted)
    
    def _fallback_synthesis(self, results: Dict[str, Any]) -> str:
        """Fallback synthesis if LLM fails."""
        lines = ["Here's what I found:\n"]
        
        for task_id, result in results.items():
            if result.get("success"):
                output = result.get("output", {})
                if isinstance(output, dict) and "text" in output:
                    lines.append(f"✓ {output['text']}\n")
                else:
                    lines.append(f"✓ {json.dumps(output)}\n")
        
        return "\n".join(lines)
```

## File 5: `src/orchestration/suggestion_engine.py`

```python
"""
Suggestion Engine - Generates context-aware next step suggestions
"""

import logging
from typing import List
from datetime import datetime, timedelta

from src.orchestration.conversation_context import ConversationContext

logger = logging.getLogger(__name__)


class SuggestionEngine:
    """
    Generates context-aware suggestions for next steps.
    """
    
    def generate_suggestions(self, context: ConversationContext) -> List[str]:
        """
        Generate 3-5 suggestions based on current context.
        
        Args:
            context: Current conversation context
        
        Returns:
            List of suggestion strings
        """
        suggestions = []
        
        # Phase-based suggestions
        if context.current_phase == "planning":
            suggestions.extend(self._planning_phase_suggestions(context))
        elif context.current_phase == "searching":
            suggestions.extend(self._searching_phase_suggestions(context))
        elif context.current_phase == "analyzing":
            suggestions.extend(self._analyzing_phase_suggestions(context))
        elif context.current_phase == "writing":
            suggestions.extend(self._writing_phase_suggestions(context))
        
        # Always include general suggestions
        suggestions.extend(self._general_suggestions(context))
        
        # Limit to 5 suggestions
        return suggestions[:5]
    
    def _planning_phase_suggestions(self, context: ConversationContext) -> List[str]:
        """Suggestions for planning phase."""
        suggestions = []
        
        if not context.has_artifact("generate_picot"):
            suggestions.append("Develop a PICOT question for your topic")
        else:
            suggestions.append("Search for research articles on your topic")
            suggestions.append("Create project timeline")
        
        return suggestions
    
    def _searching_phase_suggestions(self, context: ConversationContext) -> List[str]:
        """Suggestions for searching phase."""
        suggestions = []
        
        if context.has_artifact("search_pubmed"):
            suggestions.append("Validate the research articles found")
            suggestions.append("Search additional databases (ArXiv, ClinicalTrials)")
        
        suggestions.append("Grade evidence quality")
        
        return suggestions
    
    def _analyzing_phase_suggestions(self, context: ConversationContext) -> List[str]:
        """Suggestions for analyzing phase."""
        suggestions = []
        
        suggestions.append("Synthesize research findings")
        suggestions.append("Plan data analysis approach")
        suggestions.append("Calculate required sample size")
        
        return suggestions
    
    def _writing_phase_suggestions(self, context: ConversationContext) -> List[str]:
        """Suggestions for writing phase."""
        suggestions = []
        
        suggestions.append("Draft literature review section")
        suggestions.append("Create intervention plan")
        suggestions.append("Export findings to Word document")
        
        return suggestions
    
    def _general_suggestions(self, context: ConversationContext) -> List[str]:
        """General suggestions always available."""
        return [
            "Check upcoming deadlines",
            "Review completed work",
            "Ask me a question"
        ]
```

## File 6: Modified `run_nursing_project.py` (Main Entry Point)

```python
"""
Nursing Research Project Assistant - New Conversational Interface
"""

from dotenv import load_dotenv
load_dotenv(override=True)

import sys
from pathlib import Path

# Ensure vendored agno library is importable
_project_root = Path(__file__).parent
_agno_path = _project_root / "libs" / "agno"
if _agno_path.exists() and str(_agno_path) not in sys.path:
    sys.path.insert(0, str(_agno_path))

from project_manager import get_project_manager
from src.orchestration.intelligent_orchestrator import IntelligentOrchestrator
from src.orchestration.conversation_context import ConversationContext


def print_welcome():
    """Display welcome message."""
    print("\n" + "=" * 80)
    print("🏥 NURSING RESEARCH ASSISTANT")
    print("=" * 80)
    print("\nI'll help you develop your healthcare improvement project from")
    print("PICOT to poster presentation.")
    print("\nJust tell me what you'd like to work on, and I'll handle the rest!")
    print("=" * 80)


def get_or_create_project():
    """Get active project or help user create one."""
    pm = get_project_manager()
    active_project = pm.get_active_project()
    
    if active_project:
        return active_project
    
    # No active project - help user create one
    print("\n📋 Let's set up your project first.")
    print("\nWhat would you like to name your project?")
    print("(Examples: 'Fall Prevention Study', 'CAUTI Reduction', 'Pressure Ulcer Prevention')")
    
    project_name = input("\n📝 Project name: ").strip()
    
    if not project_name:
        print("❌ Project name cannot be empty. Exiting.")
        sys.exit(1)
    
    # Create project
    from project_manager import cli_create_project
    cli_create_project(project_name, add_milestones=True)
    
    return project_name


def main():
    """
    New main entry point: single conversation interface.
    """
    print_welcome()
    
    # Get or create project
    project_name = get_or_create_project()
    
    # Get project database path
    pm = get_project_manager()
    project_db = pm.get_project_db_path()
    
    # Initialize conversation context
    context = ConversationContext(
        project_name=project_name,
        project_db_path=project_db
    )
    
    # Load previous conversation if exists
    context.load_from_db()
    
    # Initialize intelligent orchestrator
    orchestrator = IntelligentOrchestrator()
    
    print(f"\n✅ Working on project: {project_name}")
    print("\nWhat would you like to work on today?\n")
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_message = input("💬 You: ").strip()
            
            # Handle exit
            if user_message.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye! Your work has been saved.")
                context.save_to_db()
                break
            
            # Handle empty input
            if not user_message:
                continue
            
            # Handle special commands
            if user_message.lower() == 'help':
                print_help()
                continue
            
            if user_message.lower() == 'switch project':
                # TODO: Implement project switching
                print("Project switching coming soon!")
                continue
            
            # Add to context
            context.add_message("user", user_message)
            
            # Process message (orchestrator handles everything)
            print("\n🤖 Assistant: ", end="", flush=True)
            
            response, suggestions = orchestrator.process_user_message(
                user_message, 
                context
            )
            
            # Print response
            print(response)
            
            # Add to context
            context.add_message("assistant", response)
            
            # Show suggestions
            if suggestions:
                print("\n💡 What would you like to do next?")
                for suggestion in suggestions:
                    print(f"   • {suggestion}")
            
            print()  # Blank line before next input
            
            # Save context periodically
            if len(context.messages) % 4 == 0:  # Every 2 exchanges
                context.save_to_db()
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Your work has been saved.")
            context.save_to_db()
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'help' for assistance.\n")


def print_help():
    """Print help message."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              HELP & EXAMPLES                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

📚 WHAT I CAN DO:
  • Develop PICOT questions
  • Search research databases (PubMed, ArXiv, ClinicalTrials)
  • Validate and grade evidence quality
  • Synthesize research findings
  • Plan data analysis and calculate sample sizes
  • Track project timeline and deadlines
  • Draft literature reviews and project sections

💬 EXAMPLE QUERIES:
  • "Research fall prevention in elderly patients"
  • "What's my next deadline?"
  • "Calculate sample size for a 30% reduction in falls"
  • "Validate these articles: PMID 12345, PMID 67890"
  • "Draft a literature review on CAUTI prevention"
  • "Show me my project timeline"

🔧 COMMANDS:
  • help          - Show this help message
  • exit          - Save and quit
  • switch project - Change to different project

Just describe what you want in natural language, and I'll figure out how to help!
""")


if __name__ == "__main__":
    main()
```

---

## Summary

These files implement the new conversational interface:

1. **IntelligentOrchestrator** - LLM-powered planning and execution
2. **ConversationContext** - Maintains state across interactions
3. **AgentRegistry** - Centralized agent access
4. **ResponseSynthesizer** - Combines agent outputs
5. **SuggestionEngine** - Generates next step suggestions
6. **Modified main()** - Simple conversation loop

**Key Features:**
- Natural language input (no menu navigation)
- Automatic agent selection and orchestration
- Unified responses (not separate agent outputs)
- Proactive suggestions
- Persistent context
- Graceful error handling

**User Experience:**
```
💬 You: Research fall prevention
🤖 Assistant: [Automatically runs 4 agents, synthesizes results]
💡 Suggestions: [Context-aware next steps]
```

This is true agentic behavior: **complex internally, simple externally**.
