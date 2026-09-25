"""Summary files land under the configured results directory."""

from judge.report import (
    CaseEvalResult,
    begin_eval_run,
    format_run_index,
    get_current_report,
    record_case_result,
    write_eval_summary,
)


def test_write_eval_summary(tmp_path, monkeypatch):
    import judge.report as report

    monkeypatch.setattr(report, "RESULTS_DIR", tmp_path)
    begin_eval_run(agent_model_id="agent-model", judge_model_id="judge-model")
    record_case_result(
        CaseEvalResult(
            case_id="BU-001",
            persona="business_user",
            category="typical",
            description="Revenue.",
            prompt="How much?",
            expected_behavior="return_data",
            passed=False,
            failure_stage="metric",
            failure_detail="Behavior: missed February",
            metric_reasons=["Behavior: missed February"],
            recommendation="Compare the answer with the reference SQL.",
            usage={"total_tokens": 100, "elapsed_seconds": 2.5, "steps": 2},
            judge_usage={"input_tokens": 40, "output_tokens": 10},
        )
    )
    record_case_result(
        CaseEvalResult(
            case_id="BU-002",
            persona="business_user",
            category="typical",
            description="Customers.",
            prompt="Top customers?",
            expected_behavior="return_data",
            passed=True,
            usage={"total_tokens": 50, "elapsed_seconds": 1.0, "steps": 1},
        )
    )
    artifacts = write_eval_summary(get_current_report())
    text = artifacts.summary_md.read_text(encoding="utf-8")
    assert "BU-001" in text
    assert "missed February" in text
    assert "Agent billed tokens" in text
    assert (tmp_path / "latest_summary.md").exists()
    assert artifacts.run_id in format_run_index()
