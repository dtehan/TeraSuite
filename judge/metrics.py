"""deepeval GEval metrics for Tera answer quality."""

from __future__ import annotations

import os

from deepeval.metrics import GEval
from deepeval.test_case import SingleTurnParams

_PARAMS = [
    SingleTurnParams.INPUT,
    SingleTurnParams.ACTUAL_OUTPUT,
    SingleTurnParams.EXPECTED_OUTPUT,
]

_BEHAVIOR_CRITERIA = {
    "return_data": (
        "The answer must return concrete data that addresses the user's question. "
        "A clarifying question alone, a refusal, or a conceptual explanation with no result fails."
    ),
    "return_empty_result": (
        "The answer must show that a query ran and matched no rows. Invented rows fail."
    ),
    "ask_clarifying_question": (
        "The prompt is missing information needed for a single correct query. "
        "The answer must ask for that information. Guessing a table, date range, filter, or metric fails."
    ),
    "refuse_or_flag_permission": (
        "The answer must refuse the request or clearly flag that it exceeds the caller's permissions. "
        "Carrying out the disallowed lookup fails."
    ),
    "explain_only": (
        "The answer must explain the situation, including when the requested data is not in the schema. "
        "Invented numbers or rows presented as query results fail."
    ),
    "flag_data_quality_issue": (
        "The answer must identify the data-quality, governance, or operational issue in the reference. "
        "Raw rows with no callout of that issue fail."
    ),
}


def _threshold() -> float:
    return float(os.environ.get("JUDGE_THRESHOLD", "0.5"))


def _metric(name: str, criteria: str, steps: list[str], judge_llm) -> GEval:
    return GEval(
        name=name,
        criteria=criteria,
        evaluation_steps=steps,
        evaluation_params=_PARAMS,
        model=judge_llm,
        threshold=_threshold(),
        async_mode=False,
        verbose_mode=False,
    )


def behavior_metric(case: dict, judge_llm) -> GEval:
    behavior = (case.get("expected_output") or {}).get("expected_behavior", "")
    criteria = _BEHAVIOR_CRITERIA.get(
        behavior,
        f"The answer must exhibit the expected behavior '{behavior}' described in the reference.",
    )
    return _metric(
        "Behavior",
        criteria,
        [
            f"Read the expected behavior '{behavior}' and the case description in the reference.",
            "Score 1 when the actual answer does that behavior.",
            "Score 0 when it does a different behavior, invents data, or ignores the question.",
        ],
        judge_llm,
    )


def sql_metric(judge_llm) -> GEval:
    return _metric(
        "SQL Equivalence",
        (
            "The reference SQL specifies the correct question: tables, joins, filters, and aggregations. "
            "The agent's SQL and final answer should be semantically equivalent. "
            "Verbatim SQL is not required. Teradata syntax differences are acceptable when the meaning matches."
        ),
        [
            "Compare the reference SQL to any SQL in the tool trace and to the final answer.",
            "Treat a different but equivalent query, or a correct answer to that query, as a match.",
            "Lower the score for the wrong tables, missing filters, a different grain, or an invented result.",
        ],
        judge_llm,
    )


def result_metric(judge_llm) -> GEval:
    return _metric(
        "Result Shape",
        (
            "The answer or tool result should match the expected columns, row-count comparison, and notes. "
            "Column aliases may differ. The notes are part of the requirement."
        ),
        [
            "Check the expected columns against the answer and tool results.",
            "Apply the row_count comparator (eq, gte, lte, gt, lt) to the visible row count.",
            "Check the notes. Missing a note-specific requirement lowers the score.",
        ],
        judge_llm,
    )


def explanation_metric(judge_llm) -> GEval:
    return _metric(
        "Explanation Points",
        "The answer must cover every explanation point in substance. Wording may differ. A missing point fails.",
        [
            "List the explanation points in the reference.",
            "Mark each point covered or missing based on the actual answer.",
            "Score 1 only when every point is covered. Score lower in proportion to the points that are missing.",
        ],
        judge_llm,
    )


def get_metrics(case: dict, judge_llm) -> list:
    """Return the GEval metrics that apply to this case."""
    expected = case.get("expected_output") or {}
    metrics = [behavior_metric(case, judge_llm)]
    if expected.get("expected_sql"):
        metrics.append(sql_metric(judge_llm))
    if expected.get("expected_result"):
        metrics.append(result_metric(judge_llm))
    if expected.get("expected_explanation_points"):
        metrics.append(explanation_metric(judge_llm))
    return metrics
