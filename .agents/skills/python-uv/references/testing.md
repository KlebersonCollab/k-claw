# Advanced Testing Guide with Pytest

This guide establishes quality and testing standards for Python projects, using **pytest** as the primary tool executed via **UV**.

---

## 1. TDD Methodology (Red-Green-Refactor)

Development should follow the atomic testing cycle:

1.  🔴 **RED**: Write a test that fails for the desired behavior.
2.  🟢 **GREEN**: Write the minimum code necessary to make the test pass.
3.  🔵 **REFACTOR**: Improve the code while keeping the tests green.

---

## 2. Configuration and Coverage

### Coverage Goals
- **Target**: 80%+ global coverage.
- **Critical Paths**: 100% mandatory coverage.

### Execution via UV
Configure `pyproject.toml` to include automatic reports:

```toml
[tool.pytest.ini_options]
addopts = "--cov=my_package --cov-report=term-missing --cov-report=html"
```

Execution command:
```bash
uv run pytest
```

---

## 3. Professional Testing Structure

Organize your tests by category to facilitate selective execution (using markers).

```text
tests/
├── conftest.py          # Shared fixtures
├── unit/                # Pure logic tests (fast)
├── integration/         # DB, API, I/O tests
└── e2e/                 # Complete user flows
```

---

## 4. Fixture Mastery

Use fixtures to manage state and resources cleanly.

### Setup and Teardown (Yield)
```python
import pytest

@pytest.fixture
def db_session():
    # Setup
    session = Session.create()
    session.begin_transaction()

    yield session # Provides to the test

    # Teardown
    session.rollback()
    session.close()
```

### Fixture Scopes
- `function` (default): Runs for each test.
- `module`: Runs once per file.
- `session`: Runs once per complete suite.

---

## 5. Parameterization

Avoid duplicating tests for different inputs. Use `@pytest.mark.parametrize`.

```python
@pytest.mark.parametrize("email, expected", [
    ("valid@test.com", True),
    ("invalid", False),
    ("", False),
])
def test_email_validation(email, expected):
    assert is_valid_email(email) is expected
```

---

## 6. Mocking and Isolation

Use `unittest.mock` (or `pytest-mock`) to isolate external dependencies.

### Mocking Functions/APIs
```python
from unittest.mock import patch

@patch("my_package.external_service.call_api")
def test_processing_with_mock(mock_api):
    mock_api.return_value = {"status": "ok"}
    result = process()
    assert result == "success"
    mock_api.assert_called_once()
```

### Mocking Exceptions
```python
def test_api_error(mock_api):
    mock_api.side_effect = ConnectionError("Timeout")
    with pytest.raises(ConnectionError):
        execute_call()
```

---

## 7. Asynchronous Tests

For projects with `asyncio` (FastAPI, etc.), use `pytest-asyncio`.

```python
@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    res = await async_client.get("/status")
    assert res.status_code == 200
```

---

## 8. Best Practices (DOs and DON'Ts)

✅ **DO:**
- **Descriptive names**: `test_login_with_wrong_password_should_fail`.
- **One behavior per test**: Keep tests atomic.
- **Use `tmp_path`**: Native pytest fixture for safely handling temporary files.
- **Mocks with `autospec=True`**: Ensures the mock has the same interface as the real object.

❌ **DON'T:**
- **Do not test implementation**: Focus on behavior (input/output).
- **Do not share state**: Tests should be independent and able to run in any order.
- **Do not ignore failures**: A failing test is an immediate blocker.
- **Do not use `print`**: Use logs or pytest output in case of failure.
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.664731Z"
evidence_checksum: "8e52f6a"
```
