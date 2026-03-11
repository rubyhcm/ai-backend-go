# Full AI Agent Pipeline

> **Model routing:**
> - Step 1 (PLANNING): `claude-opus-4-6` — deep reasoning for architecture
> - Steps 2–4 (TASKING → REVIEWING): `claude-sonnet-4-6` — fast execution
>
> Switch model before each step: `/model claude-opus-4-6` or `/model claude-sonnet-4-6`

You are the Workflow Orchestrator. Execute the FULL agent pipeline for the given requirement.

## Input
Requirement: $ARGUMENTS

## Instructions

Read and follow the orchestrator prompt at `prompts/orchestrator.md`.

Execute the full pipeline in this exact order:

### Step 1: PLANNING
> Switch to Opus: `/model claude-opus-4-6`
- Read `prompts/agent-plan.md` and execute Agent Plan.
- If the input is a `.md` file path, read the file content first.
- Generate: `.ai-agents/plan.md`, `.ai-agents/architecture.md`, `.ai-agents/tests-plan.md`
- Create report: `reports/<unix_timestamp>_plan_agent.md`

### Step 2: TASKING
> Switch to Sonnet: `/model claude-sonnet-4-6`
- Read `prompts/agent-task.md` and execute Agent Task.
- Generate: `.ai-agents/tasks.md`
- Create report: `reports/<unix_timestamp>_task_agent.md`

### Step 3: For each task in tasks.md (in order):

#### 3a: CODING + LINT (inline)
- Read `prompts/agent-code.md` and execute Agent Code for the current task.
- Agent Code runs lint inline: gofmt, goimports, golangci-lint on changed files.
- Create report: `reports/<unix_timestamp>_code_agent.md`

#### 3b: SECURITY SCANNING + AUTO-FIX
- Read `prompts/agent-security.md` and execute Agent Security.
- Scan changed files for vulnerabilities (gosec, govulncheck, Semgrep, Snyk).
- Create report: `reports/<unix_timestamp>_security_agent.md`
- **If CRITICAL or HIGH findings found:**
  - Set state to `SECURITY_FIXING`, increment `security_fix_count`
  - If `security_fix_count > 3`: ESCALATE to user, stop pipeline entirely
  - Read `prompts/agent-fix-security.md` and execute Agent Fix Security
  - Agent Fix Security fixes CRITICAL findings first, then HIGH (lint runs inline)
  - Create report: `reports/<unix_timestamp>_fix_security_agent.md`
  - Re-run Agent Security (back to step 3b) to verify fixes
  - Repeat until CLEAN or max attempts exceeded
- **If CLEAN (no CRITICAL/HIGH):** Set state to `REVIEWING`, proceed to 3c

#### 3c: REVIEWING
- Read `prompts/agent-review.md` and execute Agent Review.
- Review all changes including security reports.
- Create report: `reports/<unix_timestamp>_review_agent.md`

#### 3d: If review NEEDS CHANGES:
- Read `prompts/agent-fix.md` and execute Agent Fix (lint runs inline after fix).
- Create report: `reports/<unix_timestamp>_fix_agent.md`
- Go back to step 3b (Security).
- If loop_count > 3: ESCALATE to user, stop.

#### 3e: If review APPROVED:
- Mark task as complete in tasks.md
- Continue to next task.

### Step 4: DONE
- All tasks complete.
- Create final summary report.
- Stay on branch (do NOT merge to main).
- Report results to user.

## State Management
- Initialize and maintain `.ai-agents/workflow-state.json` throughout the pipeline.
- Create `reports/` directory if it doesn't exist.
- Track all reports in workflow-state.json.
