import asyncio
import sys
import os
import time
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from core.harness import harness
from core.ui_interface import UIInterface, EventType, set_ui

class StatsUI(UIInterface):
    def __init__(self):
        self.tool_calls = []
        self.agent_thinks = 0
    async def on_event(self, event_type: EventType, data: dict):
        if event_type == EventType.TOOL_START:
            self.tool_calls.append(data.get('tool'))
        elif event_type == EventType.THINKING_START:
            self.agent_thinks += 1
    async def request_approval(self, tool_name: str, args: dict) -> bool:
        return True

async def run_benchmark():
    ui = StatsUI()
    set_ui(ui)
    
    # Task designed to verify blackboard propagation
    prompt = (
        "First, identify the current working directory and save it to the blackboard with the key 'PROJECT_ROOT'. "
        "Then, delegate to the 'researcher' agent to find the file 'pyproject.toml' and ask it to report if it can see the 'PROJECT_ROOT' value in its shared blackboard."
    )
    
    print("Starting Collaboration Benchmark...")
    print(f"User Request: {prompt}\n")
    
    start_time = time.time()
    
    config = {"configurable": {"thread_id": "bench-collab-v1"}}
    initial_state = {
        "messages": [HumanMessage(content=prompt)],
        "context_budget": 50,
        "max_iterations": 15,
        "iteration_count": 0,
        "session_id": "bench-collab-v1",
        "permissions": "execute",
        "context_summary": "",
        "plan": "",
        "incognito": True,
        "yolo": True,
        "blackboard": {}
    }
    
    try:
        final_state = await asyncio.wait_for(harness.ainvoke(initial_state, config=config), timeout=300)
    except asyncio.TimeoutError:
        print("\n❌ BENCHMARK FAILED: Timed out after 300 seconds.")
        return
    
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n--- BENCHMARK RESULTS ---")
    print(f"Total Time: {duration:.2f}s")
    print(f"Total Tool Calls: {len(ui.tool_calls)}")
    print(f"Tool Calls Detail: {ui.tool_calls}")
    print(f"Total Thinking Turns: {ui.agent_thinks}")
    
    # Analyze redundancy
    list_dir_calls = [tc for tc in ui.tool_calls if tc == "list_directory"]
    grep_calls = [tc for tc in ui.tool_calls if tc == "grep_search"]
    
    print(f"List Directory Calls: {len(list_dir_calls)}")
    print("\nFINAL AGENT RESPONSE:")
    if final_state.get("messages"):
        print(final_state["messages"][-1].content)
    
    # The goal is to reduce redundant 'list_directory' or 'grep_search' if the parent already did it.
    
    # We save these results to a file for comparison
    with open("benchmark_results_baseline.txt", "w") as f:
        f.write(f"Total Tool Calls: {len(ui.tool_calls)}\n")
        f.write(f"Tool Calls Detail: {ui.tool_calls}\n")
        f.write(f"Total Thinking Turns: {ui.agent_thinks}\n")
        f.write(f"List Directory Calls: {len(list_dir_calls)}\n")
        f.write(f"Grep Search Calls: {len(grep_calls)}\n")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
