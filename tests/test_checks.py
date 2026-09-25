"""Offline checks for structural scoring and judge packets."""

from judge.checks import run_deterministic_checks
from judge.packet import extract_sql, format_actual, format_expected


def _case(behavior: str) -> dict:
    return {
        "id": "BU-001",
        "persona": "business_user",
        "category": "typical",
        "description": "Revenue for February.",
        "prompt": "How much revenue?",
        "requires_tables": ["Orders", "OrderLine"],
        "expected_output": {
            "expected_behavior": behavior,
            "expected_sql": "SELECT SUM(ol.LineTotal) FROM Orders o",
            "expected_result": {"columns": ["FebRevenue"], "row_count": 1, "notes": "February only"},
            "expected_explanation_points": ["single dollar figure"],
        },
    }


def test_empty_answer_fails():
    errors = run_deterministic_checks(_case("return_data"), final_response="  ", tool_call_count=1)
    assert errors == ["agent returned an empty answer"]


def test_data_behavior_requires_a_tool_call():
    errors = run_deterministic_checks(_case("return_data"), final_response="42", tool_call_count=0)
    assert any("tool call" in error for error in errors)


def test_refusal_does_not_require_a_tool_call():
    errors = run_deterministic_checks(_case("refuse_or_flag_permission"), final_response="I can't do that.", tool_call_count=0)
    assert errors == []


def test_packets_include_sql_and_reference():
    case = _case("return_data")
    expected = format_expected(case)
    assert "SELECT SUM" in expected
    assert "February only" in expected
    assert "single dollar figure" in expected
    actual = format_actual(
        "February revenue was 10.",
        [{"name": "query", "input_parameters": {"sql": "SELECT 1"}, "result_preview": "1"}],
    )
    assert "February revenue was 10." in actual
    assert "SELECT 1" in actual
    assert extract_sql([{"input_parameters": {"sql": "WITH t AS (SELECT 1 AS n) SELECT n FROM t"}}])


def test_extract_sql_ignores_prose():
    assert extract_sql([{"input_parameters": {"question": "How many orders?"}}]) == []
