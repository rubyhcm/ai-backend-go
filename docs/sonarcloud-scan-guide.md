# Hướng Dẫn Chạy SonarCloud Scan

## Tổng quan

SonarCloud scan phân tích code để phát hiện:
- **Vulnerabilities** — lỗ hổng bảo mật (BLOCKER / CRITICAL)
- **Bugs** — lỗi logic trong code
- **Security Hotspots** — điểm cần review bảo mật thủ công
- **Code Smells** — vấn đề chất lượng code (cognitive complexity, duplicate literals...)
- **Coverage** — tỉ lệ unit test coverage

Sau khi scan xong, script tự động tạo report markdown tại `reports/<timestamp>_sonarcloud_report.md`.

---

## Yêu cầu

| Tool | Phiên bản | Cài đặt |
|------|-----------|---------|
| Java | 17+ | `sudo apt install openjdk-17-jre-headless` |
| sonar-scanner | 6.2.1+ | Xem hướng dẫn bên dưới |
| Python | 3.x | Thường có sẵn trên Linux/macOS |
| Go | Match `go.mod` | Dùng gvm nếu có nhiều version |

---

## Cài đặt sonar-scanner (một lần)

### Linux (Ubuntu/WSL)

```bash
# 1. Cài Java 17
echo "1205" | sudo -S apt-get install -y openjdk-17-jre-headless

# 2. Tải sonar-scanner
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-linux-x64.zip \
     -O /tmp/sonar-scanner.zip

# 3. Giải nén và cài vào /opt
unzip /tmp/sonar-scanner.zip -d /tmp
sudo mv /tmp/sonar-scanner-6.2.1.4610-linux-x64 /opt/sonar-scanner

# 4. Thêm vào PATH (thêm vào ~/.bashrc để dùng lại lần sau)
echo 'export PATH="/opt/sonar-scanner/bin:$PATH"' >> ~/.bashrc
export PATH="/opt/sonar-scanner/bin:$PATH"

# 5. Kiểm tra
sonar-scanner --version
# → SonarScanner CLI 6.2.1.4610
```

> **Lưu ý:** Nếu `sonar-scanner` không nhận sau khi thêm PATH, dùng đường dẫn đầy đủ: `/opt/sonar-scanner/bin/sonar-scanner`

### macOS

```bash
brew install sonar-scanner
```

---

## Cấu hình repo

### Bước 1 — Sync files từ ai_tech

```bash
# Từ thư mục repo đích
rsync -av /path/to/ai_tech/scripts/ ./scripts/
rsync -av /path/to/ai_tech/docs/ ./docs/
```

### Bước 2 — Tạo `sonar-project.properties`

```properties
# sonar-project.properties
sonar.host.url=https://sonarcloud.io
sonar.organization=<your-org-key>       # lấy tại sonarcloud.io/account/organizations
sonar.projectKey=<your-project-key>     # lấy tại sonarcloud.io/projects

sonar.sources=.
sonar.exclusions=**/*_test.go,vendor/**,bin/**,proto/**,migrations/**,scripts/**,tools/**,docs/**
sonar.tests=.
sonar.test.inclusions=**/*_test.go
sonar.go.coverage.reportPaths=coverage.out
sonar.sourceEncoding=UTF-8
```

### Bước 3 — Tạo `.env.local` (gitignored)

```bash
cat > .env.local << 'EOF'
SONAR_TOKEN=<your-sonarcloud-token>
SONAR_HOST_URL=https://sonarcloud.io
EOF
```

> Token lấy tại: `https://sonarcloud.io/account/security`

---

## Chạy scan thủ công

### Go version bình thường (go trong PATH)

```bash
# Bước 1 — Generate coverage
go test ./... -coverprofile=coverage.out

# Bước 2 — Chạy scan
export $(cat .env.local | xargs) && sonar-scanner

# Bước 3 — Tạo report markdown
python3 scripts/gen_sonar_report.py
```

### Go version quản lý bằng gvm (version mismatch)

Nếu gặp lỗi `compile: version "X.Y.Z" does not match go tool version`, cần chỉ định đúng `GOROOT`:

