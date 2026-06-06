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
_CURRENT_UI: Optional[UIInterface] = None

def set_ui(ui: UIInterface):
    global _CURRENT_UI
    _CURRENT_UI = ui

def get_ui() -> Optional[UIInterface]:
    return _CURRENT_UI
