"""Unit tests for core/tool_executor.py — tool execution with hooks and approval."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from langchain_core.messages import AIMessage, ToolMessage
from core.tool_executor import execute_tools
from core.hooks import HookManager, HookResult


class TestExecuteTools:
    """Test tool execution."""

    @pytest.mark.asyncio
    async def test_no_tool_calls_returns_unchanged_scratchpad(self):
        """When scratchpad has no tool calls, should return as-is."""
        state = {
            "scratchpad": [AIMessage(content="Just a response")],
            "session_id": "test-session",
            "permissions": "read",
            "incognito": False,
            "yolo": False,
        }

        with patch("core.tool_executor.get_ui", return_value=None):
            with patch("core.tool_executor.SessionLogger"):
                result = await execute_tools(state)
                assert "scratchpad" in result

    @pytest.mark.asyncio
    async def test_yolo_mode_injects_parent_yolo(self):
        """When yolo=True, delegate_to_agent should get parent_yolo=True."""
        state = {
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "delegate_to_agent",
                        "args": {"agent_id": "coder", "mission": "test"},
                        "id": "call_1"
                    }]
                )
            ],
            "session_id": "test-session",
            "permissions": "read",
            "incognito": False,
            "yolo": True,
        }

        captured_args = {}

        with patch("core.tool_executor.get_ui", return_value=None):
            with patch("core.tool_executor.SessionLogger"):
                with patch("core.tool_executor.registry") as mock_registry:
                    mock_desc = MagicMock()
                    desc_handler = MagicMock()
                    desc_handler.ainvoke = AsyncMock(return_value="result")
                    mock_desc.handler = desc_handler
                    mock_desc.requires_approval = False
                    mock_registry.tools.get.return_value = mock_desc
                    result = await execute_tools(state)
                    # Check that parent_yolo was injected
                    call_args = desc_handler.ainvoke.call_args[0][0]
                    captured_args.update(call_args)

        assert captured_args.get("parent_yolo") is True

    @pytest.mark.asyncio
    async def test_hook_denial_stops_tool_execution(self):
        """When a pre-tool hook denies, tool should not execute."""
        async def deny_hook(tool_name, tool_args, context):
            return HookResult(allowed=False)

        hm = HookManager()
        hm.register_pre_tool(deny_hook)

        state = {
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "read_file",
                        "args": {"path": "test.txt"},
                        "id": "call_1"
                    }]
                )
            ],
            "session_id": "test-session",
            "permissions": "read",
            "incognito": False,
            "yolo": True,
        }

        with patch("core.tool_executor.get_ui", return_value=None):
            with patch("core.tool_executor.SessionLogger"):
                with patch("core.tool_executor.hook_manager", hm):
                    result = await execute_tools(state)

        scratchpad = result["scratchpad"]
        # The last message should be a ToolMessage with error
        last_msg = scratchpad[-1]
        assert isinstance(last_msg, ToolMessage)
        assert "denied by hook" in last_msg.content

    @pytest.mark.asyncio
    async def test_tool_not_found_returns_error(self):
        """When tool is not in registry, should return error."""
        state = {
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "nonexistent_tool",
                        "args": {},
                        "id": "call_1"
                    }]
                )
            ],
            "session_id": "test-session",
            "permissions": "read",
            "incognito": False,
            "yolo": True,
        }

        with patch("core.tool_executor.get_ui", return_value=None):
            with patch("core.tool_executor.SessionLogger"):
                with patch("core.tool_executor.registry") as mock_registry:
                    mock_registry.tools.get.return_value = None
                    result = await execute_tools(state)

        scratchpad = result["scratchpad"]
        last_msg = scratchpad[-1]
        assert isinstance(last_msg, ToolMessage)
        assert "not found" in last_msg.content

    @pytest.mark.asyncio
    async def test_incognito_does_not_log(self):
        """When incognito=True, events and messages should not be logged."""
        mock_logger = MagicMock()

        state = {
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "read_file",
                        "args": {"path": "test.txt"},
                        "id": "call_1"
                    }]
                )
            ],
            "session_id": "test-session",
            "permissions": "read",
            "incognito": True,
            "yolo": True,
        }

        with patch("core.tool_executor.get_ui", return_value=None):
            with patch("core.tool_executor.SessionLogger", return_value=mock_logger):
                with patch("core.tool_executor.registry") as mock_registry:
                    mock_desc = MagicMock()
                    desc_handler = MagicMock()
                    desc_handler.ainvoke = AsyncMock(return_value="result")
                    mock_desc.handler = desc_handler
                    mock_desc.requires_approval = False
                    mock_registry.tools.get.return_value = mock_desc
                    result = await execute_tools(state)

        mock_logger.log_event.assert_not_called()
        mock_logger.log_messages.assert_not_called()
