"""Classificação dinâmica de comandos shell por nível de risco."""

from __future__ import annotations

from typing import Dict

_SHELL_COMMAND_RISK: Dict[str, set] = {
    "read": {
        "ls", "cat", "grep", "find", "echo", "pwd", "head", "tail",
        "wc", "less", "more", "diff", "file", "stat", "which",
        "whoami", "date", "uname", "type", "env",
    },
    "write": {
        "cp", "mv", "mkdir", "touch", "tee", "sort", "uniq",
        "sed", "awk", "pip", "uv", "npm", "node", "python", "python3",
        "git", "npx", "make",
    },
    "full": {
        "rm", "sudo", "chmod", "chown", "kill", "shutdown",
        "mkfs", "dd", "iptables", "useradd", "usermod", "passwd",
    },
}


def classify_shell_command(command: str) -> str:
    """Classify a shell command by risk level."""
    base = command.strip().split()[0] if command.strip() else ""
    if base in _SHELL_COMMAND_RISK["full"]:
        return "full"
    if base in _SHELL_COMMAND_RISK["read"]:
        return "read"
    if base in _SHELL_COMMAND_RISK["write"]:
        return "write"
    return "write"


def risk_level_value(level: str) -> int:
    """Convert a risk level string to a numeric value for comparison."""
    return {"read": 1, "write": 2, "full": 3, "execute": 3}.get(level, 2)
