# Design Patterns for Go Backend

```
Agent MUST read this file before designing and generating code.
Choose the right pattern for the problem. Do NOT force a pattern when not needed.
Go prefers SIMPLICITY. If a pattern only adds a wrapper without adding value → skip.
```

---

## CREATIONAL PATTERNS

### Factory Method
```
WHEN: Creating objects with many variants (payment processor, notifier, storage)
GO IDIOM: Constructor function NewXxx() returning interface

func NewStorage(storageType string) (Storage, error) {
    switch storageType {
    case "s3":
        return &S3Storage{}, nil
    case "gcs":
        return &GCSStorage{}, nil
    default:
        return nil, fmt.Errorf("unknown storage type: %s", storageType)
    }
}

NOTE: Prefer Functional Options over complex Factory
```

### Functional Options (Go-idiomatic Builder)
```
WHEN: Object with many optional configs (server, client, service)
GO IDIOM: Option functions

type Option func(*Server)

func WithPort(p int) Option {
    return func(s *Server) { s.port = p }
}

func WithTimeout(t time.Duration) Option {
    return func(s *Server) { s.timeout = t }
}

func NewServer(opts ...Option) *Server {
    s := &Server{port: 8080, timeout: 30 * time.Second} // defaults
    for _, opt := range opts {
        opt(s)
    }
    return s
}

// Usage:
srv := NewServer(WithPort(9090), WithTimeout(60*time.Second))
```

### Singleton
```
WHEN: DB connection pool, logger, config (ONLY when truly needed)
GO IDIOM: sync.Once

var (
    instance *DB
    once     sync.Once
)

func GetDB() *DB {
    once.Do(func() {
        instance = &DB{...}
    })
    return instance
}

WARNING: Avoid overuse. Prefer Dependency Injection.
```

---

## STRUCTURAL PATTERNS

### Repository Pattern (DEFAULT for data access)
```
WHEN: Every entity needs data access
GO IDIOM: "Accept interfaces, return structs" (Consumer-side interfaces)

// service/user_service.go (CONSUMER defines interface)
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*domain.User, error)
    Save(ctx context.Context, user *domain.User) error
}

type UserService struct {
    repo UserRepository
}

func NewUserService(repo UserRepository) *UserService {
    return &UserService{repo: repo}
}

// repository/user_postgres.go (PRODUCER returns struct)
type PostgresUserRepo struct {
    db *sql.DB
}

func NewPostgresUserRepo(db *sql.DB) *PostgresUserRepo {
    return &PostgresUserRepo{db: db}
}

func (r *PostgresUserRepo) FindByID(ctx context.Context, id string) (*domain.User, error) {
    // implementation
}

REQUIRED: Interface at CONSUMER (service/), NOT in domain/
REQUIRED: Small interfaces (1-3 methods). If > 5 methods → split
```

### Adapter
```
WHEN: Wrapping external service/library (payment gateway, email provider)
GO IDIOM: Interface + wrapper struct

type EmailSender interface {
    Send(ctx context.Context, to, subject, body string) error
}

type sendgridAdapter struct {
    client *sendgrid.Client
}

func NewSendgridAdapter(apiKey string) *sendgridAdapter {
    return &sendgridAdapter{client: sendgrid.NewClient(apiKey)}
}

func (a *sendgridAdapter) Send(ctx context.Context, to, subject, body string) error {
    // wrap sendgrid-specific logic
}

DEFAULT USE, EXCEPT WHEN:
  - Library already has a good interface (e.g., AWS SDK v2)
  - Only 1 implementation and no need for mocking
  - Wrapper just forwards 1:1 without adding logic
```

### Decorator / Middleware
```
WHEN: Adding behavior without modifying original code (logging, auth, metrics, rate limit)
GO IDIOM: HTTP middleware chain, function wrapping

// HTTP Middleware
func LoggingMiddleware(logger *slog.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            next.ServeHTTP(w, r)
            logger.Info("request", "method", r.Method, "path", r.URL.Path, "duration", time.Since(start))
        })
    }
}

// Service Decorator
type loggingUserService struct {
    next   UserService
    logger *slog.Logger
}

func WithLogging(svc UserService, logger *slog.Logger) UserService {
    return &loggingUserService{next: svc, logger: logger}
}
```

