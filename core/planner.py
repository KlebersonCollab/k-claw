"""Planning node - generates a structured technical plan to guide the agent."""

from langchain_core.messages import SystemMessage, HumanMessage
from .state import HarnessState
from .model_config import get_model
from .ui_interface import EventType
from .model_caller import emit_event


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

    planning_prompt = (
        "You are the Strategic Planner K-Claw.\n"
        "Your mission is to decompose the user's request into a highly technical, multi-step PLAN.\n\n"
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
