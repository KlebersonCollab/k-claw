import asyncio
import os
from persistence import SessionLogger
from logic import call_model
from langchain_core.messages import HumanMessage

async def test_incognito_mode():
    session_id = "incognito-test-session"

    # 1. Normal mode
    state_normal = {
        "messages": [HumanMessage(content="This should be logged")],
        "iteration_count": 0, "session_id": session_id, "permissions": "read", "context_summary": "", "incognito": False
    }
    await asyncio.to_thread(call_model, state_normal)

    logger = SessionLogger(session_id)
    history = logger.get_message_history()
    print(f"History length (Normal): {len(history)}")
    assert len(history) > 0

    # 2. Incognito mode
    state_incognito = {
        "messages": [HumanMessage(content="This should NOT be logged")],
        "iteration_count": 0, "session_id": session_id, "permissions": "read", "context_summary": "", "incognito": True
    }
    await asyncio.to_thread(call_model, state_incognito)

    history_after = logger.get_message_history()
    print(f"History length (After Incognito): {len(history_after)}")
    # It should remain the same as before the second call
    assert len(history_after) == len(history)

    print("✅ Incognito Mode Validated!")

if __name__ == "__main__":
    asyncio.run(test_incognito_mode())
