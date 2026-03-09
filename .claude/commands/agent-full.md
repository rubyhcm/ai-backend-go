# Full AI Agent Pipeline

You are the Workflow Orchestrator. Execute the FULL agent pipeline for the given requirement.

## Input
Requirement: $ARGUMENTS

## Instructions

Read and follow the orchestrator prompt at `prompts/orchestrator.md`.

Execute the full pipeline in this exact order:

### Step 1: PLANNING
- Read `prompts/agent-plan.md` and execute Agent Plan.
- If the input is a `.md` file path, read the file content first.
- Generate: `.ai-agents/plan.md`, `.ai-agents/architecture.md`, `.ai-agents/tests-plan.md`
- Create report: `reports/<unix_timestamp>_plan_agent.md`

### Step 2: TASKING
- Read `prompts/agent-task.md` and execute Agent Task.
- Generate: `.ai-agents/tasks.md`
- Create report: `reports/<unix_timestamp>_task_agent.md`

### Step 3: For each task in tasks.md (in order):

#### 3a: CODING
- Read `prompts/agent-code.md` and execute Agent Code for the current task.
- Create feature branch, implement code + unit tests.
- Commit changes.
- Create report: `reports/<unix_timestamp>_code_agent.md`

#### 3b: LINTING
- Read `prompts/agent-lint.md` and execute Agent Lint.
- Format and check changed files only.
- Create report: `reports/<unix_timestamp>_lint_agent.md`

#### 3c: SECURITY SCANNING
- Read `prompts/agent-security.md` and execute Agent Security.
- Scan changed files for vulnerabilities.
- Create report: `reports/<unix_timestamp>_security_agent.md`

#### 3d: REVIEWING
- Read `prompts/agent-review.md` and execute Agent Review.
- Review all changes including lint/security reports.
- Create report: `reports/<unix_timestamp>_review_agent.md`

#### 3e: If review NEEDS CHANGES:
- Read `prompts/agent-fix.md` and execute Agent Fix.
- Create report: `reports/<unix_timestamp>_fix_agent.md`
- Go back to step 3b (Lint).
- If loop_count > 3: ESCALATE to user, stop.

#### 3f: If review APPROVED:
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
