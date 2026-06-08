"""Unit tests for tools/registry.py — tool registration and permission checking."""

import pytest
from unittest.mock import MagicMock
from tools.registry import ToolRegistry, ToolDescriptor, registry, set_harness_refs


class TestToolDescriptor:
    """Test ToolDescriptor model."""

    def test_create_descriptor(self):
        handler = MagicMock()
        desc = ToolDescriptor(
            name="test_tool",
            description="A test tool",
            permissions_required="read",
            handler=handler,
        )
        assert desc.name == "test_tool"
        assert desc.permissions_required == "read"
        assert desc.requires_approval is False

    def test_descriptor_with_approval(self):
        handler = MagicMock()
        desc = ToolDescriptor(
            name="dangerous_tool",
            description="A dangerous tool",
            permissions_required="execute",
            handler=handler,
            requires_approval=True,
        )
        assert desc.requires_approval is True


class TestToolRegistry:
    """Test ToolRegistry operations."""

    def test_register_tool(self):
        reg = ToolRegistry()
        handler = MagicMock()
        reg.register("test_tool", "A test tool", "read", handler)
        assert "test_tool" in reg.tools
        assert reg.tools["test_tool"].name == "test_tool"

    def test_register_multiple_tools(self):
        reg = ToolRegistry()
        reg.register("tool1", "Tool 1", "read", MagicMock())
        reg.register("tool2", "Tool 2", "write", MagicMock())
        assert len(reg.tools) == 2

    def test_get_langchain_tools_read_permission(self):
        """Read permission should return tools requiring read."""
        reg = ToolRegistry()
        handler1 = MagicMock()
        handler2 = MagicMock()
        reg.register("read_tool", "Read tool", "read", handler1)
        reg.register("write_tool", "Write tool", "write", handler2)
        tools = reg.get_langchain_tools("read")
        assert handler1 in tools
        assert handler2 not in tools

    def test_get_langchain_tools_write_permission(self):
        """Write permission should return read and write tools."""
        reg = ToolRegistry()
        handler1 = MagicMock()
        handler2 = MagicMock()
        handler3 = MagicMock()
        reg.register("read_tool", "Read tool", "read", handler1)
        reg.register("write_tool", "Write tool", "write", handler2)
        reg.register("exec_tool", "Exec tool", "execute", handler3)
        tools = reg.get_langchain_tools("write")
        assert handler1 in tools
        assert handler2 in tools
        assert handler3 not in tools

    def test_get_langchain_tools_execute_permission(self):
        """Execute permission should return all tools."""
        reg = ToolRegistry()
        handler1 = MagicMock()
        handler2 = MagicMock()
        handler3 = MagicMock()
        reg.register("read_tool", "Read tool", "read", handler1)
        reg.register("write_tool", "Write tool", "write", handler2)
        reg.register("exec_tool", "Exec tool", "execute", handler3)
        tools = reg.get_langchain_tools("execute")
        assert handler1 in tools
        assert handler2 in tools
        assert handler3 in tools

    def test_get_langchain_tools_empty_registry(self):
        reg = ToolRegistry()
        tools = reg.get_langchain_tools("read")
        assert tools == []

    def test_has_permission_hierarchy(self):
        """Test the permission hierarchy logic."""
        reg = ToolRegistry()
        assert reg._has_permission("read", "read") is True
        assert reg._has_permission("write", "read") is True
        assert reg._has_permission("execute", "read") is True
        assert reg._has_permission("write", "write") is True
        assert reg._has_permission("execute", "write") is True
        assert reg._has_permission("execute", "execute") is True
        assert reg._has_permission("read", "write") is False
        assert reg._has_permission("read", "execute") is False
        assert reg._has_permission("write", "execute") is False

    def test_has_permission_unknown_level(self):
        """Unknown permission levels should default to 0."""
        reg = ToolRegistry()
        assert reg._has_permission("unknown", "read") is False
        assert reg._has_permission("read", "unknown") is True  # 1 >= 0


class TestGlobalRegistry:
    """Test the global registry singleton."""

    def test_registry_exists(self):
        assert registry is not None
        assert isinstance(registry, ToolRegistry)

    def test_set_harness_refs(self):
        harness = MagicMock()
        set_harness_refs(harness)
        from tools.registry import _HARNESS_REF
        assert _HARNESS_REF is harness
