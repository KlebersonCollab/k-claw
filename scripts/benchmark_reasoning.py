import asyncio
import sys
import os
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from core.harness import harness
from core.ui_interface import UIInterface, EventType, set_ui

class MockUI(UIInterface):
    def __init__(self):
        self.events = []
    async def on_event(self, event_type: EventType, data: dict):
        self.events.append((event_type, data))
        if event_type == EventType.TOOL_START:
            print(f"-> Executing tool: {data.get('tool')}")
        elif event_type == EventType.THINKING_START:
            print(f"-> Agent {data.get('agent')} is thinking...")
    async def request_approval(self, tool_name: str, args: dict) -> bool:
        return True # Auto-approve for benchmark

async def run_benchmark():
    set_ui(MockUI())
    
    # 1. We ask the agent to act as a verifier and check the project
    prompt = "Please verify if the tests in tests/unit/test_env_tools.py pass. Make sure you use the appropriate test command for this project environment."
    
    print("Starting Benchmark...")
    print(f"User Request: {prompt}\n")
    
    config = {"configurable": {"thread_id": "benchmark-reasoning-3.0"}}
    harness_metadata = {
        "context_budget": 50, "max_iterations": 15, "iteration_count": 0,
        "session_id": "benchmark-reasoning-3.0",
        "permissions": "execute", "context_summary": "", "plan": "", "incognito": True, "yolo": True
    }
    
    current_input = {**harness_metadata, "messages": [HumanMessage(content=prompt)]}
    
    final_state = await harness.ainvoke(current_input, config=config)
    
    print("\n--- BENCHMARK RESULTS ---")
    plan = final_state.get("plan", "")
    print(f"\nPLAN:\n{plan}")
    
    print("\nAGENT RESPONSE:")
    for msg in final_state.get("messages", [])[-3:]:
        if isinstance(msg, AIMessage) and msg.content:
             print(f"\n{msg.content}\n")
    
    # Simple assertion
    if "pytest" in plan.lower() or "uv run pytest" in plan.lower() or "detect_workspace_env" in str(final_state):
        print("\n✅ BENCHMARK PASSED: The agent utilized environment awareness.")
        sys.exit(0)
    else:
        print("\n❌ BENCHMARK FAILED: Environment logic not fully utilized.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
