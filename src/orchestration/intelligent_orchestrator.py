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
from src.orchestration.request_context import RequestContext
from src.orchestration.agent_registry import AgentRegistry
from src.orchestration.response_synthesizer import ResponseSynthesizer
from src.orchestration.suggestion_engine import SuggestionEngine
from src.orchestration.mcp import new_task, to_json_line
from src.orchestration.mcp_dispatch import dispatch_mcp
from src.orchestration.resilient_orchestrator import ResilientOrchestrator, ExecutionResult
from src.orchestration.agent_specs import build_default_agent_specs

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
        use_resilient_execution: bool = True,
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

        # Agent specs for contract validation (Phase 4)
        self.agent_specs = build_default_agent_specs()

        # Model for planning (cheaper, faster)
        self.planner_model = planner_model or "gpt-4o-mini"

        # Model for synthesis (better quality)
        self.synthesis_model = synthesis_model or "gpt-4o"

        # Resilient execution with retry and fallback
        self.use_resilient_execution = use_resilient_execution
        self.resilient_orchestrator = ResilientOrchestrator() if use_resilient_execution else None

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

            # Step 1.5: Create immutable RequestContext after validation
            # Intent is derived from primary task action or generic label
            intent = plan[0].action if plan else "execute_plan"
            request_ctx = RequestContext.create(
                query=message,
                intent=intent,
                metadata={
                    "plan_size": len(plan),
                    "conversation_phase": context.current_phase
                }
            )
            logger.info(f"Created RequestContext {request_ctx.request_id} for intent: {intent}")

            # Step 2: Execute plan
            logger.info(f"Executing plan with {len(plan)} tasks")
            results = self._execute_plan(plan, context, request_ctx=request_ctx, user_message=message)

            # Step 3: Synthesize results into coherent response
            logger.info("Synthesizing results")
            response = self.synthesizer.synthesize(
                user_message=message,
                plan=plan,
                results=results,
                context=context,
                request_id=request_ctx.request_id
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
            plan = self._parse_plan(plan_json)
            return self._validate_and_repair_plan(plan, user_message=message, context=context)

        except Exception as e:
            logger.error(f"Error creating execution plan: {e}", exc_info=True)
            logger.info("Falling back to rule-based planner")
            plan = self._fallback_plan(message, context)
            return self._validate_and_repair_plan(plan, user_message=message, context=context)

    def _parse_plan(self, plan_json: Dict[str, Any]) -> List[AgentTask]:
        """Convert JSON plan into AgentTask objects."""
        # PHASE 2 TRACE: Log the raw plan from LLM
        logger.info(f"🔍 PHASE2 TRACE: Raw plan from LLM: {json.dumps(plan_json, indent=2)}")

        tasks: List[AgentTask] = []
        for task_dict in plan_json.get("tasks", []):
            task = AgentTask(
                task_id=task_dict.get("task_id", f"task_{len(tasks)+1}"),
                agent_name=task_dict.get("agent_name", "nursing_research"),
                action=task_dict.get("action", "search"),
                params=task_dict.get("params", {}),
                depends_on=task_dict.get("depends_on", [])
            )

            # PHASE 2 TRACE: Log each task's params
            logger.info(f"🔍 PHASE2 TRACE: Task {task.task_id} params: {task.params}")

            tasks.append(task)

        logger.info(f"Created plan with {len(tasks)} tasks")
        return tasks

    def _validate_and_repair_plan(
        self,
        plan: List[AgentTask],
        *,
        user_message: str,
        context: ConversationContext,
    ) -> List[AgentTask]:
        """
        Validate/repair an execution plan against the registry capability catalog.

        This reduces drift between what the planner emits and what the system can
        execute by:
        - Normalizing agent aliases to canonical names
        - Remapping unsupported (agent, action) pairs to a compatible agent
        - Filling required params with contextual fallbacks
        - Dropping invalid dependencies
        """
        if not plan:
            return plan

        # Build action -> candidate agents map from specs.
        action_to_agents: Dict[str, List[str]] = {}
        for spec in self.agent_registry.list_agent_specs():
            for action_name in spec.actions.keys():
                action_to_agents.setdefault(action_name, []).append(spec.name)

        repaired: List[AgentTask] = []
        seen_ids = set()

        for idx, task in enumerate(plan, start=1):
            task_id = (task.task_id or "").strip() or f"task_{idx}"
            if task_id in seen_ids:
                task_id = f"{task_id}_{idx}"
            seen_ids.add(task_id)

            action = (task.action or "").strip() or "search"
            params = dict(task.params or {})

            # Normalize and validate agent selection.
            agent_name = self.agent_registry.normalize_agent_name(task.agent_name or "")
            if not self.agent_registry.is_available(agent_name):
                candidates = action_to_agents.get(action, [])
                agent_name = candidates[0] if candidates else "nursing_research"

            if not self.agent_registry.supports(agent_name, action):
                candidates = action_to_agents.get(action, [])
                if candidates:
                    agent_name = candidates[0]

            # Fill required params.
            spec = self.agent_registry.get_agent_spec(agent_name)
            action_spec = spec.action_spec(action) if spec else None
            required = list(action_spec.required_params) if action_spec else []

            topic_fallback = user_message
            if not topic_fallback and hasattr(context, "get_last_user_message"):
                topic_fallback = context.get_last_user_message()  # type: ignore[assignment]

            for key in required:
                if key not in params or params[key] in (None, "", {}, []):
                    if key in ("topic", "query"):
                        params[key] = topic_fallback
                    else:
                        params[key] = topic_fallback

            # Remove dependencies that reference unknown tasks (or self).
            depends_on = [d for d in (task.depends_on or []) if d in seen_ids and d != task_id]

            repaired.append(
                AgentTask(
                    task_id=task_id,
                    agent_name=agent_name,
                    action=action,
                    params=params,
                    depends_on=depends_on,
                )
            )

        return repaired

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
                agent_name="nursing_research",
                action="search_pubmed",
                params={"query": topic},
                depends_on=["task_1"]
            ))

        return tasks

    def _build_planner_prompt(self) -> str:
        """Build system prompt for the planner LLM."""
        agents_section = self._build_agents_capabilities_section()

        # NOTE: Do not use an f-string for this prompt because it contains many literal
        # JSON examples with braces, which can trigger f-string parsing errors.
        prompt = """You are an execution planner for a nursing research assistant system.

Your job is to decompose user goals into a sequence of agent tasks.

CRITICAL: USE CONVERSATION HISTORY TO UNDERSTAND CONTEXT.
When the user says "generate a PICOT question" or "search for articles",
look at the recent conversation to understand WHAT TOPIC they're discussing.

Examples:
- If they just discussed "nurse-aide communication", then "generate a PICOT"
  means generate a PICOT about nurse-aide communication
- If they asked about "fall prevention", then "search for articles"
  means search about fall prevention

Available agents and their capabilities (generated from the registry):
__AGENTS_SECTION__

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
   - Step 2: Search PubMed (nursing_research)
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

AGENT SELECTION GUIDE:
======================
When to use each agent:
- nursing_research: Broad healthcare topics, PICOT questions, nursing practice, quality improvement, FDA device safety, Joint Commission standards
- medical_research: Synthesize local documents/library notes; cross-document comparisons (legacy name)
- academic_research: Statistical methods, AI/ML research, theoretical frameworks, citation analysis (Semantic Scholar), paper discovery
- research_writing: Synthesizing findings, drafting sections, formatting citations
- project_timeline: Project management, deadlines, milestones
- data_analysis: Statistical calculations, sample size, power analysis
- citation_validation: Checking article quality, evidence levels, retractions

TOOL-SPECIFIC QUERIES:
======================
- "Find clinical trials for X" → nursing_research (ClinicalTrials.gov tool)
- "Latest preprints on X" → nursing_research (medRxiv tool) or academic_research (ArXiv)
- "Papers citing PMID:X" → academic_research (Semantic Scholar citation analysis)
- "FDA recalls for device X" → nursing_research (SafetyTools)
- "Open access articles on X" → nursing_research (CORE/DOAJ tools)
- "Joint Commission standards for X" → nursing_research (Google search tool)
- "Synthesize my local PDFs/notes about X" → medical_research (document/library synthesis)

Common workflows:
1. Research topic → [research_writing: generate_picot] → [nursing_research: search_pubmed] → [citation_validation: validate] → [research_writing: synthesize]
2. Clinical trial search → [nursing_research: search_clinicaltrials]
3. Citation analysis → [academic_research: search_semantic_scholar]
4. Timeline query → [project_timeline: get_milestones]
5. Statistical question → [data_analysis: calculate_sample_size]
6. Validate articles → [citation_validation: grade_evidence]
7. Device safety check → [nursing_research: search]

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
      "agent_name": "nursing_research",
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
      "agent_name": "nursing_research",
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

Example output for "Find clinical trials for fall prevention":
{
  "tasks": [
    {
      "task_id": "task_1",
      "agent_name": "nursing_research",
      "action": "search_clinicaltrials",
      "params": {"query": "fall prevention elderly"},
      "depends_on": []
    }
  ]
}

Example output for "Find papers citing PMID:12345678":
{
  "tasks": [
    {
      "task_id": "task_1",
      "agent_name": "academic_research",
      "action": "search_semantic_scholar",
      "params": {"query": "PMID:12345678 citations"},
      "depends_on": []
    }
  ]
}

Example output for "Check FDA recalls for urinary catheters":
{
  "tasks": [
    {
      "task_id": "task_1",
      "agent_name": "nursing_research",
      "action": "search",
      "params": {"query": "urinary catheter FDA recalls"},
      "depends_on": []
    }
  ]
}

BE GENEROUS WITH TASK CREATION. When in doubt, create a research workflow. Users want help, not rejection.
"""
        return prompt.replace("__AGENTS_SECTION__", agents_section)

    def _build_agents_capabilities_section(self) -> str:
        """
        Render a compact (agent -> actions) section for the planner prompt.

        Uses AgentRegistry specs so the prompt doesn't drift from reality.
        """
        lines: List[str] = []
        for spec in self.agent_registry.list_agent_specs():
            action_chunks: List[str] = []
            for action_name, action_spec in spec.actions.items():
                req = ", ".join(action_spec.required_params) if action_spec.required_params else ""
                opt = ", ".join(action_spec.optional_params) if action_spec.optional_params else ""
                parts = []
                if req:
                    parts.append(f"required: {req}")
                if opt:
                    parts.append(f"optional: {opt}")
                suffix = f" ({'; '.join(parts)})" if parts else ""
                action_chunks.append(f"{action_name}{suffix}")
            actions_str = "; ".join(action_chunks) if action_chunks else "none"
            lines.append(f"- {spec.name}: {spec.description} Actions: {actions_str}")

        return "\n".join(lines) if lines else "- (no agents registered)"

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
        context: ConversationContext,
        request_ctx: RequestContext,
        user_message: str = ""
    ) -> Dict[str, Any]:
        """
        Execute plan with dependency resolution.

        Args:
            plan: List of agent tasks to execute
            context: Conversation-level context
            request_ctx: Immutable request context (preserved across retries)
            user_message: Original user message for fallback queries
        """
        results = {}

        for task in plan:
            try:
                logger.info(f"Executing task {task.task_id}: {task.agent_name}.{task.action}")

                # Resolve dependencies
                resolved_params = self._resolve_dependencies(task.params, results)

                # FIX #1: Force valid query for query-based actions
                if task.action in (
                    "search_pubmed",
                    "search",
                    "search_arxiv",
                    "search_clinicaltrials",
                    "search_semantic_scholar",
                    "synthesize_documents",
                ):
                    query = resolved_params.get("query")
                    if not query or not isinstance(query, str) or not query.strip():
                        # Use user's original message as fallback query
                        fallback_query = user_message or context.get_last_user_message() if hasattr(context, 'get_last_user_message') else user_message
                        if fallback_query and fallback_query.strip():
                            logger.warning(f"⚠️ Planner did not generate query for {task.action}. Using user message: '{fallback_query[:50]}...'")
                            resolved_params["query"] = fallback_query.strip()
                        else:
                            raise ValueError(f"Planner did not generate a query for {task.action} and no fallback available")

                # PHASE 2 TRACE: Log resolved params after dependency resolution
                logger.info(f"🔍 PHASE2 TRACE: Resolved params for {task.task_id}: {resolved_params}")

                # Get agent
                agent = self.agent_registry.get_agent(task.agent_name)

                # Execute task
                result = self._execute_agent_task(
                    agent=agent,
                    action=task.action,
                    params=resolved_params,
                    context=context,
                    request_ctx=request_ctx,
                    registry_key=task.agent_name,  # Pass registry key for resilient execution
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
        context: ConversationContext,
        request_ctx: RequestContext,
        registry_key: Optional[str] = None,
    ) -> Any:
        """
        Execute a specific action on an agent.

        Uses ResilientOrchestrator when enabled for:
        - Exponential backoff retry on failures
        - Automatic fallback to alternative agents
        - Graceful degradation with partial results

        Args:
            agent: Agent instance to execute
            action: Action to perform on the agent
            params: Parameters for the action
            context: Conversation-level context
            request_ctx: Immutable request context (preserved across retries)
            registry_key: Registry name for resilient execution
        """
        # Phase 4: Validate contract before dispatch
        agent_name_normalized = self.agent_registry.normalize_agent_name(registry_key or "unknown")
        contract_valid, contract_error = self._validate_contract(
            agent_name_normalized, action, params
        )

        if not contract_valid:
            logger.error(
                f"PHASE4 CONTRACT VIOLATION: {agent_name_normalized}.{action} - {contract_error}"
            )
            raise ValueError(f"Contract violation: {contract_error}")

        # Build query for agent based on action and params
        query = self._build_agent_query(action, params)
        # Use registry key for resilient execution, fall back to display name for logging
        agent_display_name = getattr(agent, "agent_name", getattr(agent, "name", "Agent"))
        agent_registry_name = registry_key or agent_display_name

        # Use resilient execution if enabled
        if self.use_resilient_execution and self.resilient_orchestrator:
            logger.info(f"Using resilient execution for {agent_display_name}.{action}")

            result: ExecutionResult = self.resilient_orchestrator.execute_with_resilience(
                agent_name=agent_registry_name,  # Use registry key, not display name
                query=query,
                request_ctx=request_ctx,
                metadata={"action": action, "params": params},
            )

            if result.fallback_used:
                logger.info(
                    f"Fallback agent used: {result.agent_used} "
                    f"(original: {result.original_agent})"
                )

            if result.retries_attempted > 0:
                logger.info(f"Retries attempted: {result.retries_attempted}")

            if not result.success:
                # Check for partial results
                if result.partial_results:
                    logger.warning(
                        f"Agent execution failed but partial results available: "
                        f"{len(result.partial_results)} partial result(s)"
                    )
                    # Use first partial result as fallback
                    partial = result.partial_results[0]
                    if partial.get("content"):
                        output = self._extract_agent_output(partial["content"], action)
                        output = self._normalize_agent_output(action, output)
                        context.add_artifact(action, output)
                        return output

                raise ValueError(
                    f"Agent execution failed after {result.total_attempts} attempts: "
                    f"{'; '.join(result.errors)}"
                )

            # Extract structured output from content
            output = self._extract_agent_output(result.content, action)
            output = self._normalize_agent_output(action, output)

            # Store in context if it's an artifact
            artifact_actions = ["generate_picot", "search_pubmed", "synthesize", "validate"]
            if action in artifact_actions:
                context.add_artifact(action, output)

            return output

        # Fallback: Direct dispatch (original behavior)
        return self._execute_agent_task_direct(agent, action, params, context, request_ctx, query)

    def _execute_agent_task_direct(
        self,
        agent: Any,
        action: str,
        params: Dict[str, Any],
        context: ConversationContext,
        request_ctx: RequestContext,
        query: str
    ) -> Any:
        """
        Direct agent execution without resilience (original behavior).

        Args:
            agent: Agent instance to execute
            action: Action to perform
            params: Parameters for the action
            context: Conversation-level context
            request_ctx: Immutable request context
            query: Query string built from action and params
        """
        recipient = getattr(agent, "agent_name", getattr(agent, "name", "Agent"))
        task_msg = new_task(
            sender="IntelligentOrchestrator",
            recipient=recipient,
            content=query,
            metadata={
                "action": action,
                "params": params,
                "request_context": request_ctx.to_dict()
            },
        )

        # Log outbound envelope
        logger.debug(f"MCP Outbound: {to_json_line(task_msg)}")

        result_msg, response = dispatch_mcp(agent, task_msg, request_ctx=request_ctx, return_raw=True, **{})

        # Log inbound envelope
        logger.debug(f"MCP Inbound: {to_json_line(result_msg)}")

        if result_msg.message_type == "error":
            raise ValueError(result_msg.content)

        if response is None:
            raise RuntimeError("Expected raw agent response but got None")

        # Extract structured output
        output = self._extract_agent_output(response, action)
        output = self._normalize_agent_output(action, output)

        # Store in context if it's an artifact
        artifact_actions = ["generate_picot", "search_pubmed", "synthesize", "validate"]
        if action in artifact_actions:
            context.add_artifact(action, output)

        return output

    def _normalize_agent_output(self, action: str, output: Any) -> Any:
        """
        Normalize outputs so dependency placeholders resolve reliably.

        When agents return free-form text, `parse_json_from_response()` may fall back
        to `{"text": ...}`. For some actions (notably `generate_picot`) we ensure
        a canonical key exists so `<task_id.field>` substitutions work.
        """
        if output is None:
            return {}

        if isinstance(output, str):
            if action == "generate_picot":
                return {"picot": output, "picot_text": output, "text": output}
            return {"text": output}

        if not isinstance(output, dict):
            return {"text": str(output)}

        if action == "generate_picot":
            # Common structured schema (PICOTQuestion) uses "full_question".
            if "picot" not in output:
                full_question = output.get("full_question")
                if isinstance(full_question, str) and full_question:
                    output["picot"] = full_question
                elif isinstance(output.get("text"), str) and output.get("text"):
                    output["picot"] = output["text"]

            picot_val = output.get("picot")
            if isinstance(picot_val, dict):
                fq = picot_val.get("full_question") or picot_val.get("question")
                if isinstance(fq, str) and fq:
                    output["picot"] = fq
                    output.setdefault("picot_text", fq)
            elif isinstance(picot_val, str) and picot_val:
                output.setdefault("picot_text", picot_val)

        return output

    def _build_agent_query(self, action: str, params: Dict[str, Any]) -> str:
        """
        Build natural language query for agent based on action and params.
        """
        # PHASE 2 TRACE: Log inputs to query builder
        logger.info(f"🔍 PHASE2 TRACE: _build_agent_query(action={action!r}, params={params})")

        query_templates = {
            "generate_picot": "Generate a PICOT question for research on {topic}",
            "search_pubmed": "Search PubMed for articles about: {query}",
            "search": "Search for: {query}",
            "search_semantic_scholar": "Search Semantic Scholar for papers about: {query}",
            "validate": "Validate these articles and grade evidence levels",
            "grade_evidence": "Grade the evidence level of these articles",
            "synthesize": "Synthesize these research findings into a summary",
            "synthesize_documents": "Synthesize and compare documents/library content about: {query}",
            "calculate_sample_size": "Calculate sample size for a {design} study with {effect_size} effect size",
            "get_milestones": "Show upcoming milestones and deadlines",
            "get_next_milestone": "What is my next deadline?",
        }

        template = query_templates.get(action)
        if template:
            try:
                built_query = template.format(**params)
                # PHASE 2 TRACE: Log the built natural language query
                logger.info(f"🔍 PHASE2 TRACE: Built agent query: {built_query!r}")
                return built_query
            except KeyError as e:
                logger.warning(f"⚠️ PHASE2 TRACE: Missing key in template formatting: {e}")
                pass

        # Fallback: combine action and params
        if params:
            param_str = ", ".join(f"{k}={v}" for k, v in params.items())
            fallback_query = f"{action}: {param_str}"
        else:
            fallback_query = action

        logger.info(f"🔍 PHASE2 TRACE: Using fallback query: {fallback_query!r}")
        return fallback_query

    def _validate_contract(
        self,
        agent_name: str,
        action: str,
        params: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate agent contract before dispatch (Phase 4).

        Checks:
        - Agent spec exists
        - Action is supported
        - Required params are present

        Args:
            agent_name: Normalized agent name
            action: Action to perform
            params: Parameters provided

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if agent spec exists
        agent_spec = self.agent_specs.get(agent_name)
        if not agent_spec:
            # No spec = no validation (graceful degradation)
            logger.warning(
                f"PHASE4: No spec found for agent '{agent_name}' - skipping contract validation"
            )
            return True, None

        # Check if action is supported
        action_spec = agent_spec.action_spec(action)
        if not action_spec:
            return False, f"Action '{action}' not supported by agent '{agent_name}'"

        # Check required params
        missing_params = []
        for required_param in action_spec.required_params:
            if required_param not in params or params[required_param] is None:
                missing_params.append(required_param)

        if missing_params:
            return False, (
                f"Missing required params for {agent_name}.{action}: {missing_params}. "
                f"Provided: {list(params.keys())}"
            )

        # Log optional params for observability
        provided_optional = [
            p for p in action_spec.optional_params
            if p in params and params[p] is not None
        ]
        if provided_optional:
            logger.debug(
                f"PHASE4: {agent_name}.{action} received optional params: {provided_optional}"
            )

        return True, None

    def _extract_agent_output(self, response: Any, action: str) -> Any:
        """
        Extract structured output from agent response using robust JSON parsing.

        Uses the robust JSON parser to handle:
        - JSON + commentary
        - Multiple JSON objects (takes first only)
        - Malformed JSON

        Logs raw output to /tmp on failures for debugging.

        Returns:
            Parsed dict (never None - guaranteed by Phase 3)
        """
        from src.utils.json_parser import parse_json_from_response

        # Use robust parser with context for debugging
        context = f"{action}_extraction"
        output = parse_json_from_response(response, context=context, fallback_to_text=True)

        # Phase 3 Guard: Ensure we NEVER return None
        if output is None:
            logger.error(
                f"PHASE3 GUARD: parse_json_from_response returned None for {action}. "
                f"This should never happen with fallback_to_text=True. Returning error dict."
            )
            return {"error": "extraction_failed", "action": action, "text": str(response)[:500]}

        return output

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
