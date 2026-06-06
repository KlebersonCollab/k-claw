# Changelog — YouTube Transcript

All notable changes to this skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.3.0] - 2026-05-06

### Changed
- **Governance Upgrade**: Aligned with SDD v2.3.0 Observable Governance.
- **Metadata Injection**: Added `<!-- @sdd-state -->` to all skill artifacts.
- **Purity Sweep**: Removed local `audit-report.md` in favor of centralized memory.

## [2.0.0] - 2026-05-06

### Changed
- **Governance Upgrade**: Retrofitted to SDD v2.2.0 and Skill Factory v2.2.0 standards.
- **Centralized Memory**: Migrated operational context to `.specs/project/`.
- **Prerequisites**: Aligned with `agent.md` mental and operational checklists.
- **Audit Report**: Standardized validation via `audit-report.md`.

## [1.0.0] - 2026-04-15

### Added
- **SKILL.md**: Main skill definition with decision flow and fallback.
- **README.md**: Overview and usage documentation.
- **Base Structure**: Initial scaffolding following Skills Hub standards.

---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "YT-TRANSCRIPT-ALIGNMENT"
phase: "IMPLEMENT"
status: "COMPLETED"
last_update: "2026-05-06T10:17:00Z"
evidence_checksum: "8e52f6a"
```
