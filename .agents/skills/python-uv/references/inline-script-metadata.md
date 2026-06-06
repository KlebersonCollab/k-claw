# Inline Script Metadata (PEP 723)

Complete guide for self-contained Python scripts with dependencies defined in comments, eliminating the need for `pyproject.toml` for single scripts.

---

## What it is

PEP 723 allows defining dependencies directly in Python script comments. UV reads this metadata and automatically installs dependencies upon execution.

### Syntax

```python
# /// script
# dependencies = [
#   "package-a>=1.0.0",
#   "package-b",
# ]
# requires-python = ">=3.11"
# ///
```

**Syntax rules:**
- `# /// script` — opening marker (exactly like this)
- `# dependencies = [...]` — list of dependencies in TOML format
- `# requires-python = "..."` — Python version (optional)
- `# ///` — closing marker (exactly like this)

---

## Practical Examples

### Web Scraper

```python
# /// script
# dependencies = [
#   "requests>=2.28.0",
#   "beautifulsoup4>=4.12.0",
# ]
# ///

import requests
from bs4 import BeautifulSoup

def scrape(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.title.string if soup.title else "No title"

if __name__ == "__main__":
    title = scrape("https://example.com")
    print(f"Page title: {title}")
```

```bash
uv run scraper.py
```

### API Server (FastAPI)

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "fastapi>=0.100.0",
#   "uvicorn[standard]>=0.24.0",
# ]
# ///

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Quick API")

@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Hello from inline script!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```bash
uv run server.py
# Access http://localhost:8000
```

### CLI Tool with Rich

```python
# /// script
# dependencies = [
#   "typer>=0.9.0",
#   "rich>=13.0.0",
# ]
# ///

import typer
from rich.console import Console
from pathlib import Path

app = typer.Typer()
console = Console()

@app.command()
def process(
    input_dir: Path = typer.Argument(..., help="Input directory"),
    pattern: str = typer.Option("*.txt", help="File pattern"),
) -> None:
    """Process files matching pattern."""
    files = list(input_dir.glob(pattern))
    console.print(f"[green]Found {len(files)} files[/green]")
    for f in files:
        console.print(f"  → {f.name}")

if __name__ == "__main__":
    app()
```

```bash
uv run processor.py ./data --pattern "*.csv"
```

### Data Analysis with Polars

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "polars>=0.19.0",
#   "matplotlib>=3.8.0",
# ]
# ///

import polars as pl
import matplotlib.pyplot as plt
import sys

def analyze(file_path: str) -> None:
    df = pl.read_csv(file_path)
    print(df.describe())

    # Save chart
    data_pd = df.to_pandas()
    data_pd.hist(figsize=(10, 6))
    plt.tight_layout()
    plt.savefig("analysis.png")
    print("Saved analysis.png")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run analyze.py <file.csv>")
        sys.exit(1)
    analyze(sys.argv[1])
```

---

## When to Use vs Not to Use

### ✅ Use inline metadata for:
- Single-file scripts
- Quick utilities and automation
- Shareable examples that "just work"
- Data analysis scripts
- Simple CLIs
- Rapid prototyping

### ❌ DO NOT use for:
- Multi-file projects (use `pyproject.toml`)
- Applications with many dependencies (>10-15 packages)
- Projects with dev/test dependency separation
- Production applications
- Packages for PyPI publication

---

## Best Practices

### Pin dependencies for reproducibility

```python
# ✅ Good — reproducible
# dependencies = [
#   "requests==2.31.0",
#   "pandas==2.1.0",
# ]

# ✅ Good — flexible but secure
# dependencies = [
#   "requests>=2.28.0,<3.0.0",
#   "pandas>=2.0.0",
# ]

# ⚠️ Risky — behavior might change
# dependencies = [
#   "requests",
#   "pandas",
# ]
```

### Organize dependencies

```python
# /// script
# dependencies = [
#   # Web
#   "requests>=2.28.0",
#   "beautifulsoup4>=4.12.0",
#   # Data
#   "pandas>=2.0.0",
#   "numpy>=1.24.0",
# ]
# ///
```

---

## Troubleshooting

### "Failed to parse inline script metadata"

Check exact marker syntax:

```python
# /// script        ← EXACTLY like this (with space)
# dependencies = [
#   "package",      ← Valid TOML format
# ]
# ///               ← EXACTLY like this
```

### "Package not found"

```bash
# Verify name on PyPI
curl https://pypi.org/pypi/package-name/json | head -5
```

### "Requires Python >=3.11 but found 3.10"

```bash
# Install required version
uv python install 3.11

# Execute with specific version
uv run --python 3.11 script.py
```

---

## Performance

| Execution | Time |
|----------|-------|
| First time (download + setup) | 5-30s (depends on deps) |
| Subsequent executions (cache) | <1s |
| After `uv cache clean` | Reverts to first-time duration |
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.665607Z"
evidence_checksum: "8e52f6a"
```
