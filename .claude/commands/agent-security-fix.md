# Agent Security + Auto-Fix

Run security scan on changed files and automatically fix all CRITICAL and HIGH findings.

## Instructions

Read and follow `prompts/orchestrator.md` for the SECURITY_SCANNING → SECURITY_FIXING loop.

### Step 1: Security Scan
Read and follow `prompts/agent-security.md`.

1. Identify changed `.go` files via `git diff`.
2. Run: `gosec -fmt=json ./...`
3. Run: `govulncheck ./...`
4. Run: `semgrep --config=p/golang --config=p/owasp-top-ten ./...` (if installed)
5. Run: `snyk test --all-projects && snyk code test` (if installed)
6. Perform AI review against OWASP Top 10 (2025) and Go-specific security issues.
7. Create report: `reports/<unix_timestamp>_security_agent.md`

### Step 2: Check Findings
- Extract all CRITICAL and HIGH severity findings from the report.
- If NO CRITICAL or HIGH findings → print "Security scan CLEAN. No fixes needed." and stop.
- If findings exist → proceed to Step 3.

### Step 3: Auto-Fix Security Issues
Read and follow `prompts/agent-fix-security.md`.

1. Fix each CRITICAL finding first, then HIGH findings.
2. For each finding: analyze root cause, apply minimal fix, write regression test.
3. Run: `go build ./...` and `go test ./... -race` after each fix.
4. Escalate to user if fix requires architectural change or third-party dependency upgrade.
5. Create report: `reports/<unix_timestamp>_fix_security_agent.md`

### Step 4: Re-scan
Re-run Step 1 to verify all fixed vulnerabilities no longer appear.
- If still CLEAN → done. Update state to "REVIEWING".
- If still has CRITICAL/HIGH → repeat Step 3 (max 3 total attempts).
- If 3 attempts exceeded → ESCALATE: stop and report to user.

### Step 5: Update State
Update `.ai-agents/workflow-state.json`:
- If CLEAN: state = "REVIEWING", security_fix_count unchanged
- If escalated: state = "ESCALATED"

## Loop Control

```
security_fix_count starts at 0
Each fix attempt: increment security_fix_count
If security_fix_count > max_security_fixes (3): STOP, escalate to user
```
