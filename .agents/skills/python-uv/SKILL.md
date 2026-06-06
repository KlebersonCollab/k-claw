---
name: python-uv
description: Expert in the modern Python ecosystem with UV, focused on performance (Django/Async), security, and SDD v2.3.0 governance.
version: 4.0.0
tags: [python, uv, django, async, performance, devops]
---

# Python UV Expert

This skill governs the development of high-performance Python applications using `uv` as the primary execution and management engine. It integrates advanced Django patterns, asynchronous development, and strict compliance with the **SDD (Spec-Driven Development)** framework.

## 🔒 Prerequisites (Mandatory)

This skill operates WITHIN the **SDD** framework. Before starting any technical execution:
0. **Mode Check**: Verify the current operational mode (`.hub-mode`) and apply `token-distiller` guidelines.
1. **Context Check**: Have you rehydrated the context by reading `STATE.md`, `MEMORY.md`, and `LEARNINGS.md` in `.specs/project/`?
2. **Knowledge Check**: Follow the **Knowledge Verification Chain** (see below).

---

## 🧩 Delegation Matrix

This skill maps development phases to specialized technical references to ensure structural integrity:

| Phase | Resource / Protocol | Primary Artifact | Purpose |
|---|---|---|---|
| **DISCOVERY** | `references/python-environment.md` | `pyproject.toml` | Environment mapping and stack selection (Python 3.14+). |
| **SPECIFY** | `references/patterns.md`, `django-workflow.md` | `spec.md`, `plan.md` | Architectural design, ORM optimization, and Service Layer. |
| **IMPLEMENT** | `references/testing.md`, `async-development.md` | Tested Code | Implementation with TDD, atomic commits, and `uv run`. |
| **VERIFY** | `references/ci-cd-workflows.md` | CI/CD Logs | Final audit against performance and security benchmarks. |

---

## 🔄 4-Phase Workflow

### 1. DISCOVERY
*   **Goal**: Define the environment and dependency baseline.
*   **Action**: Use `uv sync` to align with the lockfile. Check for Python 3.14/Free-threading requirements.
*   **Output**: Verified `uv.lock` and project structure.

### 2. SPECIFY
*   **Goal**: Design the technical solution (Specs & Plan).
*   **Action**: Define ORM schemas (avoiding N+1) and service boundaries. Establish `pyproject.toml` requirements.
*   **Output**: `spec.md` and `plan.md` with **Mermaid** diagrams.

### 3. IMPLEMENT
*   **Goal**: Deliver tested, high-performance code.
*   **Action**: Apply Red-Green-Refactor with `pytest`. Use `uv run` for all execution. Implement async for I/O.
*   **Output**: Atomic commits referencing task IDs.

### 4. VERIFY
*   **Goal**: Ensure production readiness and compliance.
*   **Action**: Validate through GitHub Actions (`setup-uv`). Perform security/performance audit.
*   **Output**: Updated `LEARNINGS.md` with performance gains or solved bottlenecks.

---

## 🚀 Core Knowledge: UV & Environment Management

`uv` is the "Source of Truth" for the environment. It replaces pip, poetry, pyenv, and pipx with Rust-powered performance.

### 1. Version Management (Python 3.14+)
- **New Standard**: As of UV 0.9.6, the standard is **Python 3.14**.
- **Free-Threading (PEP 703)**: Native support for Python 3.14t (no-GIL) for true multi-core parallelism.
- **Commands**:
    - `uv python install 3.14` (Installation)
    - `uv python pin 3.14` (Pins the version in the project via `.python-version`)
    - `uv run --python 3.14t script.py` (Execution in free-threaded mode)

### 2. Project and Dependency Management
- **Initialization**: `uv init project-name` (Recommended `src/` layout structure).
- **Synchronization**: `uv sync --dev --locked` (Ensures total parity with `uv.lock`).
- **Adding Packages**:
    - `uv add requests` (Production)
    - `uv add --dev ruff mypy pytest` (Development)
    - `uv add --optional group-name package` (Optional dependencies)

### 3. PEP 723: Inline Scripts
For automations and single-file tools, use inline metadata:
```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "rich"]
# ///
import httpx
# ... logic here
```
Execute with: `uv run script.py`.

---

## 🏗️ Expert Domain: Django Professional

Focused on enterprise scalability and eliminating common bottlenecks.

