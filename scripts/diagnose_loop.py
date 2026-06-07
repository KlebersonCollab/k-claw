import json
import sys
import os
from sqlalchemy import create_engine, text

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "harness.db")

engine = create_engine(f"sqlite:///{DB_PATH}")

def analyze_session(session_id):
    with engine.connect() as conn:
        print(f"\n=== Deep Analysis of Session: {session_id} ===")

        msgs = conn.execute(text("""
            SELECT role, content, additional_kwargs, created_at
            FROM messages
            WHERE session_id = :sid
            ORDER BY created_at ASC
        """), {"sid": session_id}).fetchall()

        for m in msgs:
            role, content, kwargs_json, t = m
            kwargs = json.loads(kwargs_json) if kwargs_json else {}
            t_calls = kwargs.get('tool_calls', []) or kwargs.get('response_metadata', {}).get('tool_calls', [])
            print(f"[{t}] {role.upper()}: {(content or '')[:100]}...")
            if t_calls:
                print(f"   -> TOOL CALLS FOUND: {len(t_calls)}")
                for tc in t_calls:
                    # Handle different tool call formats (LangChain/OpenAI)
                    fname = tc.get('function', {}).get('name') or tc.get('name')
                    fargs = tc.get('function', {}).get('arguments') or tc.get('args')
                    print(f"      - {fname}: {fargs}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_session(sys.argv[1])
    else:
        # Get last 3 sub-agent sessions just in case
        with engine.connect() as conn:
            res = conn.execute(text("SELECT id FROM sessions WHERE id LIKE 'sub-%' ORDER BY created_at DESC LIMIT 3")).fetchall()
            if not res:
                print("No sub-agent sessions found. Usage: python scripts/diagnose_loop.py <session_id>")
            for r in res:
                analyze_session(r[0])
