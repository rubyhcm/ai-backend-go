---
inclusion: always
---

# Project Overview & Coding Guidelines

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Go 1.21+ |
| API Protocol | gRPC (primary) + HTTP (health/metrics only) |
| Protocol Buffers | proto3, buf tool for code generation |
| Database | PostgreSQL (primary) or MySQL 8+ |
| ORM/Query | GORM |
| Logging | go.uber.org/zap (structured logging) |
| Configuration | github.com/spf13/viper |
| Testing | testify, gomock, testcontainers-go |
| Linting | golangci-lint |

## Core Principles (Non-Negotiable)

1. **Clean Architecture** — Strict layer separation. Domain knows nothing. Handler knows only service.
2. **gRPC-First** — All business APIs via gRPC + protobuf. HTTP only for `/healthz` and `/metrics`.
3. **No Global State** — Constructor injection everywhere. Zero `var` singletons for business dependencies.
4. **Error Wrapping** — Always `fmt.Errorf("%w", err)`. Never swallow errors silently.
5. **Context Propagation** — Every service/repo method takes `ctx context.Context` as first arg.
6. **Component Logger** — Create scoped logger once in constructor: `logger.With(zap.String("component", "..."))`.
7. **Config via Viper** — No magic numbers, no hardcoded timeouts, no hardcoded secrets.
8. **Table-Driven Tests** — All tests use `t.Run()`. Every case asserts both value and error.
9. **Parameterized Queries** — No SQL string concatenation. Ever.
10. **Zero-Downtime Migrations** — Expand → Migrate → Contract pattern for all schema changes.

## File Naming Conventions

```
domain entity:        internal/domain/user.go
domain errors:        internal/domain/errors.go
service:              internal/service/user_service.go
service test:         internal/service/user_service_test.go
service mock:         internal/service/mock_user_repository_test.go
repository:           internal/repository/user_postgres.go
handler (gRPC):       internal/handler/user_grpc_handler.go
handler (HTTP):       internal/handler/user_http_handler.go
middleware:           internal/handler/middleware/auth.go
infrastructure:       internal/infra/postgres.go
config:               internal/infra/config.go
migrations (up):      migrations/001_create_users.up.sql
migrations (down):    migrations/001_create_users.down.sql
proto:                api/proto/user/v1/user.proto
generated proto:      internal/grpc/pb/user/v1/user.pb.go
```

## How Kiro Should Approach a Feature Request

When asked to implement a new feature, follow this sequence:

1. **Understand the domain** — What entities are involved? What are the business rules?
2. **Define domain layer** — Create/update entities in `internal/domain/`
3. **Define domain errors** — Add to `internal/domain/errors.go` if new error types needed
4. **Write service interface** — Define repository interface in service file (consumer-side)
5. **Implement service** — Business logic in `internal/service/`
6. **Write service tests** — Table-driven tests with gomock, cover success + all error paths
7. **Implement repository** — Data access in `internal/repository/`, implement service's interface
8. **Create migration** — SQL migration file for any schema changes
9. **Define proto** — Add RPC methods to `.proto` file in `api/proto/`
10. **Generate code** — Run `buf generate`
11. **Implement gRPC handler** — In `internal/handler/`, embed UnimplementedXxxServer
12. **Register handler** — In `cmd/api/main.go` DI wiring
13. **Write handler tests** — Test request validation and error mapping

## Key Patterns to Apply by Default

- **Repository pattern** for every entity that touches the database
- **Adapter pattern** for every external service (email, SMS, payment, storage)
- **Circuit breaker** for every external HTTP/gRPC call
- **Middleware/decorator** for cross-cutting concerns (auth, logging, metrics, rate-limit)
- **Functional options** for structs with optional configuration
- **errgroup** for parallel operations that need error collection

## What NOT To Do

- Do NOT put business logic in gRPC handlers — delegate to service layer
- Do NOT define interfaces in `domain/` and import them back (Java-style anti-pattern)
- Do NOT use `SELECT *` in any query
- Do NOT hardcode timeouts, limits, or configuration values
- Do NOT log sensitive data (passwords, tokens, PII, secrets)
- Do NOT create goroutines without a cancellation mechanism
- Do NOT write tests without assertions (coverage trap)
- Do NOT use `OFFSET` pagination for large tables — use keyset pagination
- Do NOT rename or drop database columns in a single migration — use Expand-Migrate-Contract
