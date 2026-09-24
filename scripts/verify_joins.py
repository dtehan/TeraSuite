#!/usr/bin/env python3
"""
Concrete proof that the seed data is queryable across tables (joins work).

There is no live Teradata instance available, so this script loads an
equivalent copy of db/02_load_data.sql's rows into an in-memory SQLite
database (a verification aid only -- NOT a deliverable; the canonical
scripts in db/ remain pure Teradata syntax) and executes representative
cross-table join queries drawn from the eval expected_sql, asserting they
return the expected non-empty/expected-shape results.
"""
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DDL_PATH = ROOT / "db" / "01_create_database.sql"
DML_PATH = ROOT / "db" / "02_load_data.sql"

# Minimal SQLite-compatible DDL mirroring db/01_create_database.sql's columns.
# (SQLite doesn't support Teradata's CREATE DATABASE / PRIMARY INDEX / REFERENCES
# WITH NO CHECK OPTION syntax, so this is a hand-translated equivalent shape,
# not a syntax-preserving copy.)
SQLITE_DDL = """
CREATE TABLE Customer (
    CustomerID INTEGER, CustomerName TEXT, Region TEXT, Segment TEXT,
    SignupDate TEXT, Email TEXT
);
CREATE TABLE Product (
    ProductID INTEGER, ProductName TEXT, Category TEXT, UnitPrice REAL,
    Discontinued TEXT
);
CREATE TABLE Store (
    StoreID INTEGER, StoreName TEXT, Region TEXT, ManagerName TEXT
);
CREATE TABLE Orders (
    OrderID INTEGER, CustomerID INTEGER, StoreID INTEGER, OrderDate TEXT,
    Status TEXT
);
CREATE TABLE OrderLine (
    OrderLineID INTEGER, OrderID INTEGER, ProductID INTEGER, Quantity INTEGER,
    LineTotal REAL
);
CREATE TABLE Employee (
    EmployeeID INTEGER, EmployeeName TEXT, Department TEXT, JobTitle TEXT,
    ManagerID INTEGER
);
CREATE TABLE DBA_Users (
    UserName TEXT, CreateDate TEXT, DefaultDatabase TEXT, PermSpaceMB REAL,
    SpoolSpaceMB REAL, AccountRole TEXT
);
CREATE TABLE DBA_AccessRights (
    AccessID INTEGER, UserName TEXT, DatabaseName TEXT, TableName TEXT,
    AccessType TEXT, GrantedBy TEXT, GrantDate TEXT
);
CREATE TABLE DBA_SecurityAuditLog (
    LogID INTEGER, UserName TEXT, EventType TEXT, EventTimestamp TEXT,
    SourceIP TEXT, Success TEXT
);
CREATE TABLE DBA_QueryLog (
    QueryID INTEGER, UserName TEXT, QueryText TEXT, StartTime TEXT,
    ElapsedSeconds REAL, CPUTime REAL, IOCount INTEGER, SpoolUsageMB REAL,
    Status TEXT
);
CREATE TABLE DBA_TableSpaceUsage (
    DatabaseName TEXT, TableName TEXT, CurrentPermMB REAL, PeakPermMB REAL,
    RowCount INTEGER, LastStatsCollectionDate TEXT
);
"""

