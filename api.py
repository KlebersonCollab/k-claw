import uuid
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from harness import harness
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Agent Harness API")

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    permissions: Optional[str] = "read" # read, write, execute

class ChatResponse(BaseModel):
    session_id: str
    response: str
    history_length: int

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    session_id = request.session_id or str(uuid.uuid4())

    # Initial state
    initial_state = {
        "messages": [HumanMessage(content=request.message)],
        "context_budget": 10, # Low for testing compaction
        "iteration_count": 0,
        "session_id": session_id,
        "permissions": request.permissions,
        "context_summary": ""
    }

    try:
        # Run the harness
        final_state = await harness.ainvoke(initial_state)

        # Get the last AI message
        last_msg = final_state["messages"][-1]

        return ChatResponse(
            session_id=session_id,
            response=last_msg.content,
            history_length=len(final_state["messages"])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
