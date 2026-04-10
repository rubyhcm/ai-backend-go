---
inclusion: always
---

# Database Design & Migration Rules

## Global Principles

- **Consistency** — naming, structure, constraints across all tables
- **Explicitness** — no implicit assumptions; always define explicitly
- **Backward compatibility** — support zero-downtime migrations only
- **Safety first** — avoid destructive operations unless explicitly instructed
- **Access pattern driven** — design indexes and schema for real query patterns

## Target DBMS Awareness (CRITICAL)

Detect or be told which DBMS is in use. Generate SQL compatible with it.

**PostgreSQL:**
- Use `TIMESTAMPTZ` for timestamps
- Supports: Partial Index, `COMMENT ON`, `gen_random_uuid()`, `GENERATED ALWAYS AS IDENTITY`

**MySQL (8+):**
- Use `TIMESTAMP` or `DATETIME`
- NO Partial Index → use composite index workaround
- NO `COMMENT ON` → use inline column/table comments (`COMMENT 'text'`)
- Use `UUID()` or application-generated UUID
- CHECK constraints supported (MySQL 8+)

## 1. Table Requirements

### Primary Key (REQUIRED for every table)

```sql
-- PostgreSQL (preferred)
id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY

-- MySQL
id BIGINT AUTO_INCREMENT PRIMARY KEY

-- Distributed systems (optional)
id UUID PRIMARY KEY
```

### Audit Fields (REQUIRED for every table)

```sql
-- PostgreSQL
created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP

-- MySQL
created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

### Soft Delete (OPTIONAL)

```sql
deleted_at TIMESTAMP NULL
```

Rules:
- DO NOT use `is_deleted` boolean — use `deleted_at` timestamp only
- ALL queries MUST include `WHERE deleted_at IS NULL`

### Optimistic Locking (OPTIONAL)

```sql
version INT NOT NULL DEFAULT 1
```

## 2. Column Design Rules

- Column names: `snake_case`, descriptive
- Foreign keys: `<referenced_table_singular>_id` (e.g., `user_id`, `order_id`)
- Default `NOT NULL` — only allow `NULL` if truly optional
- Always define defaults when meaningful
- If table > 20 columns → evaluate vertical partitioning (split into related tables)

## 3. Enum / Status Fields

**Option A — Native ENUM** (for stable, low-change values)

**Option B — VARCHAR + CHECK** (recommended for flexibility)
```sql
status VARCHAR(20) NOT NULL CHECK (status IN ('ACTIVE', 'PENDING', 'CANCELED'))
```

**Option C — Lookup Table** (for frequently changing enums)
```sql
status_id INT NOT NULL REFERENCES statuses(id)
```

Rules:
- MUST document enum meaning via comments
- DO NOT use magic numbers without explanation

## 4. Indexing Strategy

Create index ONLY if the column is used in `WHERE`, `JOIN`, or `ORDER BY`.

```sql
-- Composite index (follow leftmost prefix rule)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Soft delete optimization
-- PostgreSQL (Partial Index)
CREATE INDEX idx_users_email_active ON users(email)
WHERE deleted_at IS NULL;

-- MySQL (Composite Index workaround)
CREATE INDEX idx_users_email_deleted_at ON users(email, deleted_at);

-- Covering index for hot paths (include all selected columns)
CREATE INDEX idx_users_covering ON users(email) INCLUDE (id, name, status);
```

## 5. Constraints

### Foreign Keys (REQUIRED)

```sql
FOREIGN KEY (user_id)
REFERENCES users(id)
ON DELETE RESTRICT  -- or CASCADE or SET NULL
```

- MUST explicitly define `ON DELETE` behavior
- RESTRICT: block deletion of parent (safest default)
- CASCADE: delete children automatically
- SET NULL: null out the FK column

### Unique Constraints

```sql
-- PostgreSQL (Soft Delete — Partial Unique Index)
CREATE UNIQUE INDEX uk_users_email_active
ON users(email)
WHERE deleted_at IS NULL;

-- MySQL (Soft Delete workaround)
UNIQUE KEY uk_users_email_deleted_at (email, deleted_at)
```

## 6. Comment Requirements (MANDATORY)

```sql
-- PostgreSQL
COMMENT ON TABLE users IS 'Registered user accounts';
COMMENT ON COLUMN users.email IS 'Unique email address used for login';
COMMENT ON COLUMN users.status IS 'Account status: ACTIVE, PENDING, SUSPENDED';

-- MySQL (inline)
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Unique user identifier',
    email VARCHAR(255) NOT NULL COMMENT 'Unique email address used for login',
    status VARCHAR(20) NOT NULL COMMENT 'Account status: ACTIVE, PENDING, SUSPENDED'
) COMMENT = 'Registered user accounts';
```

## 7. Migration Rules

### File Naming

```
migrations/
  001_create_users.up.sql
  001_create_users.down.sql
  002_add_user_status.up.sql
  002_add_user_status.down.sql
