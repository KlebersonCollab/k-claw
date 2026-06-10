"""Shared fixtures for WebUI backend tests."""

import pytest
import shutil
from pathlib import Path

from workspace_manager import WORKSPACES_DIR


@pytest.fixture
def clean_workspaces():
    """Provide a clean workspaces directory for each test."""
    # Setup: ensure clean state
    if WORKSPACES_DIR.exists():
        shutil.rmtree(WORKSPACES_DIR)
    WORKSPACES_DIR.mkdir(exist_ok=True)

    yield WORKSPACES_DIR

    # Teardown: clean up
    if WORKSPACES_DIR.exists():
        shutil.rmtree(WORKSPACES_DIR)


@pytest.fixture
def sample_workspace(clean_workspaces):
    """Create a sample workspace for testing."""
    from models import WorkspaceCreate
    from workspace_manager import create_workspace

    data = WorkspaceCreate(name="test-project", description="A test workspace")
    result = create_workspace(data)
    return result


@pytest.fixture
def multiple_workspaces(clean_workspaces):
    """Create multiple workspaces for testing."""
    from models import WorkspaceCreate
    from workspace_manager import create_workspace

    workspaces = []
    for name, desc in [
        ("project-alpha", "First test workspace"),
        ("project-beta", "Second test workspace"),
        ("project-gamma", "Third test workspace"),
    ]:
        data = WorkspaceCreate(name=name, description=desc)
        workspaces.append(create_workspace(data))
    return workspaces


@pytest.fixture
def mock_log_collector():
    """Collect log entries for verification."""
    logs = []

    async def collector(log_entry):
        logs.append(log_entry)

    return {"logs": logs, "collector": collector}
