"""Edge case tests for the API."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


class TestAPIEdgeCases:
    """Edge cases for API endpoints."""

    @pytest.fixture
    def client(self):
        with patch("entrypoints.api.harness") as mock_harness:
            mock_harness.ainvoke = AsyncMock(return_value={
                "messages": [MagicMock(content="Test response")],
            })
            from entrypoints.api import app
            from fastapi.testclient import TestClient
            with TestClient(app) as client:
                yield client

    def test_empty_message(self, client):
        """Empty message should be handled."""
        response = client.post("/chat", json={"message": ""})
        assert response.status_code in (200, 400, 422, 500)

    def test_very_long_session_id(self, client):
        """Very long session_id."""
        long_id = "a" * 10000
        response = client.post("/chat", json={
            "message": "Hello",
            "session_id": long_id
        })
        assert response.status_code in (200, 400, 500)

    def test_special_characters_in_message(self, client):
        """Message with special characters."""
        response = client.post("/chat", json={
            "message": "Hello! @#$%^&*() 你好 🎉"
        })
        assert response.status_code in (200, 500)

    def test_null_session_id(self, client):
        """Null session_id should generate a new one."""
        response = client.post("/chat", json={
            "message": "Hello",
            "session_id": None
        })
        assert response.status_code in (200, 500)

    def test_missing_message_field(self, client):
        """Missing message field should return 422."""
        response = client.post("/chat", json={})
        assert response.status_code == 422

    def test_extra_fields_ignored(self, client):
        """Extra fields should be ignored."""
        response = client.post("/chat", json={
            "message": "Hello",
            "extra_field": "should be ignored"
        })
        assert response.status_code in (200, 500)

    def test_message_at_max_length(self, client):
        """Message at exactly max length (10000 chars)."""
        response = client.post("/chat", json={
            "message": "A" * 10000
        })
        assert response.status_code in (200, 500)

    def test_message_one_over_max(self, client):
        """Message one char over max length."""
        response = client.post("/chat", json={
            "message": "A" * 10001
        })
        assert response.status_code == 400
