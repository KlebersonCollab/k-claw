# CI/CD Workflows

Complete guide for integrating UV into CI/CD pipelines, Docker, and package publishing.

---

## GitHub Actions

### Basic Workflow

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --dev --locked

      - name: Check formatting
        run: uv run ruff format --check .

      - name: Check linting
        run: uv run ruff check .

      - name: Type check
        run: uv run mypy .

      - name: Run tests
        run: uv run pytest --cov=src/
```

### Matrix Workflow

```yaml
name: CI Matrix

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --dev --locked

      - name: Run tests
        run: uv run pytest
```

### Workflow with Cache

```yaml
name: CI with Cache

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --dev --locked

      - name: Run tests
        run: uv run pytest
```

See [github-actions-example.md](../examples/github-actions-example.md) for a complete production workflow.

---

## Docker

### Basic Dockerfile

```dockerfile
FROM python:3.12-slim

# Install UV
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependencies first (layer cache)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --locked --no-dev

# Copy source code
COPY src/ src/

# Execute
CMD ["uv", "run", "python", "-m", "my_project"]
```

### Multi-stage Dockerfile

```dockerfile
# Stage 1: Build
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

# Stage 2: Runtime
FROM python:3.12-slim

COPY --from=builder /app/.venv /app/.venv
COPY src/ /app/src/

ENV PATH="/app/.venv/bin:$PATH"
WORKDIR /app

CMD ["python", "-m", "my_project"]
```

---

## Packaging and Publishing

### Build

```bash
# Simple build
uv build

# Build with cleaning of old artifacts (0.9.6+)
uv build --clear

# Verify generated artifacts
ls dist/
# my-project-0.1.0.tar.gz
# my-project-0.1.0-py3-none-any.whl
```

### Publish to PyPI

```bash
# Publish to PyPI (requires token)
uv publish

# Publish to TestPyPI
uv publish --publish-url https://test.pypi.org/legacy/
```

### GitHub Actions for Publishing

```yaml
name: Publish

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # For trusted publishing
    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4

      - name: Build
        run: uv build --clear

      - name: Publish to PyPI
        run: uv publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

---

## Local Development

### Daily Workflow

```bash
# 1. Clone / pull
git clone <repo>
cd <project>

# 2. Synchronize environment
uv sync --dev

# 3. Quality pipeline
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run pytest

# 4. Develop with hot reload (web)
uv run uvicorn app.main:app --reload

# 5. Before commit
uv run ruff format .
uv run ruff check --fix .
uv run pytest
```

### Pre-commit with UV

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-format
        name: ruff format
        entry: uv run ruff format
        language: system
        types: [python]

      - id: ruff-check
        name: ruff check
        entry: uv run ruff check --fix
        language: system
        types: [python]

      - id: mypy
        name: mypy
        entry: uv run mypy
        language: system
        types: [python]
```

```bash
uv tool install pre-commit
pre-commit install
```
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.663721Z"
evidence_checksum: "8e52f6a"
```
