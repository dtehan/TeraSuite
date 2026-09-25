"""Load persona YAML suites from evals/cases."""

from __future__ import annotations

import os
from pathlib import Path

import yaml

CASES_DIR = Path(__file__).resolve().parent.parent / "evals" / "cases"

REQUIRED_CASE_KEYS = (
    "id",
    "name",
    "persona",
    "category",
    "description",
    "prompt",
    "requires_tables",
    "expected_output",
)
EXPECTED_KEYS = (
    "expected_sql",
    "expected_result",
    "expected_explanation_points",
    "expected_behavior",
)


def _env(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def persona_names() -> list[str]:
    """Persona ids, one per YAML file, in filename order."""
    return sorted(path.stem for path in CASES_DIR.glob("*.yaml"))


def load_persona_cases(persona: str) -> list[dict]:
    """Load and validate one persona file."""
    path = CASES_DIR / f"{persona}.yaml"
    if not path.exists():
        known = ", ".join(persona_names()) or "(none)"
        raise FileNotFoundError(f"no eval file for persona {persona!r}. Known personas: {known}")
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    file_persona = document.get("persona")
    if file_persona != persona:
        raise ValueError(f"{path.name} declares persona {file_persona!r}, expected {persona!r}")
    cases = document.get("test_cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError(f"{path.name} has no test_cases")
    loaded: list[dict] = []
    for case in cases:
        _validate_case(case, persona=persona, filename=path.name)
        loaded.append(case)
    return loaded


def _validate_case(case: dict, *, persona: str, filename: str) -> None:
    if not isinstance(case, dict):
        raise ValueError(f"{filename} contains a test case that is not a mapping")
    missing = [key for key in REQUIRED_CASE_KEYS if key not in case]
    if missing:
        raise ValueError(f"{filename} case {case.get('id', '?')} is missing {', '.join(missing)}")
    if case["persona"] != persona:
        raise ValueError(f"{filename} case {case['id']} has persona {case['persona']!r}, expected {persona!r}")
    expected = case["expected_output"]
    if not isinstance(expected, dict) or not any(expected.get(key) for key in EXPECTED_KEYS):
        raise ValueError(f"{filename} case {case['id']} expected_output needs sql, a result, explanation points, or a behavior")
    if not isinstance(case["requires_tables"], list) or not case["requires_tables"]:
        raise ValueError(f"{filename} case {case['id']} requires_tables must be a non-empty list")


def load_all_cases(
    *,
    persona: str | None = None,
    category: str | None = None,
    case_id: str | None = None,
    limit: int | None = None,
    apply_env: bool = True,
) -> list[dict]:
    """Load cases, optionally filtered.

    When apply_env is true, empty arguments fall back to EVALS_PERSONA,
    EVALS_CATEGORY, EVALS_CASE_ID, and EVALS_LIMIT.
    """
    if apply_env:
        persona = persona if persona is not None else _env("EVALS_PERSONA")
        category = category if category is not None else _env("EVALS_CATEGORY")
        case_id = case_id if case_id is not None else _env("EVALS_CASE_ID")
        if limit is None and _env("EVALS_LIMIT"):
            limit = int(os.environ["EVALS_LIMIT"])

    names = [persona] if persona else persona_names()
    cases: list[dict] = []
    for name in names:
        cases.extend(load_persona_cases(name))
    if category:
        cases = [case for case in cases if case.get("category") == category]
    if case_id:
        cases = [case for case in cases if case.get("id") == case_id]
    cases.sort(key=lambda case: (case["persona"], case["id"]))
    if limit is not None:
        cases = cases[:limit]
    return cases
