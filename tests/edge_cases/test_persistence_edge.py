"""Edge case tests for infra/persistence.py."""

import os
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from infra.persistence import SessionLogger


class TestSessionLoggerEdgeCases:
    """Edge cases for SessionLogger."""

    def test_very_long_content(self, temp_dir):
        """Log messages with very long content."""
        db_path = os.path.join(temp_dir, "test_long.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from infra.persistence_db import Base, init_db, setup_engine_events

        engine = create_engine(f"sqlite:///{db_path}")
        setup_engine_events(engine)
        with patch("infra.persistence_db.engine", engine):
            init_db()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        with patch("infra.persistence.SessionLocal", SessionLocal):
            with patch("infra.persistence.engine", engine):
                logger = SessionLogger("long-content-test")
                long_content = "A" * 100000
                logger.log_messages([HumanMessage(content=long_content)])

                history = logger.get_message_history()
                assert len(history) == 1

    def test_unicode_content(self, temp_dir):
        """Log messages with unicode content."""
        db_path = os.path.join(temp_dir, "test_unicode.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from infra.persistence_db import Base, init_db, setup_engine_events

        engine = create_engine(f"sqlite:///{db_path}")
        setup_engine_events(engine)
        with patch("infra.persistence_db.engine", engine):
            init_db()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        with patch("infra.persistence.SessionLocal", SessionLocal):
            with patch("infra.persistence.engine", engine):
                logger = SessionLogger("unicode-test")
                logger.log_messages([
                    HumanMessage(content="你好世界"),
                    AIMessage(content="مرحبا بالعالم"),
                    HumanMessage(content="🎉🚀💻"),
                ])

                history = logger.get_message_history()
                assert len(history) == 3

    def test_concurrent_sessions(self, temp_dir):
        """Multiple sessions should not interfere."""
        db_path = os.path.join(temp_dir, "test_concurrent.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from infra.persistence_db import Base, init_db, setup_engine_events

        engine = create_engine(f"sqlite:///{db_path}")
        setup_engine_events(engine)
        with patch("infra.persistence_db.engine", engine):
            init_db()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        with patch("infra.persistence.SessionLocal", SessionLocal):
            with patch("infra.persistence.engine", engine):
                logger1 = SessionLogger("session-1")
                logger2 = SessionLogger("session-2")

                logger1.log_messages([HumanMessage(content="Session 1 message")])
                logger2.log_messages([HumanMessage(content="Session 2 message")])

                history1 = logger1.get_message_history()
                history2 = logger2.get_message_history()

                assert len(history1) == 1
                assert len(history2) == 1
                assert "Session 1" in history1[0].content
                assert "Session 2" in history2[0].content

    def test_empty_event_data(self, temp_dir):
        """Log event with empty data."""
        db_path = os.path.join(temp_dir, "test_empty_event.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from infra.persistence_db import Base, init_db, setup_engine_events

        engine = create_engine(f"sqlite:///{db_path}")
        setup_engine_events(engine)
        with patch("infra.persistence_db.engine", engine):
            init_db()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        with patch("infra.persistence.SessionLocal", SessionLocal):
            with patch("infra.persistence.engine", engine):
                logger = SessionLogger("empty-event-test")
                logger.log_event("empty_event", {})
                events = logger.replay()
                assert len(events) == 1

    def test_search_with_special_fts5_chars(self, temp_dir):
        """Search with special FTS5 characters."""
        db_path = os.path.join(temp_dir, "test_fts5.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from infra.persistence_db import Base, init_db, setup_engine_events

        engine = create_engine(f"sqlite:///{db_path}")
        setup_engine_events(engine)
        with patch("infra.persistence_db.engine", engine):
            init_db()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        with patch("infra.persistence.SessionLocal", SessionLocal):
            with patch("infra.persistence.engine", engine):
                logger = SessionLogger("fts5-test")
                # Should not crash with special characters
                results = logger.search_messages('test "quoted" OR something')
                assert isinstance(results, list)

    def test_message_with_tool_calls(self, temp_dir):
        """Log AIMessage with tool_calls."""
        db_path = os.path.join(temp_dir, "test_tool_calls.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from infra.persistence_db import Base, init_db, setup_engine_events

        engine = create_engine(f"sqlite:///{db_path}")
        setup_engine_events(engine)
        with patch("infra.persistence_db.engine", engine):
            init_db()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        with patch("infra.persistence.SessionLocal", SessionLocal):
            with patch("infra.persistence.engine", engine):
                logger = SessionLogger("tool-calls-test")
                msg = AIMessage(
                    content="",
                    tool_calls=[{
                        "name": "read_file",
                        "args": {"path": "test.txt"},
                        "id": "call_1"
                    }]
                )
                logger.log_messages([msg])

                history = logger.get_message_history()
                assert len(history) == 1

    def test_session_with_many_messages(self, temp_dir):
        """Session with many messages."""
        db_path = os.path.join(temp_dir, "test_many.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from infra.persistence_db import Base, init_db, setup_engine_events

        engine = create_engine(f"sqlite:///{db_path}")
        setup_engine_events(engine)
        with patch("infra.persistence_db.engine", engine):
            init_db()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        with patch("infra.persistence.SessionLocal", SessionLocal):
            with patch("infra.persistence.engine", engine):
                logger = SessionLogger("many-msgs-test")
                messages = [
                    HumanMessage(content=f"Message {i}" if i % 2 == 0 else f"Response {i}")
                    for i in range(100)
                ]
                logger.log_messages(messages)

                history = logger.get_message_history()
                assert len(history) == 100
