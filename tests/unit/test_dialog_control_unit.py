"""Unit tests for core/dialog_control.py — dialog flow control."""

import pytest
from unittest.mock import patch
from langchain_core.messages import HumanMessage, AIMessage
from core.dialog_control import should_continue


class TestShouldContinue:
    """Test the should_continue routing function."""

    def test_returns_end_when_no_scratchpad(self, clean_state):
        result = should_continue(clean_state)
        assert result == "__end__"

    def test_returns_end_when_scratchpad_empty(self, clean_state):
        state = {**clean_state, "scratchpad": []}
        result = should_continue(state)
        assert result == "__end__"

    def test_returns_end_when_no_tool_calls(self, clean_state):
        state = {
            **clean_state,
            "scratchpad": [AIMessage(content="Just a response")],
        }
        result = should_continue(state)
        assert result == "__end__"

    def test_returns_tools_when_tool_calls_present(self, clean_state):
        state = {
            **clean_state,
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "read_file", "args": {"path": "test.txt"}, "id": "call_1"}]
                )
            ],
        }
        result = should_continue(state)
        assert result == "tools"

    def test_returns_end_when_max_iterations_exceeded(self, clean_state):
        state = {
            **clean_state,
            "iteration_count": 11,
            "max_iterations": 10,
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "read_file", "args": {"path": "test.txt"}, "id": "call_1"}]
                )
            ],
        }
        result = should_continue(state)
        assert result == "__end__"

    def test_returns_compact_when_token_count_exceeded(self, clean_state):
        # estimate_tokens uses chars/4, so 140004 chars = 35001 tokens > 35000 threshold
        state = {
            **clean_state,
            "messages": [HumanMessage(content="A" * 140004)],
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "read_file", "args": {"path": "test.txt"}, "id": "call_1"}]
                )
            ],
        }
        result = should_continue(state)
        assert result == "compact"

    def test_returns_compact_when_context_budget_exceeded(self, clean_state):
        state = {
            **clean_state,
            "context_budget": 2,
            "messages": [
                HumanMessage(content="msg1"),
                AIMessage(content="msg2"),
                HumanMessage(content="msg3"),
                AIMessage(content="msg4"),
            ],
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "read_file", "args": {"path": "test.txt"}, "id": "call_1"}]
                )
            ],
        }
        result = should_continue(state)
        assert result == "compact"

    def test_iteration_count_at_boundary(self, clean_state):
        """When iteration_count equals max_iterations, should still allow."""
        state = {
            **clean_state,
            "iteration_count": 10,
            "max_iterations": 10,
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "read_file", "args": {"path": "test.txt"}, "id": "call_1"}]
                )
            ],
        }
        result = should_continue(state)
        assert result == "tools"

    def test_iteration_count_one_over_boundary(self, clean_state):
        """When iteration_count is max+1, should end."""
        state = {
            **clean_state,
            "iteration_count": 11,
            "max_iterations": 10,
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "read_file", "args": {"path": "test.txt"}, "id": "call_1"}]
                )
            ],
        }
        result = should_continue(state)
        assert result == "__end__"
