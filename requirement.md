# AI Software Engineering Agents System

**Version:** 1.0
**Purpose:** Autonomous AI-driven software development pipeline
**Language target:** Go (Golang)

---

# 1. Overview

Hệ thống này là một **multi-agent AI software engineering platform** sử dụng **Claude Code** để tự động hóa toàn bộ quy trình phát triển phần mềm.

Từ một **yêu cầu đầu vào (prompt hoặc file `.md`)**, hệ thống có thể:

1. Phân tích yêu cầu
2. Tạo plan phát triển
3. Chia nhỏ tasks
4. Viết code
5. Lint & format code
6. Kiểm tra security
7. Review code
8. Fix bugs
9. Xuất báo cáo

Mục tiêu cuối cùng:

> Tự động tạo ra **code hoàn chỉnh theo yêu cầu** thông qua một chuỗi **AI agents tự động hợp tác với nhau.**

---

# 2. Design Principles

Hệ thống phải tuân thủ các nguyên tắc sau:

### Software Engineering

* SOLID principles
* Clean Architecture
* Domain Driven Design (DDD) (khuyến nghị)
* DRY
* KISS

### Security

Tuân thủ các tiêu chuẩn bảo mật theo
**OWASP Top 10 2025**:

1. Broken Access Control
2. Security Misconfiguration
3. Software Supply Chain Failures
4. Cryptographic Failures
5. Injection
6. Insecure Design
7. Authentication Failures
8. Software/Data Integrity Failures
9. Logging and Alerting Failures
10. Mishandling of Exceptional Conditions ([owasp.org][1])

### Code Standards

* Clean code
* Idiomatic Go
* Testability
* Observability
* Security-first design

---

# 3. System Architecture

Hệ thống được thiết kế theo mô hình **Multi-Agent Architecture**.

```
                +------------------+
                |     User Input    |
                | prompt / .md file |
                +---------+--------+
                          |
                          v
                +------------------+
                |    Plan Agent     |
                +---------+--------+
                          |
                          v
                +------------------+
                |   Task Agent      |
                +---------+--------+
                          |
                          v
                +------------------+
                |   Code Agent      |
                +---------+--------+
                          |
            +-------------+--------------+
            v                            v
     +-------------+            +--------------+
     | Lint Agent  |            | Security Agent|
     +------+------ +            +------+-------+
            |                            |
            +-------------+--------------+
                          v
                +------------------+
                |   Review Agent    |
                +---------+--------+
                          |
                          v
                +------------------+
                |    Fix Agent      |
                +---------+--------+
                          |
                          v
                +------------------+
                | Final Output Code |
                +------------------+
```

---

# 4. Agent Definitions

## 4.1 Plan Agent

### Responsibility

Phân tích yêu cầu và tạo **development plan**

### Input

* User prompt
* `.md requirement file`

### Output

`plan.md`

### Nội dung

* System overview
* Feature list
* Technical architecture
* Development roadmap

---

# 4.2 Task Agent

### Responsibility

Chia nhỏ plan thành **các tasks có thể implement**

### Output

`tasks.md`

Ví dụ:

```
Task 1: Setup project structure
Task 2: Implement domain models
Task 3: Implement repository layer
Task 4: Implement service layer
Task 5: Implement REST API
Task 6: Add authentication
Task 7: Write unit tests
```

---

# 4.3 Code Agent

### Responsibility

* Tạo branch mới
* Checkout branch
* Implement code theo task

### Git Workflow

```
main
 └── feature/<task-name>
```

Agent phải:

```
git checkout -b feature/task-name
```

### Code requirements

* Clean architecture
* SOLID
* Secure coding
* Idiomatic Go

---

# 4.4 Lint Agent

### Responsibility

Format lại code theo chuẩn Go.

Sử dụng:

```
gofmt
go vet
golangci-lint
```

Chỉ xử lý **files trong git changes**.

---

# 4.5 Security Agent

### Responsibility

Phân tích code theo **security best practices**

Phải kiểm tra:

* injection
* auth logic
* secrets
* crypto usage
* dependency risks

Theo chuẩn:

**OWASP Top 10 2025**

