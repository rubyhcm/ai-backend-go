# Agent Review

> **Model:** `claude-sonnet-4-6`
> Run with: `claude --model claude-sonnet-4-6` or switch via `/model claude-sonnet-4-6`

Review code changes for quality, architecture, and design compliance.

## Instructions

Read and follow the agent prompt at `prompts/agent-review.md`.

1. Read all rules in `.rules/`.
2. Read `.ai-agents/plan.md`, `.ai-agents/tasks.md`, `.ai-agents/architecture.md`.
3. Read latest lint report and security report from `reports/`.
4. Review all changed files for:
   - Architecture compliance (layer rules, dependency direction)
   - SOLID compliance
   - Design patterns compliance
   - Code quality (error handling, naming, performance)
   - Testing quality (coverage, assertions)
   - Business logic correctness (matches plan/task requirements)
5. Save review to `.ai-agents/reviews/review-<N>.md`.
6. Create report: `reports/<unix_timestamp>_review_agent.md`
7. Update task status and workflow state:
   - If APPROVED:
     - In `.ai-agents/tasks.md`: set current task `**Status:** DONE`
     - Scan `tasks.md` for next task with `**Status:** TODO`
     - In `workflow-state.json`: increment `completed_tasks`, reset `loop_count`
       - If next TODO task found: set `current_task` to its ID, set state `"CODING"`
       - If no TODO remaining: set `current_task` to `""`, set state `"DONE"`
   - If NEEDS CHANGES:
     - In `.ai-agents/tasks.md`: set current task `**Status:** IN_PROGRESS`
     - In `workflow-state.json`: set state `"FIXING"`, increment `loop_count`

## Next Steps

```
✅ APPROVED (more tasks remain) → Implement next task:

  /agent-code

✅ APPROVED (all tasks done) → Pipeline complete! State = DONE.
   Review final reports in reports/ before merging.

⚠️  NEEDS CHANGES → Fix issues then re-lint:

  /agent-fix
  /agent-lint

⚠️  loop_count > 3 → Escalated. Read reports/*_review_agent.md
    and fix manually:

  /agent-fix "<specific issue>"
```
