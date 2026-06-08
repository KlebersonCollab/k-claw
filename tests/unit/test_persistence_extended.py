import pytest
import os
from unittest.mock import patch
from sqlalchemy.orm import sessionmaker
from infra.persistence import SessionLogger
from infra.persistence_db import init_db, SessionLocal, SessionModel
from langchain_core.messages import HumanMessage

def test_session_logger_list_sessions(temp_dir):
    db_path = os.path.join(temp_dir, "test_list_unique.db")
    from sqlalchemy import create_engine
    from infra.persistence_db import setup_engine_events
    engine = create_engine(f"sqlite:///{db_path}")
    setup_engine_events(engine)

    unique_id = f"s1-{os.urandom(4).hex()}"
    with patch("infra.persistence_db.engine", engine):
        with patch("infra.persistence.engine", engine):
            init_db()
            SessionLocalTest = sessionmaker(bind=engine)
            # Must patch where it is IMPORTED locally in the method
            with patch("infra.persistence.SessionLocal", SessionLocalTest):
                with patch("infra.persistence_db.SessionLocal", SessionLocalTest):
                    logger = SessionLogger(unique_id)
                    logger.log_messages([HumanMessage(content="test")])

                    sessions = SessionLogger.list_sessions()
                    ids = [s["id"] for s in sessions]
                    assert unique_id in ids

def test_session_logger_delete_memory(temp_dir):
    db_path = os.path.join(temp_dir, "test_del.db")
    from sqlalchemy import create_engine
    from infra.persistence_db import setup_engine_events
    engine = create_engine(f"sqlite:///{db_path}")
    setup_engine_events(engine)

    with patch("infra.persistence_db.engine", engine):
        with patch("infra.persistence.engine", engine):
            init_db()
            logger = SessionLogger("s2")
            logger.log_messages([HumanMessage(content="msg to delete")])

            logger.delete_memory_by_session("s2")
            history = logger.get_message_history()
            assert len(history) == 0
