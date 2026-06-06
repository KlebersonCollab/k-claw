# Scalable FastAPI API Structure Guide

This guide defines the recommended structure for FastAPI projects that need to scale in complexity and data volume.

## Recommended Folder Structure

```text
app/
├── main.py              # Application entry point
├── api/                 # Routing layer (v1, v2, etc.)
│   ├── api_v1/
│   │   ├── api.py       # Router aggregator
│   │   └── endpoints/   # Route implementations
│   │       ├── users.py
│   │       └── items.py
├── core/                # Global configurations and security
│   ├── config.py
│   └── security.py
├── crud/                # Database operations (Create, Read, Update, Delete)
├── db/                  # Database and Session configuration
│   ├── base.py          # Imports all models for Alembic
│   └── session.py
├── dependencies/        # Dependency injection (Auth, DB, etc.)
├── models/              # Database models (SQLAlchemy/SQLModel)
├── schemas/             # Pydantic validation schemas (Request/Response)
└── services/            # Complex business logic
```

## Key Principles

### 1. Modular Routers
Use `APIRouter` to separate routes by domain. Avoid putting too much logic directly in endpoints; delegate to `crud` or `services`.

### 2. Pydantic Schemas
Keep your database models (`models/`) separate from your API schemas (`schemas/`). This allows the API to evolve without breaking the contract with the client.

### 3. Dependency Injection
Use FastAPI's `Depends()` system to manage database sessions and authentication. This facilitates unit testing through overrides.

### 4. CRUD vs Service Layer
- **CRUD**: Pure database operations.
- **Service**: Business logic that may involve multiple CRUDs, external calls, or complex processing.

## Clean Endpoint Example

```python
@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Creates a new user.
    """
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")
    return crud.user.create(db, obj_in=user_in)
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
