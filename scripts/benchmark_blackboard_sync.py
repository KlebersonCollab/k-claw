import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.prompt_builder import assemble_system_prompt

async def run_blackboard_benchmark():
    print(f"--- BENCHMARK: Blackboard Sync ---")
    
    # 1. Setup state with a blackboard entry
    state = {
        "session_id": "sub-coder-test", # Simulate a sub-agent session
        "permissions": "write",
        "blackboard": {
            "DB_PORT": "5432",
            "API_KEY_LOCATION": ".env.local"
        },
        "context_summary": "Ongoing refactoring of the persistence layer.",
        "plan": "PHASE 1: Setup"
    }
    
    # 2. Assemble system prompt for the sub-agent
    print("1. Assembling system prompt for sub-agent 'coder'...")
    sys_msg = assemble_system_prompt(state)
    content = sys_msg.content
    
    # 3. Verify if blackboard entries are present
    print("2. Verifying blackboard content in prompt...")
    
    keywords = ["DB_PORT", "5432", "API_KEY_LOCATION", ".env.local", "GLOBAL BLACKBOARD"]
    found = [k for k in keywords if k in content]
    
    if len(found) == len(keywords):
        print(f"\n✅ SUCCESS: Sub-agent prompt contains all blackboard discoveries! (Found: {found})")
        sys.exit(0)
    else:
        print(f"\n❌ FAILURE: Sub-agent prompt is missing some blackboard discoveries. Found only: {found}")
        # print(f"DEBUG PROMPT:\n{content}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_blackboard_benchmark())
