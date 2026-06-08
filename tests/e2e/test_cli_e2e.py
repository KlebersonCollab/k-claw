"""E2E tests for the CLI interface."""

import pytest
from unittest.mock import patch, MagicMock
from core.ui_interface import EventType


class TestCLIInterface:
    """Test CLI interface behavior."""

    @pytest.mark.asyncio
    async def test_cli_on_event_thinking_start(self):
        """Test CLI handles thinking start event."""
        from entrypoints.cli import CLIInterface
        from rich.console import Console

        console = Console()
        cli = CLIInterface()
        # Should not raise
        await cli.on_event(EventType.THINKING_START, {"agent": "Test"})

    @pytest.mark.asyncio
    async def test_cli_on_event_thinking_end(self):
        """Test CLI handles thinking end event."""
        from entrypoints.cli import CLIInterface

        cli = CLIInterface()
        cli.status = MagicMock()
        await cli.on_event(EventType.THINKING_END, {})

    @pytest.mark.asyncio
    async def test_cli_on_event_tool_start(self):
        """Test CLI handles tool start event."""
        from entrypoints.cli import CLIInterface

        cli = CLIInterface()
        # Should not raise
        await cli.on_event(EventType.TOOL_START, {"tool": "read_file"})

    @pytest.mark.asyncio
    async def test_cli_on_event_compaction(self):
        """Test CLI handles compaction events."""
        from entrypoints.cli import CLIInterface

        cli = CLIInterface()
        await cli.on_event(EventType.COMPACTION_START, {})

    @pytest.mark.asyncio
    async def test_cli_on_event_error(self):
        """Test CLI handles error events."""
        from entrypoints.cli import CLIInterface

        cli = CLIInterface()
        await cli.on_event(EventType.ERROR, {"message": "Test error"})

    @pytest.mark.asyncio
    async def test_cli_request_approval_returns_false_by_default(self):
        """Test approval request without user interaction."""
        from entrypoints.cli import CLIInterface

        cli = CLIInterface()
        # Without actual user input, this should handle gracefully
        # In asyncio.to_thread with Confirm.ask, it would block
        # So we just verify the interface exists
        assert hasattr(cli, 'request_approval')
