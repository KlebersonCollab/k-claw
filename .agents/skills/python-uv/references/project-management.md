# Project Management

Complete guide for initialization, dependency management, lockfiles, project structure, and quality tools with UV.

---

## Project Initialization

### Create a new project

```bash
uv init my-project
cd my-project
```

Generated structure:

```
my-project/
├── .python-version      # Fixed Python version
├── pyproject.toml       # Project configuration
├── README.md
└── src/
    └── my_project/
        └── __init__.py
```

### Initialize an existing project

```bash
cd existing-project
uv init --pyproject       # Generates pyproject.toml
```

---

## pyproject.toml

`pyproject.toml` is the **single source of truth** for the project:

```toml
[project]
name = "my-project"
version = "0.1.0"
description = "My Python project"
requires-python = ">=3.11"
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
    "pytest-cov>=4.0.0",
]

[project.scripts]
my-cli = "my_project.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.ruff.format]
quote-style = "double"

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-xvs"
```

See [pyproject-toml-example.md](../examples/pyproject-toml-example.md) for a complete annotated template.

---

## Dependency Management

### Add

```bash
# Production dependency
uv add requests pydantic

# Development dependency
uv add --dev pytest ruff mypy

# Specific version dependency
uv add "requests>=2.31.0,<3.0.0"

# Optional dependency (group)
uv add --optional test pytest-cov
```

### Remove

```bash
uv remove requests
uv remove --dev pytest-cov
```

### Synchronize

```bash
# Install everything from pyproject.toml
uv sync

# Including development dependencies
uv sync --dev

# From lockfile (exact reproduction)
uv sync --locked

# Recreate environment from scratch
uv sync --recreate
```

### Inspect

```bash
# Dependency tree
uv tree

# Reverse dependencies (who depends on what)
uv tree --reverse

# List installed packages
uv pip list
```

---

## Lockfile (`uv.lock`)

The lockfile ensures **exact reproduction** of the environment:

```bash
# Generate/update lockfile
uv lock

# Synchronize from lockfile
uv sync --locked
```

**Rules:**
- ✅ **Always version** `uv.lock` in git
- ✅ **Use `--locked`** in CI/CD for reproducible builds
- ❌ **Never edit** `uv.lock` manually

---

## Recommended Project Structure

### Src Layout (Recommended)

```
my-project/
├── pyproject.toml
├── uv.lock
├── README.md
├── .gitignore
├── .python-version
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── core.py
│       ├── models.py
│       └── utils.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_core.py
│   └── test_models.py
└── scripts/
    └── deploy.py
```

### .gitignore for UV projects

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/

# Virtual Environment
.venv/

# IDE
.idea/
.vscode/
*.swp

# DO NOT ignore uv.lock — always version it!
# uv.lock  ← DON'T do this
```

---

## Workspaces (Monorepo)

```toml
# pyproject.toml at monorepo root
[tool.uv.workspace]
members = ["packages/*"]
```

```
monorepo/
├── pyproject.toml          # Workspace root
├── uv.lock                 # Shared lockfile
└── packages/
    ├── core/
    │   ├── pyproject.toml
    │   └── src/
    ├── api/
    │   ├── pyproject.toml
    │   └── src/
    └── cli/
        ├── pyproject.toml
        └── src/
```

---

## Quality Tools

### Ruff (Linter + Formatter)

```bash
# Install as dev dependency
uv add --dev ruff

# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Auto-fix
uv run ruff check --fix .
```

### mypy (Type Checking)

```bash
uv add --dev mypy

# Run type checking
uv run mypy .
```

### pytest (Testing)

```bash
uv add --dev pytest pytest-cov

# Run tests
uv run pytest

# With coverage
uv run pytest --cov=src/

# Specific tests
uv run pytest tests/test_core.py -xvs
```

### Complete quality workflow

```bash
# Execute entire quality pipeline
uv run ruff format --check .
uv run ruff check .
uv run mypy .
uv run pytest --cov=src/
```
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.664964Z"
evidence_checksum: "8e52f6a"
```