# Representative cross-table joins, one per persona domain, proving data is
# queryable across the schema (this mirrors the kind of joins the eval
# expected_sql files rely on).
JOIN_QUERIES = {
    "customer_orders_revenue": """
        SELECT c.Region, SUM(ol.LineTotal) AS Revenue
        FROM Customer c
        JOIN Orders o ON c.CustomerID = o.CustomerID
        JOIN OrderLine ol ON o.OrderID = ol.OrderID
        GROUP BY c.Region
    """,
    "product_category_sales": """
        SELECT p.Category, COUNT(*) AS LinesSold
        FROM Product p
        JOIN OrderLine ol ON p.ProductID = ol.ProductID
        GROUP BY p.Category
    """,
    "store_order_counts": """
        SELECT s.StoreName, COUNT(*) AS OrderCount
        FROM Store s
        JOIN Orders o ON s.StoreID = o.StoreID
        GROUP BY s.StoreName
    """,
    "employee_manager_hierarchy": """
        SELECT e.EmployeeName AS Employee, m.EmployeeName AS Manager
        FROM Employee e
        LEFT JOIN Employee m ON e.ManagerID = m.EmployeeID
    """,
    "user_access_rights": """
        SELECT u.UserName, u.AccountRole, ar.TableName, ar.AccessType
        FROM DBA_Users u
        JOIN DBA_AccessRights ar ON u.UserName = ar.UserName
    """,
    "user_query_activity": """
        SELECT u.UserName, COUNT(*) AS QueryCount, SUM(ql.SpoolUsageMB) AS TotalSpool
        FROM DBA_Users u
        JOIN DBA_QueryLog ql ON u.UserName = ql.UserName
        GROUP BY u.UserName
    """,
    "customer_with_zero_orders": """
        SELECT c.CustomerID, c.CustomerName
        FROM Customer c
        LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
        WHERE o.OrderID IS NULL
    """,
}


def parse_insert_statements(sql_text: str):
    pattern = re.compile(
        r"INSERT\s+INTO\s+(\w+)\s*\(([^)]*)\)\s*VALUES\s*\((.*?)\)\s*;",
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(sql_text):
        table, columns, values = match.groups()
        col_list = [c.strip() for c in columns.split(",")]
        yield table, col_list, split_values(values)


def split_values(values: str):
    # Split on commas that are not inside single-quoted strings.
    parts, current, in_quotes = [], "", False
    i = 0
    while i < len(values):
        ch = values[i]
        if ch == "'":
            in_quotes = not in_quotes
            current += ch
        elif ch == "," and not in_quotes:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
        i += 1
    if current.strip():
        parts.append(current.strip())
    return [coerce(p) for p in parts]


def coerce(token: str):
    token = token.strip()
    if token.upper() == "NULL":
        return None
    m = re.match(r"^(?:DATE|TIMESTAMP)\s*'([^']*)'$", token, re.IGNORECASE)
    if m:
        return m.group(1)
    if token.startswith("'") and token.endswith("'"):
        return token[1:-1].replace("''", "'")
    try:
        if "." in token:
            return float(token)
        return int(token)
    except ValueError:
        return token


def main() -> int:
    dml_text = DML_PATH.read_text()

    conn = sqlite3.connect(":memory:")
    conn.executescript(SQLITE_DDL)

    row_counts: dict[str, int] = {}
    for table, columns, values in parse_insert_statements(dml_text):
        placeholders = ", ".join("?" for _ in columns)
        conn.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})", values)
        row_counts[table] = row_counts.get(table, 0) + 1
    conn.commit()

    print("Loaded row counts (from db/02_load_data.sql):")
    for table, count in sorted(row_counts.items()):
        print(f"  {table}: {count}")

    errors = []
    print("\nRunning representative cross-table joins:")
    for name, query in JOIN_QUERIES.items():
        cur = conn.execute(query)
        rows = cur.fetchall()
        status = "OK" if rows else "EMPTY"
        print(f"  [{status}] {name}: {len(rows)} row(s)")
        if not rows:
            errors.append(f"join query '{name}' returned zero rows")

    # customer_with_zero_orders is EXPECTED to return exactly one row (CustomerID 115).
    zero_order_customers = conn.execute(JOIN_QUERIES["customer_with_zero_orders"]).fetchall()
    if len(zero_order_customers) != 1 or zero_order_customers[0][0] != 115:
        errors.append(
            f"expected exactly one zero-order customer (CustomerID 115), got {zero_order_customers}"
        )

    if errors:
        print("\nJOIN VERIFICATION: FAILED")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("\nJOIN VERIFICATION: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
