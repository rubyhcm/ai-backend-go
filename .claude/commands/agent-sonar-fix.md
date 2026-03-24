# Agent Sonar Fix

> **Model:** `claude-sonnet-4-6`
> Run with: `claude --model claude-sonnet-4-6` or switch via `/model claude-sonnet-4-6`

Fix issues found in the latest SonarCloud report.

## Input

Target report (optional): $ARGUMENTS
- If provided: path to a specific SonarCloud report file (e.g. `reports/1234567890_sonarcloud_report.md`)
- If omitted: auto-detect the latest `reports/*_sonarcloud_report.md`

## Instructions

Read and follow the agent prompt at `prompts/agent-fix-sonar.md`.

1. Find the SonarCloud report:
   - If $ARGUMENTS given: use that file path.
   - Else: find the latest `reports/*_sonarcloud_report.md`.
2. Parse ALL issues from the report (Vulnerabilities, Bugs, Security Hotspots, Code Smells).
3. Fix in priority order: BLOCKER → CRITICAL → MAJOR → MINOR.
4. For each issue: analyze root cause, apply minimal fix, write regression test.
5. Run: `go build ./...` and `go test ./... -race` after all fixes.
6. Run: `python3 scripts/gen_sonar_report.py` to regenerate the SonarCloud report.
7. Compare new report vs old report to verify fixed issues no longer appear.
8. Create fix report: `reports/<unix_timestamp>_fix_sonar_agent.md`

## Next Steps

```
✅ All BLOCKER/CRITICAL fixed → Run Agent Review:

  /agent-review

⚠️  Has remaining BLOCKER/CRITICAL (escalated) → Manual intervention required.
    Read reports/*_fix_sonar_agent.md for escalation details.
```
