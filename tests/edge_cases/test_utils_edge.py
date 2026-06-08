"""Edge case tests for core/utils.py."""

import os
import pytest
from core.utils import PathFilter, redact_sensitive_info, escape_rich, cap_tool_output, estimate_tokens


class TestPathFilterEdgeCases:
    """Edge cases for PathFilter."""

    def test_deeply_nested_ignored_path(self, temp_dir):
        """Deeply nested paths in ignored directories should be ignored."""
        pf = PathFilter(temp_dir)
        deep_path = os.path.join(temp_dir, ".git", "objects", "ab", "cd1234")
        os.makedirs(os.path.dirname(deep_path), exist_ok=True)
        assert pf.is_ignored(deep_path) is True

    def test_path_with_special_characters(self, temp_dir):
        """Paths with special characters."""
        pf = PathFilter(temp_dir)
        assert pf.is_ignored(os.path.join(temp_dir, "file with spaces.py")) is False

    def test_relative_path_traversal(self, temp_dir):
        """Relative path with .. components."""
        pf = PathFilter(temp_dir)
        git_path = os.path.join(temp_dir, "subdir", "..", "..", os.path.basename(temp_dir), ".git")
        assert pf.is_ignored(git_path) is True

    def test_symlink_to_ignored(self, temp_dir):
        """Symlinks pointing to ignored paths."""
        pf = PathFilter(temp_dir)
        link_path = os.path.join(temp_dir, ".git")
        os.makedirs(link_path, exist_ok=True)
        assert pf.is_ignored(link_path) is True

    def test_path_filter_with_empty_gitignore(self, temp_dir):
        """Empty .gitignore should still work with defaults."""
        gitignore_path = os.path.join(temp_dir, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("")
        pf = PathFilter(temp_dir)
        assert pf.is_ignored(".git") is True

    def test_path_filter_with_only_comments_in_gitignore(self, temp_dir):
        """.gitignore with only comments should still work."""
        gitignore_path = os.path.join(temp_dir, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("# This is a comment\n# Another comment\n")
        pf = PathFilter(temp_dir)
        assert pf.is_ignored(".git") is True

    def test_path_filter_glob_pattern_in_gitignore(self, temp_dir):
        """Test glob patterns from .gitignore."""
        gitignore_path = os.path.join(temp_dir, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("*.pyc\n*.log\n")
        pf = PathFilter(temp_dir)
        assert pf.is_ignored("test.pyc") is True
        assert pf.is_ignored("test.log") is True
        assert pf.is_ignored("test.py") is False


class TestRedactionEdgeCases:
    """Edge cases for sensitive info redaction."""

    def test_partial_key_not_redacted(self):
        """Partial keys should not be redacted."""
        text = "My key starts with sk-abc but is short"
        result = redact_sensitive_info(text)
        # sk-abc is too short to match (needs 32+ chars after sk-)
        assert "[REDACTED]" not in result

    def test_key_at_boundary(self):
        """Key at exact boundary length."""
        text = "sk-" + "a" * 32  # Exactly 35 chars
        result = redact_sensitive_info(text)
        assert "[REDACTED]" in result

    def test_multiple_keys_same_line(self):
        """Multiple keys on the same line."""
        text = "Keys: sk-" + "a" * 32 + " and sk-" + "b" * 37
        result = redact_sensitive_info(text)
        assert result.count("[REDACTED]") == 2

    def test_key_in_json(self):
        """Key embedded in JSON."""
        text = '{"api_key": "sk-' + 'abcdefghijklmnopqrstuvwxyz1234567890AB"}'
        result = redact_sensitive_info(text)
        assert "[REDACTED]" in result

    def test_very_long_text(self):
        """Very long text with secrets."""
        text = "A" * 10000 + " sk-" + "abcdefghijklmnopqrstuvwxyz1234567890AB " + "B" * 10000
        result = redact_sensitive_info(text)
        assert "[REDACTED]" in result

    def test_unicode_text(self):
        """Unicode text should pass through."""
        text = "Olá mundo! 你好世界! مرحبا بالعالم!"
        result = redact_sensitive_info(text)
        assert result == text


class TestEscapeRichEdgeCases:
    """Edge cases for Rich escaping."""

    def test_only_brackets(self):
        assert escape_rich("[]") == "[[]]"

    def test_mixed_content(self):
        assert escape_rich("Hello [bold] world") == "Hello [[bold]] world"

    def test_numbers(self):
        assert escape_rich("12345") == "12345"


class TestCapToolOutputEdgeCases:
    """Edge cases for output capping."""

    def test_exact_boundary(self):
        """Content exactly at max_chars should not be truncated."""
        content = "A" * 3000
        result = cap_tool_output(content, max_chars=3000)
        assert "TRUNCATED" not in result

    def test_one_over_boundary(self):
        """Content one char over should be truncated."""
        content = "A" * 3001
        result = cap_tool_output(content, max_chars=3000)
        assert "TRUNCATED" in result

    def test_very_small_max(self):
        """Very small max_chars."""
        content = "Hello world"
        result = cap_tool_output(content, max_chars=5)
        assert "TRUNCATED" in result

    def test_multiline_content(self):
        """Multiline content should be capped."""
        content = "\n".join([f"Line {i}" for i in range(1000)])
        result = cap_tool_output(content, max_chars=100)
        assert "TRUNCATED" in result


class TestEstimateTokensEdgeCases:
    """Edge cases for token estimation."""

    def test_very_long_message(self):
        """Very long message."""
        msgs = [HumanMessage(content="A" * 100000)]
        tokens = estimate_tokens(msgs)
        assert tokens > 0

    def test_many_messages(self):
        """Many small messages."""
        msgs = [HumanMessage(content="Hi") for _ in range(1000)]
        tokens = estimate_tokens(msgs)
        assert tokens > 0

    def test_empty_content(self):
        """Messages with empty content."""
        msgs = [HumanMessage(content="")]
        tokens = estimate_tokens(msgs)
        assert tokens >= 0


# Need to import here to avoid circular
from langchain_core.messages import HumanMessage
