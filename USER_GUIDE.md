# Hướng Dẫn Sử Dụng Hệ Thống AI Agents

**Phiên bản:** 2.0
**Cập nhật:** 2026-03-09

---

## Giới Thiệu

Hệ thống này giúp bạn **tự động viết code Go (Golang)** chỉ bằng cách mô tả yêu cầu bằng tiếng Việt hoặc tiếng Anh.

Bạn chỉ cần:
1. Viết yêu cầu (ví dụ: "Tạo API quản lý người dùng")
2. Chạy 1 lệnh
3. Hệ thống tự động: lập kế hoạch → chia task → viết code → kiểm tra lint → quét bảo mật → tự sửa lỗi bảo mật → review → sửa lỗi

Kết quả: **code hoàn chỉnh, đã qua kiểm tra bảo mật** sẵn sàng sử dụng.

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

> **Ghi chú:** Nếu không có Semgrep hoặc Snyk, hệ thống vẫn chạy được nhưng sẽ ghi chú "SKIPPED" trong báo cáo bảo mật.

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
cd đường/dẫn/đến/thư/mục/dự/án
```

Ví dụ:
```bash
cd ~/agrios/ai_tech
```

### Bước 2: Khởi động Claude Code

```bash
claude
```

Màn hình sẽ hiện:
```
Welcome back!
~/agrios/ai_tech
```

### Bước 3: Chọn lệnh phù hợp

---

## Các Lệnh Có Sẵn

### Lệnh 1: `/agent-full` - Chạy toàn bộ quy trình (DÙNG NHIỀU NHẤT)

Đây là lệnh chính. Hệ thống tự động làm **tất cả** từ đầu đến cuối.

**Cách dùng:**

```
/agent-full Tạo REST API quản lý người dùng với đăng ký, đăng nhập, xem thông tin
```

Hoặc nếu bạn đã viết yêu cầu trong file:

```
/agent-full requirement.md
```

**Hệ thống sẽ tự động:**
1. Phân tích yêu cầu của bạn
2. Lập kế hoạch chi tiết
3. Chia thành các bước nhỏ
4. Viết code + unit test (coverage >= 80%) cho từng bước
5. Kiểm tra và tự sửa định dạng code
6. **Quét bảo mật** (gosec + govulncheck + Semgrep + Snyk)
7. **Tự động sửa lỗi bảo mật** nếu phát hiện lỗ hổng CRITICAL hoặc HIGH
8. **Quét lại bảo mật** để xác nhận đã sửa xong
9. Review code tổng thể
10. Sửa lỗi nếu review không đạt
11. Trả về code hoàn chỉnh đã qua kiểm tra

**Trong khi chạy:** Bạn chỉ cần ngồi chờ. Hệ thống hiển thị tiến trình từng bước. Nếu cần quyết định quan trọng (ví dụ: lỗ hổng bảo mật trong thư viện bên ngoài), hệ thống sẽ dừng và hỏi bạn.

---

### Lệnh 2: `/agent-plan` - Chỉ lập kế hoạch

Khi bạn chỉ muốn xem kế hoạch trước, chưa viết code.

```
/agent-plan Tạo hệ thống thanh toán trực tuyến
```

Hoặc từ file:
```
/agent-plan requirement.md
```

**Kết quả:** File kế hoạch tại `.ai-agents/plan.md`

---

### Lệnh 3: `/agent-task` - Chia kế hoạch thành các bước nhỏ

Sau khi đã có kế hoạch (đã chạy `/agent-plan`), chia thành các task có thể thực hiện được.

```
/agent-task
```

**Kết quả:** File danh sách task tại `.ai-agents/tasks.md`

---

### Lệnh 4: `/agent-code` - Viết code cho 1 task

Viết code cho task tiếp theo trong danh sách.

```
/agent-code
```

Hoặc chỉ định task cụ thể:
```
/agent-code task-3
```

---

### Lệnh 5: `/agent-lint` - Kiểm tra định dạng code

Kiểm tra và tự động sửa định dạng code Go (gofmt, goimports, go vet, golangci-lint).

```
/agent-lint
```

---

### Lệnh 6: `/agent-security` - Quét bảo mật

Quét toàn diện các lỗ hổng bảo mật trong code. Sử dụng nhiều công cụ: gosec, govulncheck, Semgrep, Snyk.

```
/agent-security
```

**Kết quả:** Báo cáo bảo mật tại `reports/<timestamp>_security_agent.md`

---

### Lệnh 7: `/agent-security-fix` - Quét + Tự động sửa bảo mật ⭐ MỚI

Quét bảo mật **và tự động sửa** tất cả lỗ hổng mức CRITICAL và HIGH. Không cần can thiệp thủ công.

```
/agent-security-fix
```

**Quy trình tự động:**
1. Quét bảo mật (gosec + govulncheck + Semgrep + Snyk)
2. Nếu phát hiện lỗ hổng CRITICAL hoặc HIGH → tự động sửa
3. Quét lại để xác nhận đã sửa
4. Lặp lại tối đa 3 lần nếu vẫn còn lỗi
5. Nếu sau 3 lần vẫn không sửa được → báo cáo và hỏi bạn

> **Lưu ý về lỗ hổng thư viện bên ngoài:** Nếu lỗ hổng nằm trong thư viện bên ngoài (ví dụ: `github.com/some-lib`), hệ thống sẽ **không tự nâng cấp** mà sẽ báo cáo và hỏi ý kiến bạn, vì nâng cấp có thể làm hỏng code hiện tại.

---

### Lệnh 8: `/agent-review` - Review code

Kiểm tra tổng thể: chất lượng, kiến trúc, logic, độ phủ test.

```
/agent-review
```

> **Lưu ý:** Nếu coverage (độ phủ test) dưới 80%, review sẽ không đạt và yêu cầu viết thêm test.

---

### Lệnh 9: `/agent-fix` - Sửa lỗi

Khi gặp lỗi, đưa thông báo lỗi cho hệ thống tự sửa.

```
/agent-fix "Error: nil pointer dereference at internal/service/user.go:42"
```

Hoặc nếu đã có review:
```
/agent-fix
```
(Hệ thống tự đọc báo cáo review để biết cần sửa gì)

---

### Lệnh 10: `/agent-test` - Viết thêm test

Tạo thêm test cho code đã có (dùng độc lập, không thuộc pipeline chính).

```
/agent-test
```

---

## Ví Dụ Sử Dụng Thực Tế

### Ví dụ 1: Tạo API từ đầu

```
claude                          # Mở Claude Code
/agent-full Tạo REST API quản lý sản phẩm với CRUD, phân trang, tìm kiếm
```

Đợi hệ thống chạy xong. Code sẽ nằm trong các thư mục `cmd/`, `internal/`, `pkg/`.

### Ví dụ 2: Tạo từ file yêu cầu

Tạo file `yeu-cau.md` với nội dung:

```markdown
# Yêu cầu: Hệ thống quản lý đơn hàng

