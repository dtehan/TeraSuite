"""Run one YAML eval case through the Tera agent and the deepeval judge."""

from __future__ import annotations

import os
from typing import Any

from deepeval.test_case import LLMTestCase

from agent.client import Usage, run_agent
from judge.checks import run_deterministic_checks
from judge.metrics import get_metrics
from judge.packet import format_actual, format_expected
from judge.report import (
    CaseEvalResult,
    build_recommendation,
    note_available_tools,
    record_case_result,
)


def _tool_dicts(tool_calls) -> list[dict[str, Any]]:
    return [
        {
            "name": call.name,
            "input_parameters": call.input_parameters,
            "result_preview": call.result_preview,
        }
        for call in tool_calls
    ]


def _usage_dict(usage: Usage) -> dict[str, Any]:
    return {
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
        "total_tokens": usage.total_tokens,
        "elapsed_seconds": usage.elapsed_seconds,
        "steps": usage.steps,
    }


def _token_cap() -> int:
    raw = os.environ.get("AGENT_MAX_TOKENS", "").strip()
    if not raw:
        return 0
    return int(raw)


def _score(test_case: LLMTestCase, metrics) -> tuple[list[str], bool, list[dict[str, Any]]]:
    reasons: list[str] = []
    scores: list[dict[str, Any]] = []
    passed = True
    for metric in metrics:
        name = getattr(metric, "name", "metric")
        try:
            metric.measure(test_case)
        except Exception as exc:
            passed = False
            reasons.append(f"{name}: {exc}")
            scores.append({"name": name, "score": None, "success": False, "reason": str(exc)})
            continue
        success = bool(getattr(metric, "success", False))
        reason = getattr(metric, "reason", "") or ""
        score = getattr(metric, "score", None)
        scores.append({"name": name, "score": score, "success": success, "reason": reason})
        if not success:
            passed = False
            reasons.append(f"{name}: {reason or 'below threshold'}")
    return reasons, passed, scores


def _result(
    case: dict,
    *,
    passed: bool,
    failure_stage: str | None = None,
    failure_detail: str | None = None,
    actual_output: str | None = None,
    tool_calls: list[dict[str, Any]] | None = None,
    metric_reasons: list[str] | None = None,
    metric_scores: list[dict[str, Any]] | None = None,
    usage: dict[str, Any] | None = None,
    judge_usage: dict[str, Any] | None = None,
) -> CaseEvalResult:
    reasons = metric_reasons or []
    recommendation = None
    if not passed:
        recommendation = build_recommendation(
            case,
            failure_stage=failure_stage or "metric",
            failure_detail=failure_detail,
            metric_reasons=reasons,
        )
    expected = case.get("expected_output") or {}
    return CaseEvalResult(
        case_id=case.get("id", "<unknown>"),
        persona=case.get("persona", ""),
        category=case.get("category", ""),
        description=case.get("description", ""),
        prompt=case.get("prompt", ""),
        expected_behavior=expected.get("expected_behavior", ""),
        passed=passed,
        failure_stage=failure_stage,
        failure_detail=failure_detail,
        actual_output=actual_output,
        tool_calls=tool_calls or [],
        metric_reasons=reasons,
        metric_scores=metric_scores or [],
        recommendation=recommendation,
        usage=usage or {},
        judge_usage=judge_usage or {},
    )


def _judge_usage(judge_llm, before: tuple[int, int]) -> dict[str, int]:
    after_in = int(getattr(judge_llm, "input_tokens", 0) or 0)
    after_out = int(getattr(judge_llm, "output_tokens", 0) or 0)
    return {
        "input_tokens": max(0, after_in - before[0]),
        "output_tokens": max(0, after_out - before[1]),
    }


def run_eval_case(case: dict, bedrock_client, agent_model_id: str, judge_llm) -> CaseEvalResult:
    """Run one case. Does not record the result or raise."""
    try:
        agent_result = run_agent(
            case["prompt"],
            model_id=agent_model_id,
            bedrock_client=bedrock_client,
            requires_tables=list(case.get("requires_tables") or []),
        )
    except Exception as exc:
        return _result(
            case,
            passed=False,
            failure_stage="agent",
            failure_detail=str(exc),
        )

    note_available_tools(agent_result.available_tools)
    usage = _usage_dict(agent_result.usage)
    tools = _tool_dicts(agent_result.tool_calls)
    actual = format_actual(agent_result.final_response, tools)

    if agent_result.hit_step_limit and not agent_result.final_response.strip():
        return _result(
            case,
            passed=False,
            failure_stage="deterministic",
            failure_detail=f"reached AGENT_MAX_STEPS ({agent_result.usage.steps}) without a final answer",
            actual_output=actual,
            tool_calls=tools,
            usage=usage,
        )

    det_errors = run_deterministic_checks(
        case,
        final_response=agent_result.final_response,
        tool_call_count=len(agent_result.tool_calls),
    )
    if det_errors:
        return _result(
            case,
            passed=False,
            failure_stage="deterministic",
            failure_detail="; ".join(det_errors),
            actual_output=actual,
            tool_calls=tools,
            usage=usage,
        )

    cap = _token_cap()
    if cap and agent_result.usage.total_tokens > cap:
        return _result(
            case,
            passed=False,
            failure_stage="usage",
            failure_detail=(
                f"billed {agent_result.usage.total_tokens} tokens, cap is {cap}"
            ),
            actual_output=actual,
            tool_calls=tools,
            usage=usage,
        )

    test_case = LLMTestCase(
        input=case["prompt"],
        actual_output=actual,
        expected_output=format_expected(case),
    )
    before = (
        int(getattr(judge_llm, "input_tokens", 0) or 0),
        int(getattr(judge_llm, "output_tokens", 0) or 0),
    )
    reasons, passed, scores = _score(test_case, get_metrics(case, judge_llm))
    judge_usage = _judge_usage(judge_llm, before)
    if not passed:
        return _result(
            case,
            passed=False,
            failure_stage="metric",
            failure_detail="; ".join(reasons),
            actual_output=actual,
            tool_calls=tools,
            metric_reasons=reasons,
            metric_scores=scores,
            usage=usage,
            judge_usage=judge_usage,
        )
    return _result(
        case,
        passed=True,
        actual_output=actual,
        tool_calls=tools,
        metric_scores=scores,
        usage=usage,
        judge_usage=judge_usage,
    )


def assert_eval_case(case: dict, bedrock_client, agent_model_id: str, judge_llm) -> None:
    """Run one case, record it, and fail the pytest assertion when it does not pass."""
    result = run_eval_case(case, bedrock_client, agent_model_id, judge_llm)
    record_case_result(result)
    if not result.passed:
        detail = result.failure_detail or "eval case failed"
        raise AssertionError(f"[{result.case_id}] {result.failure_stage} check failed: {detail}")
