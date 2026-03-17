# GitHub Copilot Instructions

This is a **Go backend monorepo** using Clean Architecture. Follow all rules below for every suggestion.

---

## Architecture

### Layer Map

| Layer | Package | Can import |
|-------|---------|------------|
| Domain | `internal/domain/` | standard library only (zero internal imports) |
| Service / Usecase | `internal/service/` | domain only |
| Repository impl | `internal/repository/` | domain only (for types) |
| Handler (gRPC/HTTP) | `internal/handler/` or `internal/grpc/` | service only |
| Infra | `internal/infra/` | domain only (for types) |
| Pkg | `pkg/` | standard library only |

**Dependency direction:** `handler → service → domain`. Never reverse.

```
                handler/
                  |
                  v
               service/  <-- defines interfaces for dependencies
               /      \
              v        v
      repository/    infra/
              \        /
               v      v
              domain/
                  |
                  v
              (nothing)

FORBIDDEN:
  - Circular dependencies between packages
  - domain/ importing any internal package
  - handler/ importing repository/ directly
  - service/ importing infra/ directly
```

- Interfaces are defined **at the consumer side** (e.g., `service/` defines the repo interface it needs).
- Domain layer must have **zero imports** from internal packages.
- Handlers must contain **zero business logic** — delegate everything to service.

### Project Structure

```
project-root/
|-- cmd/
|   +-- api/
|       +-- main.go                  # Entry point, DI wiring
|
|-- internal/
|   |-- domain/
|   |   |-- user.go                  # Entity
|   |   |-- errors.go                # Domain errors
|   |   +-- value_objects.go         # Value objects
|   |
|   |-- service/
|   |   |-- user_service.go          # Use case + interface definition
|   |   +-- user_service_test.go     # Unit tests
|   |
|   |-- repository/
|   |   |-- user_postgres.go         # Repository implementation
|   |   +-- user_postgres_test.go    # Integration tests
|   |
|   |-- handler/                     # HTTP handlers
|   |   |-- user_handler.go
|   |   |-- middleware/
|   |   |   |-- auth.go
|   |   |   |-- logging.go
|   |   |   +-- recovery.go
|   |   +-- router.go
|   |
|   |-- grpc/                        # gRPC handlers
|   |   |-- pb/<module>/             # Generated — DO NOT edit
|   |   |-- <service>_server.go
|   |   +-- server.go
|   |
|   +-- infra/
|       |-- postgres.go
|       |-- redis.go
|       +-- config.go
|
|-- pkg/
|   |-- logger/
|   +-- validator/
|
|-- api/
|   |-- proto/                       # Protobuf definitions
|   +-- openapi/                     # OpenAPI specs
|
|-- configs/
|   |-- config.dev.yaml
|   +-- config.prod.yaml
|
|-- migrations/
|   |-- 001_create_users.up.sql
|   +-- 001_create_users.down.sql
|
|-- tests/
|   +-- integration/
|
|-- Makefile
|-- go.mod
+-- .golangci.yml
```

---

## Go Code Conventions

### Naming
- Use `CamelCase` for exported names, `camelCase` for unexported.
- No `I` prefix for interfaces (use `UserRepository`, not `IUserRepository`).
- Error variables: `ErrNotFound`, `ErrAlreadyExists`, etc.
- Constructors: `NewXxx(deps...) *Xxx`.
- Package names: lowercase, single word, no underscores.
- Receiver names: short (1–2 chars), consistent (`s` for service, `r` for repo).
- Acronyms fully capitalized: `HTTPHandler`, `JSONParser`, `URLPath`.

### Error Handling
```go
// CORRECT
return fmt.Errorf("userService.GetByID: %w", err)
if errors.Is(err, domain.ErrNotFound) { ... }

// WRONG
return err                    // loses context
if err.Error() == "not found" // string comparison
```

Custom domain errors:
```go
var (
    ErrNotFound    = errors.New("not found")
    ErrInvalid     = errors.New("invalid")
    ErrUnauthorized = errors.New("unauthorized")
)
```

Never use `panic()` in library/service code (only in `main` or `init`).

