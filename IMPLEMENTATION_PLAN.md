# AI Agents System - Implementation Plan

**Created:** 2026-03-09
**Status:** COMPLETED (Phase 1-4), Phase 5 ready for manual testing
**Version:** 1.0

---

## Phase 1: Bổ sung prompts cho agents còn thiếu [CRITICAL] ✓

- [x] Task 1.1: Tạo `prompts/agent-task.md` - Agent chia plan thành tasks
- [x] Task 1.2: Tạo `prompts/agent-lint.md` - Agent format code Go
- [x] Task 1.3: Tạo `prompts/agent-security.md` - Agent security scan
- [x] Task 1.4: Cập nhật `prompts/agent-code.md` - Đọc tasks.md, tạo branch, viết test
- [x] Task 1.5: Cập nhật `prompts/agent-review.md` - Tách Lint/Security ra, focus review logic

## Phase 2: Report system [HIGH] ✓

- [x] Task 2.1: Cập nhật tất cả agent prompts thêm report section
- [x] Task 2.2: Report template nhúng trực tiếp trong mỗi agent prompt

## Phase 3: Orchestrator update [HIGH] ✓

- [x] Task 3.1: Cập nhật `prompts/orchestrator.md` - Flow mới với Task/Lint/Security agents
- [x] Task 3.2: Cập nhật workflow-state.json schema (embedded in orchestrator.md)

## Phase 4: Slash commands & Integration [MEDIUM] ✓

- [x] Task 4.1: Tạo `.claude/commands/` cho từng agent (9 commands)
- [x] Task 4.2: Tạo command `agent-full` cho full pipeline

## Phase 5: Testing & Optimization [LOW] - READY FOR TESTING

- [ ] Task 5.1: Test từng agent riêng lẻ
- [ ] Task 5.2: Test full flow end-to-end
- [ ] Task 5.3: Context optimization & prompt tuning

---

## System Architecture (Final)

```
ai_tech/
├── .claude/
│   ├── commands/                    # Slash commands (user-facing)
│   │   ├── agent-full.md           # /agent-full - Full pipeline
│   │   ├── agent-plan.md           # /agent-plan - Create plan
│   │   ├── agent-task.md           # /agent-task - Break plan into tasks
│   │   ├── agent-code.md           # /agent-code - Implement task
│   │   ├── agent-lint.md           # /agent-lint - Format & lint
│   │   ├── agent-security.md       # /agent-security - Security scan
│   │   ├── agent-review.md         # /agent-review - Code review
│   │   ├── agent-fix.md            # /agent-fix - Fix bugs
│   │   └── agent-test.md           # /agent-test - Generate tests
│   └── settings.local.json
│
├── prompts/                         # Agent system prompts (brain)
│   ├── orchestrator.md             # Workflow orchestrator
│   ├── agent-plan.md               # Plan agent
│   ├── agent-task.md               # Task agent (NEW)
│   ├── agent-code.md               # Code agent (UPDATED)
│   ├── agent-test.md               # Test agent
│   ├── agent-lint.md               # Lint agent (NEW)
│   ├── agent-security.md           # Security agent (NEW)
│   ├── agent-review.md             # Review agent (UPDATED)
│   └── agent-fix.md                # Fix agent (UPDATED)
│
├── .rules/                          # Project rules (constitution)
│   ├── go.md                       # Go conventions
│   ├── architecture.md             # Layer rules
│   ├── design-patterns.md          # Pattern guidelines
│   ├── security.md                 # Security requirements
│   └── testing.md                  # Testing standards
│
├── .ai-agents/                      # Agent workspace (runtime)
│   ├── workflow-state.json         # Current pipeline state
│   ├── plan.md                     # Implementation plan
│   ├── architecture.md             # Architecture diagrams
│   ├── tasks.md                    # Task breakdown (generated)
│   ├── tests-plan.md               # Test plan (generated)
│   ├── reviews/                    # Review reports
│   ├── knowledge/                  # Agent memory
│   │   ├── bugs-history.md
│   │   └── architecture-decisions.md
│   └── index/                      # Code index (optional)
│
├── reports/                         # Agent reports (audit trail)
│   └── <timestamp>_<agent>.md
│
├── .golangci.yml                   # Lint configuration
└── requirement.md                  # Original requirement
```

