# FastAPI Clean Architecture

For enterprise-level APIs, `fastapi-expert` recommends layer separation to ensure testability and maintenance.

## 1. Repository Layer (Data Access)

Abstracts database access (SQLAlchemy, Tortoise, etc.).

```python
from typing import Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: int) -> T | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()
```

## 2. Service Layer (Business Logic)

Where the application's intelligence resides. Endpoints should only call services.

```python
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def create_user(self, db: AsyncSession, data: UserCreate) -> User:
        # Business validation logic, password hashing, etc.
        ...
```

## 3. Lifespan Management

Modern management of application resources.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to the database, load AI models, etc.
    await database.connect()
    yield
    # Shutdown: Close connections
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
```


---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "HUB-ALIGNMENT"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:16:19.360859Z"
evidence_checksum: "8e52f6a"
```
