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
    
    has_intent = any(kw in content.lower() for kw in intent_keywords)
    
    if has_intent:
        await emit_event(EventType.THINKING_START, {"agent": "Reflection"})
        
        correction_prompt = (
            "REFLECTION ALERT: You expressed an intent to delegate or perform an action, "
            "but you did NOT call any tools. \n\n"
            "If you intended to delegate to a specialist (architect, coder, etc.), "
            "you MUST use the `delegate_to_agent` tool now. \n"
            "Do not just talk about it; EXECUTE the tool call."
        )
        
        # We inject a small correction message to nudge the agent
        # We return it in a way that the harness can use to loop back to 'agent'
        await emit_event(EventType.THINKING_END, {"agent": "Reflection"})
        
        return {
            "scratchpad": [HumanMessage(content=correction_prompt)],
            "iteration_count": state["iteration_count"] + 1
        }

    return {}
