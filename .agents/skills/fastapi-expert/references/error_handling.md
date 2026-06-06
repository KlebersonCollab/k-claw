# FastAPI Error Handling Standard

Consistent error handling is vital for the developer experience (frontend) and API security.

## 1. Custom Exceptions

Define domain exceptions to separate logic errors from infrastructure errors.

```python
class DomainException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

class UserNotFound(DomainException):
    def __init__(self):
        super().__init__("User not found", status_code=404)
```

## 2. Global Exception Handlers

Use `@app.exception_handler` to capture exceptions and return a standardized JSON format.

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "path": request.url.path
        },
    )
```

## 3. Validation Errors (Override)

Customize the 422 error (Pydantic) to make it more friendly.

```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "message": "Invalid data"},
    )
```


---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "HUB-ALIGNMENT"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:16:19.361054Z"
evidence_checksum: "8e52f6a"
```
