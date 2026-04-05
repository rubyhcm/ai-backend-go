---
inclusion: always
---

# Design Patterns for Go Backend

Go prefers SIMPLICITY. Do NOT force a pattern when not needed.
If a pattern only adds a wrapper without adding value → skip it.

## Pattern Selection Guide

```
Situation                                 → Pattern
-----------------------------------------  -----------------------------------
Creating objects with many variants        → Factory Method
Complex config with many optional fields   → Functional Options
Data access for an entity                  → Repository (DEFAULT)
Wrapping external service/library          → Adapter (DEFAULT)
Adding logging/metrics/auth/rate-limit     → Decorator / Middleware
Calling external HTTP/gRPC API             → Circuit Breaker (DEFAULT)
Changing algorithm at runtime              → Strategy
One action triggers many side effects      → Observer / Event Bus
Batch/parallel processing with limits      → Worker Pool
Parallel calls collecting results          → Fan-Out / Fan-In (errgroup)
Data flows through multiple steps          → Pipeline
Injecting dependencies                     → Constructor Injection (DEFAULT)
Aggregating multiple services              → Facade
```

---

## CREATIONAL PATTERNS

### Functional Options (Go-idiomatic — prefer over Builder)

Use when: Object with many optional configs (server, client, service)

```go
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

### Factory Method

Use when: Creating objects with many variants (storage, notifier, payment processor)

```go
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
```

### Singleton (Use sparingly — prefer DI)

```go
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
// WARNING: Prefer Dependency Injection for testability
```

---

## STRUCTURAL PATTERNS

### Repository Pattern (DEFAULT for all data access)

Consumer (service/) defines the interface. Producer (repository/) implements it.

```go
// service/user_service.go — CONSUMER defines interface
type UserRepository interface {
    FindByID(ctx context.Context, id string) (*domain.User, error)
    FindByEmail(ctx context.Context, email string) (*domain.User, error)
    Save(ctx context.Context, user *domain.User) error
    Delete(ctx context.Context, id string) error
}

type UserService struct {
    repo   UserRepository
    logger *zap.Logger
}

func NewUserService(repo UserRepository, logger *zap.Logger) *UserService {
    return &UserService{
        repo:   repo,
        logger: logger.With(zap.String("component", "UserService")),
    }
}

// repository/user_postgres.go — PRODUCER returns concrete struct
type PostgresUserRepo struct {
    db *sql.DB
}

func NewPostgresUserRepo(db *sql.DB) *PostgresUserRepo {
    return &PostgresUserRepo{db: db}
}

func (r *PostgresUserRepo) FindByID(ctx context.Context, id string) (*domain.User, error) {
    var user domain.User
    err := r.db.QueryRowContext(ctx, "SELECT id, email, name FROM users WHERE id = $1 AND deleted_at IS NULL", id).
        Scan(&user.ID, &user.Email, &user.Name)
    if errors.Is(err, sql.ErrNoRows) {
        return nil, domain.ErrNotFound
    }
    return &user, err
}
```

### Adapter (DEFAULT for wrapping external services)

```go
// Define interface at consumer
type EmailSender interface {
    Send(ctx context.Context, to, subject, body string) error
}

// Wrap external library
type sendgridAdapter struct {
    client *sendgrid.Client
}

func NewSendgridAdapter(apiKey string) EmailSender {
    return &sendgridAdapter{client: sendgrid.NewClient(apiKey)}
}

func (a *sendgridAdapter) Send(ctx context.Context, to, subject, body string) error {
    // wrap sendgrid-specific logic, map errors to domain errors
    _, err := a.client.Send(...)
    if err != nil {
        return fmt.Errorf("send email: %w", domain.ErrInternal)
    }
    return nil
}
```

### Decorator / Middleware

Use when: Adding cross-cutting behavior without modifying original code

```go
// HTTP Middleware
func LoggingMiddleware(logger *zap.Logger) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            next.ServeHTTP(w, r)
            logger.Info("request",
                zap.String("method", r.Method),
                zap.String("path", r.URL.Path),
                zap.Duration("duration", time.Since(start)),
            )
        })
    }
}

// Service Decorator (metrics, audit logging)
type metricsUserService struct {
    next    UserService
    metrics *Metrics
}

func WithMetrics(svc UserService, m *Metrics) UserService {
    return &metricsUserService{next: svc, metrics: m}
}

