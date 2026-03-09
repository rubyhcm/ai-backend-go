# Agent Plan

Create a development plan for the given requirement.

## Input
Requirement: $ARGUMENTS

## Instructions

Read and follow the agent prompt at `prompts/agent-plan.md`.

1. If the input is a `.md` file path, read the file content as the requirement.
2. Read all rules in `.rules/` directory.
3. Read existing context in `.ai-agents/` if available.
4. Analyze the requirement thoroughly.
5. Generate:
   - `.ai-agents/plan.md` - Detailed implementation plan with Mermaid diagrams
   - `.ai-agents/architecture.md` - Architecture diagrams
   - `.ai-agents/tests-plan.md` - Test plan with coverage targets
6. Create report: `reports/<unix_timestamp>_plan_agent.md`
7. Update `.ai-agents/workflow-state.json` with state `"TASKING"`.
