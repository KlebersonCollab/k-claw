"""Ferramentas de sistema de arquivos (decoradas com @tool do LangChain)."""

from __future__ import annotations

import os
from typing import Optional

from langchain_core.tools import tool

from core.utils import redact_sensitive_info, path_filter, cap_tool_output


@tool
def list_directory(path: str = ".", workspace_path: Optional[str] = None) -> str:
    """Lists files and directories at a given path, respecting project ignore rules."""
    try:
        base = workspace_path if workspace_path and os.path.exists(workspace_path) else "."
        target = os.path.join(base, path)

        if path_filter.is_ignored(target):
            return f"Access denied: {path} is an ignored path."

        items = os.listdir(target)
        visible_items = []
        for item in items:
            item_path = os.path.join(target, item)
            # Use relative path for ignore check to keep it consistent
            try:
                rel_path = os.path.relpath(item_path, base)
            except ValueError:
                rel_path = item_path
            if not path_filter.is_ignored(rel_path):
                type_suffix = "/" if os.path.isdir(item_path) else ""
                visible_items.append(f"{item}{type_suffix}")
        return "\n".join(sorted(visible_items)) if visible_items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
def read_file(path: str, start_line: Optional[int] = None, end_line: Optional[int] = None, workspace_path: Optional[str] = None) -> str:
    """Reads a file from disk with optional line-range pagination (1-based indexing)."""
    try:
        base = workspace_path if workspace_path and os.path.exists(str(workspace_path)) else "."
        target = os.path.join(str(base), path)

        if path_filter.is_ignored(target):
            return f"Access denied: {path} is an ignored path."
        if os.path.isdir(target):
            return f"Error: {path} is a directory. Use list_directory instead."

        with open(target, "r", encoding="utf-8") as f:
            lines = f.readlines()

        total_lines = len(lines)
        s = (start_line - 1) if start_line else 0
        e = end_line if end_line else total_lines

        MAX_LINES = 150
        truncation_warning = ""
        if (e - s) > MAX_LINES:
            e = s + MAX_LINES
            truncation_warning = f"\n\n[WARNING: Output truncated to {MAX_LINES} lines to save tokens. Use pagination (start_line/end_line) to read the rest.]"

        # Format with line numbers for spatial awareness
        numbered_lines = []
        for i, line in enumerate(lines[s:e], start=s + 1):
            numbered_lines.append(f"{i:4d} | {line}")

        content = "".join(numbered_lines)
        return f"--- Lines {s + 1} to {min(e, total_lines)} of {total_lines} ---\n{content}{truncation_warning}"

    except Exception as e:
        return f"Error reading file: {str(e)}"


import subprocess

def _syntax_check(file_path: str) -> str:
    """Runs a quick syntax check on the file if supported."""
    ext = os.path.splitext(file_path)[1]
    if ext == '.py':
        res = subprocess.run(['python', '-m', 'py_compile', file_path], capture_output=True, text=True)
        if res.returncode != 0:
            return f"\n\n[WARNING: SYNTAX ERROR DETECTED]\n{res.stderr.strip()}\nPlease fix this immediately."
    return ""

@tool
def replace_string(path: str, old_string: str, new_string: str, workspace_path: Optional[str] = None) -> str:
    """Surgically replaces a specific exact string block in a file with a new string."""
    try:
        base = workspace_path if workspace_path and os.path.exists(workspace_path) else "."
        target = os.path.join(base, path)

        if path_filter.is_ignored(target):
            return f"Access denied: {path} is an ignored path."

        with open(target, "r", encoding="utf-8") as f:
            content = f.read()

        occurrences = content.count(old_string)

        if occurrences == 0:
            return "Error: The exact string block provided was not found in the file. Ensure you copy the existing text EXACTLY."
        elif occurrences > 1:
            return f"Error: The string block occurs {occurrences} times. Provide a larger context block to ensure a unique match."

        new_content = content.replace(old_string, new_string)

        with open(target, "w", encoding="utf-8") as f:
            f.write(new_content)

        feedback = _syntax_check(target)
        return f"Successfully updated {path}. Replaced 1 exact match.{feedback}"
    except Exception as e:
        return f"Error replacing string in file: {str(e)}"


@tool
def write_file(path: str, content: str, workspace_path: Optional[str] = None) -> str:
    """Writes content to a file (WARNING: Overwrites entire file)."""
    try:
        base = workspace_path if workspace_path and os.path.exists(workspace_path) else "."
        target = os.path.join(base, path)

        if path_filter.is_ignored(target):
            return f"Access denied: {path} is an ignored path."

        # Ensure directory exists
        os.makedirs(os.path.dirname(target), exist_ok=True)

        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
            
        feedback = _syntax_check(target)
        return f"File {path} written successfully.{feedback}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def grep_search(pattern: str, path: str = ".", include_pattern: Optional[str] = None, context: int = 0, workspace_path: Optional[str] = None) -> str:
    """Searches for a regex pattern in file contents.

    Args:
        pattern: Regex pattern to search for.
        path: Directory or file to search in (default is current).
        include_pattern: Glob pattern to filter files (e.g. "*.py").
        context: Number of lines of context to show around matches.
        workspace_path: Optional base path for the search.
    """
    import re
    import glob
    try:
        base = workspace_path if workspace_path and os.path.exists(workspace_path) else "."
        target = os.path.join(base, path)

        if path_filter.is_ignored(target):
            return f"Access denied: {path} is an ignored path."

        search_path = os.path.join(target, "**", include_pattern) if include_pattern else os.path.join(target, "**", "*")
        files = glob.glob(search_path, recursive=True)
        results = []
        regex = re.compile(pattern, re.IGNORECASE)

        for file_path in files:
            if os.path.isdir(file_path) or path_filter.is_ignored(file_path):
                continue

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if regex.search(line):
                            start = max(0, i - context)
                            end = min(len(lines), i + context + 1)
                            match_block = "".join(lines[start:end])

                            # Show path relative to base for better readability
                            try:
                                rel_file_path = os.path.relpath(file_path, base)
                            except ValueError:
                                rel_file_path = file_path
                            results.append(f"--- Match in {rel_file_path} (Line {i+1}) ---\n{match_block}")
            except Exception:
                continue

        if not results:
            return f"No matches found for '{pattern}'."

        output = "\n".join(results)
        return cap_tool_output(output, max_chars=4000)

    except Exception as e:
        return f"Error in grep_search: {str(e)}"


@tool
def glob_search(pattern: str, path: str = ".", workspace_path: Optional[str] = None) -> str:
    """Finds files matching a glob pattern (e.g. '**/*.py')."""
    import glob
    try:
        base = workspace_path if workspace_path and os.path.exists(workspace_path) else "."
        target = os.path.join(base, path)

        if path_filter.is_ignored(target):
            return f"Access denied: {path} is an ignored path."

        search_pattern = os.path.join(target, pattern)
        files = glob.glob(search_pattern, recursive=True)

        visible_files = []
        for f in files:
            try:
                rel_path = os.path.relpath(f, base)
            except ValueError:
                rel_path = f
            if not path_filter.is_ignored(rel_path) and not os.path.isdir(f):
                visible_files.append(rel_path)

        if not visible_files:
            return f"No files found matching pattern '{pattern}'."

        return "\n".join(sorted(visible_files))
    except Exception as e:
        return f"Error in glob_search: {str(e)}"
