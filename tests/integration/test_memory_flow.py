"""Integration tests for memory flow — logging, search, layered retrieval."""

import os
import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage
from infra.persistence import SessionLogger


class TestMemoryLoggingFlow:
    """Test the complete memory logging flow."""

    def test_log_and_retrieve_messages(self, temp_dir):
        """Log messages and retrieve them."""
        db_path = os.path.join(temp_dir, "test_memory.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from infra.persistence_db import Base, init_db, setup_engine_events

        engine = create_engine(f"sqlite:///{db_path}")
        setup_engine_events(engine)
        with patch("infra.persistence_db.engine", engine):
            with patch("infra.persistence.engine", engine):
                init_db()
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

                with patch("infra.persistence_db.SessionLocal", SessionLocal):
                    with patch("infra.persistence.SessionLocal", SessionLocal):
                        logger = SessionLogger("memory-flow-test")
                        logger.log_messages([
                            HumanMessage(content="Hello"),
                            AIMessage(content="Hi there!"),
                        ])

                        history = logger.get_message_history()
                        assert len(history) == 2

    def test_log_event_and_replay(self, temp_dir):
        """Log events and replay them."""
        db_path = os.path.join(temp_dir, "test_events.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from infra.persistence_db import Base, init_db, setup_engine_events

        engine = create_engine(f"sqlite:///{db_path}")
        setup_engine_events(engine)
        with patch("infra.persistence_db.engine", engine):
            with patch("infra.persistence.engine", engine):
                init_db()
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

                with patch("infra.persistence_db.SessionLocal", SessionLocal):
                    with patch("infra.persistence.SessionLocal", SessionLocal):
                        logger = SessionLogger("event-flow-test")
                        logger.log_event("test_event", {"key": "value"})
                        logger.log_event("another_event", {"data": 123})

                        events = logger.replay()
                        assert len(events) == 2
                        assert events[0]["event_type"] == "test_event"
                        assert events[1]["event_type"] == "another_event"


class TestLayeredSearchFlow:
    """Test layered memory search."""

    @pytest.mark.asyncio
    async def test_l1_search_integration(self):
        """Test L1 search returns indexed results."""
        with patch("infra.persistence.SessionLogger") as mock_logger_cls:
            mock_logger = MagicMock()
            mock_logger_cls.return_value = mock_logger
            mock_logger.search_messages.return_value = [
                {"rowid": 1, "content": "Server config", "session_id": "s1", "role": "human"},
                {"rowid": 2, "content": "Port 8080", "session_id": "s1", "role": "ai"},
            ]
            mock_logger.semantic_search.return_value = []

            from tools import search_memory
            result = search_memory.invoke({"query": "server", "layer": "L1"})
            assert "ID: 1" in result
            assert "ID: 2" in result

    @pytest.mark.asyncio
    async def test_l2_l3_detail_flow(self):
        """Test L2 and L3 detail retrieval."""
        with patch("infra.persistence.SessionLogger") as mock_logger_cls:
            mock_logger = MagicMock()
            mock_logger_cls.return_value = mock_logger
            mock_logger.get_memory_detail.return_value = {
                "content": "Full detailed content about the server configuration"
            }

            from tools import search_memory
            l2_result = search_memory.invoke({"query": "test", "layer": "L2", "target_id": 1})
            assert "L2 Summary" in l2_result

            l3_result = search_memory.invoke({"query": "test", "layer": "L3", "target_id": 1})
            assert "L3 Full Content" in l3_result
            assert "Full detailed content" in l3_result


class TestLongTermMemory:
    """Test long-term memory creation and retrieval."""

    def test_create_long_term_memory(self, temp_dir):
        """Create a long-term memory entry."""
        db_path = os.path.join(temp_dir, "test_ltm.db")
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from infra.persistence_db import Base, init_db, setup_engine_events
        import infra.persistence_db

        engine = create_engine(f"sqlite:///{db_path}")
        setup_engine_events(engine)
        # Base.metadata.create_all(bind=engine) # Not enough for virtual tables

        with patch("infra.persistence_db.engine", engine):
            with patch("infra.persistence.engine", engine):
                init_db() # This will create all tables including virtual ones on the new engine
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                with patch("infra.persistence_db.SessionLocal", SessionLocal):
                    with patch("infra.persistence.SessionLocal", SessionLocal):
                        with patch("infra.persistence.get_embeddings") as mock_embeddings:
                            mock_embeddings.return_value.embed_query.return_value = [0.1] * 384

                            logger = SessionLogger("ltm-test")
                            logger.create_long_term_memory(
                                content="Important context about the project",
                                summary="Project Context"
                            )
                    # Should not raise
