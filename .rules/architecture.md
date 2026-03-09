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

## API Design Rules

```
REQUIRED: RESTful naming: /api/v1/users, /api/v1/users/{id}
REQUIRED: Consistent response format:
  {
    "data": ...,
    "meta": { "page": 1, "total": 100 },
    "error": { "code": "NOT_FOUND", "message": "..." }
  }
REQUIRED: Versioning in URL path: /api/v1/, /api/v2/
REQUIRED: Pagination for list endpoints (cursor or offset)
REQUIRED: Request validation at handler layer
FORBIDDEN: Business logic in handler (delegate to service)
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
