#!/usr/bin/env python3
"""Run all sqlite3 queries against harness.db and capture output."""

import sqlite3
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "harness.db")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "query_results.txt")

if len(sys.argv) > 1:
    SESSION_ID = sys.argv[1]
else:
    print("Usage: python scripts/run_queries.py <session_id>")
    sys.exit(1)

lines = []

def header(num, title):
    lines.append(f"\n{'='*80}")
    lines.append(f"QUERY {num}: {title}")
    lines.append(f"{'='*80}\n")

def run_query(conn, query):
    try:
        cur = conn.execute(query)
        cols = [desc[0] for desc in cur.description] if cur.description else []
        rows = cur.fetchall()
        if cols:
            lines.append("  |  ".join(cols))
            lines.append("-" * (len("  |  ".join(cols)) + 10))
        for row in rows:
            lines.append("  |  ".join(str(v) for v in row))
        lines.append(f"\n[Rows returned: {len(rows)}]")
    except Exception as e:
        lines.append(f"ERROR: {e}")

conn = sqlite3.connect(DB_PATH)

# QUERY 1: List all tables
header(1, "List all tables")
run_query(conn, "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")

# QUERY 2: Check schema
header(2, "Schema")
run_query(conn, "SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name;")

# QUERY 3: List all sessions
header(3, "List all sessions")
run_query(conn, "SELECT * FROM sessions;")

# QUERY 4: Count messages for session
header(4, f"Count messages for session {SESSION_ID}")
run_query(conn, f"SELECT COUNT(*) FROM messages WHERE session_id='{SESSION_ID}';")

# QUERY 5: Message roles and counts
header(5, "Message roles and counts")
run_query(conn, f"SELECT role, COUNT(*) FROM messages WHERE session_id='{SESSION_ID}' GROUP BY role;")

# QUERY 6: All events for session
header(6, "All events for session")
run_query(conn, f"SELECT id, event_type, data FROM events WHERE session_id='{SESSION_ID}';")

# QUERY 7: additional_kwargs for token info - first 20 messages
header(7, "additional_kwargs for first 20 messages")
run_query(conn, f"SELECT id, role, LENGTH(content), additional_kwargs FROM messages WHERE session_id='{SESSION_ID}' ORDER BY id LIMIT 20;")

# QUERY 8: Token-related fields in additional_kwargs
header(8, "Token-related fields in additional_kwargs")
run_query(conn, f"SELECT id, role, additional_kwargs FROM messages WHERE session_id='{SESSION_ID}' AND additional_kwargs LIKE '%token%' LIMIT 10;")

# QUERY 9: All AI messages with kwargs
header(9, "All AI messages with kwargs")
run_query(conn, f"SELECT id, LENGTH(content), additional_kwargs FROM messages WHERE session_id='{SESSION_ID}' AND role='ai' ORDER BY id;")

# QUERY 10: Total content length
header(10, "Total content length by role")
run_query(conn, f"SELECT role, SUM(LENGTH(content)) as total_chars, COUNT(*) as msg_count FROM messages WHERE session_id='{SESSION_ID}' GROUP BY role;")

# QUERY 11: First human messages (truncated)
header(11, "First human messages (first 500 chars)")
run_query(conn, f"SELECT id, SUBSTR(content, 1, 500) FROM messages WHERE session_id='{SESSION_ID}' AND role='human' ORDER BY id LIMIT 10;")

# QUERY 12: Sub-agent sessions
header(12, "Sub-agent sessions")
run_query(conn, "SELECT id FROM sessions WHERE id LIKE 'sub-%';")

conn.close()

output = "\n".join(lines)
print(output)

with open(OUTPUT_PATH, "w") as f:
    f.write(output)

print(f"\n\nResults also written to: {OUTPUT_PATH}")
