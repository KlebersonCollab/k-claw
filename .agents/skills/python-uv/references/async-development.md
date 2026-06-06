# Async Development with UV — Complete Reference

Guide to patterns and tools for developing asynchronous applications in Python using the `uv` ecosystem.

---

## 1. Why use UV for Async?

`uv` facilitates the management of high-performance asynchronous projects by:
- **Fast Conflict Resolution**: Async libraries often have complex dependency trees.
- **Isolated Environments**: Ensures specific loop versions (like `uvloop`) are installed correctly.
- **Direct Execution**: `uv run` allows running async scripts with inline dependencies (PEP 723) without manual setup.

---

## 2. Async Project Setup

### Initialization
```bash
uv init async-app
cd async-app

# Add essential dependencies
uv add httpx pydantic anyio
uv add --dev pytest-asyncio trio
```

### Recommended Libraries

| Category | Library | UV Command |
|-----------|------------|------------|
| **HTTP Client** | `httpx` | `uv add httpx` |
| **Event Loop (Fast)** | `uvloop` | `uv add uvloop` |
| **Web Framework** | `FastAPI` | `uv add fastapi` |
| **Database** | `SQLAlchemy` (async) | `uv add sqlalchemy[asyncio]` |
| **Testing** | `pytest-asyncio` | `uv add --dev pytest-asyncio` |

---

## 3. Code Patterns in the UV Ecosystem

### Concurrent Execution (Gather)
Pattern for fetching multiple resources simultaneously.

```python
import asyncio
import httpx

async def fetch_urls(urls: list[str]):
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.status_code for r in responses]

# Run with uv
# uv run python script.py
```

### Resource Protection (Semaphores)
Prevents overloading external APIs by limiting concurrency.

```python
semaphore = asyncio.Semaphore(10) # Maximum 10 simultaneous requests

async def safe_fetch(url):
    async with semaphore:
        # Fetch logic here
        pass
```

---

## 4. Testing Async Code with UV

Configure `pytest-asyncio` in your `pyproject.toml` to avoid repetitive decorators.

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
asyncio_default_fixture_loop_scope = "function"
```

### Test Example
```python
import pytest
from app import fetch_data

@pytest.mark.asyncio
async def test_fetch():
    data = await fetch_data("https://api.example.com")
    assert data["status"] == "ok"

# Run tests
# uv run pytest
```

---

## 5. Inline Scripts (PEP 723) for Async

Ideal for scraping tools or quick automation.

```python
# /// script
# dependencies = ["httpx", "rich"]
# ///
import asyncio
import httpx
from rich import print

async def main():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://httpbin.org/get")
        print(r.json())

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. Performance: Using `uvloop`

On Linux/macOS systems, `uvloop` can make the asyncio loop 2-4x faster.

```python
import asyncio
import sys

if sys.platform != "win32":
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

async def main():
    # Your application here
    pass

asyncio.run(main())
```

---

## 7. Async Development Checklist

- [ ] Used `asyncio.run()` as the entry point?
- [ ] Avoided blocking functions like `time.sleep()`? (Use `asyncio.sleep()`)
- [ ] Configured timeouts in all network calls?
- [ ] Used `uv run` to ensure async dependencies are in the correct environment?
- [ ] Implemented robust error handling in `gather` with `return_exceptions=True`?
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.664399Z"
evidence_checksum: "8e52f6a"
```
