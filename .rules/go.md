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

### Component Logger Pattern

```
REQUIRED: Structured logging (zap)
REQUIRED: Log levels: Debug, Info, Warn, Error
REQUIRED: Include context fields: request_id, user_id, trace_id
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

### Log Classification (MANDATORY)

```
Every log statement MUST belong to one category:
  1. ASSERTION_CHECK   — input/security/data-invariant validation failure
  2. RETURN_VALUE_CHECK — err != nil, nil unexpected, external call failure
  3. EXCEPTION         — unhandled/propagated exceptions, DB/network/auth errors
  4. LOGIC_BRANCH      — rare/unexpected branch, fallback, feature flag decision
  5. OBSERVING_POINT   — request/job/transaction start & end
```

### Logging Decision Engine

```
FOR each potential log position:

IF (unexpected OR high-impact OR hard-to-debug)
    → MUST LOG

ELSE IF (important state / decision point)
    → SHOULD LOG

ELSE
    → DO NOT LOG
```

### Priority Enforcement (HIGH PRIORITY)

```
Agent MUST prioritize adding logs to:
  1. EXCEPTION (catch blocks)        — lowest real-world coverage, highest debug value
  2. RETURN_VALUE_CHECK (err != nil) — missing error logs hide failures silently
```

### Detailed Rules per Category

```
ASSERTION_CHECK:
  MUST LOG:  input validation failure, security validation failure, data invariant violation
  DO NOT LOG: internal assertions already guaranteed by tests

RETURN_VALUE_CHECK ⚠️:
  MUST LOG:   err != nil, nil/null unexpected, external call failure, retry triggered
  SHOULD LOG: external API response (optional sampling)
  DO NOT LOG: pure function return, simple getter

EXCEPTION 🚨:
  MUST LOG:   exception not fully handled, exception propagated upward,
              DB / network / auth / payment error
  SHOULD LOG: retryable exception (include retry_count)
  DO NOT LOG: fully handled + no side effect

LOGIC_BRANCH:
  MUST LOG:   rare/unexpected branch, fallback logic, feature flag decision
  SHOULD LOG: business decision (approve/reject)
  DO NOT LOG: trivial if/else

OBSERVING_POINT:
  MUST LOG:   request start/end, job start/end, transaction boundary
  SHOULD LOG: important state (user_id, request_id, latency)
  DO NOT LOG: repetitive debug info
```

### Decision Matrix

```
Critical + Unhandled   → ERROR log (MUST)
Recoverable + Retry    → WARN log
Important State        → INFO log
High-frequency trivial → NO LOG
```

### Log Format

```json
{
  "level": "ERROR | WARN | INFO",
  "category": "EXCEPTION | RETURN_VALUE_CHECK | ASSERTION_CHECK | LOGIC_BRANCH | OBSERVING_POINT",
  "message": "clear and specific message",
  "context": {
    "request_id": "...",
    "trace_id": "...",
    "user_id": "...",
    "function": "...",
    "service": "...",
    "retry_count": 0
  }
}
```

### Error Handling + Logging Rule

```
IF error is returned:
    → MUST LOG OR explicitly delegate logging to upper layer

IF delegated:
    → DO NOT log here (avoid duplication)
```

### Log Density Control

```
High-frequency paths (loops, hot APIs):
    → use sampling OR aggregated logging (log only 1/N requests)
```

### Anti-Patterns (STRICTLY FORBIDDEN)

```
❌ Blind logging:        log("start function") / log("end function")
❌ Missing error log:    if err != nil { return err }  // no log
❌ Duplicate logging:    same error logged at multiple layers
❌ Logging sensitive:    password, token, full PII
```

### Agent Validation Checklist

```
Before finishing code, verify:
[ ] All exceptions are logged or delegated
[ ] All err != nil paths are handled
[ ] No duplicate logs across layers
[ ] No sensitive data leaked
[ ] Log messages are meaningful (not generic)
[ ] High-value areas (exception, return-check) are covered
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
