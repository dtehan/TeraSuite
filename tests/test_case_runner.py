"""The case runner stops before the judge on structural and budget failures."""

from agent.client import AgentResult, ToolCallRecord, Usage
from tests.case_runner import run_eval_case


def _case(behavior: str = "return_data") -> dict:
    return {
        "id": "BU-001",
        "name": "revenue",
        "persona": "business_user",
        "category": "typical",
        "description": "Revenue question.",
        "prompt": "How much revenue?",
        "requires_tables": ["Orders"],
        "expected_output": {
            "expected_behavior": behavior,
            "expected_sql": "SELECT 1",
        },
    }


def _agent_result(*, response: str, tools: bool, tokens: int = 20) -> AgentResult:
    calls = []
    if tools:
        calls.append(ToolCallRecord(name="query", input_parameters={"sql": "SELECT 1"}, result_preview="1"))
    return AgentResult(
        tool_calls=calls,
        final_response=response,
        usage=Usage(input_tokens=tokens, output_tokens=0, total_tokens=tokens, elapsed_seconds=1.2, steps=1),
        available_tools=["query"],
    )


def test_missing_tool_call_skips_the_judge(monkeypatch):
    monkeypatch.setattr(
        "tests.case_runner.run_agent",
        lambda *args, **kwargs: _agent_result(response="about 10", tools=False),
    )

    def _boom(*args, **kwargs):
        raise AssertionError("judge should not run")

    monkeypatch.setattr("tests.case_runner.get_metrics", _boom)
    result = run_eval_case(_case(), bedrock_client=None, agent_model_id="model", judge_llm=object())
    assert result.passed is False
    assert result.failure_stage == "deterministic"


def test_token_cap_skips_the_judge(monkeypatch):
    monkeypatch.setenv("AGENT_MAX_TOKENS", "10")
    monkeypatch.setattr(
        "tests.case_runner.run_agent",
        lambda *args, **kwargs: _agent_result(response="10", tools=True, tokens=50),
    )

    def _boom(*args, **kwargs):
        raise AssertionError("judge should not run")

    monkeypatch.setattr("tests.case_runner.get_metrics", _boom)
    result = run_eval_case(_case(), bedrock_client=None, agent_model_id="model", judge_llm=object())
    assert result.failure_stage == "usage"
    assert result.usage["total_tokens"] == 50


def test_step_limit_skips_the_judge(monkeypatch):
    stopped = _agent_result(response="", tools=True)
    stopped.hit_step_limit = True
    monkeypatch.setattr("tests.case_runner.run_agent", lambda *args, **kwargs: stopped)

    def _boom(*args, **kwargs):
        raise AssertionError("judge should not run")

    monkeypatch.setattr("tests.case_runner.get_metrics", _boom)
    result = run_eval_case(_case(), bedrock_client=None, agent_model_id="model", judge_llm=object())
    assert result.failure_stage == "deterministic"
    assert "AGENT_MAX_STEPS" in (result.failure_detail or "")


def test_passing_metric_records_usage(monkeypatch):
    monkeypatch.delenv("AGENT_MAX_TOKENS", raising=False)
    monkeypatch.setattr(
        "tests.case_runner.run_agent",
        lambda *args, **kwargs: _agent_result(response="10", tools=True),
    )

    class _Metric:
        name = "Behavior"
        success = True
        reason = "matches"
        score = 1.0

        def measure(self, test_case):
            return 1.0

    monkeypatch.setattr("tests.case_runner.get_metrics", lambda case, judge: [_Metric()])
    result = run_eval_case(_case(), bedrock_client=None, agent_model_id="model", judge_llm=object())
    assert result.passed is True
    assert result.metric_scores[0]["score"] == 1.0
    assert result.usage["elapsed_seconds"] == 1.2
    assert "SELECT 1" in (result.actual_output or "")


def test_agent_exception_is_a_failure(monkeypatch):
    def _explode(*args, **kwargs):
        raise RuntimeError("TERA_BEARER_TOKEN is not set")

    monkeypatch.setattr("tests.case_runner.run_agent", _explode)
    result = run_eval_case(_case("ask_clarifying_question"), bedrock_client=None, agent_model_id="m", judge_llm=object())
    assert result.failure_stage == "agent"
    assert "TERA_BEARER_TOKEN" in (result.failure_detail or "")
