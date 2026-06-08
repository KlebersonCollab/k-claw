"""Integration tests for the complete harness flow."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from core.harness import harness
from core.model_caller import call_model
from core.dialog_control import should_continue


class TestModelCallerFlow:
    """Test the model caller integration."""

    @pytest.mark.asyncio
    async def test_call_model_returns_response(self, clean_state, mock_model):
        with patch("core.model_caller.get_model", return_value=mock_model):
            result = await call_model(clean_state)
            assert "messages" in result
            assert "iteration_count" in result

    @pytest.mark.asyncio
    async def test_call_model_increments_iteration(self, clean_state, mock_model):
        with patch("core.model_caller.get_model", return_value=mock_model):
            result = await call_model(clean_state)
            assert result["iteration_count"] == clean_state["iteration_count"] + 1

    @pytest.mark.asyncio
    async def test_call_model_with_tool_calls(self, clean_state, mock_model_with_tool_call):
        with patch("core.model_caller.get_model", return_value=mock_model_with_tool_call):
            result = await call_model(clean_state)
            assert "scratchpad" in result
            assert result["scratchpad"][-1].tool_calls is not None

    @pytest.mark.asyncio
    async def test_call_model_clears_scratchpad_on_final(self, clean_state, mock_model):
        with patch("core.model_caller.get_model", return_value=mock_model):
            result = await call_model(clean_state)
            assert result.get("scratchpad") is None

    @pytest.mark.asyncio
    async def test_call_model_incognito_no_logging(self, state_incognito, mock_model):
        with patch("core.model_caller.get_model", return_value=mock_model):
            with patch("core.model_caller.SessionLogger") as mock_logger:
                result = await call_model(state_incognito)
                mock_logger.return_value.log_messages.assert_not_called()


class TestDialogFlowIntegration:
    """Test dialog control integration with state."""

    def test_full_conversation_flow(self, clean_state):
        """Simulate a conversation: tool call → end."""
        # First: model returns tool call
        state_with_tools = {
            **clean_state,
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "read_file", "args": {"path": "test.txt"}, "id": "call_1"}]
                )
            ],
        }
        assert should_continue(state_with_tools) == "tools"

        # Then: model returns final response
        state_final = {
            **clean_state,
            "scratchpad": [AIMessage(content="Here is the result")],
        }
        assert should_continue(state_final) == "__end__"

    def test_iteration_limit_flow(self, clean_state):
        """Test that iteration limit is respected."""
        state = {
            **clean_state,
            "iteration_count": 50,
            "max_iterations": 10,
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "read_file", "args": {"path": "test.txt"}, "id": "call_1"}]
                )
            ],
        }
        assert should_continue(state) == "__end__"

    def test_compaction_flow(self, clean_state):
        """Test that compaction is triggered when context is large."""
        # 160,000 chars / 4 = 40,000 tokens (> 35,000)
        state = {
            **clean_state,
            "messages": [HumanMessage(content="A" * 160000)],
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{"name": "read_file", "args": {"path": "test.txt"}, "id": "call_1"}]
                )
            ],
        }
        assert should_continue(state) == "compact"


class TestHarnessIntegration:
    """Test harness graph execution."""

    @pytest.mark.asyncio
    async def test_harness_simple_query(self, mock_model):
        """Test a simple query through the harness."""
        session_id = "integration-test-simple"
        config = {"configurable": {"thread_id": session_id}}

        with patch("core.model_caller.get_model", return_value=mock_model):
            state = {
                "messages": [HumanMessage(content="Hello")],
                "context_budget": 10,
                "max_iterations": 5,
                "iteration_count": 0,
                "session_id": session_id,
                "permissions": "read",
                "context_summary": "",
                "incognito": True,
                "yolo": False,
            }
            result = await harness.ainvoke(state, config=config)
            assert "messages" in result

    @pytest.mark.asyncio
    async def test_harness_get_state(self, mock_model):
        """Test getting state from harness."""
        session_id = "integration-test-state"
        config = {"configurable": {"thread_id": session_id}}

        with patch("core.model_caller.get_model", return_value=mock_model):
            state = {
                "messages": [HumanMessage(content="Hello")],
                "context_budget": 10,
                "max_iterations": 5,
                "iteration_count": 0,
                "session_id": session_id,
                "permissions": "read",
                "context_summary": "",
                "incognito": True,
                "yolo": False,
            }
            await harness.ainvoke(state, config=config)
            snapshot = harness.get_state(config)
            assert snapshot is not None
