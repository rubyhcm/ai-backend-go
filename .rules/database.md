# DATABASE DESIGN & MIGRATION RULES

## 0. Global Principles

All schemas MUST follow:

- **Consistency** — naming, structure, constraints
- **Explicitness** — no implicit assumptions
- **Backward compatibility** — support zero-downtime migrations
- **Safety first** — avoid destructive operations
- **Access pattern driven design** — optimize for real queries

## 0.1 Target DBMS Awareness (CRITICAL)

Agent MUST detect or be provided target DBMS.

**PostgreSQL**
- Use `TIMESTAMPTZ`
- Support: Partial Index, CHECK, COMMENT ON, gen_random_uuid()

**MySQL (8+)**
- Use `TIMESTAMP` or `DATETIME`
- NO Partial Index → use composite index workaround
- NO `COMMENT ON` → use inline column/table comments
- Use `UUID()` or application-generated UUID
- CHECK constraints are supported (MySQL 8+)

Agent MUST generate SQL compatible with the target DBMS.

## 1. Table Requirements

### 1.1 Primary Key (REQUIRED)

Every table MUST have a primary key:

Standard (recommended):
```sql
-- PostgreSQL
id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY

-- MySQL
id BIGINT AUTO_INCREMENT PRIMARY KEY
```

Distributed systems (optional):
```sql
id UUID PRIMARY KEY
```

### 1.2 Audit Fields (REQUIRED)

Every table MUST include:

```sql
-- PostgreSQL
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP

-- MySQL
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

Rules:
- Prefer native auto-update (`ON UPDATE`) if supported.
- Otherwise, use trigger to update `updated_at`.

### 1.3 Soft Delete (OPTIONAL)

```sql
deleted_at TIMESTAMP NULL
```

Rules:
- DO NOT use `is_deleted`.
- All queries MUST include: `deleted_at IS NULL`.

### 1.4 Versioning (OPTIONAL – Optimistic Locking)

```sql
version INT NOT NULL DEFAULT 1
```

Used for concurrency control.

### 1.5 Concurrency Control (ADVANCED)

- Optimistic Locking: use `version`
- Pessimistic Locking: use `SELECT ... FOR UPDATE` in critical transactions

## 2. Column Design Rules

### 2.1 Naming Convention

- MUST use `snake_case`.
- MUST be descriptive.
- Foreign keys MUST follow: `<referenced_table_singular>_id` (e.g., `user_id`, `order_id`).

### 2.2 NULL Handling

- Columns MUST be `NOT NULL` by default.
- Only allow `NULL` if truly optional.

### 2.3 Default Values

- MUST define defaults when meaningful.
- Defaults MUST reflect business logic.

### 2.4 Column Limit

- If table > 20 columns → SHOULD evaluate vertical partitioning.

## 3. Enum / Status Fields

### 3.1 Allowed Strategies

**Option A – Native ENUM** (low-change values)
- Suitable for stable enums.

**Option B – VARCHAR + CHECK**
```sql
status VARCHAR(20) CHECK (status IN ('ACTIVE', 'PENDING', 'CANCELED'))
```

**Option C – Lookup Table (RECOMMENDED for flexibility)**
```sql
status_id INT REFERENCES statuses(id)
```

### 3.2 Rules

- MUST document enum meaning via comments.
- DO NOT use magic numbers without explanation.
- DO NOT auto-index enum fields.

## 4. Indexing Strategy

### 4.1 When to Create Index

Only if used in:
- `WHERE`
- `JOIN`
- `ORDER BY`

### 4.2 Selectivity

Prefer high-selectivity columns.

### 4.3 Composite Index (PREFERRED)

Follow leftmost prefix rule.

### 4.4 Soft Delete Optimization

```sql
-- PostgreSQL (Partial Index)
CREATE INDEX idx_users_active ON users(email)
WHERE deleted_at IS NULL;

-- MySQL workaround (Composite Index)
CREATE INDEX idx_users_email_deleted_at ON users(email, deleted_at);
```

### 4.5 Covering Index (ADVANCED)

Include all selected columns in index to avoid table lookup.

## 5. Constraints

### 5.1 Foreign Keys (REQUIRED)

```sql
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE <RESTRICT | CASCADE | SET NULL>
```

Rules:
- MUST explicitly define `ON DELETE` behavior.
- DO NOT default blindly.

### 5.2 Unique Constraints

MUST enforce business uniqueness.

```sql
-- PostgreSQL (Soft Delete — Partial Unique Index)
CREATE UNIQUE INDEX uk_email_active
ON users(email)
WHERE deleted_at IS NULL;

-- MySQL (Soft Delete workaround)
UNIQUE KEY uk_email_deleted_at (email, deleted_at)
```

## 6. Comment Requirements (MANDATORY)

Agent MUST generate comments:

```sql
-- PostgreSQL
COMMENT ON TABLE users IS 'User information';
COMMENT ON COLUMN users.email IS 'Unique email address';

-- MySQL (inline)
email VARCHAR(255) COMMENT 'Unique email address'
```

## 7. Migration Rules

### 7.1 Versioning

Every migration MUST have version (timestamp or incremental).

### 7.2 Idempotency

Use: `IF NOT EXISTS`, `IF EXISTS`.

### 7.3 Rollback

Every `UP` MUST have `DOWN`.

### 7.4 Safety

DO NOT drop columns/tables or modify data destructively without explicit instruction.

### 7.5 Zero-Downtime Strategy (CRITICAL)

Use **Expand → Migrate → Contract**:
1. Add new column (nullable)
2. Backfill data
3. Switch application
4. Remove old column (later)

- DO NOT rename columns directly or drop columns immediately.

## 8. Query Rules

### 8.1 Select Rule

```sql
-- ❌ NOT allowed
SELECT *

-- ✅ REQUIRED
SELECT id, email FROM users
```

### 8.2 Soft Delete Awareness

```sql
WHERE deleted_at IS NULL
```

### 8.3 Pagination (IMPORTANT)

Avoid:
```sql
LIMIT 10 OFFSET 10000
```

Use Keyset Pagination:
```sql
WHERE id > last_id
ORDER BY id
LIMIT 10
```

## 9. Schema Design Strategy

### 9.1 Normalization

- Default: 3NF.
- Denormalize ONLY if required.

### 9.2 Access Pattern Driven

Design based on:
- Query patterns
- Read/write ratio
- Data volume

### 9.3 Partitioning (ADVANCED)

Use for large tables:
- Time-based (e.g., `created_at`)
- Hash-based

## 10. Output Requirements for Agent

When generating schema/migration, Agent MUST:

- Provide executable SQL.
- Include: Primary keys, Audit fields, Constraints, Indexes.
- Include comments (DB-specific).
- Handle soft delete indexing correctly.
- Provide both `UP` and `DOWN` migrations.
- Ensure DBMS compatibility.

## Final Principles

- Prefer clarity over brevity
- Prefer explicit over implicit
- Prefer safe schema over premature optimization
- Design for real-world production systems, not theoretical models
