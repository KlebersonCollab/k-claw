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
                "Are you sure about the file path? The module structure? "
                "State your assumptions clearly before acting."
            )

        # If we have something to say, nudge the agent
        if correction_parts:
            await emit_event(EventType.THINKING_END, {"agent": "Reflection"})
            return {
                "scratchpad": [HumanMessage(content="\n\n".join(correction_parts))],
                "iteration_count": state["iteration_count"] + 1
            }

    return {}
