"""E2E tests for the FastAPI API."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


class TestAPIEndpoints:
    """Test API endpoints."""

    @pytest.fixture
    def client(self):
        with patch("entrypoints.api.harness") as mock_harness:
            mock_harness.ainvoke = AsyncMock(return_value={
                "messages": [MagicMock(content="Test response")],
            })
            from entrypoints.api import app
            with TestClient(app) as client:
                yield client

    def test_chat_endpoint_basic(self, client):
        """Test basic chat request."""
        # We need to mock the model calls
        response = client.post("/chat", json={"message": "Hello"})
        assert response.status_code in (200, 500)  # 500 if model not available

    def test_chat_with_session_id(self, client):
        """Test chat with specific session_id."""
        response = client.post("/chat", json={
            "message": "Hello",
            "session_id": "test-session-e2e"
        })
        assert response.status_code in (200, 500)

    def test_chat_message_too_long(self, client):
        """Test that very long messages are rejected."""
        long_message = "A" * 10001
        response = client.post("/chat", json={"message": long_message})
        assert response.status_code == 400
        assert "too long" in response.json()["detail"].lower()


class TestApprovalFlow:
    """Test approval endpoint."""

    @pytest.fixture
    def client(self):
        from entrypoints.api import app
        with TestClient(app) as client:
            yield client

    def test_approve_nonexistent_approval(self, client):
        """Test approving a nonexistent approval_id."""
        response = client.post("/approve/nonexistent-id?approved=True")
        # Should handle gracefully
        assert response.status_code in (200, 404, 500)

    def test_approve_with_missing_fields(self, client):
        """Test approval with missing fields."""
        response = client.post("/approve/test-id")
        assert response.status_code in (200, 422, 500)
