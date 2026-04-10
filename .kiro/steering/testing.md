---
inclusion: always
---

# Testing Rules — Go Backend

## Table-Driven Tests (MANDATORY)

All tests MUST use table-driven format with `t.Run()`:

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
            want:    &domain.User{ID: "user-123", Name: "John"},
            wantErr: nil,
        },
        {
            name: "error - user not found",
            id:   "user-999",
            setup: func(m *MockUserRepository) {
                m.EXPECT().FindByID(gomock.Any(), "user-999").
                    Return(nil, domain.ErrNotFound)
            },
            want:    nil,
            wantErr: domain.ErrNotFound,
        },
        {
            name:    "error - empty id",
            id:      "",
            setup:   func(m *MockUserRepository) {},
            want:    nil,
            wantErr: domain.ErrInvalidInput,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            ctrl := gomock.NewController(t)
            defer ctrl.Finish()

            repo := NewMockUserRepository(ctrl)
            tt.setup(repo)

            svc := service.NewUserService(repo, zaptest.NewLogger(t))
            got, err := svc.GetByID(context.Background(), tt.id)

            // REQUIRED: always assert error
            if tt.wantErr != nil {
                require.Error(t, err)
                assert.ErrorIs(t, err, tt.wantErr)
                return
            }
            require.NoError(t, err)

            // REQUIRED: always assert return value
            assert.Equal(t, tt.want.ID, got.ID)
            assert.Equal(t, tt.want.Name, got.Name)
        })
    }
}
```

## Assertion Rules (ANTI COVERAGE TRAP)

```
MANDATORY: Every test case MUST have assertions:
  - assert returned value (NEVER just call function and ignore result)
  - assert error (wantErr → require.Error + assert.ErrorIs, no error → require.NoError)
  - assert state changes (if side effects, verify mock expectations)

FORBIDDEN: Test that only calls a function without any assertion
FORBIDDEN: Empty assertions: assert.True(t, true)
FORBIDDEN: Test that does not check error return
FORBIDDEN: Mock returning a value that is never verified

// NOT ACCEPTED:
func TestBad(t *testing.T) {
    svc := NewService(repo)
    svc.Process(ctx, input) // no assertion = coverage trap
}
```

## Mocking

```go
// REQUIRED: gomock for interface mocking
// REQUIRED: testify/assert + testify/require for assertions

// Add generate directive in the source file:
//go:generate mockgen -source=user_service.go -destination=mock_user_repository_test.go -package=service_test

// Mock setup pattern:
ctrl := gomock.NewController(t)
defer ctrl.Finish()  // verifies all expectations were met

repo := NewMockUserRepository(ctrl)
repo.EXPECT().FindByID(gomock.Any(), "user-123").Return(user, nil).Times(1)
```

## Test File Placement

```
Unit tests:        internal/service/user_service_test.go      (same package: package service_test)
Handler tests:     internal/handler/user_handler_test.go       (same package: package handler_test)
Integration tests: tests/integration/user_test.go              (build tag: //go:build integration)
Test helpers:      internal/testutil/helpers.go                (shared test utilities)
Test fixtures:     testdata/                                   (JSON, SQL, YAML test data)
```

## Test Naming Convention

```
Format: Test<Struct>_<Method>/<scenario>

Examples:
  TestUserService_GetByID/success
  TestUserService_GetByID/not_found
  TestUserService_GetByID/empty_id
  TestUserService_Create/invalid_email
  TestUserHandler_Create/unauthorized
  TestUserHandler_Create/success
```

## Integration Tests (Testcontainers)

```go
//go:build integration

package integration_test

func TestUserRepo_Integration(t *testing.T) {
    ctx := context.Background()

    // Start real postgres container
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

    // Run tests against real DB
    host, _ := pg.Host(ctx)
    port, _ := pg.MappedPort(ctx, "5432")
    dsn := fmt.Sprintf("postgres://postgres:test@%s:%s/testdb?sslmode=disable", host, port.Port())

    db := mustConnect(t, dsn)
    repo := repository.NewPostgresUserRepo(db)

    // Clean state before each test
    t.Cleanup(func() { db.Exec("TRUNCATE TABLE users RESTART IDENTITY CASCADE") })

    // Test cases...
}

// Run:
// go test -tags=integration ./tests/integration/...
```

## Coverage Policy (Hard Gates)

```
domain/:     90%  — pure business logic, easy to test, no excuses
service/:    85%  — use cases with mocked dependencies
handler/:    80%  — request/response handling
repository/: 70%  — external deps, supplement with integration tests
Critical paths (auth, payment): 95%

Overall project minimum: 80% HARD GATE
  → Review FAILS and code must not be merged if below 80%

IMPORTANT: Coverage % is a guideline, not the goal.
Quality of assertions matters MORE than coverage number.
```

## gRPC Handler Testing

```go
func TestUserServer_Create(t *testing.T) {
    tests := []struct {
        name     string
        req      *pb.CreateUserRequest
        setup    func(*MockUserUsecase)
        wantResp *pb.CreateUserResponse
        wantCode codes.Code
    }{
        {
            name: "success",
            req:  &pb.CreateUserRequest{Email: "test@example.com", Name: "Test"},
            setup: func(m *MockUserUsecase) {
                m.EXPECT().Create(gomock.Any(), gomock.Any()).
                    Return(&domain.User{ID: "1", Email: "test@example.com"}, nil)
            },
            wantCode: codes.OK,
        },
        {
            name: "invalid argument - empty email",
            req:  &pb.CreateUserRequest{Email: "", Name: "Test"},
            setup: func(m *MockUserUsecase) {
                m.EXPECT().Create(gomock.Any(), gomock.Any()).
                    Return(nil, domain.ErrInvalid)
            },
            wantCode: codes.InvalidArgument,
        },
        {
            name: "already exists",
            req:  &pb.CreateUserRequest{Email: "exists@example.com", Name: "Test"},
            setup: func(m *MockUserUsecase) {
                m.EXPECT().Create(gomock.Any(), gomock.Any()).
                    Return(nil, domain.ErrAlreadyExists)
            },
            wantCode: codes.AlreadyExists,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            ctrl := gomock.NewController(t)
            defer ctrl.Finish()

            uc := NewMockUserUsecase(ctrl)
            tt.setup(uc)

            srv := NewUserServer(uc, zap.NewNop())
            resp, err := srv.Create(context.Background(), tt.req)

            if tt.wantCode != codes.OK {
                require.Error(t, err)
                st, ok := status.FromError(err)
                require.True(t, ok)
                assert.Equal(t, tt.wantCode, st.Code())
                return
            }
            require.NoError(t, err)
            assert.NotNil(t, resp)
        })
    }
}
```

## Race Detection

```bash
# REQUIRED: Run with race detector in CI
go test -race ./...

# REQUIRED: Run locally before commit for any concurrent code
go test -race ./internal/...

# ZERO tolerance for race conditions
```

## Running Tests

```bash
# Unit tests
go test ./...

# With coverage
go test ./... -coverprofile=coverage.out
go tool cover -func=coverage.out | grep total

# Race detection
go test -race ./...

# Integration tests only
go test -tags=integration ./tests/integration/...

# Specific test
go test -run TestUserService_GetByID ./internal/service/...

# Verbose output
go test -v -run TestUserService ./internal/service/...
```
