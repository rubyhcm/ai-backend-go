# Hướng Dẫn Sử Dụng Hệ Thống AI Agents

**Phiên bản:** 1.0
**Cập nhật:** 2026-03-09

---

## Giới Thiệu

Hệ thống này giúp bạn **tự động viết code Go (Golang)** chỉ bằng cách mô tả yêu cầu bằng tiếng Việt hoặc tiếng Anh.

Bạn chỉ cần:
1. Viết yêu cầu (ví dụ: "Tạo REST API quản lý người dùng")
2. Chạy 1 lệnh
3. Hệ thống tự động: lập kế hoạch → chia task → viết code → kiểm tra → review → sửa lỗi

Kết quả: **code hoàn chỉnh** sẵn sàng sử dụng.

---

## Yêu Cầu Trước Khi Bắt Đầu

### Phần mềm cần cài đặt

| Phần mềm | Mục đích | Cách kiểm tra đã cài chưa |
|----------|----------|--------------------------|
| **Claude Code** | Công cụ AI chính | Gõ vào terminal, gõ `claude` |
| **Go** (>= 1.21) | Ngôn ngữ lập trình | Gõ `go version` |
| **Git** | Quản lý code | Gõ `git version` |
| **golangci-lint** | Kiểm tra code | Gõ `golangci-lint version` |

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
4. Viết code cho từng bước
5. Kiểm tra định dạng code
6. Kiểm tra bảo mật
7. Review code
8. Sửa lỗi (nếu có)
9. Trả về code hoàn chỉnh

**Thời gian:** Tùy độ phức tạp, thường từ 5-30 phút.

**Trong khi chạy:** Bạn chỉ cần ngồi chờ. Hệ thống sẽ hiển thị tiến trình. Nếu có câu hỏi, hệ thống sẽ hỏi bạn.

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

Sau khi đã có kế hoạch (đã chạy `/agent-plan`), chia thành các task.

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

Kiểm tra và tự động sửa định dạng code Go.

```
/agent-lint
```

---

### Lệnh 6: `/agent-security` - Kiểm tra bảo mật

Kiểm tra code có lỗ hổng bảo mật không.

```
/agent-security
```

---

### Lệnh 7: `/agent-review` - Review code

Kiểm tra tổng thể: chất lượng, kiến trúc, logic.

```
/agent-review
```

---

### Lệnh 8: `/agent-fix` - Sửa lỗi

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

### Lệnh 9: `/agent-test` - Viết thêm test

Tạo thêm test cho code đã có.

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

### Ví dụ 3: Chỉ muốn review code đã viết

```
claude
/agent-review
```

### Ví dụ 4: Gặp lỗi cần sửa

```
claude
/agent-fix "server không khởi động được, lỗi: port 8080 already in use"
```

---

## Cấu Trúc Thư Mục

Sau khi hệ thống chạy xong, bạn sẽ thấy các thư mục sau:

```
du-an-cua-ban/
├── cmd/api/main.go          # File khởi động ứng dụng
├── internal/
│   ├── domain/              # Các đối tượng chính (User, Product,...)
│   ├── service/             # Logic xử lý nghiệp vụ
│   ├── repository/          # Truy cập database
│   └── handler/             # Xử lý HTTP request
├── reports/                 # Báo cáo của từng bước
│   ├── 1710000001_plan_agent.md
│   ├── 1710000002_task_agent.md
│   ├── 1710000003_code_agent.md
│   ├── 1710000004_lint_agent.md
│   ├── 1710000005_security_agent.md
│   └── 1710000006_review_agent.md
└── .ai-agents/              # Dữ liệu nội bộ của hệ thống
    ├── plan.md              # Kế hoạch
    ├── tasks.md             # Danh sách task
    └── reviews/             # Kết quả review
```

**Thư mục `reports/`** là nơi bạn có thể đọc báo cáo chi tiết của từng bước.

---

## Câu Hỏi Thường Gặp

### Hệ thống bị dừng giữa chừng thì sao?

Chạy lại lệnh trước đó. Hệ thống sẽ đọc trạng thái từ file `workflow-state.json` và tiếp tục từ chỗ dang dở.

### Làm sao biết code đã xong chưa?

Hệ thống sẽ thông báo "DONE" và tạo báo cáo tổng kết. Bạn cũng có thể kiểm tra file `.ai-agents/workflow-state.json` - nếu `state` là `"DONE"` thì đã xong.

### Muốn sửa yêu cầu giữa chừng?

Dừng lại (Ctrl+C), sửa yêu cầu, rồi chạy lại `/agent-full` với yêu cầu mới.

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
5. `/agent-security`
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

3. **Đọc báo cáo review.** File `reports/*_review_agent.md` cho bạn biết code có vấn đề gì và cách sửa.

4. **Chạy `/agent-review` trước khi giao code.** Ngay cả khi tự viết code, bạn có thể dùng agent review để kiểm tra.

5. **Chạy `/agent-security` thường xuyên.** Để đảm bảo code không có lỗ hổng bảo mật.

---

## Khi Gặp Sự Cố

| Vấn đề | Cách xử lý |
|--------|-----------|
| Claude Code không mở | Kiểm tra đã cài chưa: gõ `claude` trong terminal |
| Không thấy lệnh `/agent-*` | Đảm bảo đang ở đúng thư mục dự án (có file `.claude/commands/`) |
| Hệ thống báo "go: command not found" | Cài Go: https://go.dev/dl/ |
| Hệ thống báo "golangci-lint not found" | Cài golangci-lint: https://golangci-lint.run/welcome/install/ |
| Hệ thống dừng và không phản hồi | Ấn Ctrl+C để dừng, rồi chạy lại lệnh |
| Hệ thống hỏi câu hỏi bạn không hiểu | Trả lời "yes" hoặc "có" để tiếp tục, hoặc "no" để dừng |

---

## Liên Hệ Hỗ Trợ

Nếu gặp vấn đề không tự giải quyết được:
- Đọc file `IMPLEMENTATION_PLAN.md` để hiểu tổng quan hệ thống
- Đọc file `requirement.md` để hiểu yêu cầu gốc
- Đọc báo cáo trong `reports/` để hiểu hệ thống đã làm gì
