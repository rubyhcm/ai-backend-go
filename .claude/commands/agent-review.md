# Agent Review

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
7. Update `.ai-agents/workflow-state.json`:
   - If APPROVED → increment `completed_tasks`, reset `loop_count` to 0
     - If all tasks done (`completed_tasks` == `total_tasks`) → state `"DONE"`
     - Else → state `"CODING"` (proceed to next task)
   - If NEEDS CHANGES → state `"FIXING"`, increment `loop_count`