### 1. ORM Performance (N+1 Resolution)
- **Golden Rule**: NEVER perform queries inside loops.
- **select_related**: Use for Foreign Keys and One-to-One (SQL JOIN).
- **prefetch_related**: Use for Many-to-Many and reverse relations (Separate queries with IN).
- **Bulk Ops**: Use `bulk_create` and `bulk_update` for mass operations.

### 2. Service Layer & Architecture
- **Fat Models/Views are Prohibited**: Move complex business logic to `services.py`.
- **Secure Querysets**: Always filter by `owner` or `tenant` in `get_queryset` to prevent **BOLA/IDOR**.

### 3. Async Django (ASGI)
- Use asynchronous views (`async def`) for blocking I/O operations (external API calls).
- Recommended engine: `uvicorn` via `uv run`.

---

## ⚡ Expert Domain: Async Mastery

### 1. Concurrency Patterns
- **gather**: Execute multiple tasks simultaneously.
- **Semaphores**: Limit concurrency to protect external resources.
```python
sem = asyncio.Semaphore(10)
async with sem:
    await call_external_api()
```
- **uvloop**: Utilize for performance gains of 2-4x on Linux/macOS.

### 2. Testing Async
- Configure `pytest-asyncio` in `pyproject.toml` with `asyncio_mode = "auto"`.

---

## 🛠️ Operational Workflows

### 1. Quality Pipeline (TDD)
Follow the **Red-Green-Refactor** cycle:
1. `uv add --dev pytest pytest-cov`
2. Write the test in `tests/`.
3. Run: `uv run pytest`.
4. Implement the minimum code.
5. Refactor.

### 2. CI/CD & Docker
- **GitHub Actions**: Use `astral-sh/setup-uv@v4` with `enable-cache: true`.
- **Docker**: Use multi-stage builds to keep images light, copying only the `.venv`.

---

## 🛠️ Operational Protocols

### 1. Knowledge Verification Chain
To prevent pattern drift and ensure technical excellence, follow this hierarchy:
1.  **Environment State**: Current `uv sync` status and `pyproject.toml` configurations.
2.  **Internal Specs**: Project-specific `spec.md`, `plan.md`, and `tasks.md`.
3.  **Expert References**: Local domain guides in `python-uv/references/`.
4.  **Global Mandates**: `.specs/codebase/GLOBAL_MANDATES.md`.
5.  **Official Documentation**: Astral (uv), Django, and Python (3.14+) official sources.

### 2. The Gated Workflow Mandate
Phase transitions (e.g., Specify to Implement) require 100% task completion and metadata synchronization in `STATE.md`.

### 3. Safety Valve
If `uv sync` fails or dependency conflicts arise during implementation, **STOP** and re-evaluate the `pyproject.toml` design.

---

## 🔒 Prohibitive Mandates & Anti-Patterns

- **NEVER** use `pip install` globally. Use `uv tool install` for tools or `uv venv` for projects.
- **NEVER** ignore the `uv.lock` file. It must be versioned in Git.
- **NEVER** execute management commands without the `uv run` prefix (e.g., `uv run python manage.py migrate`).
- **NEVER** use mutable default arguments (`list`, `dict`) in functions.
- **AVOID** using `type()` for checking; prefer `isinstance()`.

---

## 📚 References & Resources

- [Installation & Setup](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/references/installation-and-setup.md)
- [Project Management](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/references/project-management.md)
- [Django Workflow (Performance & Pro)](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/references/django-workflow.md)
- [Async Development Mastery](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/references/async-development.md)
- [Advanced Patterns & Protocols](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/references/patterns.md)
- [Python Environment (3.14 & Free-threading)](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/references/python-environment.md)
- [Testing Standards (TDD)](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/references/testing.md)
- [CI/CD & Docker Workflows](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/references/ci-cd-workflows.md)
- [Tool Management (uv tool)](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/references/tool-management.md)
- [PEP 723 Metadata (Inline Scripts)](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/references/inline-script-metadata.md)

### 📋 Templates & Examples
- [Template: pyproject.toml](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/resources/pyproject-template.toml)
- [Example: pyproject.toml](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/examples/pyproject-toml-example.md)
- [Example: GitHub Actions](file:///Users/klebersonromero/Projetos/Kleberson/skills/python-uv/examples/github-actions-example.md)
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.662256Z"
evidence_checksum: "8e52f6a"
```
