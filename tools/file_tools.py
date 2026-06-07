"""Ferramentas de sistema de arquivos (decoradas com @tool do LangChain)."""

from __future__ import annotations

import os
from typing import Optional

from langchain_core.tools import tool

from core.utils import redact_sensitive_info, path_filter, cap_tool_output


@tool
def list_directory(path: str = ".") -> str:
    """Lists files and directories at a given path, respecting project ignore rules."""
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."
        items = os.listdir(path)
        visible_items = []
        for item in items:
            item_path = os.path.join(path, item)
            if not path_filter.is_ignored(item_path):
                type_suffix = "/" if os.path.isdir(item_path) else ""
                visible_items.append(f"{item}{type_suffix}")
        return "\n".join(sorted(visible_items)) if visible_items else "Directory is empty."
    except Exception as e:
        return f"Error listing directory: {str(e)}"


@tool
def read_file(path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """Reads a file from disk with optional line-range pagination (1-based indexing)."""
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."
        if os.path.isdir(path):
            return f"Error: {path} is a directory. Use list_directory instead."

        with open(path, "r", encoding="utf-8") as f:
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


@tool
def replace_string(path: str, old_string: str, new_string: str) -> str:
    """Surgically replaces a specific exact string block in a file with a new string."""
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        occurrences = content.count(old_string)

        if occurrences == 0:
            return "Error: The exact string block provided was not found in the file. Ensure you copy the existing text EXACTLY."
        elif occurrences > 1:
            return f"Error: The string block occurs {occurrences} times. Provide a larger context block to ensure a unique match."

        new_content = content.replace(old_string, new_string)

        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return f"Successfully updated {path}. Replaced 1 exact match."
    except Exception as e:
        return f"Error replacing string in file: {str(e)}"


@tool
def write_file(path: str, content: str) -> str:
    """Writes content to a file (WARNING: Overwrites entire file)."""
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File {path} written successfully."
    except Exception as e:
        return f"Error writing file: {str(e)}"


@tool
def grep_search(pattern: str, path: str = ".", include_pattern: Optional[str] = None, context: int = 0) -> str:
    """Searches for a regex pattern in file contents.

    Args:
        pattern: Regex pattern to search for.
        path: Directory or file to search in (default is current).
        include_pattern: Glob pattern to filter files (e.g. "*.py").
        context: Number of lines of context to show around matches.
    """
    import re
    import glob
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."

        search_path = os.path.join(path, "**", include_pattern) if include_pattern else os.path.join(path, "**", "*")
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
                            results.append(f"--- Match in {file_path} (Line {i+1}) ---\n{match_block}")
            except Exception:
                continue

        if not results:
            return f"No matches found for '{pattern}'."

        output = "\n".join(results)
        return cap_tool_output(output, max_chars=4000)

    except Exception as e:
        return f"Error in grep_search: {str(e)}"


@tool
def glob_search(pattern: str, path: str = ".") -> str:
    """Finds files matching a glob pattern (e.g. '**/*.py')."""
    import glob
    try:
        if path_filter.is_ignored(path):
            return f"Access denied: {path} is an ignored path."

        search_pattern = os.path.join(path, pattern)
        files = glob.glob(search_pattern, recursive=True)
        visible_files = [f for f in files if not path_filter.is_ignored(f) and not os.path.isdir(f)]

        if not visible_files:
            return f"No files found matching pattern '{pattern}'."

        return "\n".join(sorted(visible_files))
    except Exception as e:
        return f"Error in glob_search: {str(e)}"
