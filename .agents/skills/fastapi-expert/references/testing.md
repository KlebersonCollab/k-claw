# FastAPI Testing with UV & Pytest

Testing asynchronous APIs requires correct event loop and HTTP client configuration.

## 1. Fixtures Configuration (`tests/conftest.py`)

```python
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.core.database import get_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def client():
    # Dependency override example (e.g., in-memory database)
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

## 2. Asynchronous Test Example

Always use the `@pytest.mark.asyncio` decorator.

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_read_main(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}
```

## 3. Integration Tests (Database & Cleanups)

Use `dependency_overrides` to inject a test database (e.g., SQLite in-memory).

```python
from app.core.database import get_db

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db
```

### Resetting the Database between Tests
Use fixtures to create/clear tables in each test:

```python
@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

## 4. Execution with UV
```bash
uv add --dev pytest pytest-asyncio httpx aiosqlite
uv run pytest
```


---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "HUB-ALIGNMENT"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:16:19.362093Z"
evidence_checksum: "8e52f6a"
```
