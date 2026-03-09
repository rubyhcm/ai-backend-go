# Agent Test

Generate comprehensive tests for the codebase.

## Instructions

Read and follow the agent prompt at `prompts/agent-test.md`.

1. Read `.rules/testing.md` and `.rules/go.md`.
2. Read `.ai-agents/tests-plan.md` for test plan.
3. Read source code files to test.
4. Generate:
   - Table-driven unit tests with testify assertions
   - Mocks with gomock for interfaces
   - Edge case tests (nil, empty, boundary, context cancel, errors)
5. Run: `go test ./... -race -cover`
6. Verify coverage meets targets (domain 90%, service 85%, handler 80%).
7. Create report: `reports/<unix_timestamp>_test_agent.md`
8. Update `.ai-agents/workflow-state.json` with state `"REVIEWING"`.
