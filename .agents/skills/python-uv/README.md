# Python with UV — Skill

Extremely fast Python package and project manager, written in Rust. Replaces pip, pipx, poetry, pyenv, and more.

---

## 🚀 Overview

This skill guides modern Python development using `uv`. It covers everything from initializing simple projects to complex enterprise architectures (Django Pro), ensuring extreme performance and security.

### Core Capabilities:
- **Project Management**: Initialization (`uv init`), dependencies, and lockfiles.
- **Django Pro**: Service Layer patterns, Async Django, and Bulk Operations.
- **Performance Optimization**: N+1 Resolution (ORM), Profiling, and Memory Management.
- **Async Development**: Patterns for FastAPI, httpx, and asynchronous testing.
- **Security**: BOLA/IDOR auditing and integrated security tools.
- **PEP 723 Scripts**: Execution of single-file scripts with declared dependencies.

---

## 📂 Skill Structure

```text
python-uv/
├── SKILL.md                 # Definition and workflow (v4.0.0 Purist)
├── README.md                # This guide
├── CHANGELOG.md             # Version history
├── references/              # Detailed References (Django, Async, Setup, etc.)
├── examples/                # Practical Examples (CI/CD, pyproject, patterns)
└── resources/               # Templates and Assets
```

---

## 🛠️ How to Use

1. **Start a project**: `uv init my-app`
2. **Optimize your Django**: Consult `references/django-workflow.md` for N+1 patterns.
3. **Analyze Performance**: Use `uv run python manage.py shell_plus --print-sql`.

---

## 🎯 Command Examples

- *"Refactor this Django view to resolve the N+1 queries issue using select_related."*
- *"Set up a Service Layer for this Django project managed by uv."*
- *"How do I use uv to run bandit and audit my project's security?"*
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "python-uv-alignment"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T13:12:14.662837Z"
evidence_checksum: "8e52f6a"
```
