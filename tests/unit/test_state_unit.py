"""Unit tests for core/state.py — HarnessState and reducers."""

import pytest
from langchain_core.messages import HumanMessage, AIMessage
from core.state import HarnessState, replace_scratchpad


class TestReplaceScratchpad:
    """Test the scratchpad reducer function."""

    def test_replaces_with_new_content(self):
        existing = [HumanMessage(content="old")]
        new = [AIMessage(content="new")]
        result = replace_scratchpad(existing, new)
        assert len(result) == 1
        assert result[0].content == "new"

    def test_clears_when_new_is_none(self):
        existing = [HumanMessage(content="old")]
        result = replace_scratchpad(existing, None)
        assert result == []

    def test_empty_existing_and_new(self):
        result = replace_scratchpad([], [])
        assert result == []

    def test_none_existing_with_new(self):
        new = [AIMessage(content="new")]
        result = replace_scratchpad(None, new)
        assert len(result) == 1

    def test_preserves_multiple_messages(self):
        new = [
            HumanMessage(content="msg1"),
            AIMessage(content="msg2"),
            HumanMessage(content="msg3"),
        ]
        result = replace_scratchpad([], new)
        assert len(result) == 3


class TestHarnessState:
    """Test HarnessState TypedDict structure."""

    def test_state_has_required_fields(self, clean_state):
        expected_keys = {
            "messages", "context_budget", "max_iterations",
            "iteration_count", "session_id", "permissions", "context_summary",
            "incognito", "yolo",
        }
        assert expected_keys.issubset(set(clean_state.keys()))

    def test_state_default_values(self, clean_state):
        assert clean_state["context_budget"] == 50
        assert clean_state["max_iterations"] == 10
        assert clean_state["iteration_count"] == 0
        assert clean_state["incognito"] is False
        assert clean_state["yolo"] is False

    def test_state_with_messages(self, state_with_messages):
        assert len(state_with_messages["messages"]) == 3
        assert isinstance(state_with_messages["messages"][0], HumanMessage)
        assert isinstance(state_with_messages["messages"][1], AIMessage)

    def test_state_with_scratchpad(self, state_with_scratchpad):
        assert "scratchpad" in state_with_scratchpad
        assert len(state_with_scratchpad["scratchpad"]) == 1

    def test_state_incognito_flag(self, state_incognito):
        assert state_incognito["incognito"] is True

    def test_state_yolo_flag(self, state_yolo):
        assert state_yolo["yolo"] is True
