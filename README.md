# Teradata "Tera" Agent — Regression Eval Set

A self-contained regression eval set for the Teradata conversational agent:
a Teradata database (schema + data) the agent can be pointed at, and a
persona-driven suite of eval cases (typical + edge activities) that exercise
it.

## Layout

```
db/
  01_create_database.sql   Teradata DDL: CREATE DATABASE + all tables
  02_load_data.sql         Teradata DML: seed data, including deliberate
                            edge-case rows (see inline comments)
evals/
  schema/eval-schema.yaml  OpenAPI 3.0 schema defining the TestCase/TestSuite shape
  cases/*.yaml             One file per persona, 20+ test cases each
scripts/
  validate_sql_syntax.py   Heuristic static check that db/*.sql is valid Teradata syntax
  validate_evals.py        Validates evals/cases/*.yaml against eval-schema.yaml and
                            cross-checks every referenced table exists in the DB schema
  verify_joins.py          Loads the seed data into local SQLite (verification aid only)
                            and runs representative cross-table joins to prove the data
                            is queryable across tables
VERIFICATION.md            Results of running the checks above
```

## Database

Two-domain schema in `TeraTestingDB`:

- **Business/analytics**: `Customer`, `Product`, `Store`, `Orders`, `OrderLine`, `Employee`
- **DBA/security/ops** (modeled after Teradata DBC-style system views): `DBA_Users`,
  `DBA_AccessRights`, `DBA_SecurityAuditLog`, `DBA_QueryLog`, `DBA_TableSpaceUsage`

Every table has an explicit `PRIMARY INDEX`. Cross-table relationships use
`REFERENCES ... WITH NO CHECK OPTION` (Teradata soft referential integrity),
which is realistic EDW practice and deliberately permits a few rows that
violate logical RI for edge-case testing (e.g. an audit-log entry for a
username that was never provisioned).

The seed data includes deliberate edge cases used by the evals: a customer
with zero orders, a product with a NULL category, a discontinued product
still referenced by an old order, a suspended user account with an active
grant and query activity, a stale/orphaned access grant on a nonexistent
table, tables that have never had statistics collected, a brute-force login
pattern, and a runaway/aborted query. Each is called out inline in
`db/02_load_data.sql`.

To load the database on a real Teradata system, run `01_create_database.sql`
followed by `02_load_data.sql` (e.g. via BTEQ or a SQL client that supports
Teradata syntax).

## Eval cases

`evals/schema/eval-schema.yaml` is an OpenAPI 3.0 document defining a
`TestCase` (id, name, persona, category: typical|edge, description, prompt,
requires_tables, expected_output) and a `TestSuite` (persona + list of
TestCase). `expected_output` carries a reference `expected_sql` query and/or
`expected_result` shape and/or `expected_explanation_points`, plus an
`expected_behavior` tag (e.g. `return_data`, `return_empty_result`,
`ask_clarifying_question`, `refuse_or_flag_permission`, `flag_data_quality_issue`).

Six persona files live in `evals/cases/`, each with 20+ cases split between
typical day-to-day activities and edge cases grounded in the seed data:

| Persona | File | Focus |
|---|---|---|
| Business user | `business_user.yaml` | Plain-English sales/customer/product questions |
| Data scientist | `data_scientist.yaml` | Feature pulls, RFM/cohort extracts, modeling-adjacent queries |
| Data analyst | `data_analyst.yaml` | Trend reports, breakdowns, rankings, period comparisons |
| DBA | `dba.yaml` | Space usage, grants, user administration, stats health |
| Security expert | `security_expert.yaml` | Auth events, anomaly detection, access-control violations |
| Database operations | `database_operations.yaml` | Query performance, workload, runaway/failed queries |

## Running the checks

```bash
python3 scripts/validate_sql_syntax.py
python3 scripts/validate_evals.py
python3 scripts/verify_joins.py
```

See `VERIFICATION.md` for the latest results and how they map to the
Definition of Done.

## Eval harness

The harness sends each YAML prompt through a local Anthropic model on Amazon
Bedrock. That model calls the Teradata Tera agent over MCP, using the bearer
token in `.env`. A second Bedrock model grades the answer with
[deepeval](https://github.com/confident-ai/deepeval) `GEval` metrics:
behavior, SQL equivalence, result shape, and explanation points, whichever
fields the case defines.

```bash
uv venv && uv sync
cp .env.example .env   # Bedrock model ids, AWS credentials, TERA_BEARER_TOKEN
```

`TERA_MCP_URL` is the original preprod Tera gateway. The key is sent as `Authorization: ApiKey <token>`. The database scripts in
`db/` need to be loaded on the system that gateway can query
(`TERA_DATABASE`, default `TeraTestingDB`).

```bash
uv run python run_evals.py --list-cases
uv run python run_evals.py --list-tools
uv run python run_evals.py --persona business_user --case BU-001
uv run python run_evals.py --category edge --limit 5
uv run python run_evals.py --context minimal
```

`--context` controls what the local agent is allowed to see besides the prompt:

| Mode | What the agent sees |
|---|---|
| `minimal` | The YAML prompt only |
| `database` (default) | Prompt plus `TERA_DATABASE` |
| `tables` | Prompt, database, and the case's `requires_tables` |

The expected SQL and the expected answer stay with the judge. Open
`results/latest_summary.md` after a run. Each case records pass/fail, the
Tera tool calls, judge notes, billed Bedrock tokens, and elapsed time.
`AGENT_MAX_TOKENS` fails a case before the judge when a turn exceeds that
billed-token cap. `0` or unset means no cap.

Offline tests (no Bedrock, no Tera):

```bash
uv run pytest
```
