import json
from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///harness.db")

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
            kwargs = json.loads(kwargs_json)
            t_calls = kwargs.get('tool_calls', [])
            print(f"[{t}] {role.upper()}: {content[:100]}...")
            if t_calls:
                print(f"   -> TOOL CALLS FOUND: {len(t_calls)}")
                for tc in t_calls:
                    # Handle different tool call formats (LangChain/OpenAI)
                    fname = tc.get('function', {}).get('name') or tc.get('name')
                    fargs = tc.get('function', {}).get('arguments') or tc.get('args')
                    print(f"      - {fname}: {fargs}")

if __name__ == "__main__":
    # Get last 3 sub-agent sessions just in case
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id FROM sessions WHERE id LIKE 'sub-%' ORDER BY created_at DESC LIMIT 3")).fetchall()
        for r in res:
            analyze_session(r[0])
