# Python Environment

Complete guide for Python version management, Python 3.14 default, free-threaded Python, and platform-specific paths.

---

## Python Version Management

### Essential Commands

```bash
# List available versions
uv python list

# List installed versions
uv python list --installed

# Install a specific version
uv python install 3.12
uv python install 3.13
uv python install 3.14

# Pin a version for the project
uv python pin 3.12

# Check the pinned version
cat .python-version
```

### Execute with a specific version

```bash
# Run script with a specific Python
uv run --python 3.12 script.py

# Create venv with a specific version
uv venv --python 3.12 .venv
```

---

## Python 3.14 — New Default (UV 0.9.6+)

Starting from UV 0.9.6, `uv python install` without a version installs **Python 3.14** (previously it was 3.13).

### Impact

```bash
# Before (UV < 0.9.6)
uv python install    # → Python 3.13

# Now (UV 0.9.6+)
uv python install    # → Python 3.14
```

### Migration

If the project requires Python 3.13 or earlier:

```bash
# Pin version in the project
uv python pin 3.13

# Install specific version
uv python install 3.13

# Verify
cat .python-version
# Output: 3.13
```

---

## Free-Threaded Python (PEP 703)

Python 3.14+ supports **free-threading** — real parallel execution without the GIL (Global Interpreter Lock).

### What changes

- **Before**: GIL prevented Python threads from executing code in parallel
- **Now**: Free-threaded Python allows true multi-core parallelism

### How to use

```bash
# UV 0.9.6+ — free-threaded is automatic for 3.14+
uv python install 3.14

# Or explicitly
uv python install 3.14t
```

### Example

```python
# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///

import threading
import time

def cpu_task(n: int) -> int:
    """CPU-intensive task."""
    return sum(i ** 2 for i in range(n))

# With free-threaded Python, these threads run in parallel
threads = []
for i in range(4):
    t = threading.Thread(target=cpu_task, args=(10_000_000,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Threads executed in parallel!")
```

### When to use

- ✅ CPU-intensive code with multi-threading
- ✅ Performance-critical parallel processing
- ⚠️ Check library compatibility before using in production

---

## Platform-Specific Paths

### UV Cache

| Platform | Path |
|------------|---------|
| macOS | `~/Library/Caches/uv/` |
| Linux | `~/.cache/uv/` |
| Windows | `%LOCALAPPDATA%\uv\cache\` |

### Installed Tools

| Platform | Path |
|------------|---------|
| macOS / Linux | `~/.local/share/uv/tools/` |
| Windows | `%APPDATA%\uv\tools\` |

### Python Binaries

| Platform | Path |
|------------|---------|
| macOS / Linux | `~/.local/share/uv/python/` |
| Windows | `%APPDATA%\uv\python\` |

### Cache Management

```bash
# Check cache size
du -sh ~/.cache/uv/          # macOS/Linux
dir /s %LOCALAPPDATA%\uv\cache  # Windows

# Clean cache
uv cache clean

# Cache info
uv cache info
```

---

## Compatibility

| UV Version | Python 3.10 | Python 3.11 | Python 3.12 | Python 3.13 | Python 3.14 | Free-Threading |
|------------|-------------|-------------|-------------|-------------|-------------|----------------|
| 0.9.0-0.9.5 | ✅ | ✅ | ✅ | ✅ (default) | Beta | Experimental |
| 0.9.6+ | ✅ | ✅ | ✅ | ✅ | ✅ (default) | Stable |
| 0.9.7+ | ✅ | ✅ | ✅ | ✅ | ✅ (default) | Stable |
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.665826Z"
evidence_checksum: "8e52f6a"
```
