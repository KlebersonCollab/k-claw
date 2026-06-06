# Tool Management

Complete guide on `uv tool install` vs `uvx` — when to use each, feature matrix, and maintenance workflows.

---

## Quick Decision Guide

| Scenario | Use | Why |
|---------|------|---------|
| Install black/ruff for daily use | `uv tool install black` | Persistent, no overhead |
| Test a new tool | `uvx tool` | Temporary, no installation |
| Run MCP server | `uvx mcp-server-sqlite` | Community standard |
| Install dev tools | `uv tool install pytest` | Frequent use |
| Compare versions | `uvx package@1.0.0` | Easy version switching |
| Local project script | `uvx --from . script.py` | One-off execution |

---

## `uv tool install` — Persistent Installation

### Basic Commands

```bash
# Install from PyPI
uv tool install package

# Specific version
uv tool install package==1.2.3

# From git repository
uv tool install git+https://github.com/user/repo.git

# With extras
uv tool install "package[extra1,extra2]"

# Editable install (local dev)
uv tool install -e .
```

### Management

```bash
# List installed tools
uv tool list

# Upgrade a tool
uv tool upgrade package

# Upgrade all
uv tool upgrade --all

# Uninstall
uv tool uninstall package

# Force reinstallation
uv tool install package --force
```

### Recommended Tools

```bash
# Development
uv tool install ruff       # Linter + formatter
uv tool install mypy       # Type checker
uv tool install pytest     # Testing

# Utilities
uv tool install httpie     # HTTP client
uv tool install rich-cli   # Terminal formatting
uv tool install pre-commit # Git hooks
```

---

## `uvx` — Temporary Execution

### Basic Commands

```bash
# Execute from PyPI
uvx package

# Specific version
uvx package@1.2.3

# With arguments
uvx package arg1 arg2 --flag

# From local project
uvx --from /path/to/project script.py

# From current directory
uvx --from . script.py
```

### Use Cases

```bash
# MCP Servers
uvx mcp-server-sqlite --db-path /path/to/db
uvx mcp-server-git --repository /path/to/repo

# Version testing
uvx black@22.0.0 --check .
uvx black@23.0.0 --check .
uvx black@24.0.0 --check .

# Local scripts
uvx --from . scripts/setup_db.py
uvx --from . scripts/generate_docs.py
```

---

## Feature Matrix

| Feature | `uv tool install` | `uvx` |
|---------|-------------------|-------|
| **Persistence** | Permanent | Temporary (cache) |
| **Use Case** | Daily tools | One-off execution |
| **Speed** | Instant (already installed) | Setup on 1st execution |
| **Versioning** | Reinstall to change | Easy (`@version`) |
| **Storage** | Persistent disk | Managed cache |
| **Update** | `uv tool upgrade` | Automatic with `@latest` |
| **Local dev** | `uv tool install -e .` | `uvx --from .` |

---

## Maintenance

### Weekly Routine

```bash
# Check installed tools
uv tool list

# Upgrade all
uv tool upgrade --all

# Clean old cache
uv cache clean

# Remove unused tools
uv tool uninstall old-tool
```

### Document Team Tools

Create a `tools.txt` file for consistency:

```text
# Development tools
ruff==0.8.0
mypy==1.13.0
pytest==8.3.0

# Utilities
httpie==3.2.0
pre-commit==4.0.0
```

Install all:

```bash
cat tools.txt | grep -v '^#' | grep -v '^$' | xargs -n1 uv tool install
```

---

## Anti-Patterns

| ❌ Wrong | ✅ Correct | Why |
|-----------|-----------|---------|
| `pip install black` global | `uv tool install black` | Avoids dependency conflicts |
| `uv tool install mcp-server` | `uvx mcp-server` | MCP community standard |
| `uvx black .` daily | `uv tool install black` | Avoids setup overhead |
| Mixing `pip` and `uv tool` | Pick one | Avoids conflicts |
| Never updating tools | Weekly `uv tool upgrade --all` | Security and features |

---

## Troubleshooting

### Tool not found after installation

```bash
# Check PATH
echo $PATH | tr ':' '\n' | grep -i uv

# Add to PATH
export PATH="$HOME/.local/bin:$PATH"
```

### Dependency conflict

```bash
uv tool uninstall package
uv cache clean
uv tool install package
```

### UVX fails with local package

```bash
# Check that pyproject.toml exists
ls /path/to/project/pyproject.toml

# Use absolute path with --from
uvx --from /absolute/path/to/project script.py
```
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.666082Z"
evidence_checksum: "8e52f6a"
```
