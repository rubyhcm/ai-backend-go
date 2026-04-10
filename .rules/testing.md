# Testing Rules - Go Backend

## Table-Driven Tests (MANDATORY)

```go
func TestUserService_GetByID(t *testing.T) {
    tests := []struct {
        name    string
        id      string
        setup   func(*mockUserRepo)  // setup mocks
        want    *domain.User
        wantErr error
    }{
        {
            name: "success - user found",
            id:   "user-123",
            setup: func(m *mockUserRepo) {
                m.EXPECT().FindByID(gomock.Any(), "user-123").
                    Return(&domain.User{ID: "user-123", Name: "John"}, nil)
            },
            want:    &domain.User{ID: "user-123", Name: "John"},
            wantErr: nil,
        },
        {
            name: "error - user not found",
            id:   "user-999",
            setup: func(m *mockUserRepo) {
                m.EXPECT().FindByID(gomock.Any(), "user-999").
                    Return(nil, domain.ErrNotFound)
            },
            want:    nil,
            wantErr: domain.ErrNotFound,
        },
        {
            name: "error - empty id",
            id:   "",
            setup: func(m *mockUserRepo) {},
            want:    nil,
            wantErr: domain.ErrInvalid,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            ctrl := gomock.NewController(t)
            defer ctrl.Finish()

            repo := NewMockUserRepo(ctrl)
            tt.setup(repo)

            svc := service.NewUserService(repo)
            got, err := svc.GetByID(context.Background(), tt.id)

            // REQUIRED: assert error
            if tt.wantErr != nil {
                require.Error(t, err)
                assert.ErrorIs(t, err, tt.wantErr)
                return
            }
            require.NoError(t, err)

            // REQUIRED: assert return value
            assert.Equal(t, tt.want.ID, got.ID)
            assert.Equal(t, tt.want.Name, got.Name)
        })
    }
}
```

## Assertion Rules (ANTI COVERAGE TRAP)

```
MANDATORY: Every test case MUST have assert/require:
  - assert returned value (NEVER just call function and ignore result)
  - assert error (wantErr true → require.Error, false → require.NoError)
  - assert state changes (if side effects exist, verify mock expectations)

FORBIDDEN: Test that only calls a function without any assertion
FORBIDDEN: Test with empty assertions (assert.True(t, true))
FORBIDDEN: Test that does not check error return
FORBIDDEN: Mock returning a value that is never verified

Example NOT ACCEPTED:
  func TestBad(t *testing.T) {
      svc := NewService(repo)
      svc.Process(ctx, input) // <-- no assertion = coverage trap
  }
```

## Mocking

```
REQUIRED: gomock for interface mocking
REQUIRED: testify/assert + testify/require for assertions
OPTIONAL: testify/mock when flexibility is needed
REQUIRED: Mock EXPECTATIONS must be verified

// Generate mocks
//go:generate mockgen -source=user_service.go -destination=mock_user_repo_test.go -package=service

// Mock setup pattern
ctrl := gomock.NewController(t)
defer ctrl.Finish()  // verify all expectations
repo := NewMockUserRepo(ctrl)
```

## Test File Placement

```
Unit tests:        internal/service/user_service_test.go     (same package)
Handler tests:     internal/handler/user_handler_test.go      (same package)
Integration tests: tests/integration/user_test.go             (separate dir)
Test helpers:      internal/testutil/helpers.go               (shared test utils)
Test fixtures:     testdata/                                  (test data files)
```

## Integration Tests

```
REQUIRED: Build tag //go:build integration
REQUIRED: testcontainers-go for DB/Redis/Kafka
REQUIRED: Clean state before each test (truncate tables)
REQUIRED: Separate from unit tests

// Run unit tests only
go test ./...

// Run integration tests
go test -tags=integration ./tests/integration/...

Example:
  //go:build integration

  func TestUserRepo_Integration(t *testing.T) {
      ctx := context.Background()

      // Start postgres container
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
      dsn := fmt.Sprintf("postgres://postgres:test@%s/testdb?sslmode=disable", pg.Endpoint(ctx, ""))
      repo := repository.NewPostgresUserRepo(mustConnect(dsn))

      // ... test cases
  }
```

## Coverage Policy

```
Minimum coverage targets:
  domain/:     90%  (pure business logic, easy to test)
  service/:    85%  (use cases, mock dependencies)
  handler/:    80%  (HTTP handlers, request/response)
  repository/: 70%  (external deps, use integration tests)
  Critical paths (auth, payment): 95%

Overall project minimum: 80%

IMPORTANT: Coverage % is a guideline, not a goal.
Quality of assertions matters MORE than coverage number.
```

## Test Naming Convention

```
Format: Test<Struct>_<Method>/<scenario>

Examples:
  TestUserService_GetByID/success
  TestUserService_GetByID/not_found
  TestUserService_Create/invalid_email
  TestUserHandler_Create/unauthorized
```

## Race Detection

```
REQUIRED: Run go test -race in CI
REQUIRED: Run go test -race locally before commit for concurrent code
REQUIRED: Fix ALL race conditions (zero tolerance)
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

## Benchmark Tests

```
OPTIONAL but recommended for hot paths:

func BenchmarkUserService_GetByID(b *testing.B) {
    svc := setupService()
    ctx := context.Background()

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        svc.GetByID(ctx, "user-123")
    }
}

// Run: go test -bench=. -benchmem ./internal/service/...
```
