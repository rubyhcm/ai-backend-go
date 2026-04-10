# Hướng Dẫn Sử Dụng Hệ Thống AI Agents

**Phiên bản:** 2.4
**Cập nhật:** 2026-04-10

---

## Giới Thiệu

Hệ thống này giúp bạn **tự động viết code Go (Golang)** chỉ bằng cách mô tả yêu cầu bằng tiếng Việt hoặc tiếng Anh.

Hệ thống gồm **4 pipeline song song**:

### Pipeline A — Claude Code Agents (pipeline gốc)
Bạn chỉ cần:
1. Viết yêu cầu (ví dụ: "Tạo API quản lý người dùng")
2. Chạy 1 lệnh
3. Hệ thống tự động: lập kế hoạch → chia task → viết code → kiểm tra lint → quét bảo mật → tự sửa lỗi bảo mật → review → sửa lỗi

Kết quả: **code hoàn chỉnh, đã qua kiểm tra bảo mật** sẵn sàng sử dụng.

### Pipeline B — Kiro Spec Generator (mới)
Dành cho dự án sử dụng **Amazon Kiro IDE**:
1. Chạy `/agent-kiro` để tạo spec chi tiết cho feature
2. Copy thư mục `.kiro/` sang dự án đích
3. Mở Kiro → AI tự đọc spec và coding theo đúng conventions

