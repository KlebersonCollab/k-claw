# Example: Complete `pyproject.toml`

Annotated `pyproject.toml` template for modern Python projects with UV.

---

## Complete Template

```toml
# ============================================================
# PROJECT METADATA
# ============================================================
[project]
name = "my-project"
version = "0.1.0"
description = "Concise project description"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"
authors = [
    { name = "Your Name", email = "your@email.com" },
]
keywords = ["python", "uv", "example"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

# ============================================================
# DEPENDENCIES
# ============================================================
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
    "click>=8.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
    "pre-commit>=4.0.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
]

# ============================================================
# ENTRY POINTS (CLI commands)
# ============================================================
[project.scripts]
my-cli = "my_project.cli:main"

# ============================================================
# BUILD SYSTEM
# ============================================================
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

# ============================================================
# TOOL: RUFF (Linter + Formatter)
# ============================================================
[tool.ruff]
line-length = 88
target-version = "py311"
src = ["src"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "TCH",  # flake8-type-checking
]
ignore = [
    "E501",  # line too long (handled by formatter)
]

[tool.ruff.lint.isort]
known-first-party = ["my_project"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

# ============================================================
# TOOL: MYPY (Type Checker)
# ============================================================
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[[tool.mypy.overrides]]
module = ["tests.*"]
disallow_untyped_defs = false

# ============================================================
# TOOL: PYTEST (Testing)
# ============================================================
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-xvs --cov=src/ --cov-report=term-missing"

[tool.coverage.run]
source = ["src"]
omit = ["tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.",
]

# ============================================================
# UV SPECIFIC
# ============================================================
[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-cov>=4.0.0",
    "ruff>=0.8.0",
    "mypy>=1.13.0",
]
```

---

## Usage

```bash
# Install all dependencies
uv sync --dev

# Run tests
uv run pytest

# Verify quality
uv run ruff format --check .
uv run ruff check .
uv run mypy .

# Build
uv build --clear
```

---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:35:33Z"
evidence_checksum: "8e52f6a"
```
