"""Unit tests for core/hooks.py — lifecycle hooks."""

import pytest
from core.hooks import HookManager, HookResult


class TestHookResult:
    """Test HookResult dataclass."""

    def test_default_values(self):
        result = HookResult()
        assert result.allowed is True
        assert result.modified_args == {}

    def test_denied_result(self):
        result = HookResult(allowed=False)
        assert result.allowed is False

    def test_modified_args(self):
        result = HookResult(modified_args={"key": "value"})
        assert result.modified_args == {"key": "value"}

    def test_denied_with_modified_args(self):
        result = HookResult(allowed=False, modified_args={"key": "value"})
        assert result.allowed is False
        assert result.modified_args == {"key": "value"}


class TestHookManager:
    """Test HookManager registration and execution."""

    def test_initially_empty(self, hook_manager):
        assert len(hook_manager.pre_tool_hooks) == 0
        assert len(hook_manager.post_tool_hooks) == 0

    def test_register_pre_tool_hook(self, hook_manager, allowing_hook):
        hook_manager.register_pre_tool(allowing_hook)
        assert len(hook_manager.pre_tool_hooks) == 1

    def test_register_post_tool_hook(self, hook_manager, audit_log_hook):
        hook_manager.register_post_tool(audit_log_hook)
        assert len(hook_manager.post_tool_hooks) == 1

    def test_register_multiple_pre_hooks(self, hook_manager):
        async def hook1(tool_name, tool_args, context):
            return HookResult(allowed=True)

        async def hook2(tool_name, tool_args, context):
            return HookResult(allowed=True)

        hook_manager.register_pre_tool(hook1)
        hook_manager.register_pre_tool(hook2)
        assert len(hook_manager.pre_tool_hooks) == 2

    @pytest.mark.asyncio
    async def test_run_pre_tool_allows(self, hook_manager, allowing_hook):
        hook_manager.register_pre_tool(allowing_hook)
        result = await hook_manager.run_pre_tool("test_tool", {}, {})
        assert result.allowed is True

    @pytest.mark.asyncio
    async def test_run_pre_tool_denies(self, hook_manager, blocking_hook):
        hook_manager.register_pre_tool(blocking_hook)
        result = await hook_manager.run_pre_tool("test_tool", {}, {})
        assert result.allowed is False

    @pytest.mark.asyncio
    async def test_run_pre_tool_modifies_args(self, hook_manager, modifying_hook):
        hook_manager.register_pre_tool(modifying_hook)
        result = await hook_manager.run_pre_tool("test_tool", {"original": True}, {})
        assert result.allowed is True
        assert result.modified_args == {"modified": True}

    @pytest.mark.asyncio
    async def test_run_pre_tool_no_hooks(self, hook_manager):
        result = await hook_manager.run_pre_tool("test_tool", {}, {})
        assert result.allowed is True
        assert result.modified_args == {}

    @pytest.mark.asyncio
    async def test_run_pre_tool_first_denial_wins(self, hook_manager):
        """If first hook denies, subsequent hooks should not override."""
        async def deny_hook(tool_name, tool_args, context):
            return HookResult(allowed=False)

        async def allow_hook(tool_name, tool_args, context):
            return HookResult(allowed=True)

        hook_manager.register_pre_tool(deny_hook)
        hook_manager.register_pre_tool(allow_hook)
        result = await hook_manager.run_pre_tool("test_tool", {}, {})
        assert result.allowed is False

    @pytest.mark.asyncio
    async def test_run_post_tool(self, hook_manager, audit_log_hook):
        hook_manager.register_post_tool(audit_log_hook)
        await hook_manager.run_post_tool("test_tool", {"arg": "val"}, "result", {})
        assert len(audit_log_hook.calls) == 1
        assert audit_log_hook.calls[0]["tool"] == "test_tool"

    @pytest.mark.asyncio
    async def test_run_post_tool_multiple_hooks(self, hook_manager):
        calls1 = []
        calls2 = []

        async def hook1(tool_name, tool_args, result, context):
            calls1.append(tool_name)

        async def hook2(tool_name, tool_args, result, context):
            calls2.append(tool_name)

        hook_manager.register_post_tool(hook1)
        hook_manager.register_post_tool(hook2)
        await hook_manager.run_post_tool("tool1", {}, "res", {})
        assert "tool1" in calls1
        assert "tool1" in calls2

    @pytest.mark.asyncio
    async def test_run_post_tool_no_hooks(self, hook_manager):
        """Should not raise when no hooks are registered."""
        await hook_manager.run_post_tool("test_tool", {}, "result", {})