### Context
- Every service and repository method must have `ctx context.Context` as the **first parameter**.
- Propagate context through the entire call chain.
- Use `context.WithTimeout` for external calls (DB, HTTP, gRPC).
- Default timeouts: **30s** for HTTP, **5s** for DB, **10s** for cache.
- **Never** call `context.Background()` inside service/repository layer — use the passed `ctx`.

### Configuration
- All configurable values (timeouts, limits, URLs, rate limits, buffer sizes, token expiry, etc.) go in `configs/config.yaml` loaded via **Viper**.
- Use `mapstructure` tags on config structs.
- **Never hardcode** durations, limits, or credentials in business logic.
- Separate configs per environment (dev, staging, prod).
- Secrets via environment variables (override config.yaml values).

```go
// BAD
time.Sleep(5 * time.Second)

// GOOD
time.Sleep(cfg.Auth.TokenRefreshInterval)
```

### Logging
- Use `zap` logger.
- Every struct that logs must create a **child logger** in its constructor with a `"component"` field:
  ```go
  func NewUserService(repo UserRepository, logger *zap.Logger) *UserService {
      return &UserService{
          repo:   repo,
          logger: logger.With(zap.String("component", "UserService")),
      }
  }
  ```
  - gRPC servers use PascalCase: `"AuthServer"`
  - Usecases/services use snake_case: `"auth_usecase"`
- **FORBIDDEN**: Storing raw logger without `.With()` in constructors.
- **FORBIDDEN**: Adding `zap.String("component", ...)` inline on every log call instead of in the constructor.
- Never log sensitive data (passwords, tokens, PII).

### Functions & Structs
- Keep methods under 50 lines; extract helpers otherwise.
- Max 3 levels of nesting (`if`/`for`) — use early return.
- No naked returns in functions longer than 5 lines.
- No global mutable state.
- Structs with > 3 required fields use `NewXxx()` constructor.
- Functional Options for > 2 optional configs.
- **FORBIDDEN**: Struct with > 10 fields — split into embedded structs.
- **FORBIDDEN**: Function with > 5 parameters — use options struct.

### Interfaces
- Defined at **consumer side** (`service/` defines repo interface, not `domain/`).
- Producer (`repository/`) returns concrete struct.
- Small interfaces (1–3 methods); split if > 5 methods.
- **FORBIDDEN**: Interface with only 1 implementation and no mock needed.

### Concurrency
- Every goroutine must have a cancellation mechanism (context or done channel).
- Channel must be closed by the sender.
- Use `sync.WaitGroup` or `errgroup` for goroutine lifecycle.
- Use `sync.Mutex` for shared state; prefer channels for communication.
- **FORBIDDEN**: Unbounded goroutine spawning — use worker pool.

---

## Design Patterns

### Apply by default
- **Repository Pattern** — for every entity data access; interface at consumer side.
- **Constructor Injection** — for every dependency, no globals.
- **Middleware/Decorator** — for cross-cutting concerns (auth, logging, metrics).
- **Adapter Pattern** — for external services (unless library already exposes a clean interface).
- **Circuit Breaker** — for ALL external HTTP/gRPC calls (`github.com/sony/gobreaker/v2`).

### Apply when appropriate
- **Functional Options** — when struct has many optional configs.
- **Factory Method** — when creating objects with many variants.
- **Strategy** — when algorithm changes at runtime.
- **Observer/Event Bus** — when one action triggers many side effects.
- **Facade** — when aggregating multiple services into one entry point.
- **Worker Pool** — for batch/parallel processing with limits.
- **Fan-Out / Fan-In** (`errgroup`) — for parallel calls collecting results.
- **Pipeline** (channel chaining) — for data flowing through multiple processing steps.

### Pattern selection guide

| Situation | Pattern |
|-----------|---------|
| Creating objects with many variants | Factory Method |
| Complex config with many options | Functional Options |
| Data access for an entity | Repository (DEFAULT) |
| Wrapping external service | Adapter (DEFAULT) |
| Adding logging/metrics/auth | Decorator / Middleware |
| Calling external API/service | Circuit Breaker (DEFAULT) |
| Changing algorithm at runtime | Strategy |
| One action triggers many side effects | Observer / Event Bus |
| Batch/parallel processing with limits | Worker Pool |
| Parallel calls collecting results | Fan-Out / Fan-In (errgroup) |
| Data through multiple processing steps | Pipeline |
| Injecting dependencies | Constructor Injection (DEFAULT) |

