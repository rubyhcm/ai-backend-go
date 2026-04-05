# Kiro Configuration

Thư mục này chứa toàn bộ hướng dẫn để Kiro hiểu và tuân theo khi code Go backend.

## Cấu trúc

```
.kiro/
├── steering/                    # Project-wide guidelines (luôn được inject vào context)
│   ├── project-overview.md      # Tech stack, core principles, quy trình làm việc
│   ├── architecture.md          # Clean Architecture layers, gRPC workflow, DI rules
│   ├── go-conventions.md        # Go coding standards, error handling, logging, config
│   ├── database.md              # Database design, migration strategy, query rules
│   ├── security.md              # Security rules, OWASP Top 10, JWT, SQL injection
│   ├── testing.md               # Testing standards, table-driven tests, coverage gates
│   └── design-patterns.md      # Go design patterns với code examples
│
└── specs/                       # Feature specifications
    ├── README.md                 # Hướng dẫn tạo spec
    ├── _template/               # Template để tạo spec mới
    │   ├── requirements.md       # Template requirements
    │   ├── design.md             # Template technical design
    │   └── tasks.md              # Template task list
    └── <feature-name>/          # Spec của từng feature
        ├── requirements.md
        ├── design.md
        └── tasks.md
```

## Steering Files

Các file trong `steering/` có `inclusion: always` — Kiro sẽ luôn đọc chúng trước khi code bất kỳ thứ gì trong project này.

| File | Nội dung |
|------|----------|
| `project-overview.md` | Tech stack, 10 core principles, file naming, quy trình implement feature |
| `architecture.md` | Clean Architecture layers, gRPC 4-step workflow, DI pattern |
| `go-conventions.md` | Error handling, context, naming, interfaces, logging, config |
| `database.md` | Schema design, migrations, indexing, zero-downtime strategy |
| `security.md` | Input validation, SQL injection, JWT, CORS, OWASP Top 10 |
| `testing.md` | Table-driven tests, gomock, coverage gates, integration tests |
| `design-patterns.md` | Repository, Adapter, Circuit Breaker, Worker Pool... với code examples |

## Cách dùng với Kiro

### 1. Copy thư mục `.kiro/` vào project của bạn

```bash
cp -r .kiro/ /path/to/your-go-project/.kiro/
```

### 2. Tạo spec cho feature mới

```bash
mkdir .kiro/specs/user-authentication
cp .kiro/specs/_template/* .kiro/specs/user-authentication/
```

Điền vào 3 files:
- `requirements.md` — Mô tả yêu cầu, user stories, acceptance criteria
- `design.md` — Thiết kế kỹ thuật: entities, APIs, database schema
- `tasks.md` — Danh sách task có thứ tự

### 3. Yêu cầu Kiro implement

Mở Kiro và yêu cầu:

```
Implement the user authentication feature based on the spec in
.kiro/specs/user-authentication/. Follow all guidelines in .kiro/steering/.
Start with Task 1 (Domain Layer).
```

### 4. Kiro sẽ tự động tuân theo:
- Clean Architecture (handler → service → repository → domain)
- gRPC workflow (proto → generate → handler → register)
- Go conventions (error wrapping, component logger, context)
- Database rules (parameterized queries, soft delete, zero-downtime migrations)
- Security rules (input validation, no SQL injection, no hardcoded secrets)
- Testing standards (table-driven tests, 80% coverage gate)
- Design patterns (Repository, Circuit Breaker, Functional Options...)

## Tips

- Steering files dùng `inclusion: always` → Kiro đọc LUÔN LUÔN
- Nếu muốn rule chỉ áp dụng cho file Go: dùng `inclusion: fileMatch` với pattern `**/*.go`
- Task list trong `tasks.md` nên có dependencies rõ ràng để Kiro biết thứ tự implement
- Càng chi tiết requirements và design → code output càng chính xác
