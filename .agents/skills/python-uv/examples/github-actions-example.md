# Example: Complete GitHub Actions CI/CD

Production workflow with version matrix, caching, quality checks, and automatic publishing.

---

## CI Workflow (Validation on PRs and Pushes)

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # ────────────────────────────────────────────
  # Quality Checks
  # ────────────────────────────────────────────
  quality:
    name: Quality Checks
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

      - name: Check formatting
        run: uv run ruff format --check .

      - name: Check linting
        run: uv run ruff check .

      - name: Type check
        run: uv run mypy .

  # ────────────────────────────────────────────
  # Tests with Version and OS Matrix
  # ────────────────────────────────────────────
  test:
    name: Test (Python ${{ matrix.python-version }}, ${{ matrix.os }})
    needs: quality
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.11", "3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --dev --locked

      - name: Run tests
        run: uv run pytest --cov=src/ --cov-report=xml

      - name: Upload coverage (Ubuntu only)
        if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.12'
        uses: codecov/codecov-action@v4
        with:
          file: coverage.xml
          token: ${{ secrets.CODECOV_TOKEN }}
```

---

## CD Workflow (Publishing on Release Creation)

```yaml
name: Publish

on:
  release:
    types: [published]

jobs:
  publish:
    name: Build & Publish
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # For trusted PyPI publishing

    steps:
      - uses: actions/checkout@v4

      - name: Install UV
        uses: astral-sh/setup-uv@v4

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --locked

      - name: Build distribution
        run: uv build --clear

      - name: Publish to PyPI
        run: uv publish
        env:
          UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/
```

---

## Tips

### Efficient Caching
`astral-sh/setup-uv@v4` with `enable-cache: true` automatically caches packages between runs, significantly reducing CI time.

### `--locked` is Essential
Always use `uv sync --locked` in CI to ensure exact reproduction. If the lockfile is out of date, CI will fail — forcing an explicit update.

### Optimized Matrix
Quality checks run once (no matrix needed). Heavy tests run in a matrix for cross-platform validation.

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
