"""End-to-end tests for workspace lifecycle."""

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


class TestWorkspaceLifecycle:
    """E2E tests for complete workspace lifecycle."""

    def test_full_workspace_lifecycle(self, client):
        """Test complete lifecycle: create → list → get → delete."""
        # 1. Initially empty
        response = client.get("/api/workspaces")
        assert response.json() == []

        # 2. Create workspace
        response = client.post(
            "/api/workspaces",
            json={"name": "lifecycle-test", "description": "E2E test workspace"},
        )
        assert response.status_code == 200
        created = response.json()
        assert created["id"] == "lifecycle-test"
        assert created["agents_md_exists"] is True

        # 3. List shows the workspace
        response = client.get("/api/workspaces")
        workspaces = response.json()
        assert len(workspaces) == 1
        assert workspaces[0]["id"] == "lifecycle-test"

        # 4. Get workspace details
        response = client.get("/api/workspaces/lifecycle-test")
        assert response.status_code == 200
        details = response.json()
        assert details["id"] == "lifecycle-test"
        assert details["file_count"] > 0

        # 5. List files
        response = client.get("/api/workspaces/lifecycle-test/files")
        assert response.status_code == 200
        files = response.json()
        names = [f["name"] for f in files]
        assert "AGENTS.md" in names
        assert "README.md" in names
        assert "src" in names
        assert "tests" in names

        # 6. Delete workspace
        response = client.delete("/api/workspaces/lifecycle-test")
        assert response.status_code == 200

        # 7. Verify deletion
        response = client.get("/api/workspaces/lifecycle-test")
        assert response.status_code == 404

        # 8. List is empty again
        response = client.get("/api/workspaces")
        assert response.json() == []

    def test_multiple_workspaces_isolation(self, client):
        """Test that multiple workspaces are isolated."""
        # Create two workspaces
        client.post("/api/workspaces", json={"name": "project-a"})
        client.post("/api/workspaces", json={"name": "project-b"})

        # Both exist
        response = client.get("/api/workspaces")
        assert len(response.json()) == 2

        # Delete one
        client.delete("/api/workspaces/project-a")

        # Only one remains
        response = client.get("/api/workspaces")
        remaining = response.json()
        assert len(remaining) == 1
        assert remaining[0]["id"] == "project-b"

    def test_mission_execution_flow(self, client):
        """Test mission execution flow."""
        # Create workspace
        client.post(
            "/api/workspaces",
            json={"name": "mission-flow", "description": "Mission test"},
        )

        # Run mission
        response = client.post(
            "/api/workspaces/mission-flow/mission",
            json={"mission": "Create a calculator module", "agent_id": "coder"},
        )
        assert response.status_code == 200

        # Check files - src directory exists
        response = client.get("/api/workspaces/mission-flow/files?path=src")
        assert response.status_code == 200
        # Mission runs async, so we just verify the endpoint works
        assert isinstance(response.json(), list)

    def test_workspace_with_special_name_patterns(self, client):
        """Test workspaces with various valid name patterns."""
        valid_names = [
            "simple",
            "with-hyphens",
            "with_underscores",
            "mixed-name_123",
            "a",
            "a" * 100,
        ]

        for name in valid_names:
            response = client.post(
                "/api/workspaces",
                json={"name": name},
            )
            assert response.status_code == 200, f"Failed for name: {name}"

        # Verify all exist
        response = client.get("/api/workspaces")
        assert len(response.json()) == len(valid_names)

    def test_error_handling_nonexistent_resources(self, client):
        """Test error handling for nonexistent resources."""
        # Get nonexistent workspace
        response = client.get("/api/workspaces/does-not-exist")
        assert response.status_code == 404

        # Delete nonexistent workspace
        response = client.delete("/api/workspaces/does-not-exist")
        assert response.status_code == 404

        # List files of nonexistent workspace
        response = client.get("/api/workspaces/does-not-exist/files")
        assert response.status_code == 404

        # Run mission in nonexistent workspace
        response = client.post(
            "/api/workspaces/does-not-exist/mission",
            json={"mission": "Test"},
        )
        assert response.status_code == 404

    def test_workspace_persistence_across_requests(self, client):
        """Test that workspace data persists across requests."""
        # Create workspace
        client.post(
            "/api/workspaces",
            json={"name": "persistent", "description": "Should persist"},
        )

        # Multiple GETs should return same data
        for _ in range(3):
            response = client.get("/api/workspaces/persistent")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "persistent"
            assert data["agents_md_exists"] is True
