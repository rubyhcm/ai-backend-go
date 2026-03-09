# Huong Dan Su Dung He Thong AI Agents

**Phien ban:** 1.0
**Cap nhat:** 2026-03-09

---

## Gioi Thieu

He thong nay giup ban **tu dong viet code Go (Golang)** chi bang cach mo ta yeu cau bang tieng Viet hoac tieng Anh.

Ban chi can:
1. Viet yeu cau (vi du: "Tao REST API quan ly nguoi dung")
2. Chay 1 lenh
3. He thong tu dong: lap ke hoach → chia task → viet code → kiem tra → review → sua loi

Ket qua: **code hoan chinh** san sang su dung.

---

## Yeu Cau Truoc Khi Bat Dau

### Phan mem can cai dat

| Phan mem | Muc dich | Cach kiem tra da cai chua |
|----------|----------|--------------------------|
| **Claude Code** | Cong cu AI chinh | Go vao terminal, go `claude` |
| **Go** (>= 1.21) | Ngon ngu lap trinh | Go `go version` |
| **Git** | Quan ly code | Go `git version` |
| **golangci-lint** | Kiem tra code | Go `golangci-lint version` |

### Cach cai Claude Code

Neu chua co Claude Code, cai theo huong dan tai: https://docs.anthropic.com/en/docs/claude-code

---

## Cach Su Dung

### Buoc 1: Mo terminal va vao thu muc du an

```bash
cd duong/dan/den/thu/muc/du/an
```

Vi du:
```bash
cd ~/agrios/ai_tech
```

### Buoc 2: Khoi dong Claude Code

```bash
claude
```

Man hinh se hien:
```
Welcome back!
~/agrios/ai_tech
```

### Buoc 3: Chon lenh phu hop

---

## Cac Lenh Co San

### Lenh 1: `/agent-full` - Chay toan bo quy trinh (DUNG NHIEU NHAT)

Day la lenh chinh. He thong tu dong lam **tat ca** tu dau den cuoi.

**Cach dung:**

```
/agent-full Tao REST API quan ly nguoi dung voi dang ky, dang nhap, xem thong tin
```

Hoac neu ban da viet yeu cau trong file:

```
/agent-full requirement.md
```

**He thong se tu dong:**
1. Phan tich yeu cau cua ban
2. Lap ke hoach chi tiet
3. Chia thanh cac buoc nho
4. Viet code cho tung buoc
5. Kiem tra dinh dang code
6. Kiem tra bao mat
7. Review code
8. Sua loi (neu co)
9. Tra ve code hoan chinh

**Thoi gian:** Tuy do phuc tap, thuong tu 5-30 phut.

**Trong khi chay:** Ban chi can ngoi cho. He thong se hien thi tien trinh. Neu co cau hoi, he thong se hoi ban.

---

### Lenh 2: `/agent-plan` - Chi lap ke hoach

Khi ban chi muon xem ke hoach truoc, chua viet code.

```
/agent-plan Tao he thong thanh toan truc tuyen
```

Hoac tu file:
```
/agent-plan requirement.md
```

**Ket qua:** File ke hoach tai `.ai-agents/plan.md`

---

### Lenh 3: `/agent-task` - Chia ke hoach thanh cac buoc nho

Sau khi da co ke hoach (da chay `/agent-plan`), chia thanh cac task.

```
/agent-task
```

**Ket qua:** File danh sach task tai `.ai-agents/tasks.md`

---

### Lenh 4: `/agent-code` - Viet code cho 1 task

Viet code cho task tiep theo trong danh sach.

```
/agent-code
```

Hoac chi dinh task cu the:
```
/agent-code task-3
```

---

### Lenh 5: `/agent-lint` - Kiem tra dinh dang code

Kiem tra va tu dong sua dinh dang code Go.

```
/agent-lint
```

---

### Lenh 6: `/agent-security` - Kiem tra bao mat

Kiem tra code co lo hong bao mat khong.

```
/agent-security
```

---

### Lenh 7: `/agent-review` - Review code

Kiem tra tong the: chat luong, kien truc, logic.

```
/agent-review
```

---

### Lenh 8: `/agent-fix` - Sua loi

Khi gap loi, dua thong bao loi cho he thong tu sua.

```
/agent-fix "Error: nil pointer dereference at internal/service/user.go:42"
```

Hoac neu da co review:
```
/agent-fix
```
(He thong tu doc bao cao review de biet can sua gi)

---

### Lenh 9: `/agent-test` - Viet them test

Tao them test cho code da co.

```
/agent-test
```

---

## Vi Du Su Dung Thuc Te

### Vi du 1: Tao API tu dau

```
claude                          # Mo Claude Code
/agent-full Tao REST API quan ly san pham voi CRUD, phan trang, tim kiem
```

Doi he thong chay xong. Code se nam trong cac thu muc `cmd/`, `internal/`, `pkg/`.

### Vi du 2: Tao tu file yeu cau

Tao file `yeu-cau.md` voi noi dung:

```markdown
# Yeu cau: He thong quan ly don hang

## Chuc nang
- Tao don hang moi
- Xem danh sach don hang
- Cap nhat trang thai don hang
- Huy don hang

## Yeu cau ky thuat
- REST API
- PostgreSQL
- JWT authentication
```

