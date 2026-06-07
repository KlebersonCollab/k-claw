"""Utility functions for the Agent Harness.

Consolidates path filtering, security redaction, text formatting, and token control.
"""

import os
import re
import time
import fnmatch
from typing import List


# ── Context Loading ───────────────────────────────────────────────────────────

_CONTEXT_CACHE: dict = {"data": None, "timestamp": 0}

# Target context files to search for
CONTEXT_FILES = ["AGENTS.md", "CLAUDE.md", "GEMINI.md"]


def recursive_load_context(start_path: str = ".") -> str:
    """Walk up from start_path to root, collecting context files with a simple 60s cache.

    Args:
        start_path: The starting directory path.

    Returns:
        Concatenated content of all found context files.
    """
    now = time.time()
    if _CONTEXT_CACHE["data"] is not None and (now - _CONTEXT_CACHE["timestamp"]) < 60:
        return _CONTEXT_CACHE["data"]

    current_path = os.path.abspath(start_path)
    context_content = []
    visited_files = set()

    while True:
        for target in CONTEXT_FILES:
            file_path = os.path.join(current_path, target)
            if os.path.exists(file_path) and file_path not in visited_files:
                with open(file_path, "r", encoding="utf-8") as f:
                    context_content.append(f"--- Context from {file_path} ---\n{f.read()}\n")
                visited_files.add(file_path)

        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            break
        current_path = parent_path

    result = "\n".join(reversed(context_content))
    _CONTEXT_CACHE["data"] = result
    _CONTEXT_CACHE["timestamp"] = now
    return result


# ── Path Filtering ────────────────────────────────────────────────────────────

class PathFilter:
    """Filters paths based on ignore patterns and .gitignore rules."""

    def __init__(self, root_path: str = "."):
        self.root_path = os.path.abspath(root_path)
        # Patterns that match a whole directory name or file name
        self.ignore_patterns = [
            ".git", ".venv", "__pycache__", "node_modules",
            ".api.pid", "api.log", "harness.db", "harness.db-shm", "harness.db-wal", ".agents"
        ]
        self._load_gitignore()

    def _load_gitignore(self) -> None:
        """Load ignore patterns from .gitignore file if it exists."""
        gitignore_path = os.path.join(self.root_path, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.ignore_patterns.append(line.rstrip("/"))

    def is_ignored(self, path: str) -> bool:
        """Check if a path should be ignored based on patterns.

        Args:
            path: The path to check.

        Returns:
            True if the path should be ignored.
        """
        full_path = os.path.abspath(path)
        rel_path = os.path.relpath(full_path, self.root_path)

        if rel_path == ".":
            return False

        # Check every part of the path
        parts = rel_path.split(os.sep)
        for part in parts:
            if part in self.ignore_patterns:
                return True
            for pattern in self.ignore_patterns:
                if fnmatch.fnmatch(part, pattern):
                    return True
        return False


# Global singleton instance
path_filter = PathFilter()


# ── Security ──────────────────────────────────────────────────────────────────

def redact_sensitive_info(text: str) -> str:
    """Mask potential API keys and secrets in the text.

    Args:
        text: The text to redact.

    Returns:
        Text with sensitive patterns replaced by [REDACTED].
    """
    patterns = [
        r"(sk-[a-zA-Z0-9]{32,})",      # OpenAI/Anthropic
        r"(AIza[0-9A-Za-z-_]{35})",     # Google
        r"(hf_[a-zA-Z0-9]{34})",        # HuggingFace
        r"(gh[oprs]_[a-zA-Z0-9]{36,})", # GitHub
        r"(AKIA[0-9A-Z]{16})",          # AWS Access Key
        r"([a-f0-9]{32})",              # Generic hex (MD5/etc)
    ]
    redacted = text
    for pattern in patterns:
        redacted = re.sub(pattern, "[REDACTED]", redacted)
    return redacted


# ── Formatting ────────────────────────────────────────────────────────────────

def escape_rich(text: str) -> str:
    """Escape Rich markup characters to prevent accidental formatting.

    Args:
        text: The text to escape.

    Returns:
        Text with Rich markup characters escaped.
    """
    return str(text).replace("[", "[[").replace("]", "]]")


# ── Token & Output Control ────────────────────────────────────────────────────

def cap_tool_output(content: str, max_chars: int = 3000) -> str:
    """Truncate tool output if it exceeds max_chars to save context tokens.

    Args:
        content: The content to potentially truncate.
        max_chars: Maximum allowed characters.

    Returns:
        Original content if within limit, truncated content otherwise.
    """
    if len(content) <= max_chars:
        return content
    return (
        f"{content[:max_chars]}\n\n"
        f"--- [TRUNCATED: Result too large ({len(content)} chars). "
        f"Use paginated reading or more specific queries to see the rest.] ---"
    )


def estimate_tokens(messages: List) -> int:
    """Roughly estimate tokens based on character count (1 token ~= 4 chars).

    Args:
        messages: List of message objects with content attribute.

    Returns:
        Estimated token count.
    """
    if not messages:
        return 0
    total_chars = 0
    for msg in messages:
        if hasattr(msg, 'content'):
            total_chars += len(str(msg.content))
    return int(total_chars / 4)
