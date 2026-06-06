---
name: fastapi-expert
version: 2.3.0
description: "Expert level FastAPI implementation focused on performance, clean architecture, and Python-UV integration."
category: development-python
---

# FastAPI Expert: API Excellence

> "Fast, easy to learn, fast to code, ready for production." - This skill ensures your FastAPI code actually lives up to that promise.

---

## 🔒 Prerequisites (Mandatory)
This skill operates WITHIN the **SDD** framework. Before starting any technical execution:
0. **Mode Check**: Verify the current operational mode (`.hub-mode`) and apply the `token-distiller` skill guidelines.
1. **Context Check**: Rehydrate state by reading `.specs/project/STATE.md`, `.specs/project/MEMORY.md`, and `.specs/project/LEARNINGS.md`.
2. **Spec Check**: Does the `spec.md` file exist with clear requirements and Acceptance Criteria (ACs)? (BDD mandatory for Medium+).
3. **Plan Check**: Does the `plan.md` file define the architecture, schemas, and include **Mermaid** diagrams?
4. **Contract Check**: Was the `contract.md` file established with validation sensors?
5. **Task Check**: Is the task list in `.specs/project/tasks.md` (or feature-specific) detailed and atomized?

---
## Goal

Provide a decision and implementation framework for high-performance APIs, ensuring the correct use of Dependency Injection, Strict Typing (Annotated), and native integration with the `python-uv` ecosystem.

---

## Workflow (6 Phases)

### Phase 0: ARCHITECTURE_DESIGN
Define the project structure (Clean Architecture).
- **Rule**: Decide between Repository Pattern or Service Layer before coding.
- **Reference**: See [Architecture Guide](references/architecture.md).

### Phase 1: SCHEMA_DESIGN
Define data contracts using Pydantic V2.
- **Rule**: NEVER use `RootModel`. Prefer `TypeAdapter` or structured models.
- **Mandate**: Every field must have `Field(description=...)` for automatic documentation.

### Phase 2: DEPENDENCY_ARCHITECTURE
Map dependencies and security (JWT).
- **Rule**: Exclusively use `Annotated[Type, Depends(func)]`.
- **Logic**: Create aliases for reusable dependencies.

### Phase 3: IMPLEMENTATION & ERROR_HANDLING
Write endpoints and exception handlers.
- **Rule**: Use `async def` only for truly asynchronous I/O operations.
- **Mandate**: Implement global handlers for domain exceptions.

### Phase 4: VALIDATION & PERF
Performance audit and documentation.
- **Check**: Validate that there is no blocking code inside `async def`.
- **Mandate**: Perform performance audits using standardized benchmarking tools and document results.

### Phase 5: TESTING
Implement unit and integration tests.
- **Rule**: Ensure 100% coverage in critical services with Pytest.

---

## Key Patterns (The FastAPI Standard)

### 1. Annotated Style (Mandatory)
```python
from typing import Annotated
from fastapi import Depends, Path

# DO THIS
async def read_item(item_id: Annotated[int, Path(title="The ID of the item")]):
    ...

# NOT THIS
async def read_item(item_id: int = Path(...)):
    ...
```

### 2. UV Integration
Always initialize and manage dependencies via `python-uv`:
```bash
uv add fastapi pydantic-settings
uv run fastapi dev main.py
```

---

## Quality Rules

- **Clean Code**: Follow SOLID principles. Endpoints should be "thin" (logic in services/dependencies).
- **Security**: Utilize `OAuth2PasswordBearer` and scopes for access control.
- **Performance**: Pydantic V2 (Rust core) must be the sole source of serialization.

---

## Prohibited

- NEVER use `...` (Ellipsis) in Pydantic models or mandatory parameters.
- NEVER mix database logic directly in the endpoint (use Dependencies instead).
- NEVER use deprecated serialization libraries (ujson/orjson).

## Output Structure

Execution of this skill should result in APIs that follow this recommended file structure:

| Artifact | Location | Description |
|----------|-------------|-----------|
| **Entrypoint** | `src/main.py` | FastAPI initialization and router inclusion. |
| **Schemas** | `src/schemas/` | Pydantic V2 models for request/response. |
| **Endpoints** | `src/api/` | Routers organized by domain (tags). |
| **Dependencies** | `src/dependencies.py` | Injectable dependency factory. |
| **Config** | `src/config.py` | Environment management via `pydantic-settings`. |
| **Migrations** | `migrations/` | Database evolution scripts (Alembic). |

## Detailed References

For a deep dive into each topic, consult the specialized guides:

| Guide | Topic |
|------|--------|
| [Architecture](references/architecture.md) | Repositories, Services, and Lifespan. |
| [API Design](references/api_design.md) | REST Patterns, Status Codes, and Naming. |
| [Security](references/security.md) | JWT, OAuth2, and Password Hashing. |
| [Error Handling](references/error_handling.md) | Domain Exceptions and Global Handlers. |
| [Performance](references/performance.md) | Async vs Sync and Pydantic Rust core. |
| [Testing](references/testing.md) | Pytest, AsyncClient, and Integration Tests. |
| [Migrations](references/migrations.md) | Async Alembic and database versioning. |


---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "HUB-ALIGNMENT"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:16:19.359394Z"
evidence_checksum: "8e52f6a"
```
