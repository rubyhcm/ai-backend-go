---
inclusion: always
---

# Security Rules — Go Backend

## Input Validation (Handler Layer)

```go
// REQUIRED: Validate ALL user input at handler layer using go-playground/validator
type CreateUserRequest struct {
    Email    string `json:"email"    validate:"required,email,max=255"`
    Name     string `json:"name"     validate:"required,min=2,max=100"`
    Password string `json:"password" validate:"required,min=8,max=72"`
}

// REQUIRED: Limit request body size
r.Body = http.MaxBytesReader(w, r.Body, 1<<20) // 1MB limit

// FORBIDDEN: Trust client-side validation alone
// FORBIDDEN: Pass unvalidated input to service layer
```

## SQL Injection Prevention

```go
// REQUIRED: Parameterized queries always
db.Where("email = ?", email).First(&user)                       // GORM — SAFE
db.Raw("SELECT id FROM users WHERE id = ?", id).Scan(&user)    // GORM raw — SAFE

// FORBIDDEN:
db.Raw("SELECT * FROM users WHERE email = '" + email + "'")     // string concat — UNSAFE
db.Raw(fmt.Sprintf("SELECT * FROM users WHERE id = %s", id))   // Sprintf — UNSAFE
```

## Authentication & JWT

```go
// REQUIRED: Validate JWT algorithm (prevent "none" algorithm attack)
token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
    if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
        return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
    }
    return publicKey, nil
})

// REQUIRED: RS256 or ES256 (asymmetric) for production
// REQUIRED: Set and validate expiration (exp claim)
// REQUIRED: Store secrets in env vars or vault — NEVER hardcode
// REQUIRED: bcrypt with cost >= 12 for password hashing
// REQUIRED: Implement token refresh mechanism

// FORBIDDEN: HS256 with weak secrets
// FORBIDDEN: JWT in URL query parameters
// FORBIDDEN: Store sensitive data in JWT payload
```

## Cryptography

```go
// REQUIRED: crypto/rand for security-sensitive random values
b := make([]byte, 32)
_, err := crypto/rand.Read(b)

// REQUIRED: bcrypt or argon2 for password hashing (cost >= 12)
hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), 12)

// REQUIRED: AES-256-GCM for symmetric encryption
// REQUIRED: TLS 1.2+ for all external connections

// FORBIDDEN: math/rand for security purposes
// FORBIDDEN: MD5 or SHA1 for password hashing
// FORBIDDEN: ECB mode for encryption
// FORBIDDEN: Hardcoded encryption keys
```

## JSON Handling

```go
// REQUIRED: Use json.Decoder with size limit
decoder := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20))
decoder.DisallowUnknownFields()
if err := decoder.Decode(&req); err != nil {
    // handle error
}

// FORBIDDEN: Unlimited json.Unmarshal on user input
json.Unmarshal(body, &req)  // no size limit — UNSAFE
```

## Context & Timeout for External Calls

```go
// REQUIRED: Context timeout for ALL external calls
ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
defer cancel()
err := db.QueryRowContext(ctx, "SELECT ...").Scan(&result)

// Default timeouts (use config values, not hardcoded):
// HTTP calls: 30s
// DB queries: 5s
// Cache:      1s
// gRPC calls: 10s

// FORBIDDEN: External call without context timeout
// FORBIDDEN: context.Background() in service/repository layer
```

## Goroutine Safety

```go
// REQUIRED: Goroutines must have cancellation
// REQUIRED: Recover from panics in goroutines
go func() {
    defer func() {
        if r := recover(); r != nil {
            logger.Error("goroutine panic", zap.Any("error", r))
        }
    }()
    select {
    case <-ctx.Done():
        return
    case msg := <-ch:
        process(msg)
    }
}()

// FORBIDDEN: goroutine without lifecycle management
// FORBIDDEN: unbounded goroutine spawning (use worker pool)
```

## CORS Configuration

```go
// REQUIRED: Explicit allowed origins (NEVER "*" in production)
corsMiddleware := cors.New(cors.Options{
    AllowedOrigins:   []string{"https://app.yourcompany.com"},
    AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE"},
    AllowedHeaders:   []string{"Authorization", "Content-Type"},
    AllowCredentials: true,
})

// FORBIDDEN: Access-Control-Allow-Origin: * with credentials
```

## Logging Security

```go
// REQUIRED: Audit log for auth events (login, logout, permission change)
logger.Info("user login",
    zap.String("user_id", userID),
    zap.String("ip", clientIP),
    zap.String("action", "login"),
)

// FORBIDDEN: Log passwords, tokens, API keys, PII
logger.Info("auth", zap.String("password", pw))    // FORBIDDEN
logger.Info("auth", zap.String("token", jwt))      // FORBIDDEN
logger.Info("user", zap.String("ssn", user.SSN))   // FORBIDDEN

// FORBIDDEN: Expose stack traces to end users
// FORBIDDEN: Log full request/response bodies in production
```

## Rate Limiting

```go
// REQUIRED: Rate limiting on authentication endpoints
// REQUIRED: Rate limiting on API endpoints (per user/IP)
// REQUIRED: Return codes.ResourceExhausted when rate limit exceeded
// RECOMMENDED: Include retry delay via gRPC error details

// Recommended algorithm: token bucket or sliding window
// Use: golang.org/x/time/rate or gRPC interceptor

st := status.New(codes.ResourceExhausted, "rate limit exceeded")
ds, _ := st.WithDetails(&errdetails.RetryInfo{
    RetryDelay: durationpb.New(retryAfter),
})
return nil, ds.Err()
```

## OWASP Top 10 (2025) Checklist

```
A01 Broken Access Control     → RBAC, check permissions per endpoint
A02 Cryptographic Failures    → TLS, bcrypt cost>=12, AES-GCM, no hardcoded keys
A03 Injection                 → Parameterized queries, input validation
A04 Insecure Design           → Threat modeling, secure defaults, principle of least privilege
A05 Security Misconfiguration → No debug mode in prod, minimal permissions, review defaults
A06 Vulnerable Components     → govulncheck + snyk, regular dependency updates
A07 Auth Failures             → MFA support, secure JWT, session management
A08 Data Integrity Failures   → Signed updates, secure deserialization
A09 Logging Failures          → Audit logs, monitoring, alerting on anomalies
A10 SSRF                      → Validate URLs, block internal network ranges
```

## Security Scanning (Run before every commit/PR)

```bash
# MANDATORY
gosec ./...                                    # Go-specific security patterns
govulncheck ./...                              # Dependency CVE check

# MANDATORY if installed
semgrep --config=p/golang --config=p/owasp-top-ten ./...
snyk test --all-projects
snyk code test
sonar-scanner                                  # requires sonar-project.properties
```
