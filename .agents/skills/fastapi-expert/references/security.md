# FastAPI Security Reference

## 1. Dependency Injection for Security

FastAPI allows injecting security directly into the function signature.

```python
from typing import Annotated
from fastapi import Depends, Security
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Reusable in any endpoint
TokenDep = Annotated[str, Depends(oauth2_scheme)]

@app.get("/items/")
async def read_items(token: TokenDep):
    return {"token": token}
```

## 2. Scopes and Authorization

Use `Security` instead of `Depends` when you need scopes:

```python
async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    # Scope validation logic here
    ...
```

## 3. JWT (JSON Web Tokens) Implementation

Use `python-jose` for token manipulation.

```python
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

## 4. Password Hashing (Passlib)

NEVER store passwords in plain text. Use `passlib[bcrypt]`.

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
```

## 5. Best Practices
- **Token Expiration**: Always set a short expiration time (e.g., 15-30 min).
- **Refresh Tokens**: For long sessions, implement securely stored Refresh Tokens.
- **Pydantic-Settings**: Never put API keys in code. Use `BaseSettings`.
- **HTTPS Redirect**: In production, always use `HTTPSRedirectMiddleware`.
- **CORS**: Configure `CORSMiddleware` restrictively, never use `allow_origins=["*"]` in production.


---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "HUB-ALIGNMENT"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:16:19.361986Z"
evidence_checksum: "8e52f6a"
```