### Facade
```
WHEN: Aggregating multiple services into one entry point (order = inventory + payment + shipping)
GO IDIOM: Struct aggregating dependencies

type OrderFacade struct {
    inventory InventoryService
    payment   PaymentService
    shipping  ShippingService
}

func (f *OrderFacade) PlaceOrder(ctx context.Context, order Order) error {
    if err := f.inventory.Reserve(ctx, order.Items); err != nil {
        return fmt.Errorf("reserve inventory: %w", err)
    }
    if err := f.payment.Charge(ctx, order.Total); err != nil {
        f.inventory.Release(ctx, order.Items) // compensate
        return fmt.Errorf("charge payment: %w", err)
    }
    if err := f.shipping.Schedule(ctx, order); err != nil {
        // handle compensation...
        return fmt.Errorf("schedule shipping: %w", err)
    }
    return nil
}
```

---

## BEHAVIORAL PATTERNS

### Strategy
```
WHEN: Changing algorithm at runtime (pricing, sorting, compression, notification)
GO IDIOM: Interface + dependency injection

type PricingStrategy interface {
    Calculate(ctx context.Context, order Order) (Money, error)
}

type standardPricing struct{}
type premiumPricing struct{ discount float64 }

type OrderService struct {
    pricing PricingStrategy
}

func NewOrderService(pricing PricingStrategy) *OrderService {
    return &OrderService{pricing: pricing}
}
```

### Observer / Event-Driven
```
WHEN: One action triggers many side effects (user created → send email + create audit log)
GO IDIOM: Channel-based or Event Bus

type EventType string

const (
    UserCreated EventType = "user.created"
    OrderPlaced EventType = "order.placed"
)

type Event struct {
    Type    EventType
    Payload interface{}
}

type EventBus struct {
    handlers map[EventType][]func(context.Context, Event) error
    mu       sync.RWMutex
}

func (eb *EventBus) Subscribe(t EventType, h func(context.Context, Event) error) {
    eb.mu.Lock()
    defer eb.mu.Unlock()
    eb.handlers[t] = append(eb.handlers[t], h)
}

func (eb *EventBus) Publish(ctx context.Context, e Event) error {
    eb.mu.RLock()
    handlers := eb.handlers[e.Type]
    eb.mu.RUnlock()
    for _, h := range handlers {
        if err := h(ctx, e); err != nil {
            return fmt.Errorf("handle %s: %w", e.Type, err)
        }
    }
    return nil
}

NOTE: For microservices, use message broker (NATS, Kafka, RabbitMQ)
```

### Circuit Breaker (DEFAULT for external calls)
```
WHEN: Calling external services (API, payment, third-party)
GO IDIOM: gobreaker library

import "github.com/sony/gobreaker/v2"

cb := gobreaker.NewCircuitBreaker[*http.Response](gobreaker.Settings{
    Name:        "payment-api",
    MaxRequests: 3,
    Interval:    10 * time.Second,
    Timeout:     30 * time.Second,
    ReadyToTrip: func(counts gobreaker.Counts) bool {
        return counts.ConsecutiveFailures > 5
    },
})

resp, err := cb.Execute(func() (*http.Response, error) {
    return httpClient.Do(req)
})

REQUIRED: Every external HTTP/gRPC call MUST have a circuit breaker
```

---

## CONCURRENCY PATTERNS (GO-SPECIFIC)

### Worker Pool
```
WHEN: Processing many tasks concurrently with limits (batch processing, file upload)
GO IDIOM: Buffered channel + goroutines

func WorkerPool(ctx context.Context, numWorkers int, jobs <-chan Job, results chan<- Result) {
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for {
                select {
                case job, ok := <-jobs:
                    if !ok { return }
                    results <- process(ctx, job)
                case <-ctx.Done():
                    return
                }
            }
        }()
    }
    wg.Wait()
    close(results)
}

REQUIRED: Context or done channel for cancellation
```

