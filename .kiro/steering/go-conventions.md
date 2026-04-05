---
inclusion: always
---

# Go Backend Conventions

## Go Version & Project Layout

```
Go 1.21+

cmd/           -- Entry points (main.go)
internal/      -- Private application code
  domain/      -- Entities, value objects, business rules
  service/     -- Use cases, application logic
  repository/  -- Data access implementations
  handler/     -- HTTP/gRPC handlers
pkg/           -- Public shared libraries
api/           -- Proto files, OpenAPI specs
configs/       -- Configuration files
migrations/    -- Database migrations
```

## Error Handling

```go
// REQUIRED: wrap with context using %w
return fmt.Errorf("get user: %w", err)

// REQUIRED: check specific errors
errors.Is(err, domain.ErrNotFound)
errors.As(err, &myErr)

// REQUIRED: domain errors defined as sentinel vars
var (
    ErrNotFound     = errors.New("not found")
    ErrInvalid      = errors.New("invalid")
    ErrUnauthorized = errors.New("unauthorized")
    ErrAlreadyExists = errors.New("already exists")
)

// FORBIDDEN:
return errors.New("user not found")           // no context
_, err := doSomething(); // ignore error       // silent swallowing
panic("something failed")                     // only allowed in main/init
```

## Context Usage

```go
// REQUIRED: context.Context as FIRST parameter in all service/repository methods
func (s *UserService) GetByID(ctx context.Context, id string) (*domain.User, error)
func (r *PostgresUserRepo) FindByID(ctx context.Context, id string) (*domain.User, error)

// REQUIRED: propagate context through entire call chain
// FORBIDDEN: context.Background() inside service/repository (use passed ctx)
// FORBIDDEN: service method without context.Context as first param
```

## Naming Conventions

```
REQUIRED: CamelCase for exported, camelCase for unexported
REQUIRED: Interface names WITHOUT "I" prefix: Reader not IReader, UserRepository not IUserRepository
REQUIRED: Error variables prefixed with Err: ErrNotFound, ErrInvalid, ErrTimeout
REQUIRED: Package names: lowercase, single word, no underscores
REQUIRED: Receiver names: short (1-2 chars), consistent
          - s for service (s *UserService)
          - r for repository (r *PostgresUserRepo)
          - h for handler (h *UserHandler)
REQUIRED: Acronyms fully capitalized: HTTPHandler, JSONParser, URLPath, gRPCServer
```

## Interfaces (Go Idiom: "Accept interfaces, return structs")

```go
// REQUIRED: Interface defined at CONSUMER (service/ defines repo interface)
// service/user_service.go
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*domain.User, error)
    Save(ctx context.Context, user *domain.User) error
}

// REQUIRED: Producer (repository/) returns concrete struct
// repository/user_postgres.go
type PostgresUserRepo struct { db *sql.DB }
func NewPostgresUserRepo(db *sql.DB) *PostgresUserRepo { ... }

// REQUIRED: Small interfaces (1-3 methods). Split if > 5 methods
// FORBIDDEN: Interface defined in domain/ then imported back (Java-style anti-pattern)
// FORBIDDEN: Interface with only 1 implementation and no need for mocking
```

## Struct & Function Rules

```
REQUIRED: Structs with > 3 required fields use constructor NewXxx()
REQUIRED: Functional Options for > 2 optional configs
REQUIRED: Methods should not exceed 50 lines (extract helpers)
REQUIRED: Max 3 levels of nesting (if/for), use early return pattern
FORBIDDEN: Struct with > 10 fields (split into embedded structs)
FORBIDDEN: Function with > 5 parameters (use options struct)
```

## Logging (Mandatory Component Pattern)

```go
// REQUIRED: Use zap for structured logging
// REQUIRED: Create component-scoped logger ONCE in constructor

func NewUserService(repo UserRepository, logger *zap.Logger) *UserService {
    return &UserService{
        repo:   repo,
        logger: logger.With(zap.String("component", "UserService")), // ONCE here
    }
}

// Then use throughout the struct — component field auto-attached
func (s *UserService) Create(ctx context.Context, ...) error {
    s.logger.Info("creating user", zap.String("email", email))
    // → {"component":"UserService","msg":"creating user","email":"..."}
}

// gRPC servers: PascalCase component name ("AuthServer")
// Use cases/services: snake_case component name ("auth_usecase")

// FORBIDDEN:
logger.Info("msg", zap.String("component", "UserService"), ...) // repeated on every call
s.logger = logger  // storing raw logger without .With() in constructor
fmt.Println("debug")                                            // no structured logging
s.logger.Info("user created", zap.String("password", pw))      // log sensitive data
```

## Configuration

```go
// REQUIRED: All configurable values in configs/config.yaml via Viper
// REQUIRED: Config struct with mapstructure tags

type Config struct {
    Server struct {
        Port    int           `mapstructure:"port"`
        Timeout time.Duration `mapstructure:"timeout"`
    } `mapstructure:"server"`
    Auth struct {
        TokenExpiry          time.Duration `mapstructure:"token_expiry"`
        TokenRefreshInterval time.Duration `mapstructure:"token_refresh_interval"`
        BcryptCost           int           `mapstructure:"bcrypt_cost"`
    } `mapstructure:"auth"`
    DB struct {
        MaxOpenConns int           `mapstructure:"max_open_conns"`
        MaxIdleConns int           `mapstructure:"max_idle_conns"`
        ConnTimeout  time.Duration `mapstructure:"conn_timeout"`
    } `mapstructure:"db"`
}

// GOOD: use config
time.Sleep(cfg.Auth.TokenRefreshInterval)

// FORBIDDEN:
time.Sleep(5 * time.Second)          // magic number
const maxRetries = 3                 // hardcoded constant for business logic
"postgres://user:secret@host/db"     // hardcoded connection string
"my-secret-jwt-key"                  // hardcoded secret
```

## Concurrency

```go
// REQUIRED: goroutine must have cancellation mechanism (context or done channel)
// REQUIRED: channel must be closed by SENDER
// REQUIRED: sync.WaitGroup or errgroup for goroutine lifecycle
// REQUIRED: sync.Mutex for shared state, prefer channels for communication

// REQUIRED: recover from panics in goroutines
go func() {
    defer func() {
        if r := recover(); r != nil {
            logger.Error("goroutine panic", zap.Any("error", r))
        }
    }()
    select {
    case <-ctx.Done():
        return
    case job := <-jobs:
        process(job)
    }
}()

// FORBIDDEN: goroutine without context or done channel
go func() { doWork() }() // no cancellation

// FORBIDDEN: unbounded goroutine spawning — use worker pool
// FORBIDDEN: shared state without synchronization
```

## Domain Errors Pattern

```go
// internal/domain/errors.go
var (
    ErrNotFound       = errors.New("not found")
    ErrAlreadyExists  = errors.New("already exists")
    ErrInvalidInput   = errors.New("invalid input")
    ErrUnauthorized   = errors.New("unauthorized")
    ErrForbidden      = errors.New("forbidden")
    ErrTimeout        = errors.New("timeout")
    ErrInternal       = errors.New("internal error")
)

// Wrap with context when propagating
return fmt.Errorf("find user by email %s: %w", email, domain.ErrNotFound)

// Check with errors.Is
if errors.Is(err, domain.ErrNotFound) {
    return nil, status.Errorf(codes.NotFound, "user not found")
}
```
