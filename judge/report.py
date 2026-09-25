"""Collect eval outcomes and write summaries under results/."""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
MAX_INDEX_RUNS = 50


@dataclass
class CaseEvalResult:
    case_id: str
    persona: str
    category: str
    description: str
    prompt: str
    expected_behavior: str
    passed: bool
    failure_stage: str | None = None
    failure_detail: str | None = None
    actual_output: str | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    metric_reasons: list[str] = field(default_factory=list)
    metric_scores: list[dict[str, Any]] = field(default_factory=list)
    recommendation: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)
    judge_usage: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvalRunReport:
    started_at: str
    persona_filter: str
    category_filter: str
    case_id_filter: str
    context_mode: str
    agent_model_id: str
    judge_model_id: str
    tera_mcp_url: str
    database: str
    run_label: str | None = None
    available_tools: list[str] = field(default_factory=list)
    results: list[CaseEvalResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed_count(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def failed_count(self) -> int:
        return self.total - self.passed_count


_report: EvalRunReport | None = None


def begin_eval_run(
    *,
    agent_model_id: str,
    judge_model_id: str,
    run_label: str | None = None,
) -> None:
    """Start a fresh in-memory report for this pytest session."""
    global _report
    _report = EvalRunReport(
        started_at=datetime.now(timezone.utc).isoformat(),
        persona_filter=os.environ.get("EVALS_PERSONA") or "all",
        category_filter=os.environ.get("EVALS_CATEGORY") or "all",
        case_id_filter=os.environ.get("EVALS_CASE_ID") or "all",
        context_mode=os.environ.get("CONTEXT_MODE") or "database",
        agent_model_id=agent_model_id,
        judge_model_id=judge_model_id,
        tera_mcp_url=os.environ.get("TERA_MCP_URL", ""),
        database=os.environ.get("TERA_DATABASE", "TeraTestingDB"),
        run_label=run_label or os.environ.get("EVALS_RUN_LABEL") or None,
    )


def record_case_result(result: CaseEvalResult) -> None:
    if _report is None:
        return
    _report.results.append(result)


def note_available_tools(names: list[str]) -> None:
    if _report is None or _report.available_tools or not names:
        return
    _report.available_tools = list(names)


def get_current_report() -> EvalRunReport | None:
    return _report


def build_recommendation(
    case: dict,
    *,
    failure_stage: str,
    failure_detail: str | None,
    metric_reasons: list[str],
) -> str:
    """Turn a failure into a short note for the summary."""
    behavior = (case.get("expected_output") or {}).get("expected_behavior", "")
    prompt = case.get("prompt", "")
    if failure_stage == "agent":
        return (
            f"The agent loop failed before scoring: {failure_detail}. "
            "Check TERA_MCP_URL, TERA_BEARER_TOKEN, Bedrock credentials, and BEDROCK_MODEL_ID."
        )
    if failure_stage == "usage":
        return (
            f"This case exceeded AGENT_MAX_TOKENS ({failure_detail}). "
            "Raise the cap or lower AGENT_MAX_STEPS if the task is legitimately long."
        )
    if failure_stage == "deterministic":
        return (
            f"Structural check failed for behavior '{behavior}': {failure_detail}. "
            "Data questions must go through a Tera MCP tool. An empty answer means the loop "
            "stopped before Tera produced a reply."
        )
    return (
        f"The judge scored this below threshold for behavior '{behavior}'. "
        f"Prompt: \"{prompt}\". "
        f"Judge notes: {'; '.join(metric_reasons) or failure_detail or 'metric failed'}. "
        "Compare the Tera answer with the case expected_sql, expected_result, and explanation points."
    )


def _usage_totals(report: EvalRunReport) -> dict[str, float]:
    agent_tokens = 0
    judge_tokens = 0
    elapsed = 0.0
    for result in report.results:
        agent_tokens += int(result.usage.get("total_tokens") or 0)
        judge_tokens += int(result.judge_usage.get("input_tokens") or 0) + int(
            result.judge_usage.get("output_tokens") or 0
        )
        elapsed += float(result.usage.get("elapsed_seconds") or 0)
    return {
        "agent_tokens": agent_tokens,
        "judge_tokens": judge_tokens,
        "elapsed_seconds": elapsed,
        "mean_seconds": elapsed / report.total if report.total else 0,
    }


def render_markdown(report: EvalRunReport) -> str:
    totals = _usage_totals(report)
    lines = [
        "# Tera agent eval run",
        "",
        f"**Started (UTC):** {report.started_at}",
        f"**Persona:** {report.persona_filter}",
        f"**Category:** {report.category_filter}",
        f"**Case:** {report.case_id_filter}",
        f"**Context mode:** {report.context_mode}",
        f"**Agent model:** {report.agent_model_id}",
        f"**Judge model:** {report.judge_model_id}",
        f"**Tera MCP:** {report.tera_mcp_url or '(not set)'}",
        f"**Database:** {report.database}",
    ]
    if report.run_label:
        lines.append(f"**Run label:** {report.run_label}")
    if report.available_tools:
        lines.append("**Tera tools:** " + ", ".join(f"`{name}`" for name in report.available_tools))
    lines.extend(
        [
            "",
            "## Overview",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
            f"| Total cases | {report.total} |",
            f"| Passed | {report.passed_count} |",
            f"| Failed | {report.failed_count} |",
            f"| Agent billed tokens | {int(totals['agent_tokens'])} |",
            f"| Judge billed tokens | {int(totals['judge_tokens'])} |",
            f"| Agent time (s) | {totals['elapsed_seconds']:.1f} |",
            f"| Mean agent time (s) | {totals['mean_seconds']:.1f} |",
            "",
        ]
    )
    lines.append(
        "Agent billed tokens sum every Bedrock call, so multi-step cases count repeated context "
        "once per step. That is the billable total, not the size of the final prompt."
    )
    lines.append("")

    failed = [result for result in report.results if not result.passed]
    passed = [result for result in report.results if result.passed]
    if failed:
        lines.extend(["## Failed cases", ""])
        for result in failed:
            lines.extend(
                [
                    f"### {result.case_id} ({result.persona}, {result.category}, {result.expected_behavior})",
                    "",
                    f"**Description:** {result.description or '—'}",
                    "",
                    "**Prompt:**",
                    "",
                    f"> {result.prompt}",
                    "",
                    f"**Failure ({result.failure_stage or 'unknown'}):** {result.failure_detail or '—'}",
                    "",
                ]
            )
            if result.metric_reasons:
                lines.append("**Judge notes:**")
                lines.append("")
                for reason in result.metric_reasons:
                    lines.append(f"- {reason}")
                lines.append("")
            usage = result.usage or {}
            if usage:
                lines.append(
                    f"**Usage:** {usage.get('total_tokens', 0)} agent tokens, "
                    f"{usage.get('steps', 0)} steps, {usage.get('elapsed_seconds', 0)}s"
                )
                lines.append("")
            if result.tool_calls:
                names = ", ".join(call.get("name", "") for call in result.tool_calls)
                lines.append(f"**Tools called:** {names}")
                lines.append("")
            if result.actual_output:
                excerpt = result.actual_output[:700]
                lines.extend(["**Answer excerpt:**", "", f"> {excerpt}", ""])
            if result.recommendation:
                lines.extend(["**Recommendation:**", "", result.recommendation, ""])
    else:
        lines.extend(["## Failed cases", "", "_None._", ""])

    lines.extend(["## Passed cases", ""])
    if passed:
        for result in passed:
            usage = result.usage or {}
            lines.append(
                f"- `{result.case_id}` ({result.expected_behavior}, "
                f"{usage.get('elapsed_seconds', 0)}s, {usage.get('total_tokens', 0)} tokens)"
            )
    else:
        lines.append("_None._")
    lines.append("")
    return "\n".join(lines)


def _slugify(text: str) -> str:
    slug = re.sub(r"[^\w.-]+", "-", text.strip().lower()).strip("-")
    return slug[:40] if slug else "run"


def build_run_id(report: EvalRunReport) -> str:
    started_at = report.started_at
    if started_at.endswith("+00:00"):
        started_at = f"{started_at[:-6]}Z"
    timestamp = started_at.replace(":", "-")
    parts = [
        timestamp,
        _slugify(report.persona_filter or "all"),
        _slugify(report.category_filter or "all"),
        _slugify(report.context_mode or "database"),
    ]
    if report.case_id_filter and report.case_id_filter != "all":
        parts.append(_slugify(report.case_id_filter))
    if report.run_label:
        parts.append(_slugify(report.run_label))
    return "__".join(parts)


@dataclass
class RunArtifacts:
    run_id: str
    run_dir: Path
    summary_md: Path
    summary_json: Path
    manifest: Path


def _runs_dir() -> Path:
    return RESULTS_DIR / "runs"


def _pointer_path() -> Path:
    return RESULTS_DIR / "latest.json"


def _index_path() -> Path:
    return RESULTS_DIR / "index.json"


def load_latest_pointer() -> dict[str, Any] | None:
    path = _pointer_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def load_run_index() -> list[dict[str, Any]]:
    path = _index_path()
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("runs"), list):
            return [item for item in data["runs"] if isinstance(item, dict)]
    except Exception:
        return []
    return []


def format_run_index(limit: int = 20) -> str:
    runs = load_run_index()[:limit]
    if not runs:
        return "No indexed eval runs yet."
    lines = [
        "Recent eval runs (newest first):",
        "",
        f"{'Run ID':<64} {'Pass':>4} {'Fail':>4}",
        f"{'-' * 64} {'-' * 4} {'-' * 4}",
    ]
    for run in runs:
        run_id = str(run.get("run_id", "?"))[:64]
        lines.append(f"{run_id:<64} {run.get('passed', '?'):>4} {run.get('failed', '?'):>4}")
    lines.extend(["", f"Latest pointer: {_pointer_path()}", f"Full index: {_index_path()}"])
    return "\n".join(lines)


def _summary_payload(report: EvalRunReport) -> dict[str, Any]:
    totals = _usage_totals(report)
    return {
        "run_id": build_run_id(report),
        "started_at": report.started_at,
        "persona_filter": report.persona_filter,
        "category_filter": report.category_filter,
        "case_id_filter": report.case_id_filter,
        "context_mode": report.context_mode,
        "run_label": report.run_label,
        "agent_model_id": report.agent_model_id,
        "judge_model_id": report.judge_model_id,
        "tera_mcp_url": report.tera_mcp_url,
        "database": report.database,
        "available_tools": report.available_tools,
        "total": report.total,
        "passed": report.passed_count,
        "failed": report.failed_count,
        "usage": totals,
        "cases": [asdict(result) for result in report.results],
    }


def _update_index(entry: dict[str, Any]) -> None:
    existing = load_run_index()
    run_id = entry.get("run_id")
    existing = [item for item in existing if item.get("run_id") != run_id]
    runs = [entry, *existing][:MAX_INDEX_RUNS]
    _index_path().write_text(json.dumps({"runs": runs}, indent=2) + "\n", encoding="utf-8")


def write_eval_summary(report: EvalRunReport) -> RunArtifacts:
    """Write results/runs/<run_id>/ and refresh the latest pointer."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    runs_dir = _runs_dir()
    runs_dir.mkdir(parents=True, exist_ok=True)

    run_id = build_run_id(report)
    run_dir = runs_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    summary_md = run_dir / "summary.md"
    summary_json = run_dir / "summary.json"
    manifest = run_dir / "manifest.json"
    markdown = render_markdown(report)
    payload = _summary_payload(report)
    manifest_payload = {
        "run_id": run_id,
        "started_at": report.started_at,
        "persona_filter": report.persona_filter,
        "category_filter": report.category_filter,
        "context_mode": report.context_mode,
        "agent_model_id": report.agent_model_id,
        "judge_model_id": report.judge_model_id,
        "total": report.total,
        "passed": report.passed_count,
        "failed": report.failed_count,
        "artifacts": ["summary.md", "summary.json", "manifest.json"],
    }
    summary_md.write_text(markdown + "\n", encoding="utf-8")
    summary_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    manifest.write_text(json.dumps(manifest_payload, indent=2) + "\n", encoding="utf-8")
    (RESULTS_DIR / "latest_summary.md").write_text(markdown + "\n", encoding="utf-8")
    (RESULTS_DIR / "latest_summary.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    pointer = {
        "run_id": run_id,
        "started_at": report.started_at,
        "run_dir": f"runs/{run_id}",
        "summary_md": f"runs/{run_id}/summary.md",
        "summary_json": f"runs/{run_id}/summary.json",
        "passed": report.passed_count,
        "failed": report.failed_count,
        "total": report.total,
    }
    _pointer_path().write_text(json.dumps(pointer, indent=2) + "\n", encoding="utf-8")
    _update_index(
        {
            "run_id": run_id,
            "started_at": report.started_at,
            "persona_filter": report.persona_filter,
            "category_filter": report.category_filter,
            "context_mode": report.context_mode,
            "passed": report.passed_count,
            "failed": report.failed_count,
            "total": report.total,
            "run_dir": f"runs/{run_id}",
        }
    )
    return RunArtifacts(
        run_id=run_id,
        run_dir=run_dir,
        summary_md=summary_md,
        summary_json=summary_json,
        manifest=manifest,
    )
