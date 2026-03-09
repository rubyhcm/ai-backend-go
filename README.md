# Claude Code Agent Playbook

Repository này là bộ hướng dẫn để dùng với Claude Code theo mô hình đa agent (Plan/Code/Test/Review/Fix), không chứa runtime Go nữa.

## Thành phần chính

- `.rules/` - Luật dự án (kiến trúc, security, testing, coding style)
- `prompts/` - Prompt vai trò cho từng agent
- `AI_AGENTS_PLAN.md` - Tài liệu kiến trúc và luồng vận hành mẫu
- `.ai-agents/` - Nơi lưu artifact khi Claude tạo trong quá trình làm việc

## Cách dùng nhanh (Claude Code)

1. Mở repo đích trong Claude Code.
2. Copy `.rules/` và `prompts/` từ repo này sang repo đích.
3. Giao task bằng tiếng tự nhiên, ví dụ:
   - "Plan kiến trúc cho feature X"
   - "Implement theo plan ở `.ai-agents/plan.md`"
   - "Review security cho phần auth"
4. Claude sẽ dùng rules + prompts để xử lý theo pipeline.

## Ghi chú

- Không cần `go.mod`, `Makefile`, hoặc binary runtime trong repo playbook này.
- Nếu repo đích là Go project, các prompt/rules vẫn áp dụng bình thường.