### Anti-patterns to avoid
- No God struct (struct > 10 fields or > 7 methods).
- No circular dependencies between packages.
- No global mutable state.
- No interface pollution (define interface only when ≥2 implementations or mocking is needed).
- No premature abstraction.
- No deep inheritance thinking (Go uses composition).
- No `interface{}` when a concrete type can be used.
- No over-wrapping (adapter around adapter).

---

## SOLID Principles

```
S — Single Responsibility: each struct/function has one job
O — Open/Closed: extend via interfaces, not modification
L — Liskov Substitution: interface satisfaction
I — Interface Segregation: small interfaces (1–3 methods)
D — Dependency Inversion: depend on interfaces, not concrete structs
```

---

## Security — Secure Coding Checklist

Every code suggestion must pass:

```
- [ ] Input validation at every handler (go-playground/validator struct tags)
- [ ] Parameterized queries — NO string concat SQL (even with GORM Raw)
- [ ] JWT: explicit algorithm validation, expiry enforced, RS256/ES256 in production
- [ ] NO hardcoded secrets — use env / vault / config
- [ ] crypto/rand for security-sensitive random values (NOT math/rand)
- [ ] json.Decoder with MaxBytesReader to prevent DoS
- [ ] Context timeout on every external call (30s HTTP, 5s DB, 10s cache)
- [ ] Goroutines always have cancellation mechanism
- [ ] Passwords hashed with bcrypt (cost ≥ 12) or argon2
- [ ] TLS 1.2+ for all external connections
- [ ] No sensitive data in logs (passwords, tokens, PII)
- [ ] Audit log for authentication events
- [ ] CORS configured with specific origins (not "*" in prod)
- [ ] Rate limiting on auth and API endpoints
```

### Common Go Security Anti-patterns

```go
// WRONG — insecure random
token := fmt.Sprintf("%d", math.rand.Intn(1000000))

// CORRECT
b := make([]byte, 32)
crypto/rand.Read(b)

// WRONG — JSON without size limit
json.Unmarshal(body, &data)

// CORRECT
json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20)).Decode(&data)

// WRONG — SQL injection
db.Raw(fmt.Sprintf("SELECT * WHERE id = %s", id))

// CORRECT
db.Raw("SELECT * WHERE id = ?", id)

// WRONG — goroutine leak
go func() { doBlockingWork() }()

// CORRECT
go func() {
    defer func() {
        if r := recover(); r != nil {
            logger.Error("goroutine panic", zap.Any("error", r))
        }
    }()
    select {
    case <-ctx.Done():
        return
    case result := <-ch:
        process(result)
    }
}()
```

### Rate Limiting
- Required on all authentication endpoints.
- Required on all API endpoints (per user/IP).
- Return `429 Too Many Requests` with `Retry-After` header.
- Recommended: token bucket or sliding window algorithm.

### OWASP Top 10 (2025) Quick Reference

```
A01 Broken Access Control    --> RBAC, check permissions per endpoint
A02 Cryptographic Failures   --> TLS, bcrypt, AES-GCM, no hardcoded keys
A03 Injection                --> Parameterized queries, input validation
A04 Insecure Design          --> Threat modeling, secure defaults
A05 Security Misconfiguration--> No debug in prod, minimal permissions
A06 Vulnerable Components    --> govulncheck + Snyk, regular dependency updates
A07 Auth Failures            --> MFA, secure JWT, session management
A08 Data Integrity Failures  --> Signed updates, secure deserialization
A09 Logging Failures         --> Audit logs, monitoring, alerting
A10 SSRF                     --> Validate URLs, block internal networks
```

### Security Scanning Toolchain

```bash
# MANDATORY
gosec ./...
govulncheck ./...

# MANDATORY if installed
semgrep --config=p/golang --config=p/owasp-top-ten ./...
snyk test --all-projects
snyk code test
```

---

## Testing Standards

