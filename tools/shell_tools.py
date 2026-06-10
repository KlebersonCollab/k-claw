"""Ferramentas de execução shell (decoradas com @tool do LangChain)."""

from __future__ import annotations

import os
import subprocess
from typing import Optional

from langchain_core.tools import tool

from core.utils import cap_tool_output


@tool
def run_shell(command: str, workspace_path: Optional[str] = None) -> str:
    """Executes a bash command."""
    try:
        cwd = workspace_path if workspace_path and os.path.exists(workspace_path) else None
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd
        )
        output = f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        return cap_tool_output(output, max_chars=3000)
    except Exception as e:
        return f"Error executing command: {str(e)}"
