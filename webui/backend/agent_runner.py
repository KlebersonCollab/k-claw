"""Agent runner for executing missions in workspaces."""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional, List, Dict

from models import LogEntry
from workspace_manager import WORKSPACES_DIR


# Active WebSocket connections per workspace
_active_connections: Dict[str, List[Callable]] = {}


def register_log_callback(workspace_id: str, callback: Callable) -> None:
    """Register a callback for log messages.

    Args:
        workspace_id: The workspace identifier.
        callback: Function to call with log messages.
    """
    if workspace_id not in _active_connections:
        _active_connections[workspace_id] = []
    _active_connections[workspace_id].append(callback)


def unregister_log_callback(workspace_id: str, callback: Callable) -> None:
    """Unregister a log callback.

    Args:
        workspace_id: The workspace identifier.
        callback: Function to remove.
    """
    if workspace_id in _active_connections:
        _active_connections[workspace_id] = [
            cb for cb in _active_connections[workspace_id] if cb != callback
        ]


async def emit_log(workspace_id: str, level: str, message: str, source: str = "system") -> None:
    """Emit a log message to all registered callbacks.

    Args:
        workspace_id: The workspace identifier.
        level: Log level (INFO, WARNING, ERROR).
        message: Log message.
        source: Source of the log.
    """
    log_entry = LogEntry(
        timestamp=datetime.now().isoformat(),
        level=level,
        message=message,
        source=source,
    )

    if workspace_id in _active_connections:
        for callback in _active_connections[workspace_id]:
            try:
                await callback(log_entry.model_dump())
            except Exception:
                pass


async def run_mission(workspace_id: str, mission: str, agent_id: str = "coder") -> str:
    """Run a mission in a workspace.

    This is a simplified implementation that logs the mission execution.
    In a full implementation, this would integrate with the actual agent system.

    Args:
        workspace_id: The workspace identifier.
        mission: The mission description.
        agent_id: The agent to execute the mission.

    Returns:
        Result message.

    Raises:
        FileNotFoundError: If workspace doesn't exist.
    """
    workspace_path = WORKSPACES_DIR / workspace_id

    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace '{workspace_id}' not found")

    await emit_log(workspace_id, "INFO", f"🚀 Iniciando missão: {mission[:50]}...", "orchestrator")
    await emit_log(workspace_id, "INFO", f"📁 Workspace: {workspace_id}", "orchestrator")
    await emit_log(workspace_id, "INFO", f"🤖 Agente: {agent_id}", "orchestrator")

    # Load AGENTS.md if exists
    agents_md = workspace_path / "AGENTS.md"
    if agents_md.exists():
        await emit_log(workspace_id, "INFO", "📋 Carregando diretrizes do workspace...", "orchestrator")
        content = agents_md.read_text()
        await emit_log(workspace_id, "DEBUG", f"AGENTS.md carregado ({len(content)} chars)", "orchestrator")

    # Simulate agent execution steps
    await emit_log(workspace_id, "INFO", f"🔍 Analisando missão...", agent_id)
    await asyncio.sleep(0.5)

    await emit_log(workspace_id, "INFO", f"📝 Planejando implementação...", agent_id)
    await asyncio.sleep(0.5)

    await emit_log(workspace_id, "INFO", f"⚡ Executando tarefa...", agent_id)
    await asyncio.sleep(1)

    # In a real implementation, this would call the actual agent system
    # For now, we create a placeholder file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = workspace_path / "src" / f"output_{timestamp}.md"
    output_file.write_text(
        f"# Mission Output\n\n"
        f"**Mission:** {mission}\n"
        f"**Agent:** {agent_id}\n"
        f"**Timestamp:** {datetime.now().isoformat()}\n\n"
        f"## Result\n\n"
        f"Mission completed successfully.\n"
    )

    await emit_log(workspace_id, "INFO", f"✅ Missão concluída! Arquivo criado: {output_file.name}", "orchestrator")

    return f"Mission completed. Output saved to {output_file.name}"


def get_historical_logs(workspace_id: str, limit: int = 100) -> List[dict]:
    """Get historical logs for a workspace.

    In a real implementation, this would read from a log file or database.
    For now, returns an empty list.

    Args:
        workspace_id: The workspace identifier.
        limit: Maximum number of logs to return.

    Returns:
        List of log entries.
    """
    # TODO: Implement persistent log storage
    return []
