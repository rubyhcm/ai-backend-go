# Agent Test

> **Model:** `claude-sonnet-4-6`
> Run with: `claude --model claude-sonnet-4-6` or switch via `/model claude-sonnet-4-6`

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

## Next Steps

```
✅ Coverage >= 80% → Run Agent Review:

  /agent-review

⚠️  Coverage < 80% → Write more tests until threshold met, then:

  /agent-review

💡 To also check security before reviewing:
  /agent-security-fix
  /agent-review
```
