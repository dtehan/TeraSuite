"""Deterministic checks that run before the LLM judge."""

from __future__ import annotations

DATA_BEHAVIORS = frozenset(
    {
        "return_data",
        "return_empty_result",
        "flag_data_quality_issue",
    }
)


def run_deterministic_checks(
    case: dict,
    *,
    final_response: str,
    tool_call_count: int,
) -> list[str]:
    """Return structural failures. An empty list means the judge may run."""
    errors: list[str] = []
    if not final_response.strip():
        errors.append("agent returned an empty answer")

    behavior = (case.get("expected_output") or {}).get("expected_behavior", "")
    if behavior in DATA_BEHAVIORS and tool_call_count == 0:
        errors.append(
            f"expected at least one Tera MCP tool call for behavior {behavior}, got none"
        )
    return errors
