import pytest
import os
import shutil
from core.prompt_builder import assemble_system_prompt
from core.utils import _CONTEXT_CACHE

@pytest.mark.asyncio
async def test_recursive_context():
    # 1. Setup nested directory
    subfolder = os.path.abspath("tests/recursive_test")
    os.makedirs(subfolder, exist_ok=True)

    # 2. Create a local GEMINI.md
    local_context_path = os.path.join(subfolder, "GEMINI.md")
    with open(local_context_path, "w") as f:
        f.write("Local rule: Only use async functions in this folder.")

    # 3. Clear cache to force reload
    _CONTEXT_CACHE["data"] = None
    _CONTEXT_CACHE["timestamp"] = 0

    # 4. Use the start_path parameter of recursive_load_context indirectly
    # assemble_system_prompt calls recursive_load_context() with default "."
    # So we MUST be in that directory for the default to work as expected in the test
    old_cwd = os.getcwd()
    os.chdir(subfolder)

    try:
        state = {
            "messages": [],
            "permissions": "read",
            "context_summary": "",
            "session_id": "test-session"
        }

        # The prompt builder uses recursive_load_context()
        prompt = assemble_system_prompt(state)
        content = prompt.content

        # 5. Assertions
        assert "Local rule" in content
        assert "Orchestrator Agent" in content

    finally:
        os.chdir(old_cwd)
        # Clear cache again so it doesn't affect other tests
        _CONTEXT_CACHE["data"] = None
        _CONTEXT_CACHE["timestamp"] = 0
        if os.path.exists(subfolder):
            shutil.rmtree(subfolder)
