# Feature Specs

Thư mục này chứa các feature specs cho Kiro.

## Cách tạo spec mới

Tạo thư mục mới: `.kiro/specs/<feature-name>/`

Mỗi spec gồm 3 file:
1. `requirements.md` — Yêu cầu chức năng (user stories, acceptance criteria)
2. `design.md` — Thiết kế kỹ thuật (entities, interfaces, APIs)
3. `tasks.md` — Danh sách task implement (ordered, có dependencies)

## Ví dụ: User Authentication Feature

```
.kiro/specs/user-auth/
  requirements.md
  design.md
  tasks.md
```

## Template

Xem file `_template/` bên dưới để bắt đầu.
