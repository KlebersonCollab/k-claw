import sqlite3
import json

def get_history(session_id):
    conn = sqlite3.connect('harness.db')
    cursor = conn.cursor()
    cursor.execute("SELECT role, content, additional_kwargs FROM messages WHERE session_id = ? ORDER BY created_at ASC", (session_id,))
    rows = cursor.fetchall()
    
    print(f"History for session: {session_id}")
    for role, content, kwargs in rows:
        print(f"\n--- [{role.upper()}] ---")
        print(content)
        if kwargs:
            try:
                k = json.loads(kwargs)
                if 'tool_calls' in k:
                    print(f"Tool Calls: {k['tool_calls']}")
            except:
                pass
    
    cursor.execute("SELECT event_type, data FROM events WHERE session_id = ? ORDER BY created_at ASC", (session_id,))
    events = cursor.fetchall()
    print("\n--- EVENTS ---")
    for etype, data in events:
        print(f"Event: {etype} - {data}")
        
    conn.close()

if __name__ == "__main__":
    get_history('07fd8e57-5c36-445c-9f78-eb875551e7b2')