## Chức năng
- Tạo đơn hàng mới
- Xem danh sách đơn hàng
- Cập nhật trạng thái đơn hàng
- Hủy đơn hàng

## Yêu cầu kỹ thuật
- REST API
- PostgreSQL
- JWT authentication
```

Sau đó:
```
claude
/agent-full yeu-cau.md
```

### Ví dụ 3: Chỉ muốn kiểm tra bảo mật và tự sửa

```
claude
/agent-security-fix
```

Hệ thống quét toàn bộ code, tự sửa lỗ hổng, và báo cáo kết quả.

### Ví dụ 4: Chỉ muốn review code đã viết

```
claude
/agent-review
```

### Ví dụ 5: Gặp lỗi cần sửa

```
claude
/agent-fix "server không khởi động được, lỗi: port 8080 already in use"
```

---

## Quy Trình Xử Lý Bảo Mật

Hệ thống có **2 vòng lặp tự động sửa lỗi** độc lập:

```
Viết code
    ↓
Kiểm tra lint
    ↓
Quét bảo mật ──→ Phát hiện CRITICAL/HIGH? ──→ Tự động sửa ──→ Quét lại (tối đa 3 lần)
    ↓ (không có lỗi nghiêm trọng)
Review code ──→ Không đạt? ──→ Sửa lỗi ──→ Lint lại (tối đa 3 lần)
    ↓ (đạt)
