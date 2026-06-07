import uuid
import json
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from harness import harness
from persistence import SessionLogger
from dotenv import load_dotenv
from ui_interface import UIInterface, EventType, set_ui

load_dotenv()

app = FastAPI(title="Agent Harness API v2.0")

# --- Persistent Pending Approvals Store ---
# In production, this should be in Redis or DB. For now, in-memory.
pending_approvals = {}

class APIInterface(UIInterface):
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.events = asyncio.Queue()

    async def on_event(self, event_type: EventType, data: Dict[str, Any]):
        await self.events.put({"type": event_type.value, "data": data})

    async def request_approval(self, tool_name: str, args: Dict[str, Any]) -> bool:
        # Create a promise-like future that will be resolved via the /approve endpoint
        approval_id = str(uuid.uuid4())
        future = asyncio.get_running_loop().create_future()

        pending_approvals[approval_id] = future

        # Notify client that approval is required
        await self.on_event(EventType.APPROVAL_REQUIRED, {
            "approval_id": approval_id,
            "tool": tool_name,
            "args": args
        })

        # Wait for the future to be set by the /approve endpoint
        try:
            return await future
        finally:
            pending_approvals.pop(approval_id, None)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.post("/chat")
async def chat(request: ChatRequest):
    if len(request.message) > 10000:
        raise HTTPException(status_code=400, detail="Message too long (max 10000 characters)")

    session_id = request.session_id or str(uuid.uuid4())

    # 1. Setup API Interface
    api_ui = APIInterface(session_id)
    set_ui(api_ui)

    # 2. Get history from DB
    logger = SessionLogger(session_id)
    history = logger.get_message_history()

    config = {"configurable": {"thread_id": session_id}}
    harness_metadata = {
        "context_budget": 10, "iteration_count": 0, "session_id": session_id,
        "permissions": "execute", "context_summary": "", "incognito": False
    }

    # 3. Stream Events
    async def event_generator():
        # Start the graph in a task
        input_data = {"messages": [HumanMessage(content=request.message)], **harness_metadata}
        if history:
            input_data = {"messages": [HumanMessage(content=request.message)]} # Resume context from DB

        task = asyncio.create_task(harness.ainvoke(input_data, config=config))

        while not task.done() or not api_ui.events.empty():
            try:
                # Wait for an event with timeout to check task status
                event = await asyncio.wait_for(api_ui.events.get(), timeout=0.1)
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                continue

        # Final result
        final_state = await task
        last_msg = final_state["messages"][-1]
        yield f"data: {json.dumps({'type': 'final_response', 'content': last_msg.content})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/approve/{approval_id}")
async def approve(approval_id: str, approved: bool):
    if approval_id not in pending_approvals:
        raise HTTPException(status_code=404, detail="Approval request not found")

    future = pending_approvals[approval_id]
    if not future.done():
        future.set_result(approved)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
