"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient

from main import app
from workspace_manager import WORKSPACES_DIR


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_workspaces():
    """Clean up workspaces before each test."""
    import shutil

    if WORKSPACES_DIR.exists():
        shutil.rmtree(WORKSPACES_DIR)
    yield
    if WORKSPACES_DIR.exists():
        shutil.rmtree(WORKSPACES_DIR)


class TestWorkspaceEndpoints:
    """Tests for workspace API endpoints."""

    def test_list_workspaces_empty(self, client):
        """Test listing workspaces when none exist."""
        response = client.get("/api/workspaces")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_workspace(self, client):
        """Test creating a new workspace."""
        response = client.post(
            "/api/workspaces",
            json={"name": "test-api", "description": "Test workspace"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-api"
        assert data["name"] == "test-api"
        assert data["agents_md_exists"] is True

    def test_create_workspace_without_description(self, client):
        """Test creating workspace without description."""
        response = client.post(
            "/api/workspaces",
            json={"name": "no-desc"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "no-desc"

    def test_create_duplicate_workspace(self, client):
        """Test creating duplicate workspace returns error."""
        client.post("/api/workspaces", json={"name": "duplicate"})
        response = client.post("/api/workspaces", json={"name": "duplicate"})
        assert response.status_code == 400

    def test_create_workspace_invalid_name(self, client):
        """Test creating workspace with invalid name returns error."""
        response = client.post(
            "/api/workspaces",
            json={"name": "invalid name!"},
        )
        assert response.status_code == 422

    def test_get_workspace(self, client):
        """Test getting a specific workspace."""
        client.post("/api/workspaces", json={"name": "get-test"})
        response = client.get("/api/workspaces/get-test")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "get-test"

    def test_get_nonexistent_workspace(self, client):
        """Test getting nonexistent workspace returns 404."""
        response = client.get("/api/workspaces/nonexistent")
        assert response.status_code == 404

    def test_delete_workspace(self, client):
        """Test deleting a workspace."""
        client.post("/api/workspaces", json={"name": "delete-test"})
        response = client.delete("/api/workspaces/delete-test")
        assert response.status_code == 200

        # Verify it's gone
        response = client.get("/api/workspaces/delete-test")
        assert response.status_code == 404

    def test_delete_nonexistent_workspace(self, client):
        """Test deleting nonexistent workspace returns 404."""
        response = client.delete("/api/workspaces/nonexistent")
        assert response.status_code == 404

    def test_list_workspaces_after_creation(self, client):
        """Test listing workspaces after creating some."""
        for name in ["ws-1", "ws-2", "ws-3"]:
            client.post("/api/workspaces", json={"name": name})

        response = client.get("/api/workspaces")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


class TestFileEndpoints:
    """Tests for file API endpoints."""

    def test_list_workspace_files(self, client):
        """Test listing files in a workspace."""
        client.post("/api/workspaces", json={"name": "files-test"})
        response = client.get("/api/workspaces/files-test/files")
        assert response.status_code == 200
        data = response.json()
        names = [f["name"] for f in data]
        assert "AGENTS.md" in names
        assert "src" in names

    def test_list_files_nonexistent_workspace(self, client):
        """Test listing files of nonexistent workspace returns 404."""
        response = client.get("/api/workspaces/nonexistent/files")
        assert response.status_code == 404

    def test_list_files_in_subdirectory(self, client):
        """Test listing files in a subdirectory."""
        client.post("/api/workspaces", json={"name": "subdir-test"})
        response = client.get("/api/workspaces/subdir-test/files?path=src")
        assert response.status_code == 200
        data = response.json()
        # src should be empty
        assert data == []


class TestMissionEndpoints:
    """Tests for mission API endpoints."""

    def test_run_mission(self, client):
        """Test running a mission."""
        client.post("/api/workspaces", json={"name": "mission-test"})
        response = client.post(
            "/api/workspaces/mission-test/mission",
            json={"mission": "Create a REST API", "agent_id": "coder"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["workspace_id"] == "mission-test"

    def test_run_mission_nonexistent_workspace(self, client):
        """Test running mission in nonexistent workspace returns 404."""
        response = client.post(
            "/api/workspaces/nonexistent/mission",
            json={"mission": "Test mission"},
        )
        assert response.status_code == 404

    def test_run_mission_default_agent(self, client):
        """Test running mission with default agent."""
        client.post("/api/workspaces", json={"name": "default-agent"})
        response = client.post(
            "/api/workspaces/default-agent/mission",
            json={"mission": "Test mission"},
        )
        assert response.status_code == 200

    def test_run_mission_empty_mission(self, client):
        """Test running empty mission returns error."""
        client.post("/api/workspaces", json={"name": "empty-mission"})
        response = client.post(
            "/api/workspaces/empty-mission/mission",
            json={"mission": ""},
        )
        assert response.status_code == 422


class TestLogsEndpoints:
    """Tests for logs API endpoints."""

    def test_get_logs(self, client):
        """Test getting logs for a workspace."""
        client.post("/api/workspaces", json={"name": "logs-test"})
        response = client.get("/api/workspaces/logs-test/logs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_logs_with_limit(self, client):
        """Test getting logs with limit parameter."""
        client.post("/api/workspaces", json={"name": "logs-limit"})
        response = client.get("/api/workspaces/logs-limit/logs?limit=10")
        assert response.status_code == 200