Xem chi tiết tại phần [`/agent-kiro`](#agent-kiro---tạo-kiro-spec-cho-feature) bên dưới.

### Pipeline C — AI Editor Rules (GitHub Copilot & Cursor AI)

Dành cho các **AI editor tích hợp IDE** (không phải Claude Code). Hệ thống cung cấp bộ rules sẵn sàng dùng:

| Tool | File | Cách hoạt động |
|------|------|----------------|
| **GitHub Copilot** | `.github/instructions/copilot-instructions.md` | Copilot tự đọc khi mở repo trong VS Code |
| **Cursor AI** | `.cursor/rules/*.mdc` | Cursor inject đúng rule file theo loại file đang mở |

Xem chi tiết tại phần [AI Editor Rules](#ai-editor-rules---github-copilot--cursor-ai) bên dưới.

### Pipeline D — Antigravity IDE

Dành cho dự án sử dụng **Antigravity IDE** (Google DeepMind). Hệ thống cung cấp:

| Loại | Vị trí | Cách hoạt động |
|------|--------|----------------|
| **Workflows** | `agrios/.agent/workflows/` | Kích hoạt bằng slash command trong Antigravity |
| **Knowledge Items** | Memory của Antigravity | Tự động check mỗi đầu conversation |

Xem chi tiết tại phần [Antigravity IDE](#antigravity-ide) bên dưới.

---

## Yêu Cầu Trước Khi Bắt Đầu

### Phần mềm cần cài đặt

| Phần mềm | Mục đích | Cách kiểm tra đã cài chưa |
|----------|----------|--------------------------|
| **Claude Code** | Công cụ AI chính | Gõ `claude` trong terminal |
| **Go** (>= 1.21) | Ngôn ngữ lập trình | Gõ `go version` |
| **Git** | Quản lý code | Gõ `git version` |
| **golangci-lint** | Kiểm tra code | Gõ `golangci-lint version` |
| **gosec** | Quét bảo mật Go | Gõ `gosec --version` |
| **govulncheck** | Kiểm tra lỗ hổng dependency | Gõ `govulncheck -version` |

### Phần mềm tùy chọn (tăng cường bảo mật)

| Phần mềm | Mục đích | Cách cài |
|----------|----------|----------|
| **Semgrep** | Phân tích bảo mật tĩnh (SAST) | `pip install semgrep` |
| **Snyk** | Kiểm tra lỗ hổng dependency + code | `npm install -g snyk && snyk auth` |
| **sonar-scanner** | SAST, code smells, security hotspots (SonarCloud) | Xem [docs/sonarcloud-scan-guide.md](docs/sonarcloud-scan-guide.md) |

> **Ghi chú:** Nếu không có Semgrep, Snyk, hoặc sonar-scanner, hệ thống vẫn chạy được nhưng sẽ ghi chú "SKIPPED" trong báo cáo bảo mật.

### Cách cài các công cụ bảo mật Go

```bash
# gosec
go install github.com/securego/gosec/v2/cmd/gosec@latest

# govulncheck
go install golang.org/x/vuln/cmd/govulncheck@latest
```

### Cách cài Claude Code

Nếu chưa có Claude Code, cài theo hướng dẫn tại: https://docs.anthropic.com/en/docs/claude-code

---

## Cách Sử Dụng

### Bước 1: Mở terminal và vào thư mục dự án

```bash
cd ~/agrios/centre-auth-service   # hoặc thư mục dự án của bạn
```

### Bước 2: Khởi động Claude Code

```bash
claude
```

### Bước 3: Chọn lệnh phù hợp

---

## Các Lệnh Có Sẵn

### `/agent-kiro` - Tạo Kiro spec cho feature

Tạo bộ spec hoàn chỉnh (requirements, design, tasks) cho một feature, dành cho dự án dùng **Amazon Kiro IDE**. Agent sẽ phân tích yêu cầu và tạo ra tài liệu đủ chi tiết để Kiro có thể đọc và implement code theo đúng conventions.

```
/agent-kiro Tạo tính năng quản lý người dùng: đăng ký, đăng nhập, xem/cập nhật hồ sơ
```

Hoặc từ file mô tả:
```
/agent-kiro requirement.md
```

> **Model:** Opus (tự động dùng model mạnh nhất cho bước phân tích kiến trúc)

**Agent sẽ tự động:**
1. Đọc toàn bộ rules trong `.kiro/steering/` (architecture, Go conventions, database, security, testing, design patterns)
2. Phân tích feature: entities, use cases, gRPC methods, database tables, design patterns cần dùng
3. Tạo `.kiro/specs/<feature-slug>/requirements.md` — user stories + acceptance criteria cụ thể
4. Tạo `.kiro/specs/<feature-slug>/design.md` — Go structs, interfaces, SQL schema, proto definition, Mermaid diagram
5. Tạo `.kiro/specs/<feature-slug>/tasks.md` — task list theo đúng thứ tự dependency
6. Tạo báo cáo tại `reports/<timestamp>_kiro_agent.md`

**Kết quả:** Thư mục `.kiro/specs/<feature-slug>/` với đầy đủ 3 file spec.

**Sau khi có spec:**
```
# 1. Copy toàn bộ .kiro/ sang dự án Go của bạn
cp -r .kiro/ /path/to/your-go-project/.kiro/

# 2. Mở dự án trong Kiro IDE

# 3. Yêu cầu Kiro implement
"Implement the <feature-name> feature based on .kiro/specs/<feature-slug>/
 Follow all guidelines in .kiro/steering/. Start with Task 1."
```

**Ví dụ tên thư mục spec được tạo:**

| Input | Thư mục tạo ra |
|-------|----------------|
| `User authentication with JWT` | `.kiro/specs/user-auth/` |
| `Product inventory management` | `.kiro/specs/product-inventory/` |
| `Order processing with payment` | `.kiro/specs/order-processing/` |

---

### `/agent-full` - Chạy toàn bộ quy trình (DÙNG NHIỀU NHẤT)

Đây là lệnh chính. Hệ thống tự động làm **tất cả** từ đầu đến cuối.

```
/agent-full Tạo gRPC API quản lý người dùng với đăng ký, đăng nhập, xem thông tin
```

Hoặc từ file yêu cầu:
```
/agent-full requirement.md
```

**Hệ thống sẽ tự động:**
1. Lập kế hoạch chi tiết *(dùng model Opus — mạnh nhất)*
2. Chia thành các task nhỏ có thể thực hiện được
3. Với từng task:
   - Viết code + unit test (coverage >= 80%)
   - Kiểm tra và sửa định dạng code
   - Quét bảo mật (gosec + govulncheck + Semgrep + Snyk)
   - **Tự động sửa** lỗ hổng CRITICAL/HIGH, quét lại để xác nhận
   - Review code tổng thể
   - Sửa lỗi nếu review không đạt
4. Báo cáo hoàn thành khi tất cả task đều DONE

**Trong khi chạy:** Bạn chỉ cần ngồi chờ. Hệ thống sẽ dừng và hỏi bạn chỉ khi gặp vấn đề không tự giải quyết được (ví dụ: lỗ hổng trong thư viện bên ngoài cần nâng cấp).

---

### `/agent-plan` - Chỉ lập kế hoạch

Khi bạn chỉ muốn xem kế hoạch trước, chưa viết code.

```
/agent-plan Tạo hệ thống thanh toán trực tuyến
```

> **Model:** Opus (tự động dùng model mạnh nhất cho bước này)

**Kết quả:** `.ai-agents/plan.md`, `.ai-agents/architecture.md`, `.ai-agents/tests-plan.md`

**Tiếp theo:** `/agent-task`

---

### `/agent-task` - Chia kế hoạch thành các task

Sau khi có kế hoạch, chia thành danh sách task có thứ tự và dependency rõ ràng.

```
/agent-task
```

**Kết quả:** `.ai-agents/tasks.md` — danh sách task với status `TODO`

**Tiếp theo:** `/agent-code`

---

### `/agent-code` - Viết code cho task tiếp theo

Tự động tìm và thực hiện task tiếp theo trong danh sách.

```
/agent-code
```

Hoặc chỉ định task cụ thể:
```
/agent-code task-3
```

**Cách agent xác định task cần làm (theo thứ tự ưu tiên):**
1. Task được chỉ định qua tham số (ví dụ `task-3`)
2. `current_task` trong `workflow-state.json` nếu task đó vẫn là `TODO`
3. Task đầu tiên có `Status: TODO` trong `tasks.md`

**Tiếp theo:** `/agent-lint`

---

### `/agent-lint` - Kiểm tra định dạng code

Tự động sửa định dạng (gofmt, goimports, go vet, golangci-lint) trên các file vừa thay đổi.

```
/agent-lint
```

**Tiếp theo:** `/agent-security-fix`

---

### `/agent-security` - Quét bảo mật (chỉ xem báo cáo)

Quét toàn diện bằng gosec, govulncheck, Semgrep, Snyk. Chỉ tạo báo cáo, không tự sửa.

```
/agent-security
```

**Tiếp theo:**
- Nếu CLEAN: `/agent-review`
- Nếu có CRITICAL/HIGH: `/agent-security-fix`

---

### `/agent-security-fix` - Quét + Tự động sửa bảo mật

Quét bảo mật **và tự động sửa** tất cả lỗ hổng CRITICAL và HIGH.

```
/agent-security-fix
```

**Quy trình:**
1. Quét (gosec + govulncheck + Semgrep + Snyk)
2. Tự động sửa CRITICAL trước, rồi HIGH
3. Quét lại để xác nhận
4. Lặp tối đa 3 lần — nếu vẫn không xong thì dừng và hỏi bạn

> Lỗ hổng trong thư viện bên ngoài (govulncheck) **không tự nâng cấp** — sẽ hỏi bạn vì nâng cấp có thể gây lỗi khác.

**Tiếp theo:** `/agent-review`

---

### `/agent-review` - Review code

Kiểm tra tổng thể: kiến trúc, SOLID, logic nghiệp vụ, chất lượng test, coverage.

```
/agent-review
```

**Coverage là bắt buộc:** Nếu dưới 80%, review tự động FAIL dù code có tốt đến đâu.

**Sau khi review:**
- **APPROVED:** Task được đánh dấu `DONE`, `current_task` tự động chuyển sang task tiếp theo
- **NEEDS CHANGES:** Chạy `/agent-fix` rồi `/agent-lint` để sửa và kiểm tra lại

---

### `/agent-fix` - Sửa lỗi

Phân tích và sửa lỗi dựa trên thông báo lỗi hoặc kết quả review.

```
/agent-fix "Error: nil pointer dereference at internal/service/user.go:42"
```

Hoặc để agent tự đọc báo cáo review:
```
/agent-fix
```

**Tiếp theo:** `/agent-lint` → `/agent-security-fix` → `/agent-review`

---

### `/agent-test` - Viết thêm test (độc lập)

Tạo thêm test cho code đã có. **Không thuộc pipeline chính** — dùng khi muốn bổ sung test riêng.

```
/agent-test
```

**Tiếp theo:** `/agent-review`

---

## Theo Dõi Tiến Độ

### Xem danh sách task và trạng thái

Mở file `.ai-agents/tasks.md`. Mỗi task có trường `**Status:**`:

| Status | Ý nghĩa |
|--------|---------|
| `TODO` | Chưa bắt đầu |
| `IN_PROGRESS` | Đang thực hiện hoặc đang sửa lỗi |
| `DONE` | Review đã APPROVED ✅ |

Ví dụ:
```
## Task 3: HMAC Utility Package
**Status:** DONE

## Task 4: Repository Interface
**Status:** IN_PROGRESS

## Task 5: Repository Implementation
**Status:** TODO
```

### Xem tổng quan nhanh

Mở file `.ai-agents/workflow-state.json`:

```json
{
  "state": "CODING",
  "current_task": "task-4",
  "total_tasks": 9,
  "completed_tasks": 3
}
```

Đọc ngay: đang ở task-4, đã xong 3/9 task, state đang là CODING.

### Các trạng thái (state) có thể gặp

| State | Ý nghĩa |
|-------|---------|
| `PLANNING` | Đang lập kế hoạch |
| `TASKING` | Đang chia task |
| `CODING` | Đang viết code |
| `LINTING` | Đang kiểm tra định dạng |
| `SECURITY_SCANNING` | Đang quét bảo mật |
| `SECURITY_FIXING` | Đang tự sửa lỗ hổng bảo mật |
| `REVIEWING` | Đang review code |
| `FIXING` | Đang sửa lỗi từ review |
| `DONE` | Tất cả task hoàn thành ✅ |
| `ESCALATED` | Cần can thiệp thủ công |

---

## Quy Trình Tổng Thể

```
/agent-plan  (Opus)
    ↓
/agent-task  (Sonnet)
    ↓
┌─── /agent-code ──────────────────────────────────┐
│       ↓                                          │
│   /agent-lint                                    │
│       ↓                                          │
│   /agent-security-fix ←──────────────────┐      │
│       ↓ CLEAN                            │      │
│   /agent-review      NEEDS CHANGES       │      │
│       ↓ ──────────→ /agent-fix ──→ lint ─┘      │
│       ↓ APPROVED                                 │
│   current_task → task tiếp theo (TODO)           │
└──────────────────────────────────────────────────┘
    ↓ (tất cả task DONE)
  DONE ✅
```

**Model sử dụng:**
- `/agent-plan` → `claude-opus-4-6` (kiến trúc, thiết kế phức tạp)
- Tất cả agent còn lại → `claude-sonnet-4-6` (nhanh, hiệu quả)

Switch model khi cần:
```
/model claude-opus-4-6    # trước khi chạy /agent-plan
/model claude-sonnet-4-6  # trước khi chạy các agent còn lại
```

---

## Ví Dụ Thực Tế

### Ví dụ 0: Tạo Kiro spec rồi để Kiro IDE implement

```
# Bước 1: Tạo spec (trong repo ai_tech này)
/model claude-opus-4-6
/agent-kiro Tạo gRPC API xác thực người dùng với JWT access token và refresh token,
            hỗ trợ đăng ký, đăng nhập, đăng xuất, refresh token

# Bước 2: Copy .kiro/ sang dự án Go của bạn
# (thực hiện trong terminal, không phải Claude Code)
cp -r .kiro/ ~/projects/my-go-service/.kiro/

# Bước 3: Mở dự án trong Kiro IDE và yêu cầu:
# "Implement the user-auth feature based on .kiro/specs/user-auth/
#  Follow all guidelines in .kiro/steering/. Start with Task 1."
```

---

### Ví dụ 1: Tạo tính năng từ đầu (tự động hoàn toàn)

```
/model claude-opus-4-6
/agent-full Tạo gRPC API xác thực partner service với HMAC signature
```

Hệ thống tự chạy từ đầu đến cuối. Khi xong, toàn bộ task sẽ là `DONE`.

### Ví dụ 2: Chạy từng bước (kiểm soát thủ công)

```
/model claude-opus-4-6
/agent-plan requirement.md        # Lập kế hoạch

/model claude-sonnet-4-6
/agent-task                        # Chia task
/agent-code                        # Viết code task đầu tiên
/agent-lint                        # Kiểm tra định dạng
/agent-security-fix                # Quét và sửa bảo mật
/agent-review                      # Review → APPROVED → tự chuyển task tiếp theo
/agent-code                        # Viết code task tiếp theo
# ... lặp lại cho đến khi DONE
```

### Ví dụ 3: Tiếp tục sau khi bị gián đoạn

```
# Xem đang ở đâu
cat .ai-agents/workflow-state.json

# Ví dụ: state = "LINTING", current_task = "task-5"
/agent-lint         # Tiếp tục từ bước lint
/agent-security-fix
/agent-review
```

### Ví dụ 4: Sửa lỗi từ review

```
# Review trả về NEEDS CHANGES
/agent-fix                         # Tự đọc review và sửa
/agent-lint
/agent-security-fix
/agent-review                      # Chạy lại review
```

---

## Cấu Trúc Thư Mục

```
du-an-cua-ban/
├── cmd/api/main.go
├── internal/
│   ├── domain/              # Entities, errors, value objects
│   ├── usecase/             # Business logic
│   ├── repository/          # Repository interfaces + implementations
│   └── grpc/                # gRPC handlers
├── reports/                 # Báo cáo tự động của từng bước
│   ├── ..._plan_agent.md
│   ├── ..._task_agent.md
│   ├── ..._code_agent.md
│   ├── ..._lint_agent.md
│   ├── ..._security_agent.md
│   ├── ..._fix_security_agent.md   # chỉ có khi đã sửa lỗ hổng
│   ├── ..._review_agent.md
│   └── ..._fix_agent.md            # chỉ có khi review NEEDS CHANGES
└── .ai-agents/
    ├── plan.md
    ├── architecture.md
    ├── tests-plan.md
    ├── tasks.md             # ← theo dõi status từng task ở đây
    ├── workflow-state.json  # ← theo dõi tiến độ tổng thể ở đây
    └── reviews/
        └── review-1.md, review-2.md, ...
```

---

## AI Editor Rules — GitHub Copilot & Cursor AI

Ngoài Claude Code, hệ thống còn cung cấp **bộ rules chuẩn hóa** để các AI editor khác trong IDE cũng gợi ý code đúng convention.

> **Cập nhật 2.4:** Tất cả rules database đã được bổ sung **Transaction Safety** (wrap migration trong `BEGIN/COMMIT` cho PostgreSQL) và **Idempotency Patterns** (`IF NOT EXISTS` / `IF EXISTS` bắt buộc cho mọi migration statement).

### GitHub Copilot

**File:** `.github/instructions/copilot-instructions.md`

**Cách hoạt động:** Khi bạn mở repo trong VS Code (có extension GitHub Copilot), Copilot tự đọc file này và áp dụng cho tất cả gợi ý code trong repo.

**Không cần cấu hình gì thêm.** Chỉ cần đảm bảo file tồn tại trong repo.

**Nội dung file bao gồm:**
- Clean Architecture layer rules + dependency direction
- Go conventions: naming, error handling, context, logging, concurrency, configuration
- Design patterns: Repository, Circuit Breaker, Middleware, Worker Pool, ...
- Security: input validation, SQL injection prevention, JWT, cryptography, OWASP Top 10
- Testing: table-driven tests, mocking, coverage gates
- gRPC workflow: proto → codegen → handler → registration
- Database design: schema rules, indexing, zero-downtime migration, keyset pagination
- Feature implementation workflow (13 bước)

---

### Cursor AI

**Thư mục:** `.cursor/rules/` với 7 file `.mdc`

**Cách hoạt động:** Cursor tự động inject đúng rule file dựa trên loại file đang mở (nhờ `globs` trong frontmatter). Không cần cấu hình thủ công.

| File | Kích hoạt khi mở | alwaysApply |
|------|-----------------|-------------|
| `project-overview.mdc` | `**/*.go`, `**/*.proto` | `true` — luôn load |
| `architecture.mdc` | `internal/**/*.go`, `cmd/**/*.go` | `false` |
| `go-conventions.mdc` | `**/*.go` | `false` |
| `testing.mdc` | `**/*_test.go` | `false` |
| `security.mdc` | `internal/**/*.go` | `false` |
| `database.mdc` | `migrations/**/*.sql`, `internal/repository/**/*.go` | `false` |
| `design-patterns.mdc` | `internal/**/*.go`, `pkg/**/*.go` | `false` |

**Ví dụ:** Khi mở `internal/service/user_service_test.go`, Cursor tự động load `project-overview.mdc` + `go-conventions.mdc` + `testing.mdc`.

---

---

## Antigravity IDE

Antigravity IDE là AI coding assistant của Google DeepMind. Hệ thống tích hợp qua **Workflow files** — các file markdown trong `.agent/workflows/` được kích hoạt bằng slash command trong IDE.

> **Vị trí:** `/home/loinguyen/agrios/.agent/workflows/` (thư mục cha, dùng chung cho tất cả project trong `agrios/`)

### Workflows có sẵn

| Slash command | File | Chức năng |
|--------------|------|-----------|
| `project-rules` | `project-rules.md` | Tham chiếu toàn bộ conventions (load tự động khi viết code) |
| `/migrate new <name>` | `migrate.md` | Tạo migration UP + DOWN với transaction safety |
| `/migrate review` | `migrate.md` | Review migration files hiện có |
| `/migrate checklist` | `migrate.md` | Kiểm tra migration checklist |
| `/test [target]` | `test.md` | Tạo table-driven tests với gomock cho Go |
| `/test coverage` | `test.md` | Báo cáo coverage |
| `/test integration` | `test.md` | Chạy integration tests |
| `/security scan` | `security.md` | Chạy gosec, govulncheck, semgrep, snyk |
| `/security review` | `security.md` | Review code theo OWASP Top 10 |
| `/security fix` | `security.md` | Sửa lỗ hổng bảo mật |
| `/deploy` | `deploy.md` | Deployment với pre-flight checks |
| `/plan` | `plan.md` | Lập kế hoạch feature |

### Cơ chế hoạt động

Antigravity IDE có **3 cách nhận rules**:

**1. Workflow files (slash commands)** — được đọc khi bạn gõ lệnh tương ứng.

**2. Knowledge Items (KIs)** — conventions lưu trong memory, tự động check mỗi đầu conversation. Để thêm KI, nói với Antigravity:
```
"Save this as a Knowledge Item: [nội dung rule]"
```

**3. Global Custom Rules** — cấu hình trong IDE Settings → tìm "Custom Instructions" → paste rules vào. Được inject vào mọi conversation.

### Quy tắc database trong Antigravity

Khi gõ `/migrate new <tên>`, Antigravity tự động:
- Wrap migration trong `BEGIN/COMMIT` (PostgreSQL)
- Dùng `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`
- Tạo cả UP lẫn DOWN migration
- Thêm audit fields (`created_at`, `updated_at`, `deleted_at`, `version`)
- Tạo migration checklist trước khi commit

### Ví dụ sử dụng

```
# Tạo migration mới
/migrate new create_orders

# Tạo tests cho service
/test internal/service/order_service.go

# Audit bảo mật toàn bộ code
/security review

# Xem toàn bộ project conventions
/project-rules
```

---

## Sync Rules Sang Repo Khác

Sau khi cập nhật rules trong repo `ai_tech`, dùng lệnh sau để đồng bộ sang repo đích:

```bash
TARGET=/home/loinguyen/agrios/your-service   # thay bằng đường dẫn repo đích

# Sync toàn bộ
rsync -av /home/loinguyen/agrios/ai_tech/.rules/          $TARGET/.rules/
rsync -av /home/loinguyen/agrios/ai_tech/.github/instructions/ $TARGET/.github/instructions/
rsync -av /home/loinguyen/agrios/ai_tech/.cursor/         $TARGET/.cursor/
rsync -av /home/loinguyen/agrios/ai_tech/.kiro/           $TARGET/.kiro/
```

**Những gì được sync:**

| Thư mục | Nội dung | Dùng cho |
|---------|----------|----------|
| `.rules/` | Architecture, Go, security, testing, database, design-patterns rules | Claude Code agents |
| `.github/instructions/` | `copilot-instructions.md` | GitHub Copilot trong VS Code |
| `.cursor/rules/` | 7 file `.mdc` rules theo context | Cursor AI |
| `.kiro/` | Steering rules + spec templates | Amazon Kiro IDE |

> **Ghi chú:** `rsync` chỉ copy file mới hoặc đã thay đổi — an toàn để chạy nhiều lần.

> **Lưu ý Antigravity:** Workflows của Antigravity IDE nằm tại `agrios/.agent/workflows/` — **không nằm trong repo `ai_tech`** và không cần sync. Chúng được dùng chung cho tất cả project trong `agrios/`.

---

## Câu Hỏi Thường Gặp

### Làm sao biết task nào đã xong, task nào chưa?

Có 2 cách:

**Cách 1 — Chi tiết từng task:** Đọc `.ai-agents/tasks.md`, xem trường `**Status:**` của mỗi task (`TODO` / `IN_PROGRESS` / `DONE`).

**Cách 2 — Tổng quan nhanh:** Đọc `.ai-agents/workflow-state.json`, xem `completed_tasks` / `total_tasks` và `current_task`.

### Agent biết làm task nào tiếp theo bằng cách nào?

Khi chạy `/agent-code`, agent tự xác định theo thứ tự ưu tiên:
1. Task được chỉ định thủ công (ví dụ `/agent-code task-5`)
2. `current_task` trong `workflow-state.json` (nếu task đó vẫn là `TODO`)
3. Task đầu tiên có `Status: TODO` trong `tasks.md`

Khi một task APPROVED, agent-review **tự động cập nhật** `current_task` sang task `TODO` tiếp theo — bạn chỉ cần gõ `/agent-code` là chạy đúng task.

### Hệ thống bị dừng giữa chừng thì sao?

Đọc `workflow-state.json` để xem `state` và `current_task` đang ở đâu, rồi chạy lại đúng agent tương ứng:

| state | Chạy lại lệnh |
|-------|---------------|
| `CODING` | `/agent-code` |
| `LINTING` | `/agent-lint` |
| `SECURITY_SCANNING` | `/agent-security-fix` |
| `REVIEWING` | `/agent-review` |
| `FIXING` | `/agent-fix` |

### Hệ thống phát hiện lỗ hổng bảo mật thì sao?

Hệ thống **tự động sửa** lỗ hổng CRITICAL và HIGH, quét lại để xác nhận, lặp tối đa 3 lần. Bạn không cần làm gì. Chi tiết xem tại `reports/*_fix_security_agent.md`.

Trường hợp **dừng và hỏi bạn:**
- Lỗ hổng nằm trong thư viện bên ngoài (cần nâng cấp — bạn phải quyết định)
- Sau 3 lần tự sửa vẫn thất bại

### Coverage dưới 80% thì sao?

Review tự động FAIL. Hệ thống sẽ yêu cầu viết thêm test và chạy lại. Sau 3 lần vẫn không đạt thì dừng và báo bạn.

### Muốn xem chi tiết lỗi review?

Đọc file `.ai-agents/reviews/review-<N>.md` — có đầy đủ: severity, file:line, mô tả vấn đề, và gợi ý sửa cụ thể.

### Hệ thống có xóa code cũ không?

**Không.** Mỗi task tạo một branch riêng (`feature/task-X-ten-task`). Code cũ trên `main` không bị ảnh hưởng. Bạn quyết định merge khi nào thì merge.

---

## Khi Gặp Sự Cố

| Vấn đề | Cách xử lý |
|--------|-----------|
| Claude Code không mở | Gõ `claude` trong terminal để kiểm tra |
| Không thấy lệnh `/agent-*` | Đảm bảo đang ở đúng thư mục dự án (có `.claude/commands/`) |
| `/agent-kiro` không tạo được spec | Đảm bảo thư mục `.kiro/steering/` và `.kiro/specs/_template/` tồn tại |
| Kiro không nhận diện steering rules | Kiểm tra frontmatter `inclusion: always` trong các file `.kiro/steering/*.md` |
| `go: command not found` | Cài Go: https://go.dev/dl/ |
| `golangci-lint not found` | `go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest` |
| `gosec not found` | `go install github.com/securego/gosec/v2/cmd/gosec@latest` |
| `govulncheck not found` | `go install golang.org/x/vuln/cmd/govulncheck@latest` |
| Hệ thống không phản hồi | Ctrl+C để dừng, đọc `workflow-state.json`, chạy lại đúng agent |
| State = `ESCALATED` | Đọc `reports/` và liên hệ người phụ trách kỹ thuật |
| `security_fix_count exceeded` | Lỗ hổng phức tạp, cần xem xét thủ công `reports/*_security_agent.md` |
| `loop_count exceeded` | Code có vấn đề lớn, đọc `.ai-agents/reviews/` để hiểu rõ |
| Copilot không áp dụng rules | Kiểm tra `.github/instructions/copilot-instructions.md` tồn tại trong repo |
| Cursor không load rules | Kiểm tra `.cursor/rules/*.mdc` tồn tại; xem lại `globs` trong frontmatter |
| `sonar-scanner not found` | Xem hướng dẫn cài tại [docs/sonarcloud-scan-guide.md](docs/sonarcloud-scan-guide.md) |
| Antigravity không nhận `/migrate` | Kiểm tra `agrios/.agent/workflows/migrate.md` tồn tại; mở project trong thư mục `agrios/` |
| Antigravity không biết project conventions | Nói: *"Save this as a KI: [paste nội dung từ project-rules.md]"* hoặc cấu hình Global Custom Rules trong Settings |
| Migration không có `BEGIN/COMMIT` | Nhắc Antigravity: *"Follow the /migrate workflow rules"* hoặc gõ `/migrate new <name>` thay vì viết tay |

---

## Liên Hệ Hỗ Trợ

Khi cần nhờ người kỹ thuật hỗ trợ, cung cấp các thông tin sau:
- Nội dung file `.ai-agents/workflow-state.json`
- Các file trong thư mục `reports/`
- Các file trong thư mục `.ai-agents/reviews/`
