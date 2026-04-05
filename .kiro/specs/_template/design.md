# Design: [Feature Name]

## Domain Entities

```go
// internal/domain/[entity].go

type [Entity] struct {
    ID        string
    [Field1]  [Type]
    [Field2]  [Type]
    CreatedAt time.Time
    UpdatedAt time.Time
}

// Domain errors (add to internal/domain/errors.go if new)
var (
    Err[Entity]NotFound    = fmt.Errorf("%w: [entity]", ErrNotFound)
    Err[Entity]AlreadyExists = fmt.Errorf("%w: [entity]", ErrAlreadyExists)
)
```

## Service Layer

### Interface (defined in service file — consumer-side)

```go
// internal/service/[entity]_service.go

type [Entity]Repository interface {
    FindByID(ctx context.Context, id string) (*domain.[Entity], error)
    FindBy[Field](ctx context.Context, [field] [Type]) (*domain.[Entity], error)
    Save(ctx context.Context, entity *domain.[Entity]) error
    Delete(ctx context.Context, id string) error
}

type [Feature]Service interface {
    [Method1](ctx context.Context, input [Input1]) (*domain.[Entity], error)
    [Method2](ctx context.Context, id string) (*domain.[Entity], error)
}
```

### Use Cases

| Method | Input | Output | Business Logic |
|--------|-------|--------|----------------|
| `Create[Entity]` | `Create[Entity]Input` | `*domain.[Entity], error` | Validate, check duplicates, hash password, save |
| `Get[Entity]ByID` | `id string` | `*domain.[Entity], error` | Fetch, check existence |
| `Update[Entity]` | `id string, input Update[Entity]Input` | `*domain.[Entity], error` | Validate, check ownership, update |
| `Delete[Entity]` | `id string` | `error` | Soft delete |

## Repository Layer

### Database Schema

```sql
CREATE TABLE IF NOT EXISTS [table_name] (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    [col1]     [TYPE] NOT NULL,
    [col2]     [TYPE] NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ NULL
);

COMMENT ON TABLE [table_name] IS '[Table description]';
COMMENT ON COLUMN [table_name].[col1] IS '[Column description]';

CREATE INDEX idx_[table]_[col] ON [table_name]([col1]) WHERE deleted_at IS NULL;
```

### Migration Files

```
migrations/
  [NNN]_create_[table_name].up.sql
  [NNN]_create_[table_name].down.sql
```

## gRPC API

### Proto Definition

```protobuf
// api/proto/[module]/v1/[service].proto
syntax = "proto3";
package [project].[module].v1;

import "google/protobuf/timestamp.proto";

service [Service]Service {
    rpc Create[Entity](Create[Entity]Request) returns (Create[Entity]Response);
    rpc Get[Entity](Get[Entity]Request)       returns (Get[Entity]Response);
    rpc Update[Entity](Update[Entity]Request) returns (Update[Entity]Response);
    rpc Delete[Entity](Delete[Entity]Request) returns (Delete[Entity]Response);
    rpc List[Entity]s(List[Entity]sRequest)   returns (List[Entity]sResponse);
}

message [Entity] {
    string id          = 1;
    string [field1]    = 2;
    string [field2]    = 3;
    google.protobuf.Timestamp created_at = 10;
    google.protobuf.Timestamp updated_at = 11;
}

message Create[Entity]Request {
    string [field1] = 1; // required
    string [field2] = 2; // required
}

message Create[Entity]Response {
    [Entity] [entity] = 1;
}

message List[Entity]sRequest {
    int32  page_size  = 1; // default: 20, max: 100
    string page_token = 2; // cursor for keyset pagination
}

message List[Entity]sResponse {
    repeated [Entity] [entity]s    = 1;
    string            next_page_token = 2;
}
```

### Error Mapping

```go
domain.ErrNotFound        → codes.NotFound
domain.ErrAlreadyExists   → codes.AlreadyExists
domain.ErrInvalidInput    → codes.InvalidArgument
domain.ErrUnauthorized    → codes.Unauthenticated
domain.ErrForbidden       → codes.PermissionDenied
domain.ErrInternal        → codes.Internal
```

## Architecture Diagram

```
gRPC Client
    |
    v
[Entity]Handler (internal/handler/)
    - validate input
    - call service
    - map domain errors → gRPC status
    |
    v
[Feature]Service (internal/service/)
    - business logic
    - orchestration
    - emit events
    |
    v
[Entity]Repository interface (defined in service/)
    |
    v
Postgres[Entity]Repo (internal/repository/)
    - SQL queries
    - map rows → domain entities
    |
    v
PostgreSQL Database
```

## Dependencies

- New packages needed: [list any new go packages]
- External services: [email, SMS, payment, storage, etc.]
- Config values to add: [new config fields in config.yaml]