```

### Rules

- Every UP migration MUST have a DOWN (rollback)
- Use `IF NOT EXISTS` / `IF EXISTS` for idempotency — every migration MUST be safe to re-run
- DO NOT drop columns/tables without explicit instruction
- DO NOT destructively modify data in migrations without explicit instruction

### Idempotency Patterns

```sql
-- Tables
CREATE TABLE IF NOT EXISTS users (...);

-- Columns (PostgreSQL)
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20) NULL;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Drop
DROP TABLE IF EXISTS legacy_users;
ALTER TABLE users DROP COLUMN IF EXISTS old_field;  -- PostgreSQL only

-- Constraints (PostgreSQL)
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_orders_user_id'
  ) THEN
    ALTER TABLE orders ADD CONSTRAINT fk_orders_user_id
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT;
  END IF;
END $$;
```

### Transaction Safety (CRITICAL)

**PostgreSQL** — supports transactional DDL, ALWAYS wrap in `BEGIN/COMMIT`:

```sql
BEGIN;

ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20) NULL;
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);

COMMIT;
```

**MySQL** — DDL causes implicit commit, transactions do NOT protect DDL:
- Keep each migration file as a single atomic logical change
- Rely on migration tool (golang-migrate, Flyway) to track execution state
- Ensure idempotency via `IF NOT EXISTS` / `IF EXISTS` instead of transactions

**Rules:**
- NEVER mix DML + DDL in the same transaction on MySQL
- On failure in PostgreSQL: automatic ROLLBACK via transaction
- On failure in MySQL: migration must be idempotent to safely retry

### DOWN Migration Example

```sql
-- DOWN must exactly reverse UP
-- PostgreSQL
BEGIN;
DROP TABLE IF EXISTS orders;
COMMIT;

-- MySQL
DROP TABLE IF EXISTS orders;
```

### Migration Checklist

Before committing any migration file:
- [ ] Wrapped in `BEGIN/COMMIT` (PostgreSQL)
- [ ] All `CREATE` use `IF NOT EXISTS`
- [ ] All `DROP` use `IF EXISTS`
- [ ] DOWN migration exists and reverses UP exactly
- [ ] No destructive data changes without explicit instruction

### Zero-Downtime Strategy (CRITICAL)

Use **Expand → Migrate → Contract**:

```
Phase 1 — EXPAND: Add new column (nullable, no breaking change)
  ALTER TABLE users ADD COLUMN full_name VARCHAR(255) NULL;

Phase 2 — MIGRATE: Backfill data (application handles both old + new)
  UPDATE users SET full_name = name WHERE full_name IS NULL;

Phase 3 — CONTRACT: Remove old column (after all apps use new column)
  ALTER TABLE users DROP COLUMN name;
```

- DO NOT rename columns directly in one migration
- DO NOT drop columns immediately after rename
- Allow time between phases for deployment rollout

## 8. Query Rules

### No SELECT * (REQUIRED)

```sql
-- FORBIDDEN
SELECT * FROM users

-- REQUIRED
SELECT id, email, name, status, created_at FROM users
```

### Soft Delete Awareness

```sql
-- ALWAYS include in WHERE clause
WHERE deleted_at IS NULL
```

### Keyset Pagination (for large datasets)

```sql
-- FORBIDDEN (slow for large offsets)
SELECT id, name FROM users LIMIT 10 OFFSET 10000

-- REQUIRED: Keyset pagination
SELECT id, name FROM users
WHERE id > :last_id
ORDER BY id
LIMIT 10
```

### Parameterized Queries Only

```sql
-- FORBIDDEN
SELECT * FROM users WHERE email = '" + email + "'  -- SQL injection!

-- REQUIRED
SELECT id, email FROM users WHERE email = ?  -- MySQL
SELECT id, email FROM users WHERE email = $1 -- PostgreSQL
```

## 9. Full Table Example

```sql
-- PostgreSQL
CREATE TABLE IF NOT EXISTS users (
    id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       VARCHAR(255) NOT NULL,
    name        VARCHAR(100) NOT NULL,
    status      VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE'
                    CHECK (status IN ('ACTIVE', 'PENDING', 'SUSPENDED')),
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at  TIMESTAMPTZ  NULL,
    version     INT          NOT NULL DEFAULT 1
);

COMMENT ON TABLE users IS 'Registered user accounts';
COMMENT ON COLUMN users.email IS 'Unique email used for login';
COMMENT ON COLUMN users.status IS 'Account lifecycle status';

-- Partial unique index for soft delete
CREATE UNIQUE INDEX uk_users_email_active ON users(email)
WHERE deleted_at IS NULL;

-- Index for soft-deleted queries
CREATE INDEX idx_users_status_active ON users(status)
WHERE deleted_at IS NULL;
```

## Final Principles

- Prefer clarity over brevity
- Prefer explicit over implicit
- Prefer safe schema over premature optimization
- Design for real production systems, not theoretical models
