"""Unit tests for tools/shell_tools.py — shell execution tool."""

import pytest
from tools import run_shell


class TestRunShell:
    """Test run_shell tool."""

    def test_executes_simple_command(self):
        result = run_shell.invoke({"command": "echo hello"})
        assert "hello" in result

    def test_captures_stdout(self):
        result = run_shell.invoke({"command": "echo 'test output'"})
        assert "STDOUT" in result
        assert "test output" in result

    def test_captures_stderr(self):
        result = run_shell.invoke({"command": "ls /nonexistent_path_xyz_123"})
        assert "STDERR" in result

    def test_handles_timeout(self):
        """Commands that timeout should return error."""
        import sys
        cmd = "powershell -Command Start-Sleep 60" if sys.platform == "win32" else "sleep 60"
        result = run_shell.invoke({"command": cmd})
        assert "Error" in result or "timeout" in result.lower()

    def test_invalid_command(self):
        result = run_shell.invoke({"command": "nonexistent_command_xyz_123"})
        # Should capture error gracefully
        assert result  # Should return something, not raise
