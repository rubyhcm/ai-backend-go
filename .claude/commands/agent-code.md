# Agent Code

Implement the next TODO task from the task list.

## Input
Task override (optional): $ARGUMENTS

## Instructions

Read and follow the agent prompt at `prompts/agent-code.md`.

1. Read `.ai-agents/tasks.md` and find the next task with status `TODO`.
   - If $ARGUMENTS specifies a task ID, implement that task instead.
2. Read `.ai-agents/plan.md`, `.ai-agents/architecture.md` for context.
3. Read all rules in `.rules/`.
4. Create and checkout feature branch: `feature/<task-id>-<short-name>`.
5. Implement the code following all rules and design patterns.
6. Write unit tests (table-driven, with assertions).
7. Verify: `go build ./...`, `go test ./... -race`, `go vet ./...`
8. Commit changes on the feature branch.
9. Create report: `reports/<unix_timestamp>_code_agent.md`
10. Update `.ai-agents/workflow-state.json` with state `"LINTING"`.
