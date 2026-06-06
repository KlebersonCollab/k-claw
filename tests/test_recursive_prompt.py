import asyncio
import os
import shutil
from logic import assemble_system_prompt
from state import HarnessState

async def test_recursive_context():
    # 1. Setup nested directory
    subfolder = "tests/recursive_test"
    os.makedirs(subfolder, exist_ok=True)

    # 2. Create a local CONTEXT.md
    local_context_path = os.path.join(subfolder, "CONTEXT.md")
    with open(local_context_path, "w") as f:
        f.write("Local rule: Only use async functions in this folder.")

    # 3. Create a global AGENTS.md in root (already exists, but let's ensure it)
    # Actually AGENTS.md is in root.

    # 4. Change current working directory to subfolder for testing
    old_cwd = os.getcwd()
    os.chdir(subfolder)

    try:
        state = {
            "messages": [],
            "permissions": "read",
            "context_summary": ""
        }

        prompt = assemble_system_prompt(state)
        content = prompt.content

        print(f"Assembled Prompt (partial):\n{content[:500]}...")

        # 5. Assertions
        assert "Local rule" in content
        assert "Agent Catalog" in content # From global AGENTS.md
        assert content.find("Agent Catalog") < content.find("Local rule") # Order check: global to specific

        print("✅ Recursive Context Assembly Validated!")

    finally:
        os.chdir(old_cwd)
        shutil.rmtree(subfolder)

if __name__ == "__main__":
    asyncio.run(test_recursive_context())
