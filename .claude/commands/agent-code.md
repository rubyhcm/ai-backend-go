# Agent Code

> **Model:** `claude-sonnet-4-6`
> Run with: `claude --model claude-sonnet-4-6` or switch via `/model claude-sonnet-4-6`

Implement the next TODO task from the task list.

## Input
Task override (optional): $ARGUMENTS

## Instructions

Read and follow the agent prompt at `prompts/agent-code.md`.

1. Determine which task to implement (priority order):
   - If `$ARGUMENTS` specifies a task ID → use that task.
   - Else read `current_task` from `.ai-agents/workflow-state.json`:
     - If `current_task` is set and its `**Status:**` in `tasks.md` is `TODO` → use it.
     - Else → scan `tasks.md` top-to-bottom and pick the first task with `**Status:** TODO`.
2. Read `.ai-agents/plan.md`, `.ai-agents/architecture.md` for context.
3. Read all rules in `.rules/`.
4. Implement the code following all rules and design patterns.
6. Write unit tests (table-driven, with assertions).
7. Verify: `go build ./...`, `go test ./... -race`, `go vet ./...`
8. Do NOT commit or stage changes.
9. Create report: `reports/<unix_timestamp>_code_agent.md`
10. Update `.ai-agents/workflow-state.json`: set `state` to `"LINTING"`, set `current_task` to this task's ID.

## Next Steps

```
✅ Code written → Run Agent Lint to format and check:

  /agent-lint

⚠️  If build fails before linting:
  /agent-fix "<error message>"
```
