"""Text packets the judge scores, built from a case and an agent trace."""

from __future__ import annotations

import json
import re
from typing import Any

_SQL_START = re.compile(r"(?is)\b(SELECT|WITH|EXPLAIN)\b")
_MAX_ANSWER_CHARS = 12000
_MAX_PARAM_CHARS = 4000


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... [truncated]"


def _walk_strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_strings(item)


def extract_sql(tool_calls: list[dict[str, Any]]) -> list[str]:
    """Return SQL-looking strings found in tool arguments."""
    found: list[str] = []
    seen: set[str] = set()
    for call in tool_calls:
        for text in _walk_strings(call.get("input_parameters", {})):
            stripped = text.strip()
            if _SQL_START.search(stripped) and stripped not in seen:
                seen.add(stripped)
                found.append(stripped)
    return found


def format_expected(case: dict[str, Any]) -> str:
    """Render the case's expected_output as the judge's reference."""
    expected = case.get("expected_output") or {}
    lines = [
        f"Behavior: {expected.get('expected_behavior', '')}",
        f"Persona: {case.get('persona', '')}",
        f"Category: {case.get('category', '')}",
        f"What this case checks: {case.get('description', '')}",
        "Tables the correct answer depends on: " + ", ".join(case.get("requires_tables") or []),
    ]
    if expected.get("expected_sql"):
        lines.extend(["", "Reference SQL (semantically equivalent SQL is acceptable):", expected["expected_sql"].strip()])
    result = expected.get("expected_result") or {}
    if result:
        comparator = result.get("row_count_comparator") or "eq"
        lines.extend(
            [
                "",
                "Expected result shape:",
                f"columns: {', '.join(result.get('columns') or [])}",
                f"row_count {comparator} {result.get('row_count', '')}",
            ]
        )
        if result.get("notes"):
            lines.append(f"notes: {result['notes']}")
    points = expected.get("expected_explanation_points") or []
    if points:
        lines.extend(["", "Explanation points the answer must cover:"])
        lines.extend(f"- {point}" for point in points)
    return "\n".join(lines).strip()


def format_actual(final_response: str, tool_calls: list[dict[str, Any]]) -> str:
    """Render the agent answer and tool trace for the judge."""
    lines = ["Final answer:", _truncate(final_response.strip(), _MAX_ANSWER_CHARS), "", "Tools called:"]
    if not tool_calls:
        lines.append("(none)")
    for index, call in enumerate(tool_calls, start=1):
        params = json.dumps(call.get("input_parameters", {}), default=str)
        lines.append(f"{index}. {call.get('name', '')} {_truncate(params, _MAX_PARAM_CHARS)}")
        preview = call.get("result_preview") or ""
        if preview:
            lines.append(f"   result: {_truncate(preview, _MAX_PARAM_CHARS)}")
    sql = extract_sql(tool_calls)
    lines.extend(["", "SQL observed in tool arguments:"])
    if sql:
        lines.extend(sql)
    else:
        lines.append("(none)")
    return "\n".join(lines).strip()
