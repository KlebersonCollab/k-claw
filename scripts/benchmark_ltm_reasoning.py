import asyncio
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from langchain_core.messages import HumanMessage
from core.planner import plan_task
from infra.persistence import SessionLogger
from core.ui_interface import UIInterface, EventType, set_ui

class MockUI(UIInterface):
    async def on_event(self, event_type: EventType, data: dict):
        pass
    async def request_approval(self, tool_name: str, args: dict) -> bool:
        return True

async def run_ltm_benchmark():
    set_ui(MockUI())
    session_id = "test-ltm-reasoning"
    logger = SessionLogger(session_id)
    
    # 1. Create a "Golden Rule" in LTM
    test_rule_content = "When modifying core/planner.py, always verify that the memory retrieval threshold is 0.6."
    test_rule_summary = "Technical Lesson: Planning memory threshold for core/planner.py"
    
    print(f"--- BENCHMARK: LTM Reasoning ---")
    print(f"1. Adding Golden Rule to LTM: {test_rule_summary}")
    logger.create_long_term_memory(content=test_rule_content, summary=test_rule_summary)
    
    # 2. Simulate a planning task related to the rule
    state = {
        "session_id": session_id,
        "messages": [HumanMessage(content="I want to update the planning logic in core/planner.py")],
        "plan": "",
        "iteration_count": 0,
        "permissions": "read",
        "context_summary": ""
    }
    
    print("2. Running Planner (this will trigger semantic search)...")
    result = await plan_task(state)
    
    plan = result.get("plan", "")
    print(f"\n3. GENERATED PLAN:\n{plan}")
    
    # 4. Verify if the Golden Rule was retrieved and influenced the plan
    # We look for keywords from the injected rule
    keywords = ["threshold", "0.6", "verify"]
    found = [k for k in keywords if k.lower() in plan.lower()]
    
    if found:
        print(f"\n✅ SUCCESS: The plan reflects the Golden Rule! (Found: {found})")
        sys.exit(0)
    else:
        print("\n❌ FAILURE: The plan did NOT reflect the Golden Rule.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_ltm_benchmark())
