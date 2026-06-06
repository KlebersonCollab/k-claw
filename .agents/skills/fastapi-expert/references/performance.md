# FastAPI Performance Reference

## 1. Async vs Sync Decision Matrix

FastAPI executes `async def` functions directly in the event loop and `def` functions in a threadpool.

| Function Type | When to Use | Why? |
|----------------|-------------|----------|
| `async def` | Non-blocking I/O (HTTPX, Motor, Asyncpg) | Avoids blocking the event loop. |
| `def` | Blocking I/O (Requests, SQLAlchemy, File I/O) | Runs in separate threads so as not to freeze the API. |
| `def` | CPU-bound (Heavy calculations, image processing) | Threadpool handles it better without freezing other requests. |

### ⚠️ The Danger of "Fake Async"
NEVER use `time.sleep()` or blocking libraries (like `requests`) inside an `async def`. This freezes ALL your API requests simultaneously.

## 2. Rust-Powered Serialization (Pydantic V2)

FastAPI uses Pydantic V2, which is written in Rust. For maximum performance:

- **Strict Type Hints:** The more precise the type, the faster Rust validates.
- **Annotated:** Use `Annotated` to prevent Pydantic from needing to infer complex types multiple times.
- **Exclude Unset:** When returning models, use `response_model_exclude_unset=True` to reduce the payload size.

## 3. Tooling
- **Uvicorn vs Gunicorn:** Use Uvicorn for dev and Gunicorn with Uvicorn workers for production.
- **uv run:** Always execute via `uv run` to ensure virtual environment optimizations are active.


---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "HUB-ALIGNMENT"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:16:19.361860Z"
evidence_checksum: "8e52f6a"
```
