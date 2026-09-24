#!/usr/bin/env python3
"""
Validates every persona eval file in evals/cases/*.yaml against the
TestSuite schema in evals/schema/eval-schema.yaml, and cross-checks that
every table referenced in requires_tables (and CREATE TABLE names
mentioned in expected_sql) actually exists in db/01_create_database.sql.

This is the "evals are using the database data and structures" check from
the Definition of Done.
"""
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, RefResolver

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "evals" / "schema" / "eval-schema.yaml"
CASES_DIR = ROOT / "evals" / "cases"
DB_SCRIPT = ROOT / "db" / "01_create_database.sql"

EXPECTED_PERSONAS = {
    "business_user": "business_user.yaml",
    "data_scientist": "data_scientist.yaml",
    "data_analyst": "data_analyst.yaml",
    "dba": "dba.yaml",
    "security_expert": "security_expert.yaml",
    "database_operations": "database_operations.yaml",
}


def load_table_names() -> set[str]:
    text = DB_SCRIPT.read_text()
    return {name.upper() for name in re.findall(r"CREATE\s+SET\s+TABLE\s+(\w+)", text, re.IGNORECASE)}


def build_validator() -> Draft7Validator:
    with open(SCHEMA_PATH) as f:
        openapi_doc = yaml.safe_load(f)
    test_suite_schema = {"$ref": "#/components/schemas/TestSuite"}
    resolver = RefResolver.from_schema(openapi_doc)
    return Draft7Validator(test_suite_schema, resolver=resolver)


def main() -> int:
    errors: list[str] = []
    table_names = load_table_names()
    validator = build_validator()

    found_files = {p.name for p in CASES_DIR.glob("*.yaml")}
    for persona, filename in EXPECTED_PERSONAS.items():
        if filename not in found_files:
            errors.append(f"missing eval file for persona '{persona}': evals/cases/{filename}")

    total_cases = 0
    for filename in sorted(found_files):
        path = CASES_DIR / filename
        with open(path) as f:
            doc = yaml.safe_load(f)

        for schema_error in validator.iter_errors(doc):
            errors.append(f"{filename}: schema violation at {list(schema_error.path)}: {schema_error.message}")

        persona = doc.get("persona") if isinstance(doc, dict) else None
        cases = doc.get("test_cases", []) if isinstance(doc, dict) else []

        if persona and filename != EXPECTED_PERSONAS.get(persona):
            errors.append(f"{filename}: persona '{persona}' does not match expected filename")

        if len(cases) < 20:
            errors.append(f"{filename}: only {len(cases)} test cases (expected 20+)")

        seen_ids = set()
        typical_count = 0
        edge_count = 0
        for case in cases:
            total_cases += 1
            case_id = case.get("id", "<missing id>")

            if case_id in seen_ids:
                errors.append(f"{filename}: duplicate test case id {case_id}")
            seen_ids.add(case_id)

            if case.get("category") == "typical":
                typical_count += 1
            elif case.get("category") == "edge":
                edge_count += 1

            requires_tables = case.get("requires_tables", [])
            if not requires_tables:
                errors.append(f"{filename}/{case_id}: requires_tables is empty")
            for table in requires_tables:
                if table.upper() not in table_names:
                    errors.append(
                        f"{filename}/{case_id}: requires_tables references unknown table '{table}' "
                        f"(not found in db/01_create_database.sql)"
                    )

            expected_sql = case.get("expected_output", {}).get("expected_sql", "")
            if expected_sql:
                # Strip EXTRACT(part FROM expr) calls first -- their FROM is
                # part of EXTRACT's syntax, not a table reference, and would
                # otherwise be misread as "FROM <alias>" (e.g. "EXTRACT(YEAR
                # FROM c.SignupDate)" naively looks like "FROM c").
                sql_no_extract = re.sub(r"EXTRACT\s*\([^)]*\)", "", expected_sql, flags=re.IGNORECASE)
                referenced = {
                    t.upper()
                    for t in re.findall(r"\bFROM\s+(\w+)|\bJOIN\s+(\w+)", sql_no_extract, re.IGNORECASE)
                    for t in t if t
                }
                unknown = {t for t in referenced if t and t not in table_names}
                if unknown:
                    errors.append(f"{filename}/{case_id}: expected_sql references unknown table(s) {sorted(unknown)}")

        if edge_count == 0:
            errors.append(f"{filename}: no 'edge' category cases found")
        if typical_count == 0:
            errors.append(f"{filename}: no 'typical' category cases found")

    print(f"Checked {len(found_files)} eval file(s), {total_cases} total test case(s).")

    if errors:
        print("EVAL VALIDATION: FAILED")
        for err in errors:
            print(f"  - {err}")
        return 1

    print("EVAL VALIDATION: PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
