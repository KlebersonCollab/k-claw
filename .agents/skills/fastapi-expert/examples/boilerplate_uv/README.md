# Boilerplate FastAPI + UV

This example demonstrates the recommended structure using the `fastapi-expert` skill.

## File Structure

```text
.
├── pyproject.toml
├── src/
│   ├── main.py
│   ├── schemas.py
│   └── dependencies.py
└── .python-version
```

## 1. pyproject.toml
```toml
[project]
name = "fastapi-boilerplate"
version = "0.1.0"
dependencies = [
    "fastapi[standard]>=0.110.0",
    "pydantic-settings>=2.2.1",
]
```

## 2. src/main.py (Annotated Style)
```python
from typing import Annotated
from fastapi import FastAPI, Query, Depends
from .schemas import Item
from .dependencies import get_query_token

app = FastAPI()

@app.get("/items/")
async def read_items(
    token: Annotated[str, Depends(get_query_token)],
    q: Annotated[str | None, Query(max_length=50)] = None
) -> list[Item]:
    return []
```

## How to run
```bash
uv sync
uv run fastapi dev src/main.py
```

---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "HUB-ALIGNMENT"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T14:00:00Z"
evidence_checksum: "8e52f6a"
```
