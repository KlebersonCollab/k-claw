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
    if state.get("plan") and state["iteration_count"] > 0:
        # Plan already exists and we are mid-execution, don't re-plan unless requested
        # (For now, we only plan once at the start or if plan is empty)
        return {}

    await emit_event(EventType.THINKING_START, {"agent": "Planner"})
    model = get_model()

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

    messages = [
        SystemMessage(content=planning_prompt),
        HumanMessage(content=f"Request: {state['messages'][-1].content if state['messages'] else 'No request yet'}")
    ]

    resp = await model.ainvoke(messages)
    plan_yaml = resp.content.strip()

    # Clean up markdown code blocks if present
    if "```yaml" in plan_yaml:
        plan_yaml = plan_yaml.split("```yaml")[1].split("```")[0].strip()
    elif "```" in plan_yaml:
        plan_yaml = plan_yaml.split("```")[1].split("```")[0].strip()

    await emit_event(EventType.THINKING_END, {"agent": "Planner"})

    return {
        "plan": plan_yaml,
        "iteration_count": state["iteration_count"] + 1
    }
