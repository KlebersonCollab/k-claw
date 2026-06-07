import pytest
import os
import sqlite3
from infra.persistence import SessionLogger, init_db, engine
from tools import search_memory, fetch_memory_detail

@pytest.mark.asyncio
async def test_layered_search():
    # 1. Clear and setup
    db_file = "harness.db"
    if os.path.exists(db_file):
        # Force close connections if possible or just remove
        try:
            os.remove(db_file)
        except PermissionError:
            pass

    # 2. Re-initialize
    init_db()

    # Verify table exists using raw sqlite
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memories_vec'")
    assert cur.fetchone() is not None
    conn.close()

    logger = SessionLogger("layered-test")
    logger.create_long_term_memory(
        content="The server uses port 8080 by default but can be changed in config.json.",
        summary="Server Port Configuration: 8080"
    )

    # 3. Search Layer 1
    results = search_memory.invoke({"query": "Server Port", "layer": "L1"})
    assert "ID:" in results
    assert "Server Port Configuration" in results

    # Extract ID
    import re
    match = re.search(r"ID: (\d+)", results)
    assert match is not None
    memory_id = int(match.group(1))

    # 4. Fetch Layer 2
    detail = fetch_memory_detail.invoke({"memory_id": memory_id})
    assert "port 8080" in detail
    assert "config.json" in detail
