# Template: gRPC Handler

> Đọc file này chỉ khi task liên quan đến gRPC. Reference: `prompts/templates/grpc-handler.tmpl.md`

## 1. PROTO DEFINITION — `proto/<module>/<service>.proto`

```proto
syntax = "proto3";
package <project>.<module>.v1;
option go_package = "<module>/internal/grpc/pb/<module>;pb";

import "google/protobuf/timestamp.proto";

service <ServiceName> {
  rpc <Method>(  <Request>) returns (<Response>);
}

message <Request> {
  string field_one = 1;
  int64  field_two = 2;
}

message <Response> {
  string id         = 1;
  google.protobuf.Timestamp created_at = 2;
}
```

## 2. CODE GENERATION

```bash
buf generate
# or: make proto
# or: protoc --go_out=. --go-grpc_out=. proto/<module>/<service>.proto
```

Verify: `internal/grpc/pb/<module>/<service>.pb.go` exists. NEVER edit generated files.

## 3. HANDLER IMPLEMENTATION — `internal/grpc/<service>_server.go`

```go
type <Service>Server struct {
    pb.Unimplemented<Service>Server          // REQUIRED — forward compat
    usecase usecase.<Service>Usecase
    log     *zap.Logger
}

func New<Service>Server(uc usecase.<Service>Usecase, logger *zap.Logger) *<Service>Server {
    return &<Service>Server{
        usecase: uc,
        log:     logger.With(zap.String("component", "<Service>")),
    }
}

func (s *<Service>Server) <Method>(ctx context.Context, req *pb.<Request>) (*pb.<Response>, error) {
    if req.GetFieldOne() == "" {
        return nil, status.Errorf(codes.InvalidArgument, "field_one is required")
    }
    result, err := s.usecase.<Method>(ctx, req.GetFieldOne())
    if err != nil {
        return nil, mapGRPCError(err)
    }
    return &pb.<Response>{Id: result.ID}, nil
}

// mapGRPCError — in same file or grpc/errors.go (shared across services)
func mapGRPCError(err error) error {
    switch {
    case errors.Is(err, domain.ErrNotFound):          return status.Errorf(codes.NotFound, "not found")
    case errors.Is(err, domain.ErrPermissionDenied):  return status.Errorf(codes.PermissionDenied, "permission denied")
    case errors.Is(err, domain.ErrInvalidInput):      return status.Errorf(codes.InvalidArgument, "invalid input")
    case errors.Is(err, domain.ErrUnauthenticated):   return status.Errorf(codes.Unauthenticated, "unauthenticated")
    case errors.Is(err, domain.ErrAlreadyExists):     return status.Errorf(codes.AlreadyExists, "already exists")
    default:                                           return status.Errorf(codes.Internal, "internal error")
    }
}
```

## 4. SERVICE REGISTRATION

```go
// internal/grpc/server.go — register BEFORE Serve()
pb.Register<Service>Server(s.grpcServer, handler)

// internal/api/init.go — wire dependencies
<service>Handler := grpc.New<Service>Server(l.<Service>Usecase, logger)
```