### Rules
- Use **table-driven tests** with `t.Run()` — always.
- Use `testify/assert` and `testify/require` for assertions.
- Use `gomock` for mocking interfaces.
- **Every** test case MUST have assertions (no coverage traps).
- Mock all external dependencies via interfaces.
- Run `go test -race` in CI; zero tolerance for race conditions.

### Coverage Gates
| Layer | Target |
|-------|--------|
| `domain/` | ≥ 90% |
| `service/` or `usecase/` | ≥ 85% |
| `handler/` or `grpc/` | ≥ 80% |
| `repository/` | ≥ 70% |
| Critical paths (auth, payment) | ≥ 95% |
| Overall | ≥ 80% |

### Test Cases Required
- Happy path
- Error paths (DB error, validation error, not found)
- Edge cases: nil input, empty string, zero value, boundary values
- Context cancellation / timeout

### Test Naming Convention
```
Format: Test<Struct>_<Method>/<scenario>

Examples:
  TestUserService_GetByID/success
  TestUserService_GetByID/not_found
  TestUserService_Create/invalid_email
  TestUserHandler_Create/unauthorized
```

### Test File Placement
```
Unit tests:        internal/service/user_service_test.go     (same package)
Handler tests:     internal/handler/user_handler_test.go      (same package)
Integration tests: tests/integration/user_test.go             (separate dir)
Test helpers:      internal/testutil/helpers.go               (shared test utils)
Test fixtures:     testdata/                                  (test data files)
```

### Unit Test Example
```go
func TestUserService_GetByID(t *testing.T) {
    tests := []struct {
        name    string
        id      string
        setup   func(*MockUserRepository)
        want    *domain.User
        wantErr error
    }{
        {
            name: "success - user found",
            id:   "user-123",
            setup: func(m *MockUserRepository) {
                m.EXPECT().FindByID(gomock.Any(), "user-123").
                    Return(&domain.User{ID: "user-123", Name: "John"}, nil)
            },
            want: &domain.User{ID: "user-123", Name: "John"},
        },
        {
            name: "error - user not found",
            id:   "user-999",
            setup: func(m *MockUserRepository) {
                m.EXPECT().FindByID(gomock.Any(), "user-999").
                    Return(nil, domain.ErrNotFound)
            },
            wantErr: domain.ErrNotFound,
        },
        {
            name:    "error - empty id",
            id:      "",
            setup:   func(m *MockUserRepository) {},
            wantErr: domain.ErrInvalid,
        },
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            ctrl := gomock.NewController(t)
            defer ctrl.Finish()
            repo := NewMockUserRepository(ctrl)
            tt.setup(repo)
            svc := NewUserService(repo, zap.NewNop())
            got, err := svc.GetByID(context.Background(), tt.id)
            if tt.wantErr != nil {
                require.ErrorIs(t, err, tt.wantErr)
                return
            }
            require.NoError(t, err)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

### Integration Tests
```go
//go:build integration

func TestUserRepo_Integration(t *testing.T) {
    ctx := context.Background()
    pg, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: testcontainers.ContainerRequest{
            Image:        "postgres:16-alpine",
            ExposedPorts: []string{"5432/tcp"},
            Env: map[string]string{
                "POSTGRES_PASSWORD": "test",
                "POSTGRES_DB":       "testdb",
            },
            WaitingFor: wait.ForListeningPort("5432/tcp"),
        },
        Started: true,
    })
    require.NoError(t, err)
    defer pg.Terminate(ctx)
    // ... test cases against real DB
}
```

---

## gRPC Conventions

### Workflow (MANDATORY for all gRPC features)

```
Step 1 — PROTO DEFINITION
  File: api/proto/<module>/<service>.proto
  - syntax proto3, package <project>.<module>.v1
  - google.protobuf.Timestamp for time fields
  - Add field validation comments

Step 2 — CODE GENERATION
  buf generate           # preferred
  OR make proto
  Generated files → internal/grpc/pb/<module>/
  NEVER edit generated files manually.

Step 3 — HANDLER IMPLEMENTATION
  File: internal/grpc/<service>_server.go
  - Embed pb.Unimplemented<Service>Server
  - Constructor: New<Service>Server(usecase, logger) *<Service>Server
  - Each RPC: validate input → call usecase → map to proto response
  - Map domain errors to gRPC status codes
  - Component-scoped logger: logger.With(zap.String("component", "<Service>Server"))

