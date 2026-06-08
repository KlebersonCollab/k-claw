import pytest
import os
import sqlite3
from unittest.mock import patch
from infra.persistence import SessionLogger, init_db, engine
from infra.persistence_db import setup_engine_events
from tools import search_memory, fetch_memory_detail
@pytest.mark.asyncio
async def test_layered_search(temp_dir):
    # 1. Clear and setup
    db_file = os.path.join(temp_dir, "test_layered.db")

    from sqlalchemy import create_engine
    from infra.persistence_db import setup_engine_events, init_db
    engine = create_engine(f"sqlite:///{db_file}")
    setup_engine_events(engine)

    with patch("infra.persistence_db.engine", engine):
        with patch("infra.persistence.engine", engine):
            init_db()

            # Verify table exists using the same engine
            from sqlalchemy import text
            with engine.connect() as conn:
                res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='memories_vec'"))
                assert res.fetchone() is not None

            logger = SessionLogger("layered-test")
            logger.create_long_term_memory(
                content="The server uses port 8080 by default but can be changed in config.json.",
                summary="Server Port Configuration: 8080"
            )

            # 3. Search Layer 1
            # search_memory is a tool, we use .invoke
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
