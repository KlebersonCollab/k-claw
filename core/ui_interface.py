import contextvars
from enum import Enum
from typing import Any, Dict, Optional, Callable, Awaitable

class EventType(Enum):
    THINKING_START = "thinking_start"
    THINKING_END = "thinking_end"
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    APPROVAL_REQUIRED = "approval_required"
    COMPACTION_START = "compaction_start"
    COMPACTION_END = "compaction_end"
    ERROR = "error"

class UIInterface:
    """Base class for UI implementations (CLI, API, etc.)"""
    async def on_event(self, event_type: EventType, data: Dict[str, Any]):
        pass

    async def request_approval(self, tool_name: str, args: Dict[str, Any]) -> bool:
        """Should return True if approved, False otherwise."""
        return False

# Context-based singleton to avoid passing UI everywhere
# Using ContextVar for thread-safety in async/multi-user environments
_UI_VAR: contextvars.ContextVar[Optional[UIInterface]] = contextvars.ContextVar("current_ui", default=None)
_SESSION_ID_VAR: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("current_session_id", default=None)

def set_ui(ui: UIInterface):
    _UI_VAR.set(ui)

def get_ui() -> Optional[UIInterface]:
    return _UI_VAR.get()

def set_current_session_id(session_id: str):
    _SESSION_ID_VAR.set(session_id)

def get_current_session_id() -> Optional[str]:
    return _SESSION_ID_VAR.get()
