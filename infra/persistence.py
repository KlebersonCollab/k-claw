import json
from typing import Any, Dict, List, Optional
import os
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from .persistence_db import SessionLocal, SessionModel, MessageModel, EventModel, MemoryModel, init_db, engine

# Lazy load embeddings to save latency
_EMBEDDINGS_MODEL = None

def get_embeddings():
    global _EMBEDDINGS_MODEL
    if _EMBEDDINGS_MODEL is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        # BGE Small v1.5: 384 dimensions, state-of-the-art technical retrieval
        _EMBEDDINGS_MODEL = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    return _EMBEDDINGS_MODEL

class SessionLogger:
    def __init__(self, session_id: str):
        self.session_id = session_id
        init_db()
        self._ensure_session_exists()

    def _ensure_session_exists(self):
        with SessionLocal() as db:
            session = db.query(SessionModel).filter(SessionModel.id == self.session_id).first()
            if not session:
                new_session = SessionModel(id=self.session_id)
                db.add(new_session)
                db.commit()

    def log_event(self, event_type: str, data: Dict[str, Any]):
        with SessionLocal() as db:
            new_event = EventModel(session_id=self.session_id, event_type=event_type, data=json.dumps(data))
            db.add(new_event)
            db.commit()

    def log_messages(self, messages: List[BaseMessage]):
        with SessionLocal() as db:
            for msg in messages:
                if isinstance(msg, HumanMessage): role = "human"
                elif isinstance(msg, AIMessage): role = "ai"
                elif isinstance(msg, SystemMessage): role = "system"
                elif isinstance(msg, ToolMessage): role = "tool"
                else: role = "unknown"

                usage_metadata = None
                if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                    usage_metadata = json.dumps(msg.usage_metadata)
                    # Aggregate input + output tokens for accurate cost tracking
                    input_tokens = msg.usage_metadata.get("input_tokens", 0)
                    output_tokens = msg.usage_metadata.get("output_tokens", 0)
                    total = input_tokens + output_tokens
                    self._add_session_tokens(db, total)

                new_msg = MessageModel(
                    session_id=self.session_id,
                    role=role,
                    content=str(msg.content) if msg.content else "",
                    additional_kwargs=json.dumps(msg.additional_kwargs),
                    usage_metadata=usage_metadata
                )
                db.add(new_msg)
            db.commit()

    def _add_session_tokens(self, db, tokens: int):
        if tokens > 0:
            session = db.query(SessionModel).filter(SessionModel.id == self.session_id).first()
            if session:
                session.total_tokens = (session.total_tokens or 0) + tokens

    def replay(self) -> List[Dict[str, Any]]:
        with SessionLocal() as db:
            events = db.query(EventModel).filter(EventModel.session_id == self.session_id).all()
            return [{"event_type": e.event_type, "data": json.loads(e.data)} for e in events]

    def get_message_history(self) -> List[BaseMessage]:
        with SessionLocal() as db:
            db_messages = db.query(MessageModel).filter(MessageModel.session_id == self.session_id).order_by(MessageModel.created_at).all()
            history = []
            for m in db_messages:
                kwargs = json.loads(m.additional_kwargs) if m.additional_kwargs else {}
                if m.usage_metadata:
                    kwargs['usage_metadata'] = json.loads(m.usage_metadata)

                if m.role == "human": history.append(HumanMessage(content=m.content, **kwargs))
                elif m.role == "ai": history.append(AIMessage(content=m.content, **kwargs))
                elif m.role == "system": history.append(SystemMessage(content=m.content, **kwargs))
                elif m.role == "tool": history.append(ToolMessage(content=m.content, **kwargs))
            return history

    def search_messages(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        from sqlalchemy import text
        with SessionLocal() as db:
            # Escape double quotes by doubling them for FTS5 phrase search
            # and wrap the whole query in double quotes to treat it as a single phrase.
            # This prevents interpretation of FTS5 operators like OR, AND, NEAR.
            clean_q = query.replace('"', '""').strip()
            if not clean_q:
                return []
            sanitized_query = f'"{clean_q}"'
            sql = text("SELECT content, session_id, role, content_rowid FROM messages_fts WHERE messages_fts MATCH :q LIMIT :limit")
            results = db.execute(sql, {"q": sanitized_query, "limit": limit}).fetchall()
            return [{"content": r[0], "session_id": r[1], "role": r[2], "rowid": r[3]} for r in results]

    def create_long_term_memory(self, content: str, summary: str):
        vector = get_embeddings().embed_query(summary)
        with SessionLocal() as db:
            new_memory = MemoryModel(session_id=self.session_id, content=content, summary=summary, vector=json.dumps(vector))
            db.add(new_memory)
            db.commit()
            memory_id = new_memory.id

            from sqlalchemy import text
            import struct
            with engine.connect() as conn:
                sql = text("INSERT INTO memories_vec(embedding, session_id, content, summary, original_rowid) VALUES (:embedding, :session_id, :content, :summary, :original_rowid)")
                vec_blob = struct.pack('<' + 'f' * len(vector), *vector)
                conn.execute(sql, {"embedding": vec_blob, "session_id": self.session_id, "content": content, "summary": summary, "original_rowid": memory_id})
                conn.commit()

    def semantic_search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        query_vector = get_embeddings().embed_query(query)
        from sqlalchemy import text
        import struct
        vec_blob = struct.pack('<' + 'f' * len(query_vector), *query_vector)
        with engine.connect() as conn:
            sql = text("SELECT content, summary, session_id, vec_distance_cosine(embedding, :query_vec) as distance, original_rowid FROM memories_vec ORDER BY distance LIMIT :limit")
            results = conn.execute(sql, {"query_vec": vec_blob, "limit": limit}).fetchall()
            scored_memories = []
            for r in results:
                scored_memories.append({"content": r[0], "summary": r[1], "session_id": r[2], "score": 1.0 - float(r[3]), "rowid": r[4]})
            return scored_memories

    def get_memory_detail(self, rowid: int) -> Optional[Dict[str, Any]]:
        with SessionLocal() as db:
            memory = db.query(MemoryModel).filter(MemoryModel.id == rowid).first()
            return {"content": memory.content, "summary": memory.summary, "session_id": memory.session_id} if memory else None

    def delete_memory_by_session(self, target_session_id: str):
        from .persistence_db import MemoryModel, MessageModel, EventModel
        with SessionLocal() as db:
            db.query(MemoryModel).filter(MemoryModel.session_id == target_session_id).delete()
            db.query(MessageModel).filter(MessageModel.session_id == target_session_id).delete()
            db.query(EventModel).filter(EventModel.session_id == target_session_id).delete()
            db.commit()

    @staticmethod
    def list_sessions() -> List[Dict[str, Any]]:
        from .persistence_db import SessionModel, SessionLocal, init_db
        init_db()
        with SessionLocal() as db:
            sessions = db.query(SessionModel).order_by(SessionModel.created_at.desc()).all()
            return [{"id": s.id, "created_at": s.created_at.isoformat(), "total_tokens": s.total_tokens} for s in sessions]
