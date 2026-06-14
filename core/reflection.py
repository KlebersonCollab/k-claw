"""Reflection node - validates agent responses against the plan and catches missing tool calls."""

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .state import HarnessState
from .ui_interface import EventType
from .model_caller import emit_event


async def reflect_on_action(state: HarnessState) -> dict:
    """Analyze the last agent response for missing actions or plan deviations.

    Args:
        state: The current harness state.

    Returns:
        A dictionary that can trigger a self-correction message if needed.
    """
    messages = state.get("messages", [])
    if not messages or not isinstance(messages[-1], AIMessage):
        return {}

    last_msg = messages[-1]
    content = last_msg.content or ""
    
    # If the message already has tool calls, it's proceeding, no need for reflection now
    if last_msg.tool_calls:
        return {}

    # Keywords that indicate intent to act but might be missing a tool call
    intent_keywords = ["vou solicitar", "delegar", "solicitar ao", "call the", "delegate to", "i will", "preciso envolver"]
    
    # Technical actions that require assumption validation
    action_keywords = ["escrever", "alterar", "deletar", "executar", "write", "modify", "delete", "execute"]

    has_intent = any(kw in content.lower() for kw in intent_keywords)
    requires_validation = any(kw in content.lower() for kw in action_keywords)
    
    # Plan Alignment Check
    plan = state.get("plan", "")
    is_deviating = False
    if plan and requires_validation:
        # Check if keywords from the proposed action are at least mentioned in the plan
        # (This is a fuzzy check, but helps catch completely random actions)
        # We look at the current action words and check if they exist in the plan.
        pass # Fuzzy logic can be complex, let's stick to explicit protocol enforcement for now

    if has_intent or requires_validation:
        await emit_event(EventType.THINKING_START, {"agent": "Reflection"})
        
        correction_parts = []
        if has_intent and not last_msg.tool_calls:
            correction_parts.append(
                "ACTION REQUIRED: You expressed intent to act but didn't call a tool. "
                "Execute the tool call immediately (e.g., `delegate_to_agent`)."
            )
        
        if requires_validation:
            correction_parts.append(
                "EPISTEMOLOGICAL CHECK: Before performing this technical action, "
                "you MUST explicitly list your ASSUMPTIONS (premises). "
                "Verify file paths and module structure in the `GLOBAL BLACKBOARD` or via `grep_search` before acting."
            )
            
            # More aggressive Pivot suggestion
            if plan:
                content_lower = content.lower()
                plan_keywords = [step.split(":")[0].lower() for step in plan.split("-") if ":" in step]
                is_matching_plan = any(kw in content_lower for kw in plan_keywords)
                
                if not is_matching_plan and "ajustar o plano" not in content_lower:
                    correction_parts.append(
                        "PLAN DEVIATION DETECTED: Your proposed action does not seem to match any step in your ACTIVE TECHNICAL PLAN. "
                        "If you have discovered a better way or found a roadblock, you MUST say 'Preciso ajustar o plano' to update your strategy before proceeding."
                    )
                elif "erro" in content_lower or "falha" in content_lower or "não encontrei" in content_lower:
                    correction_parts.append(
                        "STRATEGIC ADVICE: You've encountered an issue or a gap. "
                        "Consider saying 'Preciso ajustar o plano' to perform a PIVOT and incorporate these findings into a revised technical strategy."
                    )

        # If we have something to say, nudge the agent
        if correction_parts:
            await emit_event(EventType.THINKING_END, {"agent": "Reflection"})
            return {
                "scratchpad": [HumanMessage(content="\n\n".join(correction_parts))],
                "iteration_count": state["iteration_count"] + 1
            }

    return {}