## Pipeline Flow (Final)

```
/agent-full "requirement"
    │
    ▼
┌─ PLANNING ──────────────────────────┐
│  Agent Plan → plan.md, arch.md      │
│  Report: <ts>_plan_agent.md         │
└─────────────────────────────────────┘
    │
    ▼
┌─ TASKING ───────────────────────────┐
│  Agent Task → tasks.md              │
│  Report: <ts>_task_agent.md         │
└─────────────────────────────────────┘
    │
    ▼
┌─ FOR EACH TASK ─────────────────────┐
│                                     │
│  ┌─ CODING ───────────────────────┐ │
│  │  Agent Code → code + tests     │ │
│  │  git checkout -b feature/...   │ │
│  │  Report: <ts>_code_agent.md    │ │
│  └────────────────────────────────┘ │
│      │                              │
│      ▼                              │
│  ┌─ LINTING ──────────────────────┐ │
│  │  Agent Lint → format + check   │ │
│  │  Report: <ts>_lint_agent.md    │ │
│  └────────────────────────────────┘ │
│      │                              │
│      ▼                              │
│  ┌─ SECURITY ─────────────────────┐ │
│  │  Agent Security → OWASP scan   │ │
│  │  Report: <ts>_security_agent.md│ │
│  └────────────────────────────────┘ │
│      │                              │
│      ▼                              │
│  ┌─ REVIEWING ────────────────────┐ │
│  │  Agent Review → verdict        │ │
│  │  Report: <ts>_review_agent.md  │ │
│  └────────────────────────────────┘ │
│      │                              │
│      ├── APPROVED → next task       │
│      │                              │
│      └── NEEDS CHANGES              │
│          │                          │
│          ▼                          │
│      ┌─ FIXING ───────────────────┐ │
│      │  Agent Fix → patch + test  │ │
│      │  Report: <ts>_fix_agent.md │ │
│      └────────────────────────────┘ │
│          │                          │
│          └── back to LINTING        │
│              (max 3 loops)          │
│                                     │
└─────────────────────────────────────┘
    │
    ▼
  DONE → all reports in reports/
```

## Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/agent-full` | Full pipeline | `/agent-full "Build REST API for users"` |
| `/agent-plan` | Create plan | `/agent-plan requirement.md` |
| `/agent-task` | Break into tasks | `/agent-task` |
| `/agent-code` | Implement task | `/agent-code task-1` |
| `/agent-lint` | Lint changed files | `/agent-lint` |
| `/agent-security` | Security scan | `/agent-security` |
| `/agent-review` | Review code | `/agent-review` |
| `/agent-fix` | Fix bug | `/agent-fix "nil pointer at user.go:42"` |
| `/agent-test` | Generate tests | `/agent-test` |

---

## Progress Log

| Date | Phase | Task | Status |
|------|-------|------|--------|
| 2026-03-09 | 1 | Created agent-task.md, agent-lint.md, agent-security.md | DONE |
| 2026-03-09 | 1 | Updated agent-code.md, agent-review.md | DONE |
| 2026-03-09 | 2 | Added report sections to all 8 agent prompts | DONE |
| 2026-03-09 | 3 | Updated orchestrator.md with new flow + state schema | DONE |
| 2026-03-09 | 4 | Created 9 slash commands in .claude/commands/ | DONE |
| 2026-03-09 | 5 | Created directories: reports/, reviews/, index/ | DONE |
| 2026-03-09 | 5 | Created workflow-state.json template | DONE |
