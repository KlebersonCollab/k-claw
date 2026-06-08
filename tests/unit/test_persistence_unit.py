"""Unit tests for infra/persistence.py — session logging and message management."""

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from infra.persistence import SessionLogger


class TestSessionLoggerInit:
    """Test SessionLogger initialization."""

    def test_creates_session_on_init(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = None

                logger = SessionLogger("test-session")
                # Should have tried to create a session
                mock_db.add.assert_called_once()
                mock_db.commit.assert_called_once()

    def test_reuses_existing_session(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

                logger = SessionLogger("existing-session")
                # Should not add a new session
                mock_db.add.assert_not_called()


class TestLogMessages:
    """Test message logging."""

    def test_logs_human_message(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

                logger = SessionLogger("test-session")
                logger.log_messages([HumanMessage(content="Hello")])
                mock_db.add.assert_called()
                mock_db.commit.assert_called()

    def test_logs_ai_message(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

                logger = SessionLogger("test-session")
                logger.log_messages([AIMessage(content="Response")])
                mock_db.add.assert_called()

    def test_logs_tool_message(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

                logger = SessionLogger("test-session")
                logger.log_messages([ToolMessage(content="result", tool_call_id="call_1")])
                mock_db.add.assert_called()

    def test_logs_multiple_messages(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

                logger = SessionLogger("test-session")
                messages = [
                    HumanMessage(content="Hello"),
                    AIMessage(content="Hi"),
                    HumanMessage(content="Bye"),
                ]
                logger.log_messages(messages)
                assert mock_db.add.call_count == 3


class TestLogEvent:
    """Test event logging."""

    def test_logs_event(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

                logger = SessionLogger("test-session")
                logger.log_event("test_event", {"key": "value"})
                mock_db.add.assert_called()
                mock_db.commit.assert_called()


class TestGetMessageHistory:
    """Test message history retrieval."""

    def test_returns_empty_for_new_session(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()
                mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

                logger = SessionLogger("test-session")
                history = logger.get_message_history()
                assert history == []

    def test_returns_messages(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

                mock_msg = MagicMock()
                mock_msg.role = "human"
                mock_msg.content = "Hello"
                mock_msg.additional_kwargs = "{}"
                mock_msg.usage_metadata = None
                mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_msg]

                logger = SessionLogger("test-session")
                history = logger.get_message_history()
                assert len(history) == 1
                assert isinstance(history[0], HumanMessage)


class TestSearchMessages:
    """Test FTS5 message search."""

    def test_search_returns_results(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

                mock_result = MagicMock()
                mock_result.__getitem__ = lambda self, i: ["content", "session", "human", 1][i]
                mock_db.execute.return_value.fetchall.return_value = [mock_result]

                logger = SessionLogger("test-session")
                results = logger.search_messages("test query")
                assert len(results) > 0

    def test_search_empty_query(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

                logger = SessionLogger("test-session")
                results = logger.search_messages("")
                assert results == []

    def test_search_with_special_chars(self):
        with patch("infra.persistence.init_db"):
            with patch("infra.persistence.SessionLocal") as mock_session_local:
                mock_db = MagicMock()
                mock_session_local.return_value.__enter__ = MagicMock(return_value=mock_db)
                mock_session_local.return_value.__exit__ = MagicMock(return_value=False)
                mock_db.query.return_value.filter.return_value.first.return_value = MagicMock()

                mock_db.execute.return_value.fetchall.return_value = []

                logger = SessionLogger("test-session")
                # Should not crash with special FTS5 characters
                results = logger.search_messages('test" OR "1"="1')
                assert isinstance(results, list)