```bash
# Xem các version Go có sẵn
ls ~/.gvm/gos/

# Bước 1 — Generate coverage với đúng Go version
GOROOT="$HOME/.gvm/gos/go1.25.7" \
PATH="$HOME/.gvm/gos/go1.25.7/bin:$PATH" \
  go test ./internal/... -coverprofile=coverage.out

# Bước 2 — Chạy scan (sonar-scanner dùng đường dẫn đầy đủ nếu cần)
export $(cat .env.local | xargs) && /opt/sonar-scanner/bin/sonar-scanner

# Bước 3 — Tạo report markdown
python3 scripts/gen_sonar_report.py
```

> **Lưu ý:** Nếu project có nhiều package build failed (proto, scripts...), dùng `./internal/...` thay vì `./...` để chỉ test các package chính.

---

## Chạy scan qua Agent

Security agent tự động chạy toàn bộ pipeline:

```
/agent-security
```

hoặc scan + auto-fix CRITICAL/HIGH:

```
/agent-security-fix
```

Agent sẽ thực hiện theo thứ tự:
1. `gosec` — Go-specific security patterns
2. `govulncheck` — dependency CVE check
3. `semgrep` — SAST multi-language (nếu có)
4. `snyk` — dependency + code scan (nếu có)
5. `sonar-scanner` → `python3 scripts/gen_sonar_report.py` — SonarCloud scan + report
6. AI review OWASP Top 10 + Go-specific issues
7. Tạo report tổng hợp: `reports/<timestamp>_security_agent.md`

---

## Cấu trúc report

Report markdown được tạo tự động gồm các phần:

```
# SonarCloud Security Report
## Summary              ← metrics tổng quan + gate result (PASS/BLOCKED)
## Issue Breakdown      ← bảng phân loại theo type × severity
## Vulnerabilities      ← tất cả BLOCKER / CRITICAL / MAJOR / MINOR
## Bugs                 ← nếu có
## Security Hotspots    ← HIGH / MEDIUM / LOW
## Code Smells          ← CRITICAL / MAJOR / MINOR / INFO (toàn bộ)
## Recommendations      ← fix suggestions theo priority
## Scan Details         ← host, project key, timestamp
```

---

## Giới hạn free plan SonarCloud

Free plan giới hạn tổng số dòng code. Nếu gặp lỗi:

```
This analysis will make your organization to reach the maximum allowed lines limit
```

**Kiểm tra lỗi chi tiết:**
```bash
# taskId lấy từ output của sonar-scanner dòng cuối
export $(cat .env.local | xargs)
curl -s -u "$SONAR_TOKEN:" \
  "https://sonarcloud.io/api/ce/task?id=<taskId>" | python3 -m json.tool
```

**Fix:** Thu hẹp scope trong `sonar-project.properties`:
```properties
sonar.exclusions=**/*_test.go,vendor/**,bin/**,proto/**,migrations/**,scripts/**,tools/**,docs/**,schemas/**
```

---

## Xử lý lỗi thường gặp

| Lỗi | Nguyên nhân | Fix |
|-----|-------------|-----|
| `No organization with key 'xxx'` | Sai organization key | Kiểm tra tại `sonarcloud.io/account/organizations` |
| `maximum allowed lines limit` | Vượt giới hạn free plan | Thêm exclusions vào `sonar-project.properties` |
| `SONAR_TOKEN not set` | Thiếu token | Thêm vào `.env.local` |
| `sonar-scanner: command not found` | Chưa add PATH | Dùng `/opt/sonar-scanner/bin/sonar-scanner` |
| `compile: version mismatch` | Sai Go version (gvm) | `GOROOT="$HOME/.gvm/gos/goX.Y.Z" go test ./...` |
| `The last analysis has failed` | Lỗi phía server | Xem API: `curl -u "$SONAR_TOKEN:" "sonarcloud.io/api/ce/task?id=<taskId>"` |
| `build failed` trên nhiều packages | Proto/scripts không compile | Dùng `./internal/...` thay vì `./...` |

---

## Files liên quan

| File | Mô tả |
|------|-------|
| `scripts/gen_sonar_report.py` | Script tạo report markdown từ SonarCloud API |
| `sonar-project.properties` | Cấu hình SonarCloud (org, project key, exclusions) |
| `.env.local` | Token + host URL — **gitignored, không commit** |
| `.rules/security.md` | Security rules cho agents |
| `prompts/agent-security.md` | System prompt của Security Agent |
| `.claude/commands/agent-security.md` | Slash command `/agent-security` |
| `.claude/commands/agent-security-fix.md` | Slash command `/agent-security-fix` |
