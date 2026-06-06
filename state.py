from typing import Annotated, TypedDict, List
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class HarnessState(TypedDict):
    # Standard LangGraph message history
    messages: Annotated[List[BaseMessage], add_messages]

    # Harness specific metadata
    context_budget: int  # Max tokens before compaction
    iteration_count: int # Safety cap
    session_id: str      # For persistence
    permissions: str     # Current permission level (e.g., "read", "write", "admin")

    # Summary of older context (for compaction)
    context_summary: str

    # Flags
    incognito: bool # If True, don't log to DB
