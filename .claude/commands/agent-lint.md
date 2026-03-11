# Agent Lint

> **Model:** `claude-sonnet-4-6`
> Run with: `claude --model claude-sonnet-4-6` or switch via `/model claude-sonnet-4-6`

Format and lint check all changed Go files.

## Instructions

Read and follow the agent prompt at `prompts/agent-lint.md`.

1. Identify changed `.go` files via `git diff`.
2. Read `.rules/go.md` for conventions.
3. Run `gofmt -w` and `goimports -w` on changed files.
4. Run `go vet ./...`.
5. Run `golangci-lint run --config .golangci.yml`.
6. Auto-fix formatting issues. Document non-fixable issues.
7. Create report: `reports/<unix_timestamp>_lint_agent.md`
8. Update `.ai-agents/workflow-state.json` with state `"SECURITY_SCANNING"`.

## Next Steps

```
✅ Lint passed → Run security scan with auto-fix (recommended):

  /agent-security-fix

💡 Or scan only (no auto-fix):
  /agent-security

⚠️  If lint has unfixable errors:
  /agent-fix "<lint error>"
```