Sau do:
```
claude
/agent-full yeu-cau.md
```

### Vi du 3: Chi muon review code da viet

```
claude
/agent-review
```

### Vi du 4: Gap loi can sua

```
claude
/agent-fix "server khong khoi dong duoc, loi: port 8080 already in use"
```

---

## Cau Truc Thu Muc

Sau khi he thong chay xong, ban se thay cac thu muc sau:

```
du-an-cua-ban/
├── cmd/api/main.go          # File khoi dong ung dung
├── internal/
│   ├── domain/              # Cac doi tuong chinh (User, Product,...)
│   ├── service/             # Logic xu ly nghiep vu
│   ├── repository/          # Truy cap database
│   └── handler/             # Xu ly HTTP request
├── reports/                 # Bao cao cua tung buoc
│   ├── 1710000001_plan_agent.md
│   ├── 1710000002_task_agent.md
│   ├── 1710000003_code_agent.md
│   ├── 1710000004_lint_agent.md
│   ├── 1710000005_security_agent.md
│   └── 1710000006_review_agent.md
└── .ai-agents/              # Du lieu noi bo cua he thong
    ├── plan.md              # Ke hoach
    ├── tasks.md             # Danh sach task
    └── reviews/             # Ket qua review
```

**Thu muc `reports/`** la noi ban co the doc bao cao chi tiet cua tung buoc.

---

## Cau Hoi Thuong Gap

### He thong bi dung giua chung thi sao?

Chay lai lenh truoc do. He thong se doc trang thai tu file `workflow-state.json` va tiep tuc tu cho dang do.

### Lam sao biet code da xong chua?

He thong se thong bao "DONE" va tao bao cao tong ket. Ban cung co the kiem tra file `.ai-agents/workflow-state.json` - neu `state` la `"DONE"` thi da xong.

### Muon sua yeu cau giua chung?

Dung lai (Ctrl+C), sua yeu cau, roi chay lai `/agent-full` voi yeu cau moi.

### Code bi loi nhieu qua, review khong qua?

He thong tu dong sua toi da 3 lan. Neu van khong qua, se dung lai va bao cho ban biet van de. Luc nay ban co the:
- Doc bao cao review trong `reports/`
- Chay `/agent-fix "mo ta van de"` de sua thu cong

### Muon chay tung buoc thay vi chay het?

Co the! Chay theo thu tu:
1. `/agent-plan "yeu cau"`
2. `/agent-task`
3. `/agent-code`
4. `/agent-lint`
5. `/agent-security`
6. `/agent-review`

### File bao cao o dau?

Trong thu muc `reports/`. Ten file co dang `<so>_<ten_agent>.md`. Mo bang bat ky trinh doc text nao.

### He thong co xoa code cu cua toi khong?

**Khong.** He thong luon tao branch moi (nhanh Git) truoc khi viet code. Code cu cua ban van nguyen ven tren branch `main`. Chi khi ban tu quyet dinh merge (gop) thi code moi duoc them vao.

### Toi khong biet Git la gi, co sao khong?

Khong sao. He thong tu dong xu ly Git. Ban chi can biet:
- Code moi nam tren "branch" rieng (nhu ban sao)
- Code cu van an toan tren branch "main"
- Khi hai long voi code moi, nho nguoi biet ky thuat giup merge

---

## Meo Su Dung

1. **Viet yeu cau cang chi tiet cang tot.** "Tao API" se cho ket qua chung chung. "Tao REST API quan ly nguoi dung voi dang ky bang email, dang nhap bang JWT, phan quyen admin/user" se cho ket qua tot hon.

2. **Dung file .md cho yeu cau phuc tap.** Khi yeu cau dai, viet vao file roi dung `/agent-full ten-file.md`.

3. **Doc bao cao review.** File `reports/*_review_agent.md` cho ban biet code co van de gi va cach sua.

4. **Chay `/agent-review` truoc khi giao code.** Ngay ca khi tu viet code, ban co the dung agent review de kiem tra.

5. **Chay `/agent-security` thuong xuyen.** De dam bao code khong co lo hong bao mat.

---

## Khi Gap Su Co

| Van de | Cach xu ly |
|--------|-----------|
| Claude Code khong mo | Kiem tra da cai chua: go `claude` trong terminal |
| Khong thay lenh `/agent-*` | Dam bao dang o dung thu muc du an (co file `.claude/commands/`) |
| He thong bao "go: command not found" | Cai Go: https://go.dev/dl/ |
| He thong bao "golangci-lint not found" | Cai golangci-lint: https://golangci-lint.run/welcome/install/ |
| He thong dung va khong phan hoi | An Ctrl+C de dung, roi chay lai lenh |
| He thong hoi cau hoi ban khong hieu | Tra loi "yes" hoac "co" de tiep tuc, hoac "no" de dung |

---

## Lien He Ho Tro

Neu gap van de khong tu giai quyet duoc:
- Doc file `IMPLEMENTATION_PLAN.md` de hieu tong quan he thong
- Doc file `requirement.md` de hieu yeu cau goc
- Doc bao cao trong `reports/` de hieu he thong da lam gi
