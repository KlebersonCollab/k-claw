"""Dialog flow control - determines whether to continue, compact, or end the conversation."""

from typing import Literal
from langchain_core.messages import AIMessage
from .state import HarnessState
from .utils import estimate_tokens


import os

def is_path_verified(path: str, verified_paths: set, is_directory_op: bool = False) -> bool:
    """Check if a path or its parent has been verified.
    
    Args:
        path: The path to check.
        verified_paths: Set of paths already verified.
        is_directory_op: If True, parent-level verification is sufficient.
                        If False (default), exact path match or a deep read is required.
    """
    if not path:
        return False
    norm_path = os.path.normcase(os.path.normpath(path))
    
    for p in verified_paths:
        norm_p = os.path.normcase(os.path.normpath(p))
        # Exact match is always good
        if norm_path == norm_p:
            return True
        # For directory operations (like listing), parent verification is ok
        if is_directory_op and (norm_p == "." or norm_path.startswith(norm_p)):
            return True
    return False

def should_continue(state: HarnessState) -> Literal["tools", "compact", "reflection", "planner", "limit_handler", "__end__"]:
    """Determine the next step in the dialog flow.

    Args:
        state: The current harness state.

    Returns:
        "tools" if there are tool calls to execute,
        "compact" if context needs to be compacted,
        "reflection" if the agent might have missed a tool call,
        "planner" if a pivot is requested,
        "limit_handler" if iteration limit is reached,
        "__end__" if the conversation should end.
    """
    scratchpad = state.get("scratchpad", [])

    # Use max_iterations from state (default to 50 if not present)
    max_iters = state.get("max_iterations", 50)
    if state["iteration_count"] >= max_iters:
        # If we hit the limit, we must end, but let's go via limit_handler
        return "limit_handler"

    if scratchpad and scratchpad[-1].tool_calls:
        # EPISTEMOLOGICAL LOCK: If any tool is destructive, check if verified
        destructive_tools = ["write_file", "replace_string", "run_shell"]
        violations = []
        for tc in scratchpad[-1].tool_calls:
            if tc["name"] in destructive_tools:
                path = tc["args"].get("path") or tc["args"].get("file_path")
                # write_file and replace_string are ALWAYS file ops
                is_dir = tc["name"] not in ["write_file", "replace_string"]
                if path and not is_path_verified(path, state.get("verified_paths", set()), is_directory_op=is_dir):
                    violations.append(path)
        
        if violations:
            return "reflection"

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
