#!/usr/bin/env python3
"""
Heuristic static syntax checks for the Teradata DDL/DML scripts in db/.

There is no live Teradata instance available to this project, so this
script performs structural/regex-based checks for common Teradata SQL
requirements and common non-Teradata constructs that would indicate the
scripts were written for a different RDBMS. It is a heuristic aid, not a
substitute for running the scripts against a real Teradata engine -- see
VERIFICATION.md for the accompanying manual review checklist.
"""
import re
import sys
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "db"

NON_TERADATA_PATTERNS = [
    (r"\bAUTO_INCREMENT\b", "AUTO_INCREMENT is MySQL syntax; Teradata uses GENERATED ALWAYS AS IDENTITY"),
    (r"\bGETDATE\s*\(", "GETDATE() is SQL Server syntax; Teradata uses CURRENT_DATE / CURRENT_TIMESTAMP"),
    (r"\bNOW\s*\(\)", "NOW() is MySQL/Postgres syntax; Teradata uses CURRENT_TIMESTAMP"),
    (r"\bLIMIT\s+\d+", "LIMIT is MySQL/Postgres syntax; Teradata uses TOP n or QUALIFY RANK()"),
    (r"\bIFNULL\s*\(", "IFNULL is MySQL syntax; Teradata uses COALESCE / ZEROIFNULL"),
    (r"\bAUTOINCREMENT\b", "AUTOINCREMENT is SQLite syntax; Teradata uses GENERATED ALWAYS AS IDENTITY"),
    (r"`[^`]+`", "Backtick-quoted identifiers are MySQL syntax; Teradata uses double quotes if needed"),
]

REQUIRED_DDL_ELEMENTS = [
    (r"CREATE\s+DATABASE\s+\w+", "at least one CREATE DATABASE statement"),
    (r"CREATE\s+DATABASE[\s\S]*?\bPERM\s*=", "CREATE DATABASE must include a PERM allocation"),
]

VALID_TERADATA_TYPES = {
    "INTEGER", "SMALLINT", "BYTEINT", "BIGINT", "DECIMAL", "NUMERIC", "FLOAT",
    "REAL", "DOUBLE", "CHAR", "VARCHAR", "CLOB", "DATE", "TIME", "TIMESTAMP",
    "BYTE", "VARBYTE", "BLOB",
}


def strip_comments(text):
    """Blank out comment contents (preserving length/newlines/line numbers)
    so regex checks below don't false-positive on comment text that merely
    *describes* a forbidden construct."""
    def blank(match):
        return "".join(ch if ch == "\n" else " " for ch in match.group(0))

    text = re.sub(r"/\*.*?\*/", blank, text, flags=re.DOTALL)
    text = re.sub(r"--[^\n]*", blank, text)
    return text


def check_non_teradata_constructs(text, filename, errors):
    code_only = strip_comments(text)
    for pattern, message in NON_TERADATA_PATTERNS:
        for m in re.finditer(pattern, code_only, re.IGNORECASE):
            line_no = code_only.count("\n", 0, m.start()) + 1
            errors.append(f"{filename}:{line_no}: {message} (found: {m.group(0)!r})")


def check_create_table_has_primary_index(text, filename, errors):
    # Split on CREATE (SET|MULTISET) TABLE ... up to the trailing semicolon
    table_blocks = re.finditer(
        r"CREATE\s+(?:SET|MULTISET)\s+TABLE\s+(\w+)\s*\((.*?)\)\s*\n?PRIMARY INDEX\s*\(([^)]+)\)\s*;",
        text, re.IGNORECASE | re.DOTALL,
    )
    found_tables = set()
    for m in table_blocks:
        found_tables.add(m.group(1))

    # Now find every CREATE TABLE statement regardless of whether it matched
    # the PRIMARY INDEX pattern above, to catch ones that are missing it.
    all_tables = re.finditer(r"CREATE\s+(?:SET|MULTISET)\s+TABLE\s+(\w+)", text, re.IGNORECASE)
    for m in all_tables:
        table_name = m.group(1)
        if table_name not in found_tables:
            line_no = text.count("\n", 0, m.start()) + 1
            errors.append(
                f"{filename}:{line_no}: table {table_name!r} does not appear to declare an explicit PRIMARY INDEX"
            )


def check_statements_terminated(text, filename, errors):
    # Strip comments before checking terminators.
    stripped = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    stripped = re.sub(r"--.*", "", stripped)
    stripped = stripped.strip()
    if stripped and not stripped.endswith(";"):
        errors.append(f"{filename}: file does not end with a semicolon-terminated statement")


def check_insert_value_types(text, filename, errors):
    # Multi-row VALUES lists like VALUES (1,'a'),(2,'b') are not standard
    # Teradata syntax for INSERT ... VALUES; flag them if present.
    code_only = strip_comments(text)
    for m in re.finditer(r"VALUES\s*\([^)]*\)\s*,\s*\(", code_only, re.IGNORECASE):
        line_no = code_only.count("\n", 0, m.start()) + 1
        errors.append(f"{filename}:{line_no}: multi-row VALUES(...),(...)  is not standard Teradata INSERT syntax")


def check_required_elements(text, filename, errors):
    for pattern, description in REQUIRED_DDL_ELEMENTS:
        if not re.search(pattern, text, re.IGNORECASE):
            errors.append(f"{filename}: missing {description}")


def main():
    errors = []
    ddl_file = DB_DIR / "01_create_database.sql"
    dml_file = DB_DIR / "02_load_data.sql"

    if not ddl_file.exists() or not dml_file.exists():
        print(f"ERROR: expected files not found under {DB_DIR}")
        sys.exit(1)

    ddl_text = ddl_file.read_text()
    dml_text = dml_file.read_text()

    check_non_teradata_constructs(ddl_text, ddl_file.name, errors)
    check_non_teradata_constructs(dml_text, dml_file.name, errors)
    check_create_table_has_primary_index(ddl_text, ddl_file.name, errors)
    check_statements_terminated(ddl_text, ddl_file.name, errors)
    check_statements_terminated(dml_text, dml_file.name, errors)
    check_insert_value_types(dml_text, dml_file.name, errors)
    check_required_elements(ddl_text, ddl_file.name, errors)

    if errors:
        print(f"FAIL: {len(errors)} issue(s) found\n")
        for e in errors:
            print(" -", e)
        sys.exit(1)

    print("PASS: no heuristic Teradata syntax issues found in db/01_create_database.sql and db/02_load_data.sql")
    sys.exit(0)


if __name__ == "__main__":
    main()
