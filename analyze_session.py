import json
from persistence_db import SessionLocal, SessionModel, MessageModel, EventModel, MemoryModel, init_db, engine
from sqlalchemy import text, func

init_db()

TARGET_SESSION = "019e9b66-230e-7ae2-b5b3-d7e2c113afd6"

print("=" * 80)
print("1. ALL SESSIONS IN DB")
print("=" * 80)
with SessionLocal() as db:
    sessions = db.query(SessionModel).all()
    for s in sessions:
        msg_count = db.query(func.count(MessageModel.id)).filter(MessageModel.session_id == s.id).scalar()
        evt_count = db.query(func.count(EventModel.id)).filter(EventModel.session_id == s.id).scalar()
        print(f"  Session: {s.id} | Created: {s.created_at} | Messages: {msg_count} | Events: {evt_count}")

print("\n" + "=" * 80)
print(f"2. MESSAGE COUNT FOR TARGET SESSION: {TARGET_SESSION}")
print("=" * 80)
with SessionLocal() as db:
    count = db.query(func.count(MessageModel.id)).filter(MessageModel.session_id == TARGET_SESSION).scalar()
    print(f"  Total messages: {count}")

print("\n" + "=" * 80)
print("3. MESSAGE ROLE DISTRIBUTION")
print("=" * 80)
with SessionLocal() as db:
    results = db.query(MessageModel.role, func.count(MessageModel.id), func.sum(func.length(MessageModel.content))).filter(MessageModel.session_id == TARGET_SESSION).group_by(MessageModel.role).all()
    for role, cnt, total_len in results:
        print(f"  Role: {role} | Count: {cnt} | Total chars: {total_len}")

print("\n" + "=" * 80)
print("4. ALL AI MESSAGES WITH TOKEN INFO FROM additional_kwargs")
print("=" * 80)
with SessionLocal() as db:
    ai_msgs = db.query(MessageModel).filter(MessageModel.session_id == TARGET_SESSION, MessageModel.role == "ai").order_by(MessageModel.id).all()
    total_input_tokens = 0
    total_output_tokens = 0
    for m in ai_msgs:
        kwargs = json.loads(m.additional_kwargs) if m.additional_kwargs else {}
        usage = kwargs.get("usage_metadata", {}) or kwargs.get("usage", {})
        input_tokens = usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0)
        output_tokens = usage.get("output_tokens", 0) or usage.get("completion_tokens", 0)
        total_input_tokens += input_tokens
        total_output_tokens += output_tokens
        content_preview = (m.content or "")[:200].replace("\n", "\\n")
        print(f"  Msg#{m.id} | input_tok: {input_tokens} | output_tok: {output_tokens} | content_len: {len(m.content or '')} | preview: {content_preview}")
    print(f"\n  TOTAL INPUT TOKENS: {total_input_tokens}")
    print(f"  TOTAL OUTPUT TOKENS: {total_output_tokens}")
    print(f"  TOTAL TOKENS: {total_input_tokens + total_output_tokens}")

print("\n" + "=" * 80)
print("5. ALL HUMAN MESSAGES (content preview)")
print("=" * 80)
with SessionLocal() as db:
    human_msgs = db.query(MessageModel).filter(MessageModel.session_id == TARGET_SESSION, MessageModel.role == "human").order_by(MessageModel.id).all()
    for m in human_msgs:
        content_preview = (m.content or "")[:500].replace("\n", "\\n")
        print(f"  Msg#{m.id} | len: {len(m.content or '')} | preview: {content_preview}")

print("\n" + "=" * 80)
print("6. ALL TOOL MESSAGES (content preview)")
print("=" * 80)
with SessionLocal() as db:
    tool_msgs = db.query(MessageModel).filter(MessageModel.session_id == TARGET_SESSION, MessageModel.role == "tool").order_by(MessageModel.id).all()
    for m in tool_msgs:
        content_preview = (m.content or "")[:300].replace("\n", "\\n")
        print(f"  Msg#{m.id} | len: {len(m.content or '')} | preview: {content_preview}")

print("\n" + "=" * 80)
print("7. ALL EVENTS FOR THIS SESSION")
print("=" * 80)
with SessionLocal() as db:
    events = db.query(EventModel).filter(EventModel.session_id == TARGET_SESSION).order_by(EventModel.id).all()
    print(f"  Total events: {len(events)}")
    for e in events:
        data_preview = json.dumps(json.loads(e.data), ensure_ascii=False)[:500] if e.data else ""
        print(f"  Event#{e.id} | type: {e.event_type} | data: {data_preview}")

print("\n" + "=" * 80)
print("8. SUB-AGENT SESSIONS (sessions starting with 'sub-')")
print("=" * 80)
with SessionLocal() as db:
    sub_sessions = db.query(SessionModel).filter(SessionModel.id.like("sub-%")).all()
    for s in sub_sessions:
        msg_count = db.query(func.count(MessageModel.id)).filter(MessageModel.session_id == s.id).scalar()
        # Get token info for sub-sessions too
        sub_msgs = db.query(MessageModel).filter(MessageModel.session_id == s.id, MessageModel.role == "ai").all()
        sub_input = 0
        sub_output = 0
        for m in sub_msgs:
            kwargs = json.loads(m.additional_kwargs) if m.additional_kwargs else {}
            usage = kwargs.get("usage_metadata", {}) or kwargs.get("usage", {})
            sub_input += usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0)
            sub_output += usage.get("output_tokens", 0) or usage.get("completion_tokens", 0)
        print(f"  Session: {s.id} | Messages: {msg_count} | Input tokens: {sub_input} | Output tokens: {sub_output} | Total: {sub_input + sub_output}")

print("\n" + "=" * 80)
print("9. MEMORIES FOR THIS SESSION")
print("=" * 80)
with SessionLocal() as db:
    memories = db.query(MemoryModel).filter(MemoryModel.session_id == TARGET_SESSION).all()
    print(f"  Total memories: {len(memories)}")
    for m in memories:
        summary_preview = (m.summary or "")[:300].replace("\n", "\\n")
        print(f"  Memory#{m.id} | summary: {summary_preview}")

print("\n" + "=" * 80)
print("10. TOP 10 LARGEST MESSAGES BY CONTENT LENGTH")
print("=" * 80)
with SessionLocal() as db:
    large_msgs = db.query(MessageModel).filter(MessageModel.session_id == TARGET_SESSION).order_by(func.length(MessageModel.content).desc()).limit(10).all()
    for m in large_msgs:
        content_preview = (m.content or "")[:200].replace("\n", "\\n")
        print(f"  Msg#{m.id} | role: {m.role} | len: {len(m.content or '')} | preview: {content_preview}")

print("\n" + "=" * 80)
print("DONE - ANALYSIS COMPLETE")
print("=" * 80)
