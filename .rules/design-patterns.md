# Design Patterns for Go Backend

```
Agent PHAI doc file nay truoc khi thiet ke va sinh code.
Chon pattern phu hop voi van de, KHONG ep pattern khi khong can.
Go uu tien DON GIAN. Neu pattern chi them 1 lop boc ma khong them gia tri --> bo qua.
```

---

## CREATIONAL PATTERNS

### Factory Method
```
KHI NAO: Tao objects co nhieu variant (payment processor, notifier, storage)
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

LUU Y: Uu tien Functional Options hon Factory phuc tap
```

### Functional Options (Go-idiomatic Builder)
```
KHI NAO: Object co nhieu optional config (server, client, service)
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
KHI NAO: DB connection pool, logger, config (CHI khi that su can)
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

CANH BAO: Tranh lam dung. Uu tien Dependency Injection.
```

---

## STRUCTURAL PATTERNS

### Repository Pattern (MAC DINH cho data access)
```
KHI NAO: Moi entity can data access
GO IDIOM: "Accept interfaces, return structs" (Consumer-side interfaces)

// service/user_service.go (CONSUMER dinh nghia interface)
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

// repository/user_postgres.go (PRODUCER tra ve struct)
type PostgresUserRepo struct {
    db *sql.DB
}

func NewPostgresUserRepo(db *sql.DB) *PostgresUserRepo {
    return &PostgresUserRepo{db: db}
}

func (r *PostgresUserRepo) FindByID(ctx context.Context, id string) (*domain.User, error) {
    // implementation
}

REQUIRED: Interface tai CONSUMER (service/), KHONG o domain/
REQUIRED: Interface nho (1-3 methods). Neu > 5 methods --> tach nho
```

### Adapter
```
KHI NAO: Wrap external service/library (payment gateway, email provider)
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

MAC DINH SU DUNG, TRU KHI:
  - Library da co interface tot (vd: AWS SDK v2)
  - Chi co 1 implementation va khong can mock
  - Wrapper chi forward 1:1 khong them logic
```

### Decorator / Middleware
```
KHI NAO: Them behavior khong sua code goc (logging, auth, metrics, rate limit)
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
KHI NAO: Gom nhieu service vao 1 entry point (order = inventory + payment + shipping)
GO IDIOM: Struct aggregate dependencies

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
KHI NAO: Thay doi algorithm luc runtime (pricing, sorting, compression, notification)
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
KHI NAO: Action trigger nhieu side effects (user created -> email + audit log)
GO IDIOM: Channel-based hoac Event Bus

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

LUU Y: Microservices --> message broker (NATS, Kafka, RabbitMQ)
```

### Circuit Breaker (MAC DINH cho external calls)
```
KHI NAO: Goi external service (API, payment, third-party)
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

REQUIRED: Moi external HTTP/gRPC call PHAI co circuit breaker
```

---

## CONCURRENCY PATTERNS (GO-SPECIFIC)

### Worker Pool
```
KHI NAO: Xu ly nhieu task dong thoi co gioi han (batch, file upload)
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

REQUIRED: Context hoac done channel de cancel
```

### Fan-Out / Fan-In
```
KHI NAO: Parallel calls roi gom ket qua (parallel API calls, batch fetch)
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
KHI NAO: Data di qua nhieu buoc xu ly (ETL, data transformation)
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

## DEPENDENCY INJECTION (MAC DINH)

### Constructor Injection
```
GO IDIOM: NewXxx(deps...) pattern

func NewUserService(repo UserRepository, logger *slog.Logger, eventBus *EventBus) *UserService {
    return &UserService{
        repo:     repo,
        logger:   logger,
        eventBus: eventBus,
    }
}

REQUIRED: Moi dependency inject qua constructor
FORBIDDEN: Global variables cho dependencies
OPTIONAL: wire (Google) hoac fx (Uber) cho complex DI
```

---

## PATTERN SELECTION GUIDE

```
Tinh huong                              --> Pattern
Tao object co nhieu variant             --> Factory Method
Config phuc tap, nhieu option           --> Functional Options
Data access cho entity                  --> Repository (MAC DINH)
Wrap external service                   --> Adapter (MAC DINH, tru khi over-engineering)
Them logging/metrics/auth               --> Decorator / Middleware
Goi external API/service                --> Circuit Breaker (MAC DINH)
Thay doi algorithm luc runtime          --> Strategy
Action trigger nhieu side effects       --> Observer / Event Bus
Xu ly batch/parallel co limit           --> Worker Pool
Parallel calls gom ket qua             --> Fan-Out / Fan-In (errgroup)
Data qua nhieu buoc xu ly              --> Pipeline
Inject dependencies                     --> Constructor Injection (MAC DINH)
```

---

## ANTI-PATTERNS (KHONG DUOC LAM)

```
FORBIDDEN: God struct (struct > 10 fields hoac > 7 methods)
FORBIDDEN: Circular dependencies giua packages
FORBIDDEN: Global mutable state (dung DI)
FORBIDDEN: Interface pollution (interface khi chi co 1 impl va khong can mock)
FORBIDDEN: Premature abstraction (pattern cho 1 use case)
FORBIDDEN: Deep inheritance thinking (Go dung composition)
FORBIDDEN: Empty interface{} khi co the dung concrete type
FORBIDDEN: Over-wrapping (adapter quanh adapter)
```
