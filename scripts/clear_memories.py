import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text
from infra.persistence_db import engine, init_db

def clear_all_memories():
    print("Initializing database and loading extensions...")
    init_db()
    
    with engine.connect() as conn:
        print("Clearing memories and memories_vec...")
        conn.execute(text("DELETE FROM memories;"))
        conn.execute(text("DELETE FROM memories_vec;"))
        
        print("Rebuilding FTS5 index...")
        conn.execute(text("DELETE FROM messages_fts;"))
        conn.execute(text("INSERT INTO messages_fts(content, session_id, role, content_rowid) SELECT content, session_id, role, id FROM messages;"))
        
        conn.commit()
        print("✅ Database maintenance complete. Ready for high-precision embeddings.")

if __name__ == "__main__":
    clear_all_memories()
