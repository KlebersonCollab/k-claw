from typing import Annotated, TypedDict, List, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

def replace_scratchpad(existing: Optional[List[BaseMessage]], new: Optional[List[BaseMessage]]) -> List[BaseMessage]:
    """Reducer that replaces the scratchpad instead of appending, allowing it to be cleared."""
    if new is None:
        return []
    return new

class HarnessState(TypedDict):
    # Standard LangGraph message history (Only User and Final AI responses)
    messages: Annotated[List[BaseMessage], add_messages]

    # Ephemeral scratchpad for tools and intermediate thoughts within a turn
    scratchpad: Annotated[List[BaseMessage], replace_scratchpad]

    # Harness specific metadata
    context_budget: int  # Max tokens/messages before compaction
    max_iterations: int  # Max tool loops before termination
    iteration_count: int # Current iteration count
    session_id: str      # For persistence
    permissions: str     # Current permission level (e.g., "read", "write", "admin")
    workspace_path: Optional[str] # Path to the active workspace (e.g. root or git worktree)

    # Summary of older context (for compaction)
    context_summary: str

    # Structured technical plan (YAML)
    plan: str

    # Flags
    incognito: bool # If True, don't log to DB
    yolo: bool      # If True, bypass all approvals
