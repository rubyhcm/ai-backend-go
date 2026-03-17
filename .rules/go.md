# Go Backend Rules

## Go Project Layout

```
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

## Dependency Direction (STRICT)

```
domain --> (nothing)
service --> domain
repository --> domain
handler --> service
FORBIDDEN: handler --> domain (direct)
FORBIDDEN: domain --> repository
FORBIDDEN: domain --> infra
```

## Error Handling

```
REQUIRED: fmt.Errorf("%w", err) for wrapping
REQUIRED: errors.Is() / errors.As() for checking
REQUIRED: Custom error types for domain errors:
  var (
      ErrNotFound    = errors.New("not found")
      ErrInvalid     = errors.New("invalid")
      ErrUnauthorized = errors.New("unauthorized")
  )
FORBIDDEN: return errors.New(...) without wrapping context
FORBIDDEN: silent error swallowing (_, err := ...; ignore err)
FORBIDDEN: panic() in library/service code (only in main or init)
```

## Context Usage

```
REQUIRED: func(ctx context.Context, ...) for all service/repository methods
REQUIRED: context.Context as FIRST parameter
REQUIRED: Context propagation through entire call chain
FORBIDDEN: service method without context.Context as first param
FORBIDDEN: context.Background() inside service/repository (use passed ctx)
```

## Naming Conventions

```
REQUIRED: CamelCase for exported, camelCase for unexported
REQUIRED: interface names without "I" prefix (Reader not IReader)
REQUIRED: error variables prefixed with Err: ErrNotFound, ErrInvalid
REQUIRED: Package names: lowercase, single word, no underscores
REQUIRED: Receiver names: short (1-2 chars), consistent (s for service, r for repo)
REQUIRED: Acronyms fully capitalized: HTTPHandler, JSONParser, URLPath
```

## Interfaces (Go Idiom: "Accept interfaces, return structs")

```
REQUIRED: Interface defined at CONSUMER (service/ defines repo interface)
REQUIRED: Producer (repository/) returns concrete struct
REQUIRED: Small interfaces (1-3 methods), split if > 5 methods
FORBIDDEN: Interface defined in domain/ then imported back (Java-style)
FORBIDDEN: Interface with only 1 implementation and no mock needed
```

## Concurrency

```
REQUIRED: goroutine must have cancellation mechanism (context or done channel)
REQUIRED: channel must be closed by sender
REQUIRED: sync.WaitGroup or errgroup for goroutine lifecycle
REQUIRED: sync.Mutex for shared state, prefer channel for communication
FORBIDDEN: goroutine without context or done channel
FORBIDDEN: unbounded goroutine spawning (use worker pool)
FORBIDDEN: shared state without synchronization
```

## Struct & Function Rules

```
REQUIRED: Structs with > 3 required fields use constructor NewXxx()
REQUIRED: Functional Options for > 2 optional configs
REQUIRED: Methods should not exceed 50 lines (extract helpers)
REQUIRED: Max 3 levels of nesting (if/for), use early return
FORBIDDEN: Struct with > 10 fields (split into embedded structs)
FORBIDDEN: Function with > 5 parameters (use options struct)
```

## Logging

```
REQUIRED: Structured logging (zap)
REQUIRED: Log levels: Debug, Info, Warn, Error
REQUIRED: Include context fields: request_id, user_id, trace_id
REQUIRED: Every log statement MUST include a "component" field as prefix
          so logs can be filtered/searched by component name.
          Format: logger.Info("message", zap.String("component", "PartnerAuth"), ...)
          Or use a child logger: log = logger.With(zap.String("component", "PartnerAuth"))
REQUIRED: Use the child logger pattern — create component logger ONCE in constructor:
          func NewXxxServer(..., logger *zap.Logger) *XxxServer {
              return &XxxServer{
                  logger: logger.With(zap.String("component", "XxxServer")),
              }
          }
          Naming: gRPC servers use PascalCase ("AuthServer"), usecases use snake_case ("auth_usecase")
          then use s.logger.Info/Warn/Error throughout the struct methods
FORBIDDEN: Storing raw logger without .With() in constructors (logger: logger)
FORBIDDEN: Adding zap.String("component", ...) inline on every log call instead of constructor
FORBIDDEN: fmt.Println for logging
FORBIDDEN: Log sensitive data (passwords, tokens, PII)
FORBIDDEN: Bare log statements without component field
```

## Configuration

```
REQUIRED: All configurable values MUST be defined in config/config.yaml (or config.go struct)
          and loaded via Viper — never hardcoded in business logic.
REQUIRED: This includes: timeouts, limits, thresholds, feature flags, retry counts,
          buffer sizes, rate limits, max connections, token expiry durations, etc.
REQUIRED: Config struct fields must have mapstructure tags for Viper binding
REQUIRED: Separate configs per environment (dev, staging, prod)
REQUIRED: Environment variables for secrets (override config.yaml values)
FORBIDDEN: Hardcoded secrets, API keys, passwords
FORBIDDEN: Hardcoded URLs, ports, or connection strings
FORBIDDEN: Magic numbers — extract to named config fields
          BAD:  time.Sleep(5 * time.Second)
          GOOD: time.Sleep(cfg.Auth.TokenRefreshInterval)
```
