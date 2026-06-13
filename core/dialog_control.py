"""Dialog flow control - determines whether to continue, compact, or end the conversation."""

from typing import Literal
from langchain_core.messages import AIMessage
from .state import HarnessState
from .utils import estimate_tokens


def should_continue(state: HarnessState) -> Literal["tools", "compact", "reflection", "__end__"]:
    """Determine the next step in the dialog flow.

    Args:
        state: The current harness state.

    Returns:
        "tools" if there are tool calls to execute,
        "compact" if context needs to be compacted,
        "reflection" if the agent might have missed a tool call,
        "__end__" if the conversation should end.
    """
    scratchpad = state.get("scratchpad", [])

    # Use max_iterations from state (default to 50 if not present)
    max_iters = state.get("max_iterations", 50)
    if state["iteration_count"] > max_iters:
        return "__end__"

    if scratchpad and scratchpad[-1].tool_calls:
        # Include scratchpad in token count to detect long turns
        token_count = estimate_tokens(state["messages"] + scratchpad)
        # Increased message threshold to 50 to allow more turns before summarizing
        if token_count > 35000 or len(state["messages"]) > state.get("context_budget", 50):
            return "compact"
        return "tools"

    # If no tools were called, check if we should reflect or pivot
    messages = state.get("messages", [])
    if messages and isinstance(messages[-1], AIMessage):
        content = messages[-1].content or ""
        
        # PIVOT Check: If agent says it needs to change plan or discovered something critical
        pivot_keywords = ["preciso ajustar o plano", "mudar estratégia", "descobri que o plano", "update plan", "pivot"]
        if any(kw in content.lower() for kw in pivot_keywords):
            return "planner"

        intent_keywords = ["vou solicitar", "delegar", "solicitar ao", "call the", "delegate to", "i will", "preciso envolver"]
        if any(kw in content.lower() for kw in intent_keywords):
            return "reflection"

    return "__end__"
