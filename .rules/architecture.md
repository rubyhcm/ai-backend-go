# Architecture Rules

## Clean Architecture Layers

```
Layer            | Responsibility                  | Allowed Imports
-----------------|---------------------------------|------------------
domain/          | Entities, value objects, rules   | standard library only
service/         | Use cases, orchestration         | domain/
repository/      | Data access implementation       | domain/ (for types)
handler/         | HTTP/gRPC entry points           | service/
infra/           | DB, cache, queue connections     | domain/ (for types)
pkg/             | Shared utilities                 | standard library
```

## Dependency Rules

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

## Project Structure Template

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
|   |-- handler/
|   |   |-- user_handler.go          # HTTP/gRPC handler
|   |   |-- user_handler_test.go     # Handler tests
|   |   |-- middleware/
|   |   |   |-- auth.go              # Auth middleware
|   |   |   |-- logging.go           # Logging middleware
|   |   |   +-- recovery.go          # Panic recovery
|   |   +-- router.go                # Route registration
|   |
|   +-- infra/
|       |-- postgres.go              # DB connection
|       |-- redis.go                 # Cache connection
|       +-- config.go                # App configuration
|
|-- pkg/
|   |-- logger/                      # Structured logger
|   +-- validator/                   # Input validator
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
|   +-- integration/                 # Integration tests
|
|-- Makefile
|-- go.mod
|-- go.sum
+-- .golangci.yml
```

## gRPC Workflow (MANDATORY for all gRPC features)

Every new gRPC service or method MUST follow this exact order:

```
Step 1 — PROTO DEFINITION
  File: proto/<module>/<service>.proto
  - Define service, rpc methods, request/response messages
  - Use google.protobuf.Timestamp for time fields
  - Add field validation comments (required, min, max)
  - Follow proto3 syntax, package naming: <project>.<module>.v1

Step 2 — CODE GENERATION
  Run after every proto change:
    buf generate           # preferred (uses buf.gen.yaml)
    OR
    make proto             # if Makefile target exists
    OR
    protoc --go_out=. --go-grpc_out=. proto/<module>/<service>.proto

  Generated files land in: internal/grpc/pb/<module>/

  NEVER edit generated files manually.
  Re-run generation whenever .proto changes.

Step 3 — HANDLER IMPLEMENTATION
  File: internal/grpc/<service>_server.go
  - Embed pb.Unimplemented<Service>Server for forward compatibility
  - Constructor: New<Service>Server(usecase, logger) *<Service>Server
  - Each RPC method: validate input → call usecase → map to proto response
  - Map domain errors to gRPC status codes (see error mapping below)
  - Use component-scoped logger: logger.With(zap.String("component", "<Service>"))

Step 4 — SERVICE REGISTRATION
  File: internal/grpc/server.go (or internal/api/init.go)
  - pb.Register<Service>Server(grpcServer, handler)
  - Register BEFORE server.Serve()
  - Add to DI wiring in internal/api/init.go if needed
```

### gRPC Project Structure

```
proto/
  <module>/
    <service>.proto          ← Step 1: define here

internal/grpc/
  pb/
    <module>/
      <service>.pb.go        ← Step 2: generated, DO NOT edit
      <service>_grpc.pb.go   ← Step 2: generated, DO NOT edit
  <service>_server.go        ← Step 3: implement here
  <service>_server_test.go   ← Step 3: tests
  server.go                  ← Step 4: register here
```

### gRPC Error Mapping

```go
// Domain error → gRPC status code
domain.ErrNotFound         → codes.NotFound
domain.ErrAlreadyExists    → codes.AlreadyExists
domain.ErrPermissionDenied → codes.PermissionDenied
domain.ErrUnauthenticated  → codes.Unauthenticated
domain.ErrInvalidInput     → codes.InvalidArgument
domain.ErrTimeout          → codes.DeadlineExceeded
domain.ErrInternal         → codes.Internal

// Use status.Errorf — never return raw errors from gRPC handlers
return nil, status.Errorf(codes.NotFound, "resource not found")
```

### gRPC Handler Rules

```
REQUIRED: Embed pb.Unimplemented<Service>Server in handler struct
REQUIRED: Validate all input fields before calling usecase
REQUIRED: Map ALL domain errors to appropriate gRPC status codes
REQUIRED: Never leak internal error details in gRPC status messages
REQUIRED: Use context deadline from incoming ctx — do NOT create new timeout
REQUIRED: Log each RPC call with: method, duration, status code, partner/user id
FORBIDDEN: Business logic inside gRPC handler (delegate to usecase)
FORBIDDEN: Direct repository access from handler
FORBIDDEN: Returning raw Go errors — always wrap with status.Errorf
FORBIDDEN: Editing generated pb/*.go files
```

## API Design Rules

```
REQUIRED: gRPC-first — all business APIs use gRPC + protobuf
REQUIRED: HTTP only for health checks (/healthz) and metrics (/metrics)
REQUIRED: Proto versioning: package <project>.<module>.v1
REQUIRED: Pagination for list RPCs (use page_token + page_size pattern)
REQUIRED: Request validation at handler layer before calling usecase
FORBIDDEN: Business logic in handler (delegate to usecase)
FORBIDDEN: Database queries in handler
```

## Dependency Injection

```
REQUIRED: Constructor injection via NewXxx(deps...)
REQUIRED: All wiring in cmd/api/main.go
REQUIRED: Interfaces for all external dependencies

Example:
  // cmd/agent/main.go
  db := postgres.NewConnection(cfg.DB)
  userRepo := repository.NewPostgresUserRepo(db)
  userSvc := service.NewUserService(userRepo, logger)
  userHandler := handler.NewUserHandler(userSvc)

OPTIONAL: wire (Google) or fx (Uber) for complex DI
FORBIDDEN: Global variables for dependencies
FORBIDDEN: init() for dependency setup
```

## Database Rules

```
REQUIRED: Migrations for all schema changes (golang-migrate or goose)
REQUIRED: Transactions for multi-table operations
REQUIRED: Connection pooling configuration
REQUIRED: Prepared statements / parameterized queries
FORBIDDEN: Raw SQL string concatenation
FORBIDDEN: Schema changes without migration files
FORBIDDEN: Database logic in domain/ layer
```
