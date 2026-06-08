"""Unit tests for tools/classification.py — shell command risk classification."""

import pytest
from tools.classification import classify_shell_command, risk_level_value


class TestClassifyShellCommand:
    """Test shell command risk classification."""

    def test_classifies_rm_as_full(self):
        assert classify_shell_command("rm -rf /tmp/test") == "full"

    def test_classifies_sudo_as_full(self):
        assert classify_shell_command("sudo apt update") == "full"

    def test_classifies_ls_as_read(self):
        assert classify_shell_command("ls -la") == "read"

    def test_classifies_cat_as_read(self):
        assert classify_shell_command("cat file.txt") == "read"

    def test_classifies_grep_as_read(self):
        assert classify_shell_command("grep pattern file.txt") == "read"

    def test_classifies_cp_as_write(self):
        assert classify_shell_command("cp file1 file2") == "write"

    def test_classifies_mv_as_write(self):
        assert classify_shell_command("mv file1 file2") == "write"

    def test_classifies_git_as_write(self):
        assert classify_shell_command("git commit -m 'msg'") == "write"

    def test_classifies_unknown_as_write(self):
        """Unknown commands default to write level."""
        assert classify_shell_command("custom_command arg1") == "write"

    def test_classifies_kill_as_full(self):
        assert classify_shell_command("kill -9 1234") == "full"

    def test_classifies_chmod_as_full(self):
        assert classify_shell_command("chmod 755 file") == "full"

    def test_empty_string(self):
        assert classify_shell_command("") == "write"

    def test_whitespace_only(self):
        assert classify_shell_command("   ") == "write"


class TestRiskLevelValue:
    """Test risk level numeric conversion."""

    def test_read_level(self):
        assert risk_level_value("read") == 1

    def test_write_level(self):
        assert risk_level_value("write") == 2

    def test_full_level(self):
        assert risk_level_value("full") == 3

    def test_execute_level(self):
        assert risk_level_value("execute") == 3

    def test_unknown_level_defaults_to_write(self):
        assert risk_level_value("unknown") == 2

    def test_empty_string_defaults_to_write(self):
        assert risk_level_value("") == 2
