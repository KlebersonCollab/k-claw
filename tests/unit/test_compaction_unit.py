"""Unit tests for core/compaction.py — context compaction."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from core.compaction import compact_context


class TestCompactContext:
    """Test context compaction."""

    def test_returns_empty_when_few_messages(self, clean_state):
        """When messages <= to_keep_count, should return empty dict."""
        import asyncio
        state = {**clean_state, "messages": [HumanMessage(content="Hello")]}
        result = asyncio.run(compact_context(state))
        assert result == {}

    def test_returns_empty_when_messages_at_boundary(self):
        """When messages == to_keep_count, should return empty dict."""
        import asyncio
        messages = [HumanMessage(content=f"msg{i}") for i in range(10)]
        state = {
            "messages": messages,
            "context_budget": 50,
            "max_iterations": 10,
            "iteration_count": 0,
            "session_id": "test-session",
            "permissions": "read",
            "context_summary": "",
            "incognito": False,
            "yolo": False,
        }
        result = asyncio.run(compact_context(state))
        assert result == {}

    @patch("core.compaction.get_model")
    @patch("core.compaction.SessionLogger")
    @patch("core.compaction.emit_event")
    def test_compacts_when_many_messages(self, mock_emit, mock_logger, mock_get_model):
        """When messages > to_keep_count, should compact."""
        import asyncio

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "State memo summary"
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_get_model.return_value = mock_model

        messages = [HumanMessage(content=f"msg{i}") for i in range(15)]
        state = {
            "messages": messages,
            "context_budget": 50,
            "max_iterations": 10,
            "iteration_count": 0,
            "session_id": "test-session",
            "permissions": "read",
            "context_summary": "",
            "incognito": False,
            "yolo": False,
        }

        result = asyncio.run(compact_context(state))

        assert "messages" in result
        assert "context_summary" in result
        assert result["context_summary"] == "State memo summary"
        mock_model.ainvoke.assert_called_once()

    @patch("core.compaction.get_model")
    @patch("core.compaction.SessionLogger")
    @patch("core.compaction.emit_event")
    def test_compaction_creates_long_term_memory(self, mock_emit, mock_logger, mock_get_model):
        """Compaction should create a long-term memory entry."""
        import asyncio

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "State memo"
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_get_model.return_value = mock_model

        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        messages = [HumanMessage(content=f"msg{i}") for i in range(15)]
        state = {
            "messages": messages,
            "context_budget": 50,
            "max_iterations": 10,
            "iteration_count": 0,
            "session_id": "test-session",
            "permissions": "read",
            "context_summary": "",
            "incognito": False,
            "yolo": False,
        }

        asyncio.run(compact_context(state))
        mock_logger_instance.create_long_term_memory.assert_called_once()

    @patch("core.compaction.get_model")
    @patch("core.compaction.SessionLogger")
    @patch("core.compaction.emit_event")
    def test_compaction_emits_events(self, mock_emit, mock_logger, mock_get_model):
        """Compaction should emit start and end events."""
        import asyncio

        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "State memo"
        mock_model.ainvoke = AsyncMock(return_value=mock_response)
        mock_get_model.return_value = mock_model

        messages = [HumanMessage(content=f"msg{i}") for i in range(15)]
        state = {
            "messages": messages,
            "context_budget": 50,
            "max_iterations": 10,
            "iteration_count": 0,
            "session_id": "test-session",
            "permissions": "read",
            "context_summary": "",
            "incognito": False,
            "yolo": False,
        }

        asyncio.run(compact_context(state))
        assert mock_emit.call_count == 2
