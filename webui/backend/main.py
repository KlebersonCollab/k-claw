"""FastAPI main application for WebUI."""

import json
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from models import WorkspaceCreate, WorkspaceResponse, MissionRequest, LogEntry
from workspace_manager import (
    create_workspace,
    list_workspaces,
    get_workspace,
    delete_workspace,
    list_workspace_files,
    workspace_exists,
)
from agent_runner import run_mission, register_log_callback, unregister_log_callback, emit_log

# Create FastAPI app
app = FastAPI(
    title="K-Claw WebUI",
    description="Web interface for managing K-Claw workspaces and agents",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
websocket_connections: dict[str, List[WebSocket]] = {}


# ==================== Workspace Endpoints ====================

@app.get("/api/workspaces", response_model=List[WorkspaceResponse])
async def api_list_workspaces():
    """List all workspaces."""
    return list_workspaces()


@app.post("/api/workspaces", response_model=WorkspaceResponse)
async def api_create_workspace(data: WorkspaceCreate):
    """Create a new workspace."""
    try:
        return create_workspace(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/workspaces/{workspace_id}", response_model=WorkspaceResponse)
async def api_get_workspace(workspace_id: str):
    """Get workspace details."""
    try:
        return get_workspace(workspace_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found")


@app.delete("/api/workspaces/{workspace_id}")
async def api_delete_workspace(workspace_id: str):
    """Delete a workspace."""
    try:
        delete_workspace(workspace_id)
        return {"message": f"Workspace '{workspace_id}' deleted"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found")


@app.get("/api/workspaces/{workspace_id}/files")
async def api_list_workspace_files(workspace_id: str, path: str = ""):
    """List files in a workspace."""
    try:
        return list_workspace_files(workspace_id, path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found")


# ==================== Mission Endpoints ====================

@app.post("/api/workspaces/{workspace_id}/mission")
async def api_run_mission(workspace_id: str, data: MissionRequest):
    """Run a mission in a workspace."""
    if not workspace_exists(workspace_id):
        raise HTTPException(status_code=404, detail=f"Workspace '{workspace_id}' not found")

    # Start mission in background
    import asyncio
    asyncio.create_task(run_mission(workspace_id, data.mission, data.agent_id))

    return {"message": "Mission started", "workspace_id": workspace_id}


# ==================== Logs Endpoints ====================

@app.get("/api/workspaces/{workspace_id}/logs")
async def api_get_logs(workspace_id: str, limit: int = 100):
    """Get historical logs for a workspace."""
    from agent_runner import get_historical_logs
    return get_historical_logs(workspace_id, limit)


# ==================== WebSocket Endpoint ====================

@app.websocket("/ws/{workspace_id}")
async def websocket_endpoint(websocket: WebSocket, workspace_id: str):
    """WebSocket endpoint for real-time logs."""
    await websocket.accept()

    if workspace_id not in websocket_connections:
        websocket_connections[workspace_id] = []
    websocket_connections[workspace_id].append(websocket)

    try:
        # Send connection confirmation
        await websocket.send_json({
            "timestamp": __import__("datetime").datetime.now().isoformat(),
            "level": "INFO",
            "message": f"Connected to workspace '{workspace_id}'",
            "source": "system",
        })

        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back for now, could handle commands
            await websocket.send_json({
                "timestamp": __import__("datetime").datetime.now().isoformat(),
                "level": "INFO",
                "message": f"Received: {data}",
                "source": "system",
            })

    except WebSocketDisconnect:
        if workspace_id in websocket_connections:
            websocket_connections[workspace_id].remove(websocket)


# ==================== Static Files (Frontend) ====================

# Serve frontend build if exists
frontend_build = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_build.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_build / "assets")), name="assets")

    @app.get("/")
    async def serve_frontend():
        index_file = frontend_build / "index.html"
        if index_file.exists():
            return HTMLResponse(content=index_file.read_text())
        return {"message": "K-Claw WebUI API - Frontend not built yet"}


# ==================== Health Check ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