func (s *metricsUserService) Create(ctx context.Context, input CreateUserInput) (*domain.User, error) {
    start := time.Now()
    user, err := s.next.Create(ctx, input)
    s.metrics.RecordDuration("user.create", time.Since(start), err != nil)
    return user, err
}
```

### Facade

Use when: Aggregating multiple services into one operation

```go
type OrderFacade struct {
    inventory InventoryService
    payment   PaymentService
    shipping  ShippingService
    logger    *zap.Logger
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
        // compensate both inventory and payment...
        return fmt.Errorf("schedule shipping: %w", err)
    }
    return nil
}
```

---

## BEHAVIORAL PATTERNS

### Strategy

Use when: Changing algorithm at runtime (pricing, notification, compression)

```go
type PricingStrategy interface {
    Calculate(ctx context.Context, order Order) (Money, error)
}

type standardPricing struct{}
type premiumPricing struct{ discountPct float64 }
type bulkPricing struct{ threshold int }

type OrderService struct {
    pricing PricingStrategy
    repo    OrderRepository
}

func NewOrderService(pricing PricingStrategy, repo OrderRepository) *OrderService {
    return &OrderService{pricing: pricing, repo: repo}
}
```

### Observer / Event Bus

Use when: One action triggers many side effects

```go
type EventType string
const (
    UserCreated EventType = "user.created"
    OrderPlaced EventType = "order.placed"
)

type Event struct {
    Type    EventType
    Payload interface{}
    OccurredAt time.Time
}

type EventBus struct {
    handlers map[EventType][]func(context.Context, Event) error
    mu       sync.RWMutex
}

func NewEventBus() *EventBus {
    return &EventBus{handlers: make(map[EventType][]func(context.Context, Event) error)}
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
// NOTE: For microservices, use message broker (NATS, Kafka, RabbitMQ)
```

### Circuit Breaker (DEFAULT for all external calls)

```go
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

// REQUIRED: Every external HTTP/gRPC call MUST have a circuit breaker
```

---

## CONCURRENCY PATTERNS

### Worker Pool

Use when: Processing many tasks with bounded concurrency

```go
func WorkerPool(ctx context.Context, numWorkers int, jobs <-chan Job, results chan<- Result) {
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for {
                select {
                case job, ok := <-jobs:
                    if !ok {
                        return
                    }
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
```

### Fan-Out / Fan-In (errgroup)

Use when: Parallel calls then collecting results

```go
import "golang.org/x/sync/errgroup"

g, ctx := errgroup.WithContext(ctx)
results := make([]*Result, len(items))

for i, item := range items {
    i, item := i, item // capture loop vars
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
    return fmt.Errorf("fan-out processing: %w", err)
}
```

### Constructor Injection (DEFAULT — how to wire everything)

```go
// cmd/api/main.go — wire all dependencies here
func main() {
    cfg := config.Load()
    logger := zap.NewProduction()

    db := postgres.NewConnection(cfg.DB)
    cache := redis.NewClient(cfg.Cache)

    userRepo := repository.NewPostgresUserRepo(db)
    emailSvc := sendgrid.NewSendgridAdapter(cfg.SendgridAPIKey)
    eventBus := events.NewEventBus()

    userSvc := service.NewUserService(userRepo, emailSvc, eventBus, logger)
    userHandler := handler.NewUserHandler(userSvc, logger)

    grpcServer := grpc.NewServer(...)
    pb.RegisterUserServiceServer(grpcServer, userHandler)
    grpcServer.Serve(lis)
}
```

---

## ANTI-PATTERNS (FORBIDDEN)

```
FORBIDDEN: God struct (struct > 10 fields or > 7 methods — split it)
FORBIDDEN: Circular dependencies between packages
FORBIDDEN: Global mutable state (use constructor injection instead)
FORBIDDEN: Interface pollution (interface with 1 impl and no mock need)
FORBIDDEN: Premature abstraction (pattern for only 1 use case)
FORBIDDEN: Deep inheritance thinking (Go uses composition, not inheritance)
FORBIDDEN: Empty interface{} when a concrete type can be used
FORBIDDEN: Over-wrapping (adapter wrapping adapter wrapping adapter)
FORBIDDEN: Returning interface from constructor (return concrete struct)
```
