"""Unit tests for tools/file_tools.py — file system tools."""

import os
import pytest
from unittest.mock import patch
from tools import list_directory, read_file, replace_string, write_file, grep_search, glob_search


class TestListDirectory:
    """Test list_directory tool."""

    def test_lists_visible_items(self, temp_project_dir):
        result = list_directory.invoke({"path": temp_project_dir})
        assert "AGENTS.md" in result
        assert "README.md" in result
        assert "main.py" in result

    def test_excludes_ignored_items(self, temp_project_dir):
        result = list_directory.invoke({"path": temp_project_dir})
        assert ".git" not in result
        assert ".venv" not in result
        assert "__pycache__" not in result

    def test_denies_ignored_path(self, temp_project_dir):
        git_path = os.path.join(temp_project_dir, ".git")
        result = list_directory.invoke({"path": git_path})
        assert "Access denied" in result

    def test_empty_directory(self, temp_dir):
        result = list_directory.invoke({"path": temp_dir})
        assert "empty" in result.lower()

    def test_nonexistent_path(self):
        result = list_directory.invoke({"path": "/nonexistent/path/xyz"})
        assert "Error" in result


class TestReadFile:
    """Test read_file tool."""

    def test_reads_file_content(self, temp_project_dir):
        result = read_file.invoke({"path": os.path.join(temp_project_dir, "main.py")})
        assert "print('hello')" in result

    def test_denies_ignored_path(self, temp_project_dir):
        git_config = os.path.join(temp_project_dir, ".git", "config")
        result = read_file.invoke({"path": git_config})
        assert "Access denied" in result

    def test_rejects_directory(self, temp_project_dir):
        result = read_file.invoke({"path": temp_project_dir})
        assert "directory" in result.lower()

    def test_nonexistent_file(self):
        result = read_file.invoke({"path": "/nonexistent/file.txt"})
        assert "Error" in result

    def test_line_pagination(self, temp_project_dir):
        # Create a file with many lines
        test_file = os.path.join(temp_project_dir, "lines.txt")
        with open(test_file, "w") as f:
            for i in range(100):
                f.write(f"Line {i}\n")

        result = read_file.invoke({"path": test_file, "start_line": 1, "end_line": 5})
        assert "Line 0" in result
        assert "Line 4" in result
        assert "Line 5" not in result

    def test_truncation_warning(self, temp_project_dir):
        test_file = os.path.join(temp_project_dir, "big.txt")
        with open(test_file, "w") as f:
            for i in range(200):
                f.write(f"Line {i}\n")

        result = read_file.invoke({"path": test_file})
        assert "truncated" in result.lower()


class TestReplaceString:
    """Test replace_string tool."""

    def test_replaces_string(self, temp_project_dir):
        test_file = os.path.join(temp_project_dir, "replace_test.txt")
        with open(test_file, "w") as f:
            f.write("Hello World")

        result = replace_string.invoke({
            "path": test_file,
            "old_string": "Hello",
            "new_string": "Goodbye"
        })
        assert "Successfully updated" in result
        with open(test_file) as f:
            assert f.read() == "Goodbye World"

    def test_string_not_found(self, temp_project_dir):
        test_file = os.path.join(temp_project_dir, "replace_test.txt")
        with open(test_file, "w") as f:
            f.write("Hello World")

        result = replace_string.invoke({
            "path": test_file,
            "old_string": "Nonexistent",
            "new_string": "Replacement"
        })
        assert "not found" in result

    def test_multiple_occurrences(self, temp_project_dir):
        test_file = os.path.join(temp_project_dir, "replace_test.txt")
        with open(test_file, "w") as f:
            f.write("Hello Hello Hello")

        result = replace_string.invoke({
            "path": test_file,
            "old_string": "Hello",
            "new_string": "Goodbye"
        })
        assert "occurs 3 times" in result

    def test_denies_ignored_path(self, temp_project_dir):
        git_config = os.path.join(temp_project_dir, ".git", "config")
        result = replace_string.invoke({
            "path": git_config,
            "old_string": "old",
            "new_string": "new"
        })
        assert "Access denied" in result


class TestWriteFile:
    """Test write_file tool."""

    def test_writes_file(self, temp_dir):
        test_file = os.path.join(temp_dir, "new_file.txt")
        result = write_file.invoke({"path": test_file, "content": "Hello World"})
        assert "written successfully" in result
        with open(test_file) as f:
            assert f.read() == "Hello World"

    def test_overwrites_existing(self, temp_dir):
        test_file = os.path.join(temp_dir, "existing.txt")
        with open(test_file, "w") as f:
            f.write("Old content")

        result = write_file.invoke({"path": test_file, "content": "New content"})
        assert "written successfully" in result
        with open(test_file) as f:
            assert f.read() == "New content"

    def test_denies_ignored_path(self, temp_project_dir):
        git_config = os.path.join(temp_project_dir, ".git", "config")
        result = write_file.invoke({"path": git_config, "content": "new"})
        assert "Access denied" in result


class TestGrepSearch:
    """Test grep_search tool."""

    def test_finds_pattern(self, temp_project_dir):
        result = grep_search.invoke({
            "pattern": "print",
            "path": temp_project_dir,
        })
        assert "print" in result

    def test_no_matches(self, temp_project_dir):
        result = grep_search.invoke({
            "pattern": "NONEXISTENT_PATTERN_XYZ",
            "path": temp_project_dir,
        })
        assert result == "" or "No matches" in result or result.strip() == ""

    def test_with_include_pattern(self, temp_project_dir):
        result = grep_search.invoke({
            "pattern": "print",
            "path": temp_project_dir,
            "include_pattern": "*.py",
        })
        assert "print" in result

    def test_denies_ignored_path(self, temp_project_dir):
        git_path = os.path.join(temp_project_dir, ".git")
        result = grep_search.invoke({"pattern": "test", "path": git_path})
        assert "Access denied" in result


class TestGlobSearch:
    """Test glob_search tool."""

    def test_finds_py_files(self, temp_project_dir):
        result = glob_search.invoke({
            "pattern": "**/*.py",
            "path": temp_project_dir,
        })
        assert "main.py" in result

    def test_finds_all_files(self, temp_project_dir):
        result = glob_search.invoke({
            "pattern": "**/*",
            "path": temp_project_dir,
        })
        assert "AGENTS.md" in result

    def test_no_matches(self, temp_project_dir):
        result = glob_search.invoke({
            "pattern": "**/*.xyz",
            "path": temp_project_dir,
        })
        assert "No files found" in result or result.strip() == ""
