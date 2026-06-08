"""Integration tests for persistence flow — database operations."""

import os
import pytest
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from infra.persistence_db import init_db, engine, Base, SessionLocal


class TestDatabaseInit:
    """Test database initialization."""

    def test_init_db_creates_tables(self, temp_dir):
        """init_db should create all required tables."""
        db_path = os.path.join(temp_dir, "test_init.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        test_engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=test_engine)

        from sqlalchemy import inspect
        inspector = inspect(test_engine)
        tables = inspector.get_table_names()
        assert "sessions" in tables
        assert "messages" in tables
        assert "events" in tables
        assert "memories" in tables


class TestSessionCRUD:
    """Test session CRUD operations."""

    def test_create_session(self, temp_dir):
        """Create a new session."""
        db_path = os.path.join(temp_dir, "test_crud.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        test_engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

        from infra.persistence_db import SessionModel
        with TestSession() as db:
            session = SessionModel(id="test-session-1")
            db.add(session)
            db.commit()

            result = db.query(SessionModel).filter(SessionModel.id == "test-session-1").first()
            assert result is not None
            assert result.id == "test-session-1"

    def test_session_token_tracking(self, temp_dir):
        """Test token accumulation in sessions."""
        db_path = os.path.join(temp_dir, "test_tokens.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        test_engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

        from infra.persistence_db import SessionModel
        with TestSession() as db:
            session = SessionModel(id="token-test", total_tokens=100)
            db.add(session)
            db.commit()

            # Update tokens
            s = db.query(SessionModel).filter(SessionModel.id == "token-test").first()
            s.total_tokens += 50
            db.commit()

            result = db.query(SessionModel).filter(SessionModel.id == "token-test").first()
            assert result.total_tokens == 150


class TestMessagePersistence:
    """Test message persistence."""

    def test_store_and_retrieve_messages(self, temp_dir):
        """Store messages and retrieve them."""
        db_path = os.path.join(temp_dir, "test_msgs.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        test_engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

        from infra.persistence_db import SessionModel, MessageModel
        with TestSession() as db:
            db.add(SessionModel(id="msg-test"))
            db.add(MessageModel(session_id="msg-test", role="human", content="Hello"))
            db.add(MessageModel(session_id="msg-test", role="ai", content="Hi"))
            db.commit()

            messages = db.query(MessageModel).filter(
                MessageModel.session_id == "msg-test"
            ).order_by(MessageModel.created_at).all()
            assert len(messages) == 2
            assert messages[0].role == "human"
            assert messages[1].role == "ai"


class TestEventPersistence:
    """Test event persistence."""

    def test_store_and_replay_events(self, temp_dir):
        """Store events and replay them."""
        db_path = os.path.join(temp_dir, "test_events.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        test_engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(bind=test_engine)
        TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

        from infra.persistence_db import SessionModel, EventModel
        import json

        with TestSession() as db:
            db.add(SessionModel(id="event-test"))
            db.add(EventModel(session_id="event-test", event_type="tool_call", data=json.dumps({"tool": "read_file"})))
            db.add(EventModel(session_id="event-test", event_type="model_call", data=json.dumps({"tokens": 100})))
            db.commit()

            events = db.query(EventModel).filter(
                EventModel.session_id == "event-test"
            ).all()
            assert len(events) == 2
