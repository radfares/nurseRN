"""
Intelligent Orchestrator - LLM-powered agent coordination.

Decomposes user goals into agent tasks and synthesizes results.
Uses GPT-4o-mini for planning and GPT-4o for synthesis.

Created: 2025-12-11
FIXED: 2025-12-12 - Improved planner prompt to handle conversational queries
"""

import json
import logging
from typing import Any, Dict, List, Tuple, Optional
from dataclasses import dataclass, field

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
    params: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)


class IntelligentOrchestrator:
    """
    Orchestrates multiple agents based on user goals.

    Uses LLM to decompose goals, execute tasks, and synthesize results.
    """

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        planner_model: Optional[str] = None,
        synthesis_model: Optional[str] = None,
    ):
        """Initialize orchestrator with OpenAI client and components."""
        if client is not None:
            self.client = client
        else:
            # Only initialize OpenAI when an API key is available; otherwise rely on fallback planner.
            import os
            api_key = os.getenv("OPENAI_API_KEY")
            self.client = OpenAI() if api_key else None
        self.agent_registry = AgentRegistry()
        self.synthesizer = ResponseSynthesizer(client=self.client)
        self.suggestion_engine = SuggestionEngine()

        # Model for planning (cheaper, faster)
        self.planner_model = planner_model or "gpt-4o-mini"

        # Model for synthesis (better quality)
        self.synthesis_model = synthesis_model or "gpt-4o"

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
            # Add message to context
            context.add_message("user", message)

            # Step 1: Create execution plan
            logger.info(f"Creating execution plan for: {message[:100]}...")
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

            # Add response to context
            context.add_message("assistant", response)

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
        system_prompt = self._build_planner_prompt()
        user_prompt = self._build_planning_request(message, context)

        try:
            if self.client is None:
                raise RuntimeError("OpenAI client not configured")

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
            return self._parse_plan(plan_json)

        except Exception as e:
            logger.error(f"Error creating execution plan: {e}", exc_info=True)
            logger.info("Falling back to rule-based planner")
            return self._fallback_plan(message, context)

    def _parse_plan(self, plan_json: Dict[str, Any]) -> List[AgentTask]:
        """Convert JSON plan into AgentTask objects."""
        tasks: List[AgentTask] = []
        for task_dict in plan_json.get("tasks", []):
            tasks.append(AgentTask(
                task_id=task_dict.get("task_id", f"task_{len(tasks)+1}"),
                agent_name=task_dict.get("agent_name", "nursing_research"),
                action=task_dict.get("action", "search"),
                params=task_dict.get("params", {}),
                depends_on=task_dict.get("depends_on", [])
            ))

        logger.info(f"Created plan with {len(tasks)} tasks")
        return tasks

    def _fallback_plan(
        self,
        message: str,
        context: ConversationContext
    ) -> List[AgentTask]:
        """
        Deterministic planner used when LLM planning is unavailable.

        Keeps tests/network-restricted environments working by mapping common
        intents to a minimal task list.
        """
        topic = context.messages[-1]["content"] if getattr(context, "messages", None) else message
        topic = topic if topic else "nursing research"

        lowered = message.lower()
        tasks: List[AgentTask] = []

        if "timeline" in lowered or "milestone" in lowered:
            tasks.append(AgentTask(
                task_id="task_1",
                agent_name="project_timeline",
                action="get_milestones",
                params={"topic": topic},
                depends_on=[]
            ))
        elif "sample size" in lowered or "power" in lowered or "statistical" in lowered:
            tasks.append(AgentTask(
                task_id="task_1",
                agent_name="data_analysis",
                action="calculate_sample_size",
                params={"topic": topic, "design": "parallel", "effect_size": "estimate"},
                depends_on=[]
            ))
        elif "validate" in lowered or "retraction" in lowered:
            tasks.append(AgentTask(
                task_id="task_1",
                agent_name="citation_validation",
                action="validate",
                params={"topic": topic},
                depends_on=[]
            ))
        else:
            tasks.append(AgentTask(
                task_id="task_1",
                agent_name="research_writing",
                action="generate_picot",
                params={"topic": topic},
                depends_on=[]
            ))
            tasks.append(AgentTask(
                task_id="task_2",
                agent_name="medical_research",
                action="search_pubmed",
                params={"query": topic},
                depends_on=["task_1"]
            ))

        return tasks

    def _build_planner_prompt(self) -> str:
        """Build system prompt for the planner LLM."""
        return """You are an execution planner for a nursing research assistant system.

Your job is to decompose user goals into a sequence of agent tasks.

CRITICAL: USE CONVERSATION HISTORY TO UNDERSTAND CONTEXT.
When the user says "generate a PICOT question" or "search for articles",
look at the recent conversation to understand WHAT TOPIC they're discussing.

Examples:
- If they just discussed "nurse-aide communication", then "generate a PICOT"
  means generate a PICOT about nurse-aide communication
- If they asked about "fall prevention", then "search for articles"
  means search about fall prevention

Available agents and their capabilities:
- nursing_research: PICOT development, web search, healthcare standards, Joint Commission guidelines
- medical_research: PubMed search, clinical studies, systematic reviews, peer-reviewed articles
- academic_research: ArXiv search, statistical methods, research methodologies
- research_writing: Literature synthesis, PICOT refinement, drafting sections, citation formatting
- project_timeline: Milestone tracking, deadline reminders, project phase management
- data_analysis: Sample size calculation, statistical test selection, power analysis
- citation_validation: Evidence grading (Johns Hopkins), retraction detection, quality scoring

IMPORTANT RULES FOR PLANNING:

1. **Use Conversation History**: Always check the recent messages for the topic being discussed. Extract and reuse that topic in params.

2. **Extract Topic from Context**:
   - Look at the last 3-5 messages
   - Find the research topic or clinical question
   - Use that topic in task parameters (e.g., params.topic, params.query)

3. **Be Helpful, Not Strict**: If a user asks about a nursing/healthcare topic, create a research plan. Don't return empty tasks.

4. **Interpret Conversational Queries**: 
   - "what do you recommend" → suggest next steps based on context
   - "what are promising research topics" → search for trending topics
   - "how does X help Y" → research the relationship between X and Y

5. **Default Research Workflow** (when user asks about a topic):
   - Step 1: Generate PICOT question (research_writing)
   - Step 2: Search PubMed (medical_research)
   - Step 3: Validate articles (citation_validation) [OPTIONAL - only if articles found]
   - Step 4: Synthesize findings (research_writing)

6. **Single-Agent Queries** (simple requests):
   - Timeline questions → project_timeline only
   - Statistical calculations → data_analysis only
   - Article validation → citation_validation only

7. **Extract Topics from Natural Language**:
   - "communication between nurses and aides" → topic: "nurse-aide communication"
   - "fall prevention" → topic: "fall prevention"
   - "CAUTI reduction" → topic: "catheter-associated urinary tract infection prevention"

8. **Only Return Empty Tasks If**:
   - User says "help", "exit", "quit", "back"
   - User message is gibberish or completely unrelated to healthcare
   - User is just chatting without a request

Common workflows:
1. Research topic → [research_writing: generate_picot] → [medical_research: search_pubmed] → [citation_validation: validate] → [research_writing: synthesize]
2. Timeline query → [project_timeline: get_milestones]
3. Statistical question → [data_analysis: calculate_sample_size]
4. Validate articles → [citation_validation: grade_evidence]

Return a JSON object with a "tasks" array. Each task has:
- task_id: Unique identifier (e.g., "task_1")
- agent_name: One of the available agents
- action: The action to perform
- params: Parameters for the action (object). Include "topic" derived from recent conversation when relevant.
- depends_on: Array of task_ids this depends on

Use "<task_id.field>" syntax for dependency values.

Example output for "research fall prevention":
{
  "tasks": [
    {
      "task_id": "task_1",
      "agent_name": "research_writing",
      "action": "generate_picot",
      "params": {"topic": "fall prevention", "population": "elderly"},
      "depends_on": []
    },
    {
      "task_id": "task_2",
      "agent_name": "medical_research",
      "action": "search_pubmed",
      "params": {"query": "<task_1.picot>"},
      "depends_on": ["task_1"]
    }
  ]
}

Example output for "what do you recommend":
{
  "tasks": [
    {
      "task_id": "task_1",
      "agent_name": "project_timeline",
      "action": "get_next_milestone",
      "params": {},
      "depends_on": []
    }
  ]
}

Example output for "how does X help Y":
{
  "tasks": [
    {
      "task_id": "task_1",
      "agent_name": "research_writing",
      "action": "generate_picot",
      "params": {"topic": "X and Y relationship"},
      "depends_on": []
    },
    {
      "task_id": "task_2",
      "agent_name": "medical_research",
      "action": "search_pubmed",
      "params": {"query": "<task_1.picot>"},
      "depends_on": ["task_1"]
    }
  ]
}

Example output for "generate a PICOT" (when discussing nurse-aide communication):
{
  "tasks": [
    {
      "task_id": "task_1",
      "agent_name": "research_writing",
      "action": "generate_picot",
      "params": {"topic": "nurse-aide communication and workflow efficiency"},
      "depends_on": []
    }
  ]
}

BE GENEROUS WITH TASK CREATION. When in doubt, create a research workflow. Users want help, not rejection.
"""

    def _build_planning_request(
        self,
        message: str,
        context: ConversationContext
    ) -> str:
        """Build the user prompt for planning."""
        artifacts_list = list(context.artifacts.keys()) if context.artifacts else ["None"]
        completed_list = list(context.completed_tasks) if context.completed_tasks else ["None"]

        # Get recent conversation history (last 5 messages), truncated for brevity
        recent_messages = []
        if hasattr(context, 'messages') and context.messages:
            last_n = min(5, len(context.messages))
            for msg in context.messages[-last_n:]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                if isinstance(content, str) and len(content) > 200:
                    content = content[:200] + "..."
                recent_messages.append(f"{role}: {content}")

        conversation_history = "\n".join(recent_messages) if recent_messages else "No previous messages"

        return f"""User message: "{message}"

Recent conversation (last 5 messages):
{conversation_history}

Conversation context:
- Project: {context.project_name}
- Phase: {context.current_phase}
- Completed tasks: {', '.join(completed_list)}
- Available artifacts: {', '.join(artifacts_list)}

Create an execution plan as a JSON object with a "tasks" array.

IMPORTANT: Look at the recent conversation to understand what topic the user is discussing.
If they say "generate a PICOT" or "search for articles", use the topic from the recent messages.
Remember: Be helpful! If the user is asking about a nursing/healthcare topic, create a research plan. Don't return empty tasks unless the request is truly unclear or unrelated."""

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

                # Mark task as completed in context
                context.mark_task_completed(task.agent_name, task.action)

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
            params = {"query": "<task_1.picot>"}
            results = {"task_1": {"output": {"picot": "In elderly..."}}}
            → {"query": "In elderly..."}
        """
        resolved = {}

        for key, value in params.items():
            if isinstance(value, str) and value.startswith("<") and value.endswith(">"):
                # Dependency reference: <task_id.field>
                ref = value[1:-1]  # Remove < >
                if "." in ref:
                    task_id, field_path = ref.split(".", 1)

                    if task_id in results and "output" in results[task_id]:
                        resolved[key] = self._get_nested_value(
                            results[task_id]["output"],
                            field_path
                        )
                    else:
                        logger.warning(f"Dependency not found: {ref}")
                        resolved[key] = value
                else:
                    # Just task reference, get full output
                    if ref in results and "output" in results[ref]:
                        resolved[key] = results[ref]["output"]
                    else:
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
            elif hasattr(value, key):
                value = getattr(value, key)
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

        # Run agent - prefer grounding-checked method
        if hasattr(agent, 'run_with_grounding_check'):
            response = agent.run_with_grounding_check(query)
        elif hasattr(agent, 'agent') and hasattr(agent.agent, 'run'):
            response = agent.agent.run(query)
        elif hasattr(agent, 'run'):
            response = agent.run(query)
        else:
            raise ValueError(f"Agent has no compatible run method")

        # Extract structured output
        output = self._extract_agent_output(response, action)

        # Store in context if it's an artifact
        artifact_actions = ["generate_picot", "search_pubmed", "synthesize", "validate"]
        if action in artifact_actions:
            context.add_artifact(action, output)

        return output

    def _build_agent_query(self, action: str, params: Dict[str, Any]) -> str:
        """
        Build natural language query for agent based on action and params.
        """
        query_templates = {
            "generate_picot": "Generate a PICOT question for research on {topic}",
            "search_pubmed": "Search PubMed for articles about: {query}",
            "search": "Search for: {query}",
            "validate": "Validate these articles and grade evidence levels",
            "grade_evidence": "Grade the evidence level of these articles",
            "synthesize": "Synthesize these research findings into a summary",
            "calculate_sample_size": "Calculate sample size for a {design} study with {effect_size} effect size",
            "get_milestones": "Show upcoming milestones and deadlines",
            "get_next_milestone": "What is my next deadline?",
        }

        template = query_templates.get(action)
        if template:
            try:
                return template.format(**params)
            except KeyError:
                pass

        # Fallback: combine action and params
        if params:
            param_str = ", ".join(f"{k}={v}" for k, v in params.items())
            return f"{action}: {param_str}"
        return action

    def _extract_agent_output(self, response: Any, action: str) -> Any:
        """
        Extract structured output from agent response.
        """
        # Handle Pydantic models (from data_analysis_agent)
        if hasattr(response, 'model_dump'):
            return response.model_dump()
        elif hasattr(response, 'dict'):  # Older Pydantic versions
            return response.dict()

        # Handle dict responses (from grounding check)
        if isinstance(response, dict):
            return response

        # Try to get content from response object
        content = None
        if hasattr(response, 'content'):
            content = response.content
        elif hasattr(response, 'messages') and response.messages:
            content = response.messages[-1].content if hasattr(response.messages[-1], 'content') else str(response.messages[-1])
        else:
            content = str(response)

        # Try to parse as JSON
        if content and isinstance(content, str):
            try:
                if "{" in content and "}" in content:
                    start = content.index("{")
                    end = content.rindex("}") + 1
                    json_str = content[start:end]
                    return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                pass

        # Return as text
        return {"text": content if content else str(response)}

    def _handle_unclear_intent(
        self,
        message: str,
        context: ConversationContext
    ) -> Tuple[str, List[str]]:
        """
        Handle cases where intent is unclear.
        """
        response = """I'm not sure I understand what you'd like to do.

Could you clarify? For example:
- "Research fall prevention in elderly patients"
- "What's my next deadline?"
- "Calculate sample size for my study"
- "Validate these articles: PMID 12345, PMID 67890"

Or type 'help' to see what I can do."""

        suggestions = self.suggestion_engine.get_help_suggestions()

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

        suggestions = ["Try again", "Get help", "Check project status"]

        return response, suggestions


__all__ = ['IntelligentOrchestrator', 'AgentTask']
