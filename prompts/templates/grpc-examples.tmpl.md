# Template: gRPC Examples File

> Đọc file này khi cần tạo `docs/grpc/<module>/<service>_examples.md`. Reference: `prompts/templates/grpc-examples.tmpl.md`

---

Output file: `docs/grpc/<module>/<service>_examples.md`

```markdown
# gRPC Service: <ServiceName>

**Proto package:** `<project>.<module>.v1`
**Proto file:** `proto/<module>/<service>.proto`
**Handler:** `internal/grpc/<service>_server.go`

---

## Prerequisites

```bash
# Install grpcurl
brew install grpcurl          # macOS
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

grpcurl -plaintext localhost:50051 list
grpcurl -plaintext localhost:50051 describe <project>.<module>.v1.<ServiceName>
```

---

## RPC: <MethodName>

**Description:** [What this RPC does]
**Auth:** [Bearer JWT / API Key / None]

**grpcurl:**
```bash
grpcurl -plaintext \
  -H "authorization: Bearer <token>" \
  -d '{"field_one": "value", "field_two": 123}' \
  localhost:50051 \
  <project>.<module>.v1.<ServiceName>/<MethodName>
```

**Request:**
```json
{ "field_one": "value", "field_two": 123 }
```

**Success (`OK`):**
```json
{ "id": "uuid", "created_at": "2026-01-01T00:00:00Z" }
```

**Errors:**
| Code | Trigger | Message |
|------|---------|---------|
| `INVALID_ARGUMENT` | Missing required field | `"field_one is required"` |
| `NOT_FOUND` | Resource missing | `"not found"` |
| `UNAUTHENTICATED` | Bad/missing token | `"unauthenticated"` |
| `PERMISSION_DENIED` | Insufficient role | `"permission denied"` |

---

[Repeat RPC block for each method]

---

## Go Client

```go
conn, _ := grpc.Dial("localhost:50051", grpc.WithInsecure())
client  := pb.New<ServiceName>Client(conn)
resp, err := client.<MethodName>(ctx, &pb.<Request>{FieldOne: "value"})
```

---

## Config Values

| Key | Default | Description |
|-----|---------|-------------|
| `<section>.<key>` | `<value>` | [What it controls] |
```
