# Security Rules - Go Backend

## Input Validation (Handler Layer)

```
REQUIRED: Validate ALL user input at handler layer
REQUIRED: Use struct tags for validation (go-playground/validator)
REQUIRED: Whitelist allowed values, not blacklist
REQUIRED: Limit request body size (http.MaxBytesReader)
REQUIRED: Validate Content-Type header
FORBIDDEN: Trust client-side validation alone
FORBIDDEN: Pass unvalidated input to service layer

Example:
  type CreateUserRequest struct {
      Email    string `json:"email" validate:"required,email,max=255"`
      Name     string `json:"name" validate:"required,min=2,max=100"`
      Password string `json:"password" validate:"required,min=8,max=72"`
  }

  // Limit request body
  r.Body = http.MaxBytesReader(w, r.Body, 1<<20) // 1MB
```

## SQL Injection Prevention

```
REQUIRED: Parameterized queries ALWAYS
REQUIRED: Use query builder or ORM methods (GORM .Where(), sqlx.Select)
FORBIDDEN: String concatenation for SQL
FORBIDDEN: GORM .Raw() or .Exec() with fmt.Sprintf

SAFE:
  db.Where("email = ?", email).First(&user)
  db.Raw("SELECT * FROM users WHERE id = ?", id).Scan(&user)

UNSAFE:
  db.Raw("SELECT * FROM users WHERE email = '" + email + "'")
  db.Raw(fmt.Sprintf("SELECT * FROM users WHERE id = %s", id))
```

## Authentication & JWT

```
REQUIRED: Validate JWT algorithm (prevent "none" algorithm attack)
REQUIRED: Set and validate expiration (exp claim)
REQUIRED: Use RS256 or ES256 (asymmetric) for production
REQUIRED: Store secrets in env vars or vault (NEVER hardcode)
REQUIRED: Implement token refresh mechanism
REQUIRED: bcrypt with cost >= 12 for password hashing
FORBIDDEN: HS256 with weak secrets
FORBIDDEN: JWT in URL query parameters
FORBIDDEN: Store sensitive data in JWT payload

Example:
  token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
      if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
          return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
      }
      return publicKey, nil
  })
```

## Cryptography

```
REQUIRED: crypto/rand for security-sensitive random values
REQUIRED: bcrypt or argon2 for password hashing
REQUIRED: AES-256-GCM for symmetric encryption
REQUIRED: TLS 1.2+ for all external connections
FORBIDDEN: math/rand for security purposes
FORBIDDEN: MD5 or SHA1 for password hashing
FORBIDDEN: ECB mode for encryption
FORBIDDEN: Hardcoded encryption keys
```

## JSON Handling

```
REQUIRED: Use json.Decoder with size limit
REQUIRED: Decode into typed structs (not map[string]interface{})
REQUIRED: DisallowUnknownFields when strict parsing needed
FORBIDDEN: Unlimited json.Unmarshal on user input

Example:
  decoder := json.NewDecoder(http.MaxBytesReader(w, r.Body, 1<<20))
  decoder.DisallowUnknownFields()
  if err := decoder.Decode(&req); err != nil {
      // handle error
  }
```

## Context & Timeout

```
REQUIRED: Context timeout for ALL external calls (DB, HTTP, gRPC)
REQUIRED: Propagate context through entire call chain
REQUIRED: Default timeout: 30s for HTTP, 5s for DB, 10s for cache
FORBIDDEN: External call without context timeout
FORBIDDEN: context.Background() in service/repository layer

Example:
  ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
  defer cancel()
  err := db.QueryRowContext(ctx, "SELECT ...").Scan(&result)
```

## Goroutine Safety

```
REQUIRED: Goroutine must have cancellation (context or done channel)
REQUIRED: Recover from panics in goroutines
REQUIRED: Use sync.Mutex for shared state
FORBIDDEN: Goroutine without lifecycle management
FORBIDDEN: Unbounded goroutine spawning

Example:
  go func() {
      defer func() {
          if r := recover(); r != nil {
              logger.Error("goroutine panic", "error", r)
          }
      }()
      select {
      case <-ctx.Done():
          return
      case msg := <-ch:
          process(msg)
      }
  }()
```

## CORS

```
REQUIRED: Explicit allowed origins (not "*" in production)
REQUIRED: Explicit allowed methods and headers
REQUIRED: Credentials mode only with specific origins
FORBIDDEN: Access-Control-Allow-Origin: * with credentials
```

## Logging Security

```
REQUIRED: Structured logging with appropriate levels
REQUIRED: Audit log for auth events (login, logout, permission change)
REQUIRED: Log request ID for traceability
FORBIDDEN: Log passwords, tokens, API keys, PII
FORBIDDEN: Log full request/response bodies in production
FORBIDDEN: Expose stack traces to end users
```

## Rate Limiting

```
REQUIRED: Rate limiting on authentication endpoints
REQUIRED: Rate limiting on API endpoints (per user/IP)
REQUIRED: Return gRPC status codes.ResourceExhausted when rate limit exceeded
RECOMMENDED: Use token bucket or sliding window algorithm
RECOMMENDED: Include retry delay in gRPC status details (google.golang.org/grpc/status + errdetails)

Example:
  st := status.New(codes.ResourceExhausted, "rate limit exceeded")
  ds, _ := st.WithDetails(&errdetails.RetryInfo{
      RetryDelay: durationpb.New(retryAfter),
  })
  return nil, ds.Err()
```

## OWASP Top 10 (2025) Quick Reference

```
A01 Broken Access Control    --> RBAC, check permissions per endpoint
A02 Cryptographic Failures   --> TLS, bcrypt, AES-GCM, no hardcoded keys
A03 Injection                --> Parameterized queries, input validation
A04 Insecure Design          --> Threat modeling, secure defaults
A05 Security Misconfiguration--> No debug in prod, minimal permissions
A06 Vulnerable Components    --> govulncheck + Snyk, regular dependency updates
A07 Auth Failures            --> MFA, secure JWT, session management
A08 Data Integrity Failures  --> Signed updates, secure deserialization
A09 Logging Failures         --> Audit logs, monitoring, alerting
A10 SSRF                     --> Validate URLs, block internal networks
```

## Security Scanning Toolchain

```
MANDATORY:
  gosec ./...                           # Go-specific security patterns
  govulncheck ./...                     # Go dependency CVE check

MANDATORY (if installed):
  semgrep --config=p/golang \
          --config=p/owasp-top-ten ./.. # SAST: multi-language rules
  snyk test --all-projects              # Dependency vulnerability scan
  snyk code test                        # SAST: Snyk code analysis
  sonar-scanner                         # SAST: SonarQube security hotspots,
                                        #       bugs, vulnerabilities, code smells
                                        # Config: sonar-project.properties (repo root)
                                        # Requires: SONAR_TOKEN env var (see .env.local)
                                        # Host: https://sonarcloud.io

Coverage gate:
  go test ./... -coverprofile=coverage.out
  go tool cover -func=coverage.out | grep total
  # MUST be >= 80% overall
```