---

# 4.6 Review Agent

### Responsibility

Code review toàn bộ **git changes**

Kiểm tra:

* code quality
* architecture
* security
* performance
* conventions

Checklist:

```
- SOLID
- Clean architecture
- Go conventions
- security issues
- performance issues
```

---

# 4.7 Fix Agent

### Responsibility

Fix bugs dựa trên:

* error message
* logs
* review feedback
* test failures

Agent có thể:

* sửa code
* refactor
* retry build

---

# 5. Git Integration

Agents phải sử dụng Git để quản lý changes.

Workflow:

```
1 clone repo
2 create branch
3 implement task
4 commit changes
5 run lint
6 security scan
7 review
8 fix
```

Commit message format:

```
feat: implement user authentication
fix: resolve nil pointer in service layer
refactor: improve repository abstraction
```

---

# 6. Agent Report System

Sau khi mỗi agent hoàn thành nhiệm vụ, phải tạo report.

### File naming

```
<unix_timestamp>_<agent_name>.md
```

Ví dụ:

```
1712341234_plan_agent.md
1712341250_task_agent.md
1712341300_code_agent.md
1712341320_lint_agent.md
1712341350_security_agent.md
1712341400_review_agent.md
1712341500_fix_agent.md
```

---

# 7. Report Format

Mỗi report `.md` phải có cấu trúc:

```
# Agent Report

Agent Name:
Timestamp:

## Input

...

## Process

...

## Output

...

## Issues Found

...

## Recommendations

...
```

---

# 8. Flow Execution

Hệ thống phải hỗ trợ chạy **full pipeline flow**

### Flow

```
Plan
 ↓
Task
 ↓
Code
 ↓
Lint
 ↓
Security
 ↓
Review
 ↓
Fix
 ↓
Final Code
```

---

# 9. Flow Command

Ví dụ:

```
run_flow(requirement.md)
```

hoặc

```
run_flow("build a REST API for user management")
```

---

# 10. Final Output

Kết quả cuối cùng phải bao gồm:

```
/src
/tests
/docs
/reports
```

Reports:

```
reports/
  17123_plan.md
  17124_tasks.md
  17125_code.md
  17126_lint.md
  17127_security.md
  17128_review.md
  17129_fix.md
```

---

# 11. Error Handling

Nếu agent fail:

```
retry <= 3
```

Nếu vẫn fail:

```
create error report
stop flow
```

---

# 12. Future Enhancements

Có thể bổ sung:

### Testing Agent

* unit test
* integration test

### Architecture Agent

review kiến trúc hệ thống.

### Performance Agent

* benchmark
* profiling

### Documentation Agent

auto generate:

```
README
API docs
architecture docs
```

---

# 13. Expected Result

Hệ thống có thể:

```
Input:
  requirement.md

Output:
  fully working codebase
```

Pipeline được **tự động hóa hoàn toàn**.

---

# 14. Success Criteria

Hệ thống thành công khi:

* Code build thành công
* Code pass lint
* Không có security issue nghiêm trọng
* Pass review agent

---

# 15. Key Benefits

Hệ thống mang lại:

* Autonomous development
* Faster development cycles
* Consistent code quality
* Built-in security
* Automated documentation

---

# Kết luận (review CTO)

Requirement ban đầu của bạn **rất đúng hướng**, nhưng thiếu:

* system architecture
* git workflow
* agent orchestration
* report structure
* security framework

Phiên bản trên đã **chuẩn hóa thành spec có thể build system thật**.

---

Nếu bạn muốn, tôi có thể viết thêm 3 phần rất quan trọng mà **90% hệ thống AI agents code ngoài kia thiếu**:

1️⃣ **Orchestrator architecture (phần quan trọng nhất)**
2️⃣ **Prompt design cho từng agent (production-grade)**
3️⃣ **Folder structure cho hệ thống AI agents**

Nếu làm đúng 3 phần này, hệ thống của bạn sẽ **mạnh ngang Devin / OpenDevin / Cursor Agent architecture**.

[1]: https://owasp.org/Top10/2025/?utm_source=chatgpt.com "OWASP Top 10:2025"
