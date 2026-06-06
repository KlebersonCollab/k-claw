import asyncio
import os
from utils import path_filter

async def test_safety_guards():
    # 1. Test .gitignore logic
    print("Testing PathFilter...")
    # Test specific folders
    assert path_filter.is_ignored(".git") == True
    assert path_filter.is_ignored(".git/config") == True
    assert path_filter.is_ignored(".venv") == True
    assert path_filter.is_ignored(".venv/bin/python") == True
    assert path_filter.is_ignored("api.py") == False

    # 2. Test list_directory with ignore
    from tools import list_directory
    print("Testing list_directory ignore...")
    output = list_directory.invoke({"path": "."})
    print(f"Directory listing:\n{output}")

    # Clean verification
    items = output.split("\n")
    assert ".venv" not in items
    assert ".git" not in items
    assert ".git/" not in items
    assert "api.py" in items

    # 3. Test read_file protection
    from tools import read_file
    print("Testing read_file protection...")
    denied = read_file.invoke({"path": ".venv/some_lib.py"})
    print(f"Read denied output: {denied}")
    assert "Access denied" in denied

    print("✅ Safety Guards & Intelligent Listing Validated!")

if __name__ == "__main__":
    asyncio.run(test_safety_guards())
