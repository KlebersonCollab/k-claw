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
    
    prompt = "Please use the 'update_blackboard' tool to save the value '12345' under the key 'SECRET_CODE'. Then, confirm you have saved it."
    
    print("Starting Blackboard Benchmark...")
    print(f"User Request: {prompt}\n")
    
    config = {"configurable": {"thread_id": "benchmark-blackboard"}}
    harness_metadata = {
        "context_budget": 50, "max_iterations": 15, "iteration_count": 0,
        "session_id": "benchmark-blackboard",
        "permissions": "execute", "context_summary": "", "plan": "", "blackboard": {}, "incognito": True, "yolo": True
    }
    
    current_input = {**harness_metadata, "messages": [HumanMessage(content=prompt)]}
    
    final_state = await harness.ainvoke(current_input, config=config)
    
    print("\n--- BENCHMARK RESULTS ---")
    blackboard = final_state.get("blackboard", {})
    print(f"\nFINAL BLACKBOARD STATE:\n{blackboard}")
    
    print("\nAGENT RESPONSE:")
    for msg in final_state.get("messages", [])[-3:]:
        if isinstance(msg, AIMessage) and msg.content:
             print(f"\n{msg.content}\n")
    
    if blackboard.get("SECRET_CODE") == "12345":
        print("\n✅ BENCHMARK PASSED: The Blackboard pattern successfully updated state via tool interception.")
        sys.exit(0)
    else:
        print("\n❌ BENCHMARK FAILED: Blackboard state was not updated correctly.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_benchmark())
