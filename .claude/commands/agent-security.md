# Agent Security

> **Model:** `claude-sonnet-4-6`
> Run with: `claude --model claude-sonnet-4-6` or switch via `/model claude-sonnet-4-6`

Scan changed code for security vulnerabilities.

## Instructions

Read and follow the agent prompt at `prompts/agent-security.md`.

1. Identify changed `.go` files via `git diff`.
2. Read `.rules/security.md`.
3. Run `gosec ./...` and `govulncheck ./...`.
4. Perform AI security review against OWASP Top 10 (2025).
5. Check Go-specific security issues (JSON injection, goroutine leaks, SQL injection, etc.).
6. Create report: `reports/<unix_timestamp>_security_agent.md`
7. Update `.ai-agents/workflow-state.json` with state `"REVIEWING"`.

## Next Steps

```
✅ CLEAN (no CRITICAL/HIGH) → Run Agent Review:

  /agent-review

⚠️  Has CRITICAL or HIGH findings → Auto-fix and re-scan:

  /agent-security-fix
```
