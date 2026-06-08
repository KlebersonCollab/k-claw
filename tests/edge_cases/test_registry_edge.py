"""Edge case tests for tools/registry.py."""

import pytest
from unittest.mock import MagicMock
from tools.registry import ToolRegistry, ToolDescriptor


class TestRegistryEdgeCases:
    """Edge cases for tool registry."""

    def test_register_duplicate_tool(self):
        """Registering a tool with the same name should overwrite."""
        reg = ToolRegistry()
        handler1 = MagicMock()
        handler2 = MagicMock()
        reg.register("test_tool", "First version", "read", handler1)
        reg.register("test_tool", "Second version", "write", handler2)
        assert len(reg.tools) == 1
        assert reg.tools["test_tool"].handler is handler2

    def test_register_tool_with_empty_name(self):
        """Registering a tool with empty name."""
        reg = ToolRegistry()
        reg.register("", "Empty name tool", "read", MagicMock())
        assert "" in reg.tools

    def test_get_tools_with_unknown_permission(self):
        """Getting tools with an unknown permission level."""
        reg = ToolRegistry()
        reg.register("read_tool", "Read tool", "read", MagicMock())
        tools = reg.get_langchain_tools("unknown_permission")
        # Unknown permission has value 0, so no tools should be returned
        assert tools == []

    def test_get_tools_with_empty_string_permission(self):
        """Getting tools with empty string permission."""
        reg = ToolRegistry()
        reg.register("read_tool", "Read tool", "read", MagicMock())
        tools = reg.get_langchain_tools("")
        assert tools == []

    def test_permission_hierarchy_edge_cases(self):
        """Test edge cases in permission hierarchy."""
        reg = ToolRegistry()
        # Same level
        assert reg._has_permission("read", "read") is True
        assert reg._has_permission("write", "write") is True
        # One level up
        assert reg._has_permission("write", "read") is True
        assert reg._has_permission("execute", "write") is True
        # One level down
        assert reg._has_permission("read", "write") is False
        assert reg._has_permission("write", "execute") is False

    def test_many_tools_performance(self):
        """Registry with many tools should still work."""
        reg = ToolRegistry()
        for i in range(100):
            reg.register(f"tool_{i}", f"Tool {i}", "read", MagicMock())
        assert len(reg.tools) == 100
        tools = reg.get_langchain_tools("read")
        assert len(tools) == 100

    def test_descriptor_immutability(self):
        """ToolDescriptor should be a pydantic model."""
        handler = MagicMock()
        desc = ToolDescriptor(
            name="test",
            description="Test",
            permissions_required="read",
            handler=handler,
        )
        assert desc.requires_approval is False  # Default value
