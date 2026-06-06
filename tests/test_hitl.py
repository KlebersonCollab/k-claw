import asyncio
import os
from langchain_core.messages import HumanMessage, AIMessage
from harness import harness
from tools import registry
from persistence import SessionLogger

async def test_hitl_interrupt():
    session_id = "test-hitl-session"
    config = {"configurable": {"thread_id": session_id}}

    # 1. Setup state that triggers a tool requiring approval (write_file)
    state = {
        "messages": [HumanMessage(content="Escreva 'Olá' no arquivo test.txt")],
        "context_budget": 10,
        "iteration_count": 0,
        "session_id": session_id,
        "permissions": "write",
        "context_summary": ""
    }

    print("Testing HITL Interrupt...")
    # Invoke. This should stop before 'tools'
    final_state = await harness.ainvoke(state, config=config)

    # Check if we are at an interrupt
    snapshot = await harness.aget_state(config)
    print(f"Next node in graph: {snapshot.next}")
    assert snapshot.next == ("tools",)

    # Check that tool hasn't run yet (no tool message in history)
    history = final_state["messages"]
    assert not any(isinstance(m, AIMessage) and m.tool_calls == [] for m in history[1:]) # Simplified check

    print("✅ HITL Interrupt Validated!")

if __name__ == "__main__":
    # Ensure a clean state for testing if needed
    asyncio.run(test_hitl_interrupt())
