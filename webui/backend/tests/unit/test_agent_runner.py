"""Unit tests for agent runner."""

import pytest
import asyncio
from pathlib import Path

from agent_runner import (
    register_log_callback,
    unregister_log_callback,
    emit_log,
    run_mission,
    get_historical_logs,
    _active_connections,
)
from workspace_manager import WORKSPACES_DIR, create_workspace


class TestLogCallbacks:
    """Tests for log callback registration."""

    def test_register_callback(self):
        """Test registering a log callback."""
        logs = []

        async def callback(log_entry):
            logs.append(log_entry)

        register_log_callback("test-ws", callback)
        assert "test-ws" in _active_connections
        assert callback in _active_connections["test-ws"]

        # Cleanup
        unregister_log_callback("test-ws", callback)

    def test_unregister_callback(self):
        """Test unregistering a log callback."""
        logs = []

        async def callback(log_entry):
            logs.append(log_entry)

        register_log_callback("test-ws", callback)
        unregister_log_callback("test-ws", callback)
        assert "test-ws" not in _active_connections or callback not in _active_connections.get("test-ws", [])

    def test_multiple_callbacks(self):
        """Test registering multiple callbacks."""
        logs1 = []
        logs2 = []

        async def callback1(log_entry):
            logs1.append(log_entry)

        async def callback2(log_entry):
            logs2.append(log_entry)

        register_log_callback("test-ws", callback1)
        register_log_callback("test-ws", callback2)
        assert len(_active_connections["test-ws"]) == 2

        # Cleanup
        unregister_log_callback("test-ws", callback1)
        unregister_log_callback("test-ws", callback2)


class TestEmitLog:
    """Tests for emit_log function."""

    @pytest.mark.asyncio
    async def test_emit_to_registered_callback(self):
        """Test emitting log to registered callback."""
        received = []

        async def callback(log_entry):
            received.append(log_entry)

        register_log_callback("emit-test", callback)
        await emit_log("emit-test", "INFO", "Test message", "test-source")

        assert len(received) == 1
        assert received[0]["level"] == "INFO"
        assert received[0]["message"] == "Test message"
        assert received[0]["source"] == "test-source"
        assert "timestamp" in received[0]

        # Cleanup
        unregister_log_callback("emit-test", callback)

    @pytest.mark.asyncio
    async def test_emit_to_multiple_callbacks(self):
        """Test emitting log to multiple callbacks."""
        received1 = []
        received2 = []

        async def cb1(log_entry):
            received1.append(log_entry)

        async def cb2(log_entry):
            received2.append(log_entry)

        register_log_callback("multi-test", cb1)
        register_log_callback("multi-test", cb2)
        await emit_log("multi-test", "WARNING", "Warning message")

        assert len(received1) == 1
        assert len(received2) == 1

        # Cleanup
        unregister_log_callback("multi-test", cb1)
        unregister_log_callback("multi-test", cb2)

    @pytest.mark.asyncio
    async def test_emit_no_callback_silently_passes(self):
        """Test emitting log when no callback is registered."""
        # Should not raise
        await emit_log("no-callback-ws", "INFO", "Test message")

    @pytest.mark.asyncio
    async def test_emit_different_log_levels(self):
        """Test emitting different log levels."""
        received = []

        async def callback(log_entry):
            received.append(log_entry)

        register_log_callback("levels-test", callback)

        for level in ["INFO", "WARNING", "ERROR", "DEBUG"]:
            await emit_log("levels-test", level, f"{level} message")

        assert len(received) == 4
        assert [r["level"] for r in received] == ["INFO", "WARNING", "ERROR", "DEBUG"]

        # Cleanup
        unregister_log_callback("levels-test", callback)


class TestRunMission:
    """Tests for run_mission function."""

    @pytest.mark.asyncio
    async def test_run_mission_in_workspace(self, clean_workspaces):
        """Test running a mission in a workspace."""
        from models import WorkspaceCreate
        from workspace_manager import create_workspace

        # Create a real workspace via the manager
        data = WorkspaceCreate(name="mission-test")
        create_workspace(data)

        result = await run_mission("mission-test", "Create a test file", "coder")
        assert "completed" in result.lower() or "Mission completed" in result

        # Check that output file was created
        output_files = list((WORKSPACES_DIR / "mission-test" / "src").glob("output_*.md"))
        assert len(output_files) == 1

    @pytest.mark.asyncio
    async def test_run_mission_nonexistent_workspace(self):
        """Test running mission in nonexistent workspace raises error."""
        with pytest.raises(FileNotFoundError):
            await run_mission("nonexistent-ws", "Test mission")

    @pytest.mark.asyncio
    async def test_run_mission_emits_logs(self, clean_workspaces):
        """Test that running a mission emits log entries."""
        from models import WorkspaceCreate
        from workspace_manager import create_workspace

        # Create a real workspace
        data = WorkspaceCreate(name="logs-test")
        create_workspace(data)

        logs = []

        async def callback(log_entry):
            logs.append(log_entry)

        register_log_callback("logs-test", callback)

        try:
            await run_mission("logs-test", "Test mission")
            assert len(logs) > 0
            # Should have orchestrator logs
            sources = [log["source"] for log in logs]
            assert "orchestrator" in sources
        finally:
            unregister_log_callback("logs-test", callback)


class TestGetHistoricalLogs:
    """Tests for get_historical_logs function."""

    def test_get_historical_logs(self):
        """Test getting historical logs."""
        # This function currently returns empty list
        result = get_historical_logs("any-ws")
        assert isinstance(result, list)

    def test_get_historical_logs_with_limit(self):
        """Test getting historical logs with limit."""
        result = get_historical_logs("any-ws", limit=10)
        assert isinstance(result, list)
