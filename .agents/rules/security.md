# Security & Data Privacy

- **Secrets**: Never hardcode API keys, passwords, or tokens. Use `.env` or environment variables.
- **Redaction**: Always use `redact_sensitive_info` when logging or displaying external data.
- **Path Safety**: Validate all file paths against the `PathFilter` before performing disk I/O.
- **Permissions**: Respect the current permission level (`read`, `write`, `execute`) and never escalate without orchestrator approval.
