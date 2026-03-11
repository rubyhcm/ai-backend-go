# Agent Task

> **Model:** `claude-sonnet-4-6`
> Run with: `claude --model claude-sonnet-4-6` or switch via `/model claude-sonnet-4-6`

Break down the existing plan into implementable tasks.

## Instructions

Read and follow the agent prompt at `prompts/agent-task.md`.

1. Read `.ai-agents/plan.md` and `.ai-agents/architecture.md`.
2. Read relevant rules in `.rules/`.
3. Break the plan into ordered, implementable tasks.
4. Generate: `.ai-agents/tasks.md`
5. Create report: `reports/<unix_timestamp>_task_agent.md`
6. Update `.ai-agents/workflow-state.json` with state `"CODING"`.

## Next Steps

```
✅ Tasks generated → Run Agent Code to implement the first task:

  /agent-code

💡 To implement a specific task:
  /agent-code task-1
```
