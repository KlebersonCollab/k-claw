"""Unit tests for core/ui_interface.py — UI interface and context vars."""

import pytest
from core.ui_interface import (
    UIInterface,
    EventType,
    set_ui,
    get_ui,
    set_current_session_id,
    get_current_session_id,
    _UI_VAR,
    _SESSION_ID_VAR,
)


class TestEventType:
    """Test EventType enum."""

    def test_all_event_types_exist(self):
        assert EventType.THINKING_START.value == "thinking_start"
        assert EventType.THINKING_END.value == "thinking_end"
        assert EventType.TOOL_START.value == "tool_start"
        assert EventType.TOOL_END.value == "tool_end"
        assert EventType.APPROVAL_REQUIRED.value == "approval_required"
        assert EventType.COMPACTION_START.value == "compaction_start"
        assert EventType.COMPACTION_END.value == "compaction_end"
        assert EventType.ERROR.value == "error"

    def test_event_type_count(self):
        assert len(EventType) == 8


class TestUIInterface:
    """Test UIInterface base class."""

    @pytest.mark.asyncio
    async def test_on_event_default(self):
        ui = UIInterface()
        # Should not raise
        await ui.on_event(EventType.THINKING_START, {})

    @pytest.mark.asyncio
    async def test_request_approval_default(self):
        ui = UIInterface()
        result = await ui.request_approval("test_tool", {})
        assert result is False


class TestContextVars:
    """Test context variable management."""

    def test_set_and_get_ui(self):
        ui = UIInterface()
        set_ui(ui)
        assert get_ui() is ui

    def test_get_ui_default(self):
        _UI_VAR.set(None)
        assert get_ui() is None

    def test_set_and_get_session_id(self):
        set_current_session_id("test-session-123")
        assert get_current_session_id() == "test-session-123"

    def test_get_session_id_default(self):
        _SESSION_ID_VAR.set(None)
        assert get_current_session_id() is None

    def test_session_id_isolation(self):
        """Context vars should be isolated per context."""
        set_current_session_id("session-1")
        assert get_current_session_id() == "session-1"
        set_current_session_id("session-2")
        assert get_current_session_id() == "session-2"
