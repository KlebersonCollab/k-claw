import pytest
from utils import path_filter
from tools import list_directory, read_file

@pytest.mark.asyncio
async def test_safety_guards():
    # 1. Test .gitignore logic
    assert path_filter.is_ignored(".git") is True
    assert path_filter.is_ignored(".git/config") is True
    assert path_filter.is_ignored(".venv") is True
    assert path_filter.is_ignored(".venv/bin/python") is True
    assert path_filter.is_ignored("api.py") is False

@pytest.mark.asyncio
async def test_list_directory_ignore():
    # 2. Test list_directory with ignore
    output = list_directory.invoke({"path": "."})
    items = output.split("\n")
    assert ".venv" not in items
    assert ".git" not in items
    assert ".git/" not in items
    assert "api.py" in items

@pytest.mark.asyncio
async def test_read_file_protection():
    # 3. Test read_file protection
    denied = read_file.invoke({"path": ".venv/some_lib.py"})
    assert "Access denied" in denied
