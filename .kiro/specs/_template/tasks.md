# Tasks: [Feature Name]

Status: TODO | IN_PROGRESS | DONE | BLOCKED

---

## Task 1: Domain Layer

**Status:** TODO
**Files:**
- `internal/domain/[entity].go`
- `internal/domain/errors.go` (update)

**What to implement:**
- [ ] `[Entity]` struct with all fields
- [ ] Domain validation methods (if needed)
- [ ] New error sentinel variables

**Acceptance Criteria:**
- Domain struct has all required fields
- No imports from internal packages (stdlib only)
- Unit tests for any validation methods

---

## Task 2: Database Migration

**Status:** TODO
**Depends on:** Task 1
**Files:**
- `migrations/[NNN]_create_[table].up.sql`
- `migrations/[NNN]_create_[table].down.sql`

**What to implement:**
- [ ] CREATE TABLE with all required columns
- [ ] Primary key, audit fields, soft delete column
- [ ] Indexes for query patterns
- [ ] Constraints (FK, UNIQUE, CHECK)
- [ ] Comments on table and columns
- [ ] DOWN migration (DROP TABLE)

**Acceptance Criteria:**
- Migration runs without error
- DOWN migration fully reverses UP
- All indexes match query patterns in design

---

## Task 3: Repository Layer

**Status:** TODO
**Depends on:** Task 2
**Files:**
- `internal/repository/[entity]_postgres.go`
- `internal/repository/[entity]_postgres_test.go`

**What to implement:**
- [ ] `Postgres[Entity]Repo` struct
- [ ] `NewPostgres[Entity]Repo(db *sql.DB) *Postgres[Entity]Repo`
- [ ] `FindByID(ctx, id)` — return ErrNotFound if not exists
- [ ] `FindBy[Field](ctx, value)` — as needed
- [ ] `Save(ctx, entity)` — INSERT or UPDATE
- [ ] `Delete(ctx, id)` — soft delete (set deleted_at)
- [ ] All queries use parameterized values
- [ ] All queries filter `deleted_at IS NULL`

**Acceptance Criteria:**
- All methods return domain errors (not raw DB errors)
- No `SELECT *`
- Integration tests pass with testcontainers

---

## Task 4: Service Layer

**Status:** TODO
**Depends on:** Task 1
**Files:**
- `internal/service/[feature]_service.go`
- `internal/service/[feature]_service_test.go`

**What to implement:**
- [ ] `[Entity]Repository` interface (consumer-side)
- [ ] `[Feature]Service` struct with constructor
- [ ] `Create[Entity](ctx, input)` — validate, check dups, save
- [ ] `Get[Entity]ByID(ctx, id)` — fetch, return ErrNotFound
- [ ] `Update[Entity](ctx, id, input)` — validate, check ownership, update
- [ ] `Delete[Entity](ctx, id)` — soft delete
- [ ] Component-scoped logger in constructor

**Acceptance Criteria:**
- Table-driven tests with gomock
- Cover: success, not found, invalid input, duplicate
- 85%+ coverage
- No business logic skipped

---

## Task 5: gRPC Handler

**Status:** TODO
**Depends on:** Task 4
**Files:**
- `api/proto/[module]/v1/[service].proto` (update)
- `internal/handler/[entity]_grpc_handler.go`
- `internal/handler/[entity]_grpc_handler_test.go`

**What to implement:**
- [ ] Define RPC methods in `.proto` file
- [ ] Run `buf generate` to regenerate pb files
- [ ] `[Entity]Handler` struct embedding `pb.Unimplemented[Service]Server`
- [ ] Input validation for each RPC method
- [ ] Call service method
- [ ] Map domain errors to gRPC status codes
- [ ] Log each RPC: method, user_id, duration, status

**Acceptance Criteria:**
- Embeds UnimplementedXxxServer
- All domain errors mapped to correct gRPC codes
- Never leaks internal error details to caller
- Handler tests cover all error paths
- No business logic in handler

---

## Task 6: DI Wiring

**Status:** TODO
**Depends on:** Tasks 3, 4, 5
**Files:**
- `cmd/api/main.go`

**What to implement:**
- [ ] Instantiate `Postgres[Entity]Repo`
- [ ] Instantiate `[Feature]Service`
- [ ] Instantiate `[Entity]Handler`
- [ ] Register handler with gRPC server

**Acceptance Criteria:**
- Application starts without error
- All dependencies injected via constructors
- No global variables

---

## Task 7: Integration Test

**Status:** TODO
**Depends on:** Tasks 2, 3
**Files:**
- `tests/integration/[entity]_test.go`

**What to implement:**
- [ ] `//go:build integration` tag
- [ ] Start PostgreSQL container with testcontainers
- [ ] Test full CRUD flow against real DB
- [ ] Clean state between tests

**Acceptance Criteria:**
- Tests pass: `go test -tags=integration ./tests/integration/...`
- Each test cleans up after itself
- Tests verify actual DB state

---

## Notes

- [Bất kỳ ghi chú, quyết định kỹ thuật, hoặc rủi ro nào]
- [Dependency ngoài cần cài thêm]
- [Config values cần thêm vào config.yaml]
