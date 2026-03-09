# Agent Fix

Fix bugs based on error messages, logs, or review feedback.

## Input
Error/issue: $ARGUMENTS

## Instructions

Read and follow the agent prompt at `prompts/agent-fix.md`.

1. Read the error/issue provided:
   - If $ARGUMENTS is provided: use as the error description.
   - If no arguments: read latest review from `.ai-agents/reviews/` for issues to fix.
2. Read `.rules/go.md`, `.rules/security.md`, `.rules/testing.md`.
3. Read `.ai-agents/knowledge/bugs-history.md` for past context.
4. Analyze the error: parse message, identify file & line, trace code flow.
5. Identify root cause (distinguish symptom vs root cause).
6. Write regression test FIRST (reproduce the bug).
7. Apply minimal code fix.
8. Verify: `go build ./...`, `go test ./... -race`, `go vet ./...`
9. Document in `.ai-agents/knowledge/bugs-history.md`.
10. Create report: `reports/<unix_timestamp>_fix_agent.md`
11. Update `.ai-agents/workflow-state.json` with state `"LINTING"`, increment `loop_count`.
