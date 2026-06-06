# Installation & Setup

Complete guide for UV installation and Python environment configuration on all platforms.

---

## Installation

### macOS

```bash
# Homebrew (Recommended)
brew install uv

# Standalone installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Linux

```bash
# Standalone installer (Recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Via pipx (if you already have Python)
pipx install uv
```

### Windows

```powershell
# PowerShell (Recommended)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Via pip (if you already have Python)
pip install uv
```

### Verification

```bash
uv --version
uvx --version
# Should display something like: uv 0.9.7
```

---

## Virtual Environment Setup

### Method 1: UV Project (Recommended for new projects)

```bash
# UV creates and manages venv automatically
uv init my-project
cd my-project
uv sync  # creates .venv automatically
uv run python -c "print('Hello UV!')"
```

### Method 2: Manual with venv

```bash
# Create venv manually
python -m venv .venv

# Activate (macOS / Linux)
source .venv/bin/activate

# Activate (Windows Git Bash)
. .venv/Scripts/activate

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Install packages with UV inside the venv
uv pip install requests numpy pandas
```

### Method 3: UV without activating (Recommended for automation)

```bash
# Execute directly without activating venv
uv run python script.py
uv run pytest
uv run ruff check .
```

---

## PATH Configuration

If UV is not found after installation:

### macOS / Linux

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$HOME/.local/bin:$PATH"

# Reload configuration
source ~/.zshrc  # or source ~/.bashrc
```

### Windows

```powershell
# Check if it's in the PATH
$env:PATH -split ';' | Select-String "uv"

# Add manually if necessary
$env:PATH += ";$env:LOCALAPPDATA\Programs\uv"
```

---

## Troubleshooting

### UV not found after installation

```bash
# Check location
which uv           # macOS/Linux
where.exe uv       # Windows

# If not found, reinstall
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Venv does not activate

```bash
# Check if activation script exists
ls .venv/bin/activate        # macOS/Linux
ls .venv/Scripts/activate    # Windows

# If it doesn't exist, recreate
rm -rf .venv
uv venv .venv
# or
python -m venv .venv
```

### Permissions denied

```bash
# macOS/Linux
chmod +x ~/.local/bin/uv
chmod +x ~/.local/bin/uvx
chmod -R u+w ~/.cache/uv/
```

---

## Quick Reference Card

```bash
# Installation
curl -LsSf https://astral.sh/uv/install.sh | sh    # Linux/Mac
brew install uv                                      # macOS Homebrew

# New project
uv init my-project && cd my-project

# Dependencies
uv add requests pydantic
uv add --dev pytest ruff mypy
uv sync

# Execute
uv run python main.py
uv run pytest

# Global tools
uv tool install ruff
uv tool install mypy

# Python version
uv python install 3.12
uv python pin 3.12
```
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.666298Z"
evidence_checksum: "8e52f6a"
```
