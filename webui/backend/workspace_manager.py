"""Workspace manager for creating, listing, and managing workspaces."""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from models import WorkspaceCreate, WorkspaceResponse, FileEntry


# Base directory for all workspaces
WORKSPACES_DIR = Path("workspaces")
TEMPLATES_DIR = Path(__file__).parent / "templates"


def ensure_workspaces_dir() -> None:
    """Ensure the workspaces directory exists."""
    WORKSPACES_DIR.mkdir(exist_ok=True)


def get_workspace_path(workspace_id: str) -> Path:
    """Get the path to a workspace directory."""
    return WORKSPACES_DIR / workspace_id


def workspace_exists(workspace_id: str) -> bool:
    """Check if a workspace exists."""
    return get_workspace_path(workspace_id).exists()


def create_workspace(data: WorkspaceCreate) -> WorkspaceResponse:
    """Create a new workspace with template files.

    Args:
        data: Workspace creation data.

    Returns:
        WorkspaceResponse with created workspace info.

    Raises:
        ValueError: If workspace already exists.
    """
    ensure_workspaces_dir()

    workspace_id = data.name.lower().strip()
    workspace_path = get_workspace_path(workspace_id)

    if workspace_path.exists():
        raise ValueError(f"Workspace '{workspace_id}' already exists")

    # Create directory structure
    workspace_path.mkdir(parents=True)
    (workspace_path / "src").mkdir()
    (workspace_path / "tests").mkdir()
    (workspace_path / "tests" / "unit").mkdir()
    (workspace_path / "tests" / "integration").mkdir()
    (workspace_path / "tests" / "e2e").mkdir()
    (workspace_path / "tests" / "edge_cases").mkdir()

    # Generate AGENTS.md from template
    agents_template = TEMPLATES_DIR / "agents_template.md"
    if agents_template.exists():
        content = agents_template.read_text()
        content = content.replace("{{WORKSPACE_NAME}}", data.name)
        content = content.replace("{{CREATED_AT}}", datetime.now().isoformat())
        (workspace_path / "AGENTS.md").write_text(content)
    else:
        # Fallback minimal AGENTS.md
        (workspace_path / "AGENTS.md").write_text(
            f"# 🤖 Agent Catalog - {data.name}\n\n"
            f"Created: {datetime.now().isoformat()}\n\n"
            f"## Diretrizes\n"
            f"- Framework: (a definir)\n"
            f"- Testes: pytest + coverage >= 90%\n"
        )

    # Create README.md for the workspace
    (workspace_path / "README.md").write_text(
        f"# {data.name}\n\n"
        f"{data.description}\n\n"
        f"## Estrutura\n"
        f"- `src/` - Código fonte\n"
        f"- `tests/` - Testes (unit, integration, e2e, edge_cases)\n"
    )

    # Create pyproject.toml stub
    (workspace_path / "pyproject.toml").write_text(
        f"[project]\n"
        f"name = \"{data.name}\"\n"
        f"version = \"0.1.0\"\n"
        f"description = \"{data.description}\"\n"
        f"requires-python = \">=3.11\"\n"
    )

    return WorkspaceResponse(
        id=workspace_id,
        name=data.name,
        description=data.description or "",
        created_at=datetime.now().isoformat(),
        file_count=4,
        agents_md_exists=True,
    )


def list_workspaces() -> List[WorkspaceResponse]:
    """List all existing workspaces.

    Returns:
        List of WorkspaceResponse for each workspace.
    """
    ensure_workspaces_dir()

    workspaces = []
    for item in sorted(WORKSPACES_DIR.iterdir()):
        if item.is_dir():
            agents_md = item / "AGENTS.md"
            file_count = sum(1 for _ in item.rglob("*") if _.is_file())

            # Get creation time from directory stat
            created = datetime.fromtimestamp(item.stat().st_ctime).isoformat()

            workspaces.append(WorkspaceResponse(
                id=item.name,
                name=item.name,
                description="",
                created_at=created,
                file_count=file_count,
                agents_md_exists=agents_md.exists(),
            ))

    return workspaces


def get_workspace(workspace_id: str) -> WorkspaceResponse:
    """Get details of a specific workspace.

    Args:
        workspace_id: The workspace identifier.

    Returns:
        WorkspaceResponse with workspace info.

    Raises:
        FileNotFoundError: If workspace doesn't exist.
    """
    workspace_path = get_workspace_path(workspace_id)

    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace '{workspace_id}' not found")

    agents_md = workspace_path / "AGENTS.md"
    file_count = sum(1 for _ in workspace_path.rglob("*") if _.is_file())
    created = datetime.fromtimestamp(workspace_path.stat().st_ctime).isoformat()

    return WorkspaceResponse(
        id=workspace_id,
        name=workspace_id,
        description="",
        created_at=created,
        file_count=file_count,
        agents_md_exists=agents_md.exists(),
    )


def delete_workspace(workspace_id: str) -> bool:
    """Delete a workspace and all its contents.

    Args:
        workspace_id: The workspace identifier.

    Returns:
        True if deleted successfully.

    Raises:
        FileNotFoundError: If workspace doesn't exist.
    """
    workspace_path = get_workspace_path(workspace_id)

    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace '{workspace_id}' not found")

    shutil.rmtree(workspace_path)
    return True


def list_workspace_files(workspace_id: str, subpath: str = "") -> List[FileEntry]:
    """List files in a workspace.

    Args:
        workspace_id: The workspace identifier.
        subpath: Optional subdirectory path.

    Returns:
        List of FileEntry for each file/directory.

    Raises:
        FileNotFoundError: If workspace doesn't exist.
    """
    workspace_path = get_workspace_path(workspace_id)

    if not workspace_path.exists():
        raise FileNotFoundError(f"Workspace '{workspace_id}' not found")

    target_path = workspace_path / subpath if subpath else workspace_path

    if not target_path.exists():
        return []

    files = []
    for item in sorted(target_path.iterdir()):
        # Skip hidden files and __pycache__
        if item.name.startswith(".") or item.name == "__pycache__":
            continue

        files.append(FileEntry(
            name=item.name,
            path=str(item.relative_to(workspace_path)),
            is_dir=item.is_dir(),
            size=item.stat().st_size if item.is_file() else 0,
        ))

    return files
