"""Unit tests for core/utils.py — path filtering, security, formatting, token control."""

import os
import time
import pytest
from langchain_core.messages import HumanMessage, AIMessage
from core.utils import (
    PathFilter,
    redact_sensitive_info,
    escape_rich,
    cap_tool_output,
    estimate_tokens,
    recursive_load_context,
    _CONTEXT_CACHE,
)


# ── PathFilter Tests ───────────────────────────────────────────────────────────

class TestPathFilterBasics:
    """Test basic PathFilter initialization and pattern loading."""

    def test_default_ignore_patterns(self, temp_dir):
        pf = PathFilter(temp_dir)
        assert ".git" in pf.ignore_patterns
        assert ".venv" in pf.ignore_patterns
        assert "__pycache__" in pf.ignore_patterns
        assert "node_modules" in pf.ignore_patterns

    def test_root_path_is_absolute(self, temp_dir):
        pf = PathFilter(temp_dir)
        assert os.path.isabs(pf.root_path)


class TestPathFilterIsIgnored:
    """Test the is_ignored method."""

    def test_dotgit_ignored(self, temp_project_dir):
        pf = PathFilter(temp_project_dir)
        assert pf.is_ignored(".git") is True
        assert pf.is_ignored(".git/config") is True

    def test_dotvenv_ignored(self, temp_project_dir):
        pf = PathFilter(temp_project_dir)
        assert pf.is_ignored(".venv") is True
        assert pf.is_ignored(".venv/lib") is True

    def test_pycache_ignored(self, temp_project_dir):
        pf = PathFilter(temp_project_dir)
        assert pf.is_ignored("__pycache__") is True
        assert pf.is_ignored("__pycache__/module.cpython-313.pyc") is True

    def test_allowed_files(self, temp_project_dir):
        pf = PathFilter(temp_project_dir)
        assert pf.is_ignored("main.py") is False
        assert pf.is_ignored("README.md") is False
        assert pf.is_ignored("src/app.py") is False

    def test_current_dir_not_ignored(self, temp_project_dir):
        pf = PathFilter(temp_project_dir)
        assert pf.is_ignored(".") is False

    def test_absolute_path_ignored(self, temp_project_dir):
        pf = PathFilter(temp_project_dir)
        git_path = os.path.join(temp_project_dir, ".git")
        assert pf.is_ignored(git_path) is True

    def test_absolute_path_allowed(self, temp_project_dir):
        pf = PathFilter(temp_project_dir)
        main_path = os.path.join(temp_project_dir, "main.py")
        assert pf.is_ignored(main_path) is False


class TestPathFilterGitignore:
    """Test .gitignore loading."""

    def test_loads_gitignore_patterns(self, temp_project_dir):
        gitignore_path = os.path.join(temp_project_dir, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("*.log\n")
            f.write("# comment\n")
            f.write("dist/\n")
            f.write("  \n")  # blank line

        pf = PathFilter(temp_project_dir)
        assert pf.is_ignored("app.log") is True
        assert pf.is_ignored("dist") is True
        assert pf.is_ignored("dist/main.js") is True
        assert pf.is_ignored("main.py") is False

    def test_no_gitignore_file(self, temp_dir):
        pf = PathFilter(temp_dir)
        # Should still work with default patterns
        assert pf.is_ignored(".git") is True


# ── Redaction Tests ────────────────────────────────────────────────────────────

class TestRedactSensitiveInfo:
    """Test sensitive info redaction."""

    def test_redacts_openai_key(self):
        text = "My key is sk-" + "abcdefghijklmnopqrstuvwxyz1234567890AB"
        result = redact_sensitive_info(text)
        assert "[REDACTED]" in result
        assert "sk-abc" not in result

    def test_redacts_google_key(self):
        text = "My key is AIza" + "SyAbCdEfGhIjKlMnOpQrStUvWxYz123456789"
        result = redact_sensitive_info(text)
        assert "[REDACTED]" in result

    def test_redacts_huggingface_key(self):
        text = "hf_" + "a" * 34
        result = redact_sensitive_info(text)
        assert "[REDACTED]" in result

    def test_redacts_github_token(self):
        text = "Token: ghp_" + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop"
        result = redact_sensitive_info(text)
        assert "[REDACTED]" in result

    def test_redacts_aws_key(self):
        text = "AWS key: AKIA" + "IOSFODNN7EXAMPLE"
        result = redact_sensitive_info(text)
        assert "[REDACTED]" in result

    def test_passes_safe_text(self):
        text = "Hello world, this is a normal message"
        result = redact_sensitive_info(text)
        assert result == text

    def test_empty_string(self):
        assert redact_sensitive_info("") == ""

    def test_multiple_secrets(self):
        text = "OpenAI: sk-" + "abcdefghijklmnopqrstuvwxyz1234567890AB and Google: AIza" + "SyAbCdEfGhIjKlMnOpQrStUvWxYz123456789"
        result = redact_sensitive_info(text)
        assert result.count("[REDACTED]") == 2


# ── Rich Escaping Tests ───────────────────────────────────────────────────────

class TestEscapeRich:
    """Test Rich markup escaping."""

    def test_escapes_brackets(self):
        assert escape_rich("[bold]") == "[[bold]]"

    def test_safe_text_unchanged(self):
        assert escape_rich("Hello world") == "Hello world"

    def test_empty_string(self):
        assert escape_rich("") == ""

    def test_nested_brackets(self):
        assert escape_rich("[a[b]]") == "[[a[[b]]]]"


# ── Token & Output Control Tests ───────────────────────────────────────────────

class TestCapToolOutput:
    """Test output capping."""

    def test_truncates_long_output(self):
        huge = "A" * 5000
        result = cap_tool_output(huge, max_chars=1000)
        assert "TRUNCATED" in result
        assert len(result) < 1500  # 1000 + TRUNCATED message

    def test_passes_short_output(self):
        short = "Hello world"
        result = cap_tool_output(short, max_chars=1000)
        assert result == short

    def test_empty_string(self):
        assert cap_tool_output("") == ""

    def test_custom_max_chars(self):
        content = "A" * 200
        result = cap_tool_output(content, max_chars=50)
        assert "TRUNCATED" in result


class TestEstimateTokens:
    """Test token estimation."""

    def test_basic_estimation(self):
        msgs = [HumanMessage(content="Hello world")]
        tokens = estimate_tokens(msgs)
        assert tokens > 0

    def test_multiple_messages(self):
        msgs = [
            HumanMessage(content="Hello world"),
            AIMessage(content="I am an AI assistant here to help."),
        ]
        tokens = estimate_tokens(msgs)
        assert tokens > 5 and tokens < 20

    def test_empty_list(self):
        tokens = estimate_tokens([])
        assert tokens == 0


# ── Recursive Context Loading Tests ───────────────────────────────────────────

class TestRecursiveLoadContext:
    """Test recursive context file loading."""

    def test_loads_agents_md(self, temp_project_dir):
        os.chdir(temp_project_dir)
        result = recursive_load_context(".")
        assert "Test Agent" in result

    def test_caching(self, temp_project_dir):
        os.chdir(temp_project_dir)
        result1 = recursive_load_context(".")
        result2 = recursive_load_context(".")
        assert result1 == result2

    def test_cache_expiry(self, temp_project_dir):
        os.chdir(temp_project_dir)
        recursive_load_context(".")
        # Force cache expiry
        _CONTEXT_CACHE["timestamp"] = 0
        result = recursive_load_context(".")
        assert result is not None

    def test_no_context_files(self, temp_dir):
        os.chdir(temp_dir)
        result = recursive_load_context(".")
        assert result == ""
