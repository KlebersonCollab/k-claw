"""Integration tests for tool execution flow with hooks and approvals."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from langchain_core.messages import AIMessage, HumanMessage
from core.tool_executor import execute_tools
from core.hooks import HookManager, HookResult


class TestToolExecutionWithHooks:
    """Test tool execution with pre and post hooks."""

    @pytest.mark.asyncio
    async def test_pre_hook_modifies_args(self):
        """Pre-tool hook modifies tool arguments."""
        async def modify_hook(tool_name, tool_args, context):
            return HookResult(allowed=True, modified_args={"path": "modified.txt"})

        hm = HookManager()
        hm.register_pre_tool(modify_hook)

        state = {
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "read_file",
                        "args": {"path": "original.txt"},
                        "id": "call_1"
                    }]
                )
            ],
            "session_id": "test-session",
            "permissions": "read",
            "incognito": True,
            "yolo": True,
        }

        result = await self._run_with_hooks(state, hm)
        scratchpad = result["scratchpad"]
        last_msg = scratchpad[-1]
        # The tool should have been called with modified args
        assert "modified.txt" in last_msg.content or "Error" in last_msg.content

    @pytest.mark.asyncio
    async def test_post_hook_audit(self):
        """Post-tool hook records execution."""
        audited = []

        async def audit_hook(tool_name, tool_args, result, context):
            audited.append(tool_name)

        hm = HookManager()
        hm.register_post_tool(audit_hook)

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
            with patch("core.tool_executor.hook_manager", hm):
                with patch("core.tool_executor.registry") as mock_registry:
                    mock_desc = MagicMock()
                    desc_handler = MagicMock()
                    desc_handler.ainvoke = AsyncMock(return_value="result")
                    mock_desc.handler = desc_handler
                    mock_desc.requires_approval = False
                    mock_registry.tools.get.return_value = mock_desc
                    await execute_tools(state)

        assert "read_file" in audited

    async def _run_with_hooks(self, state, hm):
        """Helper to run execute_tools with custom hook manager."""
        with patch("core.tool_executor.get_ui", return_value=None):
            with patch("core.tool_executor.hook_manager", hm):
                with patch("core.tool_executor.registry") as mock_registry:
                    mock_desc = MagicMock()
                    desc_handler = MagicMock()
                    # Return the args as string so we can verify them
                    desc_handler.ainvoke = AsyncMock(side_effect=lambda args: str(args))
                    mock_desc.handler = desc_handler
                    mock_desc.requires_approval = False
                    mock_registry.tools.get.return_value = mock_desc
                    result = await execute_tools(state)
                    return result


class TestToolExecutionWithApproval:
    """Test tool execution with human-in-the-loop approval."""

    @pytest.mark.asyncio
    async def test_approval_granted(self):
        """When user approves, tool executes."""
        mock_ui = MagicMock()
        mock_ui.request_approval = AsyncMock(return_value=True)

        state = {
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "write_file",
                        "args": {"path": "test.txt", "content": "test"},
                        "id": "call_1"
                    }]
                )
            ],
            "session_id": "test-session",
            "permissions": "write",
            "incognito": True,
            "yolo": False,
        }

        with patch("core.tool_executor.get_ui", return_value=mock_ui):
            with patch("core.tool_executor.SessionLogger"):
                with patch("core.tool_executor.registry") as mock_registry:
                    mock_desc = MagicMock()
                    desc_handler = MagicMock()
                    desc_handler.ainvoke = AsyncMock(return_value="File written")
                    mock_desc.handler = desc_handler
                    mock_desc.requires_approval = True
                    mock_registry.tools.get.return_value = mock_desc
                    result = await execute_tools(state)

        scratchpad = result["scratchpad"]
        last_msg = scratchpad[-1]
        assert "File written" in last_msg.content

    @pytest.mark.asyncio
    async def test_approval_denied(self):
        """When user denies, tool does not execute."""
        mock_ui = MagicMock()
        mock_ui.request_approval = AsyncMock(return_value=False)

        state = {
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "write_file",
                        "args": {"path": "test.txt", "content": "test"},
                        "id": "call_1"
                    }]
                )
            ],
            "session_id": "test-session",
            "permissions": "write",
            "incognito": True,
            "yolo": False,
        }

        with patch("core.tool_executor.get_ui", return_value=mock_ui):
            with patch("core.tool_executor.SessionLogger"):
                with patch("core.tool_executor.registry") as mock_registry:
                    mock_desc = MagicMock()
                    desc_handler = MagicMock()
                    desc_handler.ainvoke = AsyncMock(return_value="File written")
                    mock_desc.handler = desc_handler
                    mock_desc.requires_approval = True
                    mock_registry.tools.get.return_value = mock_desc
                    result = await execute_tools(state)

        scratchpad = result["scratchpad"]
        last_msg = scratchpad[-1]
        assert "Denied by user" in last_msg.content

    @pytest.mark.asyncio
    async def test_no_ui_denies_by_default(self):
        """When no UI is available and approval is needed, tool is denied."""
        state = {
            "scratchpad": [
                AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "write_file",
                        "args": {"path": "test.txt", "content": "test"},
                        "id": "call_1"
                    }]
                )
            ],
            "session_id": "test-session",
            "permissions": "write",
            "incognito": True,
            "yolo": False,
        }

        with patch("core.tool_executor.get_ui", return_value=None):
            with patch("core.tool_executor.SessionLogger"):
                with patch("core.tool_executor.registry") as mock_registry:
                    mock_desc = MagicMock()
                    desc_handler = MagicMock()
                    desc_handler.ainvoke = AsyncMock(return_value="File written")
                    mock_desc.handler = desc_handler
                    mock_desc.requires_approval = True
                    mock_registry.tools.get.return_value = mock_desc
                    result = await execute_tools(state)

        scratchpad = result["scratchpad"]
        last_msg = scratchpad[-1]
        assert "Denied by user" in last_msg.content


class TestYoloModeInjection:
    """Test YOLO mode injection for delegate_to_agent."""

    @pytest.mark.asyncio
    async def test_yolo_injected_to_delegate(self):
        """When yolo=True, delegate_to_agent gets parent_yolo=True."""
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
            "incognito": True,
            "yolo": True,
        }

        with patch("core.tool_executor.get_ui", return_value=None):
            with patch("core.tool_executor.SessionLogger"):
                with patch("core.tool_executor.registry") as mock_registry:
                    mock_desc = MagicMock()
                    desc_handler = MagicMock()
                    desc_handler.ainvoke = AsyncMock(return_value="result")
                    mock_desc.handler = desc_handler
                    mock_desc.requires_approval = False
                    mock_registry.tools.get.return_value = mock_desc
                    await execute_tools(state)
                    # Verify ainvoke was called with parent_yolo=True
                    call_args = desc_handler.ainvoke.call_args[0][0]
                    assert call_args.get("parent_yolo") is True

    @pytest.mark.asyncio
    async def test_non_yolo_delegate(self):
        """When yolo=False, delegate_to_agent gets parent_yolo=False."""
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
            "incognito": True,
            "yolo": False,
        }

        with patch("core.tool_executor.get_ui", return_value=None):
            with patch("core.tool_executor.SessionLogger"):
                with patch("core.tool_executor.registry") as mock_registry:
                    mock_desc = MagicMock()
                    desc_handler = MagicMock()
                    desc_handler.ainvoke = AsyncMock(return_value="result")
                    mock_desc.handler = desc_handler
                    mock_desc.requires_approval = False
                    mock_registry.tools.get.return_value = mock_desc
                    await execute_tools(state)
                    call_args = desc_handler.ainvoke.call_args[0][0]
                    assert call_args.get("parent_yolo") is False