XONG
```

**Các công cụ bảo mật sử dụng:**

| Công cụ | Kiểm tra gì |
|---------|-------------|
| **gosec** | Lỗi bảo mật Go phổ biến (hardcode secret, SQL injection, ...) |
| **govulncheck** | Lỗ hổng đã biết trong thư viện (CVE database) |
| **Semgrep** | Phân tích code tĩnh theo OWASP Top 10 |
| **Snyk** | Lỗ hổng dependency + lỗi code nâng cao |

**Mức độ nghiêm trọng:**

| Mức | Ý nghĩa | Hành động |
|-----|---------|-----------|
| **CRITICAL** | Lỗ hổng có thể bị tấn công ngay | Bắt buộc sửa trước khi tiếp tục |
| **HIGH** | Nguy cơ cao, thiếu kiểm soát bảo mật | Bắt buộc sửa trước khi tiếp tục |
| **MEDIUM** | Thực hành bảo mật yếu | Nên sửa |
| **LOW** | Cải thiện nhỏ | Tùy chọn |

---

## Cấu Trúc Thư Mục

Sau khi hệ thống chạy xong, bạn sẽ thấy:

```
du-an-cua-ban/
├── cmd/api/main.go          # File khởi động ứng dụng
├── internal/
│   ├── domain/              # Các đối tượng chính (User, Product,...)
│   ├── usecase/             # Logic xử lý nghiệp vụ
│   ├── repository/          # Truy cập database
│   └── handler/             # Xử lý HTTP/gRPC request
├── reports/                 # Báo cáo của từng bước
│   ├── 1710000001_plan_agent.md
│   ├── 1710000002_task_agent.md
│   ├── 1710000003_code_agent.md
│   ├── 1710000004_lint_agent.md
│   ├── 1710000005_security_agent.md
│   ├── 1710000006_fix_security_agent.md  # (nếu có lỗ hổng được sửa)
│   └── 1710000007_review_agent.md
└── .ai-agents/              # Dữ liệu nội bộ của hệ thống
    ├── plan.md              # Kế hoạch
    ├── tasks.md             # Danh sách task
    └── reviews/             # Kết quả review