Step 4 — SERVICE REGISTRATION
  File: internal/grpc/server.go
  - pb.Register<Service>Server(grpcServer, handler)
```

### gRPC Handler Rules
- **REQUIRED**: Embed `pb.Unimplemented<Service>Server`.
- **REQUIRED**: Validate all input fields before calling usecase.
- **REQUIRED**: Map ALL domain errors to gRPC status codes.
- **REQUIRED**: Use context deadline from incoming `ctx` — do NOT create new timeout.
- **REQUIRED**: Log each RPC call with: method, duration, status code, partner/user id.
- **FORBIDDEN**: Business logic inside gRPC handler.
- **FORBIDDEN**: Direct repository access from handler.
- **FORBIDDEN**: Returning raw Go errors — always wrap with `status.Errorf`.
- **FORBIDDEN**: Editing generated `pb/*.go` files.

### Domain Error → gRPC Status Code Mapping

| Domain Error | gRPC Code |
|---|---|
| `ErrNotFound` | `codes.NotFound` |
| `ErrAlreadyExists` | `codes.AlreadyExists` |
| `ErrPermissionDenied` | `codes.PermissionDenied` |
| `ErrUnauthenticated` | `codes.Unauthenticated` |
| `ErrInvalidInput` | `codes.InvalidArgument` |
| `ErrTimeout` | `codes.DeadlineExceeded` |
| `ErrInternal` | `codes.Internal` |
| default | `codes.Internal` |

```go
// Use status.Errorf — never return raw errors from gRPC handlers
return nil, status.Errorf(codes.NotFound, "resource not found")
```

### API Design Rules
- gRPC-first — all business APIs use gRPC + protobuf.
- HTTP only for health checks (`/healthz`) and metrics (`/metrics`).
- Pagination for list RPCs: `page_token` + `page_size` pattern.
- Every new or modified gRPC service must have a `docs/grpc/<module>/<service>_examples.md` with `grpcurl` examples.

---

## Dependency Injection

```go
// cmd/api/main.go — all wiring here
db := postgres.NewConnection(cfg.DB)
userRepo := repository.NewPostgresUserRepo(db)
userSvc := service.NewUserService(userRepo, logger)
userHandler := handler.NewUserHandler(userSvc)
```

- **REQUIRED**: Constructor injection via `NewXxx(deps...)`.
- **REQUIRED**: All wiring in `cmd/api/main.go`.
- **REQUIRED**: Interfaces for all external dependencies.
- **OPTIONAL**: `wire` (Google) or `fx` (Uber) for complex DI.
- **FORBIDDEN**: Global variables for dependencies.
- **FORBIDDEN**: `init()` for dependency setup.

---

## Database Rules

- Migrations for all schema changes (`golang-migrate` or `goose`).
- Transactions for multi-table operations.
- Connection pooling configuration required.
- Parameterized queries / prepared statements always.
- **FORBIDDEN**: Raw SQL string concatenation.
- **FORBIDDEN**: Schema changes without migration files.
- **FORBIDDEN**: Database logic in `domain/` layer.

---

## Pre-completion Checklist

Before finalizing any suggestion, verify:

- [ ] Dependency direction correct (no reverse imports)
- [ ] Every service/repository method has `ctx context.Context` as first param
- [ ] No hardcoded values — config via Viper from `configs/`
- [ ] Logger creates child with `component` name in constructor (not inline)
- [ ] Error wrapped with `fmt.Errorf("...: %w", err)`
- [ ] `errors.Is` / `errors.As` used for error checking
- [ ] Goroutines have cancellation mechanism + panic recovery
- [ ] SOLID principles followed
- [ ] Repository pattern applied for data access (interface at consumer side)
- [ ] Unit tests written (table-driven, all paths covered)
- [ ] Coverage target met per layer
- [ ] Secure coding checklist passed
- [ ] `go build ./...` and `go test ./... -race` would pass
- [ ] No global mutable state
- [ ] Circuit breaker on all external calls