### Fan-Out / Fan-In
```
WHEN: Parallel calls then collecting results (parallel API calls, batch fetch)
GO IDIOM: errgroup.Group

import "golang.org/x/sync/errgroup"

g, ctx := errgroup.WithContext(ctx)
results := make([]*Result, len(items))

for i, item := range items {
    i, item := i, item
    g.Go(func() error {
        res, err := process(ctx, item)
        if err != nil {
            return fmt.Errorf("process item %d: %w", i, err)
        }
        results[i] = res
        return nil
    })
}

if err := g.Wait(); err != nil {
    return fmt.Errorf("fan-out: %w", err)
}
```

### Pipeline
```
WHEN: Data flows through multiple processing steps (ETL, data transformation)
GO IDIOM: Channel chaining

func generate(ctx context.Context, data []int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, d := range data {
            select {
            case out <- d:
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}

func transform(ctx context.Context, in <-chan int) <-chan string {
    out := make(chan string)
    go func() {
        defer close(out)
        for v := range in {
            select {
            case out <- fmt.Sprintf("processed: %d", v):
            case <-ctx.Done():
                return
            }
        }
    }()
    return out
}
```

---

## DEPENDENCY INJECTION (DEFAULT)

### Constructor Injection
```
GO IDIOM: NewXxx(deps...) pattern

func NewUserService(repo UserRepository, logger *zap.Logger, eventBus *EventBus) *UserService {
    return &UserService{
        repo:     repo,
        logger:   logger.With(zap.String("component", "UserService")), // component-scoped logger
        eventBus: eventBus,
    }
}

REQUIRED: Every dependency injected via constructor
REQUIRED: Create a component-scoped child logger in constructor using logger.With().
          This pre-attaches "component" field to ALL log statements from this struct
          without repeating it on every log call.

          // BAD — repeated on every log call:
          s.logger.Info("creating user", zap.String("component", "UserService"), ...)
          s.logger.Error("failed", zap.String("component", "UserService"), ...)

          // GOOD — set once in constructor, auto-appended everywhere:
          s.logger = logger.With(zap.String("component", "UserService"))
          s.logger.Info("creating user", ...)   // → {"component":"UserService","msg":"creating user"}
          s.logger.Error("failed", ...)         // → {"component":"UserService","msg":"failed"}

          Benefit: logs are filterable by component in Kibana/Loki/Datadog:
          component="UserService" AND level="error"

FORBIDDEN: Global variables for dependencies
OPTIONAL: wire (Google) or fx (Uber) for complex DI
```

---

## PATTERN SELECTION GUIDE

```
Situation                               --> Pattern
Creating objects with many variants     --> Factory Method
Complex config with many options        --> Functional Options
Data access for an entity               --> Repository (DEFAULT)
Wrapping external service               --> Adapter (DEFAULT, unless over-engineering)
Adding logging/metrics/auth             --> Decorator / Middleware
Calling external API/service            --> Circuit Breaker (DEFAULT)
Changing algorithm at runtime           --> Strategy
One action triggers many side effects   --> Observer / Event Bus
Batch/parallel processing with limits   --> Worker Pool
Parallel calls collecting results       --> Fan-Out / Fan-In (errgroup)
Data through multiple processing steps  --> Pipeline
Injecting dependencies                  --> Constructor Injection (DEFAULT)
```

---

## ANTI-PATTERNS (FORBIDDEN)

```
FORBIDDEN: God struct (struct > 10 fields or > 7 methods)
FORBIDDEN: Circular dependencies between packages
FORBIDDEN: Global mutable state (use DI instead)
FORBIDDEN: Interface pollution (interface with only 1 impl and no need for mocking)
FORBIDDEN: Premature abstraction (pattern for only 1 use case)
FORBIDDEN: Deep inheritance thinking (Go uses composition)
FORBIDDEN: Empty interface{} when a concrete type can be used
FORBIDDEN: Over-wrapping (adapter around adapter)
```
