"""Dialog flow control - determines whether to continue, compact, or end the conversation."""

from typing import Literal
from .state import HarnessState
from .utils import estimate_tokens


def should_continue(state: HarnessState) -> Literal["tools", "compact", "__end__"]:
    """Determine the next step in the dialog flow.

    Args:
        state: The current harness state.

    Returns:
        "tools" if there are tool calls to execute,
        "compact" if context needs to be compacted,
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

    return "__end__"
