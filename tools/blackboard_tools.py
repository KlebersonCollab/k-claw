"""Blackboard tools - allows agents to share variables and structured state."""

import json
from langchain_core.tools import tool
from core.state import HarnessState
from tools.registry import set_harness_refs, _HARNESS_REF

# Note: Since standard tools don't return state updates directly to LangGraph 
# without special Artifact mapping in newer LangChain versions, we interact 
# directly with the state by utilizing the fact that these functions are invoked
# within the executor, or we can use a simpler approach: 
# The executor will detect 'update_blackboard' and handle the state dict return natively.

@tool
def read_blackboard() -> str:
    """Reads all variables currently stored in the shared Blackboard."""
    # This is a bit tricky as tools are stateless. We'll handle state injection
    # dynamically in the executor or prompt builder. For the tool itself, 
    # we return a placeholder that the executor intercepts, OR we rely on 
    # the prompt builder injecting the blackboard content into every turn.
    return "Check your SYSTEM PROMPT to see the current BLACKBOARD STATE. It is injected automatically."

@tool
def update_blackboard(key: str, value: str) -> str:
    """
    Saves a variable to the shared Blackboard. Use this to pass specific 
    paths, IDs, or findings to other agents without relying on long text reports.
    Returns a special command string intercepted by the tool executor.
    """
    # The executor will catch this specific string format to update the state
    payload = json.dumps({key: value})
    return f"__BLACKBOARD_UPDATE__:{payload}"
