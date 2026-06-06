import os
import sqlite_vec
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, text, event
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class SessionModel(Base):
    __tablename__ = 'sessions'
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_tokens = Column(Integer, default=0)  # Accumulated token usage for the session
    messages = relationship("MessageModel", back_populates="session")
    events = relationship("EventModel", back_populates="session")

class MessageModel(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'))
    role = Column(String) # human, ai, tool, system
    content = Column(Text)
    additional_kwargs = Column(Text) # JSON string
    usage_metadata = Column(Text, nullable=True) # JSON string: {input_tokens, output_tokens, total_tokens}
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("SessionModel", back_populates="messages")

class EventModel(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'))
    event_type = Column(String)
    data = Column(Text) # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("SessionModel", back_populates="events")

class MemoryModel(Base):
    __tablename__ = 'memories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'))
    content = Column(Text)
    summary = Column(Text)
    vector = Column(Text) # JSON string of the embedding
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
DB_URL = "sqlite:///harness.db"
# Set connect_args for timeout and check_same_thread (important for FastAPI/Uvicorn)
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False, "timeout": 30}
)

@event.listens_for(engine, "connect")
def load_sqlite_extensions(dbapi_connection, connection_record):
    dbapi_connection.enable_load_extension(True)
    sqlite_vec.load(dbapi_connection)
    dbapi_connection.enable_load_extension(False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    # Manual SQL for FTS5, WAL mode, Triggers, and migrations
    with engine.connect() as conn:
        # Enable WAL mode for concurrency
        conn.execute(text("PRAGMA journal_mode=WAL;"))
        conn.execute(text("PRAGMA synchronous=NORMAL;"))

        # Migration: add usage_metadata to messages if missing
        result = conn.execute(text("PRAGMA table_info(messages);"))
        msg_cols = {row[1] for row in result.fetchall()}
        if "usage_metadata" not in msg_cols:
            conn.execute(text("ALTER TABLE messages ADD COLUMN usage_metadata TEXT;"))

        # Migration: add total_tokens to sessions if missing
        result = conn.execute(text("PRAGMA table_info(sessions);"))
        sess_cols = {row[1] for row in result.fetchall()}
        if "total_tokens" not in sess_cols:
            conn.execute(text("ALTER TABLE sessions ADD COLUMN total_tokens INTEGER DEFAULT 0;"))

        # Create FTS5 virtual table
        conn.execute(text("CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(content, session_id UNINDEXED, role UNINDEXED, content_rowid UNINDEXED);"))

        # Create sqlite-vec virtual table for memories (384 dimensions for all-MiniLM-L6-v2)
        conn.execute(text("CREATE VIRTUAL TABLE IF NOT EXISTS memories_vec USING vec0(embedding float[384], session_id TEXT, content TEXT, summary TEXT, original_rowid INTEGER);"))

        # Trigger to sync FTS5 on insert
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS messages_after_insert AFTER INSERT ON messages BEGIN
                INSERT INTO messages_fts(content, session_id, role, content_rowid)
                VALUES (new.content, new.session_id, new.role, new.id);
            END;
        """))
        conn.commit()
