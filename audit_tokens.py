import json
import sqlite3
from collections import Counter

DB_PATH = "harness.db"
TARGET_SESSION = "019e9b66-230e-7ae2-b5b3-d7e2c113afd6"

def analyze_token_usage(session_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print(f"=== Token Audit for Session: {session_id} ===")

    # 1. Total messages and roles
    cur.execute("SELECT role, COUNT(*), SUM(LENGTH(content)) FROM messages WHERE session_id=? GROUP BY role", (session_id,))
    roles = cur.fetchall()
    print("\nMessage Counts by Role:")
    for role, count, total_len in roles:
        print(f" - {role}: {count} messages ({total_len or 0} characters)")

    # 2. Check for Token Info in metadata
    cur.execute("SELECT additional_kwargs FROM messages WHERE session_id=? AND role='ai'", (session_id,))
    ai_msgs = cur.fetchall()

    total_prompt_tokens = 0
    total_completion_tokens = 0
    usage_records = 0

    for (kwargs_json,) in ai_msgs:
        kwargs = json.loads(kwargs_json)
        # Look for typical usage patterns (OpenAI/Anthropic/LangChain)
        usage = kwargs.get('usage') or kwargs.get('token_usage') or kwargs.get('response_metadata', {}).get('token_usage')
        if usage:
            total_prompt_tokens += usage.get('prompt_tokens', 0)
            total_completion_tokens += usage.get('completion_tokens', 0)
            usage_records += 1

    if usage_records > 0:
        print(f"\nExtracted Token Usage (from {usage_records} AI responses):")
        print(f" - Total Prompt Tokens: {total_prompt_tokens:,}")
        print(f" - Total Completion Tokens: {total_completion_tokens:,}")
        print(f" - Total Estimated: {total_prompt_tokens + total_completion_tokens:,}")
    else:
        print("\nNo explicit token usage metadata found in DB. Estimating based on content length...")
        # 1 token ~= 4 characters for English/Code
        cur.execute("SELECT SUM(LENGTH(content)) FROM messages WHERE session_id=?", (session_id,))
        total_chars = cur.fetchone()[0] or 0
        print(f" - Total characters in history: {total_chars:,}")
        print(f" - Rough Estimate: {int(total_chars / 4):,} tokens (content only)")

    # 3. Analyze growth per turn
    cur.execute("SELECT id, role, LENGTH(content) FROM messages WHERE session_id=? ORDER BY id", (session_id,))
    history = cur.fetchall()
    print("\nHistory Growth (First 15 messages):")
    acc_len = 0
    for i, (msg_id, role, length) in enumerate(history[:15]):
        acc_len += length
        print(f" - Msg {msg_id} ({role}): +{length} chars | Total history size: {acc_len} chars")

    # 4. Check for Sub-agents spawned by this session
    cur.execute("SELECT id FROM sessions WHERE id LIKE ?", (f"sub-%{session_id[-8:]}%",))
    subs = cur.fetchall()
    if subs:
        print(f"\nPotential Sub-Agent sessions found: {len(subs)}")
        for (sub_id,) in subs:
            print(f" - {sub_id}")

    conn.close()

if __name__ == "__main__":
    analyze_token_usage(TARGET_SESSION)
