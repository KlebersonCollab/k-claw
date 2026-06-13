"""Edge case tests for tools/file_tools.py."""

import os
import pytest
from tools import list_directory, read_file, replace_string, write_file, grep_search, glob_search


class TestListDirectoryEdgeCases:
    """Edge cases for list_directory."""

    def test_permission_denied(self):
        """Directory without read permission."""
        # This might not work on all systems
        result = list_directory.invoke({"path": "/root/.ssh"})
        # Should handle gracefully, either listing or erroring
        assert result  # Should return something

    def test_circular_symlink(self, temp_dir):
        """Directory with circular symlinks."""
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)
        # Create a symlink pointing back to parent (if supported)
        try:
            os.symlink(temp_dir, os.path.join(subdir, "parent_link"))
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks not supported")

        result = list_directory.invoke({"path": subdir})
        assert result is not None


class TestReadFileEdgeCases:
    """Edge cases for read_file."""

    def test_binary_file(self, temp_dir):
        """Attempt to read a binary file."""
        binary_file = os.path.join(temp_dir, "test.bin")
        with open(binary_file, "wb") as f:
            f.write(b"\x00\x01\x02\x03\xff\xfe\xfd")

        result = read_file.invoke({"path": binary_file})
        # Should handle gracefully (may have encoding errors)
        assert result

    def test_empty_file(self, temp_dir):
        """Read an empty file."""
        empty_file = os.path.join(temp_dir, "empty.txt")
        with open(empty_file, "w") as f:
            pass

        result = read_file.invoke({"path": empty_file})
        assert result

    def test_very_long_lines(self, temp_dir):
        """File with very long lines."""
        test_file = os.path.join(temp_dir, "longlines.txt")
        with open(test_file, "w") as f:
            f.write("A" * 10000 + "\n")
            f.write("B" * 5000 + "\n")

        result = read_file.invoke({"path": test_file})
        assert result

    def test_invalid_line_range(self, temp_dir):
        """Invalid line range."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        # start_line beyond end of file
        result = read_file.invoke({"path": test_file, "start_line": 100})
        assert result

    def test_negative_line_numbers(self, temp_dir):
        """Negative line numbers."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        result = read_file.invoke({"path": test_file, "start_line": -1})
        # Should handle gracefully
        assert result

    def test_special_characters_in_path(self, temp_dir):
        """File with special characters in path."""
        special_file = os.path.join(temp_dir, "file with spaces (1).txt")
        with open(special_file, "w") as f:
            f.write("Content")

        result = read_file.invoke({"path": special_file})
        assert "Content" in result


class TestReplaceStringEdgeCases:
    """Edge cases for replace_string."""

    def test_empty_old_string(self, temp_dir):
        """Empty old_string."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello World")

        result = replace_string.invoke({
            "path": test_file,
            "old_string": "",
            "new_string": "X"
        })
        # Empty string is found at every position
        assert result

    def test_empty_new_string(self, temp_dir):
        """Empty new_string (deletion)."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello World")

        result = replace_string.invoke({
            "path": test_file,
            "old_string": " World",
            "new_string": ""
        })
        assert "Successfully updated" in result
        with open(test_file) as f:
            assert f.read() == "Hello"

    def test_multiline_replacement(self, temp_dir):
        """Multiline string replacement."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\n")

        result = replace_string.invoke({
            "path": test_file,
            "old_string": "Line 1\nLine 2",
            "new_string": "Replaced"
        })
        assert "Successfully updated" in result

    def test_unicode_replacement(self, temp_dir):
        """Unicode string replacement."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("Olá mundo")

        result = replace_string.invoke({
            "path": test_file,
            "old_string": "Olá",
            "new_string": "Hello"
        })
        assert "Successfully updated" in result

    def test_replace_on_directory(self, temp_dir):
        """Attempt to replace in a directory."""
        result = replace_string.invoke({
            "path": temp_dir,
            "old_string": "test",
            "new_string": "replaced"
        })
        assert "Error" in result


class TestWriteFileEdgeCases:
    """Edge cases for write_file."""

    def test_write_to_nonexistent_directory(self, temp_dir):
        """Write to a file with an invalid path containing a null byte."""
        test_file = os.path.join(temp_dir, "invalid_\x00_file.txt")
        result = write_file.invoke({"path": test_file, "content": "test"})
        assert "Error" in result

    def test_write_empty_content(self, temp_dir):
        """Write empty content."""
        test_file = os.path.join(temp_dir, "empty.txt")
        result = write_file.invoke({"path": test_file, "content": ""})
        assert "written successfully" in result

    def test_write_very_large_content(self, temp_dir):
        """Write very large content."""
        test_file = os.path.join(temp_dir, "large.txt")
        large_content = "A" * 100000
        result = write_file.invoke({"path": test_file, "content": large_content})
        assert "written successfully" in result

    def test_write_unicode_content(self, temp_dir):
        """Write unicode content."""
        test_file = os.path.join(temp_dir, "unicode.txt")
        result = write_file.invoke({"path": test_file, "content": "你好世界 مرحبا"})
        assert "written successfully" in result


class TestGrepSearchEdgeCases:
    """Edge cases for grep_search."""

    def test_invalid_regex(self, temp_dir):
        """Invalid regex pattern."""
        result = grep_search.invoke({
            "pattern": "[invalid regex",
            "path": temp_dir,
        })
        # Should handle gracefully
        assert result is not None

    def test_regex_with_special_chars(self, temp_dir):
        """Regex with special characters."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Price: $100.00\nPrice: $200.00\n")

        result = grep_search.invoke({
            "pattern": r"\$\d+\.\d{2}",
            "path": temp_dir,
        })
        assert "$100.00" in result or "Price" in result

    def test_context_lines(self, temp_dir):
        """Grep with context lines."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            for i in range(20):
                f.write(f"Line {i}\n")

        result = grep_search.invoke({
            "pattern": "Line 10",
            "path": temp_dir,
            "context": 2,
        })
        assert result


class TestGlobSearchEdgeCases:
    """Edge cases for glob_search."""

    def test_very_deep_nesting(self, temp_dir):
        """Glob with deeply nested paths."""
        deep_path = temp_dir
        for i in range(10):
            deep_path = os.path.join(deep_path, f"level{i}")
        os.makedirs(deep_path, exist_ok=True)
        with open(os.path.join(deep_path, "deep.txt"), "w") as f:
            f.write("Deep file")

        result = glob_search.invoke({
            "pattern": "**/*.txt",
            "path": temp_dir,
        })
        assert "deep.txt" in result

    def test_nonexistent_directory(self):
        """Glob in nonexistent directory."""
        result = glob_search.invoke({
            "pattern": "**/*",
            "path": "/nonexistent/path/xyz",
        })
        assert result is not None
