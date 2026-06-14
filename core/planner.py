"""Planning node - generates a structured technical plan to guide the agent."""

from langchain_core.messages import SystemMessage, HumanMessage
from .state import HarnessState
from .model_config import get_model
from .ui_interface import EventType
from .model_caller import emit_event
from tools.env_tools import detect_workspace_env
from infra.persistence import SessionLogger


async def plan_task(state: HarnessState) -> dict:
    """Generate or update a structured technical plan.

    Args:
        state: The current harness state.

    Returns:
        Updated state with the generated plan.
    """
    model = get_model()
    
    # Determine if this is initial planning or a PIVOT (re-planning)
    is_pivot = bool(state.get("plan") and state["iteration_count"] > 0)
    
    await emit_event(EventType.THINKING_START, {"agent": "Planner" if not is_pivot else "Pivot"})

    # Detect the environment to adapt the plan
    env_info = detect_workspace_env.invoke({})

    # RETRIEVE GOLDEN RULES (Long-Term Memory)
    # Use the last message content to find relevant past lessons
    query = state["messages"][-1].content if state["messages"] else "technical project patterns"
    logger = SessionLogger(state["session_id"])
    
    past_lessons = ""
    try:
        # Search for "Technical Post-Mortem" or relevant technical keywords
        memories = logger.semantic_search(query, limit=3)
        if memories:
            past_lessons = "\n\n### RELEVANT PAST LESSONS (GOLDEN RULES):\n"
            for mem in memories:
                if mem["score"] > 0.6: # Relevance threshold
                    past_lessons += f"- {mem['summary']}: {mem['content']}\n"
    except Exception as e:
        print(f"[Planner] Warning: Could not retrieve past lessons: {e}")

    planning_prompt = (
        "You are the Strategic Planner K-Claw.\n"
        "Your mission is to decompose the user's request into a highly technical, multi-step PLAN.\n\n"
        "STRATEGIC MANDATE:\n"
        "1. BATCH RESEARCH: Group multiple file reads, searches, or listings into a single step to minimize turns.\n"
        "2. VERIFY BEFORE ACTION: Always include steps to verify file contents (read/grep) before suggesting modifications (Epistemological Rigor).\n"
        "3. PARALLEL EXECUTION: Encourage the agent to call multiple independent tools in a single turn whenever possible.\n\n"
        f"ENVIRONMENT AWARENESS:\n{env_info}\n"
        f"{past_lessons}\n"
        "Use this information to ensure your steps, test commands, and tools match the exact tech stack of the project.\n\n"
        "FORMAT: YAML block with the following fields:\n"
        "- PHASE: Brief name of the current phase.\n"
        "- STEPS: List of specific technical steps to execute.\n"
        "- DEPENDENCIES: Any tools, agents, or information required for each step.\n"
        "- SUCCESS_CRITERIA: How to know when the plan is complete.\n\n"
        "Return ONLY the YAML block."
    )
    
    if is_pivot:
        planning_prompt += (
            "\n\nCRITICAL: This is a PIVOT. You are updating an existing plan because new information was discovered.\n"
            "Analyze the last findings and the PREVIOUS plan. Adjust the steps to stay on track or change strategy if necessary."
        )
        current_context = f"PREVIOUS PLAN:\n{state['plan']}\n\nLATEST FINDINGS:\n{state['messages'][-1].content}"
    else:
        current_context = f"Request: {state['messages'][-1].content if state['messages'] else 'No request yet'}"

    messages = [
        SystemMessage(content=planning_prompt),
        HumanMessage(content=current_context)
    ]

    resp = await model.ainvoke(messages)
    plan_yaml = resp.content.strip()

    # Clean up markdown code blocks if present
    if "```yaml" in plan_yaml:
        plan_yaml = plan_yaml.split("```yaml")[1].split("```")[0].strip()
    elif "```" in plan_yaml:
        plan_yaml = plan_yaml.split("```")[1].split("```")[0].strip()

    await emit_event(EventType.THINKING_END, {"agent": "Planner" if not is_pivot else "Pivot"})

    return {
        "plan": plan_yaml,
        "iteration_count": state["iteration_count"] + 1
    }