```

**Thư mục `reports/`** là nơi bạn có thể đọc báo cáo chi tiết của từng bước, bao gồm cả báo cáo bảo mật.

---

## Câu Hỏi Thường Gặp

### Hệ thống bị dừng giữa chừng thì sao?

Chạy lại lệnh trước đó. Hệ thống sẽ đọc trạng thái từ file `.ai-agents/workflow-state.json` và tiếp tục từ chỗ dang dở.

### Làm sao biết code đã xong chưa?

Hệ thống sẽ thông báo "DONE". Bạn cũng có thể kiểm tra file `.ai-agents/workflow-state.json` — nếu `state` là `"DONE"` thì đã xong.

### Muốn sửa yêu cầu giữa chừng?

Dừng lại (Ctrl+C), sửa yêu cầu, rồi chạy lại `/agent-full` với yêu cầu mới.

### Hệ thống phát hiện lỗ hổng bảo mật thì sao?

Hệ thống **tự động sửa** lỗ hổng CRITICAL và HIGH mà không cần bạn can thiệp. Sau khi sửa, nó quét lại để xác nhận. Bạn có thể xem báo cáo chi tiết tại `reports/*_fix_security_agent.md`.

Nếu lỗ hổng nằm trong thư viện bên ngoài (không phải code của bạn), hệ thống sẽ dừng và hỏi bạn vì nâng cấp thư viện có thể gây ra vấn đề khác.

### Hệ thống báo "security_fix_count exceeded"?

Nghĩa là hệ thống đã thử sửa lỗ hổng bảo mật 3 lần nhưng vẫn không thành công. Lúc này:
1. Đọc báo cáo tại `reports/*_security_agent.md` và `reports/*_fix_security_agent.md`
2. Liên hệ người phụ trách kỹ thuật để xem xét

### Coverage dưới 80% thì sao?

Review sẽ không đạt. Hệ thống sẽ tự động yêu cầu viết thêm test. Nếu sau 3 lần vẫn không đạt coverage, sẽ báo cáo và dừng lại.

### Code bị lỗi nhiều quá, review không qua?

Hệ thống tự động sửa tối đa 3 lần. Nếu vẫn không qua, sẽ dừng lại và báo cho bạn biết vấn đề. Lúc này bạn có thể:
- Đọc báo cáo review trong `reports/`
- Chạy `/agent-fix "mô tả vấn đề"` để sửa thủ công

### Muốn chạy từng bước thay vì chạy hết?

Có thể! Chạy theo thứ tự:
1. `/agent-plan "yêu cầu"`
2. `/agent-task`
3. `/agent-code`
4. `/agent-lint`
5. `/agent-security-fix` (hoặc `/agent-security` nếu chỉ muốn xem báo cáo)
6. `/agent-review`

### File báo cáo ở đâu?

Trong thư mục `reports/`. Tên file có dạng `<số>_<tên_agent>.md`. Mở bằng bất kỳ trình đọc text nào.

### Hệ thống có xóa code cũ của tôi không?

**Không.** Hệ thống luôn tạo branch mới (nhánh Git) trước khi viết code. Code cũ của bạn vẫn nguyên vẹn trên branch `main`. Chỉ khi bạn tự quyết định merge (gộp) thì code mới được thêm vào.

### Tôi không biết Git là gì, có sao không?

Không sao. Hệ thống tự động xử lý Git. Bạn chỉ cần biết:
- Code mới nằm trên "branch" riêng (như bản sao)
- Code cũ vẫn an toàn trên branch "main"
- Khi hài lòng với code mới, nhờ người biết kỹ thuật giúp merge

---

## Mẹo Sử Dụng

1. **Viết yêu cầu càng chi tiết càng tốt.** "Tạo API" sẽ cho kết quả chung chung. "Tạo REST API quản lý người dùng với đăng ký bằng email, đăng nhập bằng JWT, phân quyền admin/user" sẽ cho kết quả tốt hơn.

2. **Dùng file .md cho yêu cầu phức tạp.** Khi yêu cầu dài, viết vào file rồi dùng `/agent-full ten-file.md`.

3. **Đọc báo cáo bảo mật.** File `reports/*_security_agent.md` và `reports/*_fix_security_agent.md` cho bạn biết lỗ hổng gì đã được phát hiện và sửa như thế nào.

4. **Dùng `/agent-security-fix` thường xuyên.** Ngay cả khi không phát triển tính năng mới, chạy lệnh này định kỳ để đảm bảo code luôn an toàn.

5. **Chạy `/agent-review` trước khi giao code.** Ngay cả khi tự viết code, bạn có thể dùng agent review để kiểm tra tổng thể.

---

## Khi Gặp Sự Cố

| Vấn đề | Cách xử lý |
|--------|-----------|
| Claude Code không mở | Kiểm tra đã cài chưa: gõ `claude` trong terminal |
| Không thấy lệnh `/agent-*` | Đảm bảo đang ở đúng thư mục dự án (có file `.claude/commands/`) |
| Hệ thống báo "go: command not found" | Cài Go: https://go.dev/dl/ |
| Hệ thống báo "golangci-lint not found" | Cài golangci-lint: https://golangci-lint.run/welcome/install/ |
| Hệ thống báo "gosec not found" | Chạy: `go install github.com/securego/gosec/v2/cmd/gosec@latest` |
| Hệ thống báo "govulncheck not found" | Chạy: `go install golang.org/x/vuln/cmd/govulncheck@latest` |
| Hệ thống dừng và không phản hồi | Ấn Ctrl+C để dừng, rồi chạy lại lệnh |
| Hệ thống hỏi câu hỏi bạn không hiểu | Trả lời "yes" hoặc "có" để tiếp tục, hoặc "no" để dừng |
| Báo cáo bảo mật có "ESCALATED" | Lỗ hổng phức tạp, cần người kỹ thuật xem xét |

---

## Liên Hệ Hỗ Trợ

Nếu gặp vấn đề không tự giải quyết được:
- Đọc báo cáo trong `reports/` để hiểu hệ thống đã làm gì
- Đọc file `.ai-agents/workflow-state.json` để xem trạng thái hiện tại
- Liên hệ người phụ trách kỹ thuật và cung cấp nội dung thư mục `reports/`
