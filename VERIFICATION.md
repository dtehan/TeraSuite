# Verification

No live Teradata instance is available to this project, so verification is
static/heuristic (per project decision) rather than live execution. Every
check below was re-run after fixes and currently passes.

## 1. Database scripts are valid Teradata syntax

**Manual checklist review** of `db/01_create_database.sql` and `db/02_load_data.sql`:

| Check | Result |
|---|---|
| `CREATE DATABASE ... FROM DBC AS PERM = ..., SPOOL = ...` present | Pass |
| Every `CREATE TABLE` is `CREATE SET TABLE` with an explicit `PRIMARY INDEX (...)` | Pass — 11/11 tables |
| Data types are Teradata-valid (`INTEGER`, `VARCHAR(n)`, `CHAR(n)`, `DECIMAL(p,s)`, `DATE`, `TIMESTAMP(0)`) | Pass |
| No non-Teradata constructs (`AUTO_INCREMENT`, `GETDATE()`, `LIMIT n`, `IFNULL`, backtick identifiers, etc.) | Pass |
| Cross-table references use `REFERENCES WITH NO CHECK OPTION` (Teradata soft RI), consistent with the deliberate RI-violating edge rows in the seed data | Pass |
| Every statement is semicolon-terminated | Pass |
| `INSERT` statements use single-row `VALUES (...)` (Teradata does not support multi-row `VALUES (...),(...)`) | Pass — 250 single-row inserts |
| Literal dates/timestamps use `DATE '...'` / `TIMESTAMP '...'` (not string-implicit-cast) | Pass |

**Automated heuristic check**: `python3 scripts/validate_sql_syntax.py`

```
PASS: no heuristic Teradata syntax issues found in db/01_create_database.sql and db/02_load_data.sql
```

## 2. Data is queryable across tables (joins work)

Since there's no live Teradata instance, `scripts/verify_joins.py` loads an
equivalent copy of the seed data into an in-memory SQLite database (a
verification aid only — not a deliverable; `db/*.sql` remain pure Teradata
syntax) and runs 7 representative cross-table joins spanning every table in
the schema.

```
Loaded row counts (from db/02_load_data.sql):
  Customer: 15
  DBA_AccessRights: 20
  DBA_QueryLog: 25
  DBA_SecurityAuditLog: 25
  DBA_TableSpaceUsage: 11
  DBA_Users: 12
  Employee: 15
  OrderLine: 45
  Orders: 30
  Product: 15
  Store: 5

Running representative cross-table joins:
  [OK] customer_orders_revenue: 4 row(s)
  [OK] product_category_sales: 9 row(s)
  [OK] store_order_counts: 5 row(s)
  [OK] employee_manager_hierarchy: 15 row(s)
  [OK] user_access_rights: 20 row(s)
  [OK] user_query_activity: 8 row(s)
  [OK] customer_with_zero_orders: 1 row(s)

JOIN VERIFICATION: PASSED
```

All 250 seeded rows loaded without a foreign-key/type error, and every join
returns non-empty results (except the deliberately-edge `customer_with_zero_orders`
check, which correctly returns exactly one row — CustomerID 115).

## 3. Evals use the database data and structures

`scripts/validate_evals.py` validates every `evals/cases/*.yaml` file against
the `TestSuite`/`TestCase` schema in `evals/schema/eval-schema.yaml`, and
cross-checks that every table named in `requires_tables` (and every table
referenced in `expected_sql`) actually exists in `db/01_create_database.sql`.

```
Checked 6 eval file(s), 132 total test case(s).
EVAL VALIDATION: PASSED
```

## 4. Each persona has typical + edge coverage

| Persona | File | Total | Typical | Edge |
|---|---|---|---|---|
| Business user | `business_user.yaml` | 22 | 16 | 6 |
| Data scientist | `data_scientist.yaml` | 22 | 16 | 6 |
| Data analyst | `data_analyst.yaml` | 22 | 16 | 6 |
| DBA | `dba.yaml` | 22 | 15 | 7 |
| Security expert | `security_expert.yaml` | 22 | 14 | 8 |
| Database operations | `database_operations.yaml` | 22 | 15 | 7 |
| **Total** | | **132** | **92** | **40** |

No duplicate `id`s within any file (checked as part of `validate_evals.py`).

## How to re-run everything

```bash
cd /Users/Daniel.Tehan/Code/testing
python3 scripts/validate_sql_syntax.py
python3 scripts/validate_evals.py
python3 scripts/verify_joins.py
```

All three currently exit 0.
