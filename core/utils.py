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


def load_global_rules(root_path: str = ".") -> str:
    """Load all rules from the .agents/rules directory.

    Args:
        root_path: The root directory of the project.

    Returns:
        Concatenated content of all rule files found.
    """
    rules_path = os.path.join(os.path.abspath(root_path), ".agents", "rules")
    if not os.path.exists(rules_path):
        return ""
    
    rules_content = []
    try:
        # Sort files to ensure consistent prompt ordering
        for entry in sorted(os.listdir(rules_path)):
            if entry.endswith(".md"):
                file_path = os.path.join(rules_path, entry)
                with open(file_path, "r", encoding="utf-8") as f:
                    rules_content.append(f"### RULE: {entry[:-3].upper()}\n{f.read()}")
    except Exception as e:
        return f"[Warning] Could not load global rules: {e}"
    
    return "\n\n".join(rules_content)


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
        # Patterns that match a whole directory name or file name (always checked)
        self.core_patterns = [
            ".git", ".venv", "__pycache__", "node_modules",
            ".api.pid", "api.log", "harness.db", "harness.db-shm", "harness.db-wal", ".agents"
        ]
        self.gitignore_patterns = []
        self._load_gitignore()

    def _load_gitignore(self) -> None:
        """Load ignore patterns from .gitignore file if it exists."""
        gitignore_path = os.path.join(self.root_path, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.gitignore_patterns.append(line.rstrip("/"))

    @property
    def ignore_patterns(self) -> List[str]:
        """Expose full list of ignore patterns for compatibility with tests."""
        return self.core_patterns + self.gitignore_patterns

    def is_ignored(self, path: str) -> bool:
        """Check if a path should be ignored based on patterns.

        Args:
            path: The path to check.

        Returns:
            True if the path should be ignored.
        """
        # Resolve relative paths relative to root_path, not the current working directory
        if not os.path.isabs(path):
            full_path = os.path.abspath(os.path.join(self.root_path, path))
        else:
            full_path = os.path.abspath(path)

        is_outside = False
        try:
            rel_path = os.path.relpath(full_path, self.root_path)
            if rel_path == ".":
                return False
            if rel_path.startswith(".."):
                is_outside = True
            parts = rel_path.split(os.sep)
        except ValueError:
            # On Windows, paths on different drives/mounts cannot have a relative path.
            is_outside = True
            parts = full_path.split(os.sep)

        # Check every part of the path
        for part in parts:
            if not part or part.endswith(":"):
                continue

            # 1. Check core patterns (always checked)
            if part in self.core_patterns:
                return True
            for pattern in self.core_patterns:
                if fnmatch.fnmatch(part, pattern):
                    return True

            # 2. Check gitignore patterns (only checked if inside the workspace)
            if not is_outside:
                if part in self.gitignore_patterns:
                    return True
                for pattern in self.gitignore_patterns:
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
