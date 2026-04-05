---
inclusion: always
---

# Architecture Rules

## Clean Architecture Layers

```
Layer            | Responsibility                   | Allowed Imports
-----------------|----------------------------------|------------------
domain/          | Entities, value objects, rules   | standard library only
service/         | Use cases, orchestration         | domain/
repository/      | Data access implementation       | domain/ (for types)
handler/         | HTTP/gRPC entry points           | service/
infra/           | DB, cache, queue connections     | domain/ (for types)
pkg/             | Shared utilities                 | standard library
```

## Dependency Rules (STRICT)

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
|   |   |   |-- auth.go
|   |   |   |-- logging.go
|   |   |   +-- recovery.go
|   |   +-- router.go
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
|   +-- openapi/
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
    make proto
    OR
    protoc --go_out=. --go-grpc_out=. proto/<module>/<service>.proto

  Generated files land in: internal/grpc/pb/<module>/
  NEVER edit generated files manually.

Step 3 — HANDLER IMPLEMENTATION
  File: internal/grpc/<service>_server.go
  - Embed pb.Unimplemented<Service>Server for forward compatibility
  - Constructor: New<Service>Server(usecase, logger) *<Service>Server
  - Each RPC method: validate input → call usecase → map to proto response
  - Map domain errors to gRPC status codes
  - Use component-scoped logger: logger.With(zap.String("component", "<Service>"))

Step 4 — SERVICE REGISTRATION
  File: internal/grpc/server.go
  - pb.Register<Service>Server(grpcServer, handler)
  - Register BEFORE server.Serve()
```

### gRPC Error Mapping

```go
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
REQUIRED: Log each RPC call with: method, duration, status code, user id
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
REQUIRED: Pagination for list RPCs (page_token + page_size pattern)
REQUIRED: Request validation at handler layer before calling usecase
FORBIDDEN: Business logic in handler
FORBIDDEN: Database queries in handler
```

## Dependency Injection

```
REQUIRED: Constructor injection via NewXxx(deps...)
REQUIRED: All wiring in cmd/api/main.go
REQUIRED: Interfaces for all external dependencies

Example:
  db := postgres.NewConnection(cfg.DB)
  userRepo := repository.NewPostgresUserRepo(db)
  userSvc := service.NewUserService(userRepo, logger)
  userHandler := handler.NewUserHandler(userSvc)

OPTIONAL: wire (Google) or fx (Uber) for complex DI
FORBIDDEN: Global variables for dependencies
FORBIDDEN: init() for dependency setup
```
