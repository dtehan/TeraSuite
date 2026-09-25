"""Fixtures for live Tera evals. Unit tests skip anything marked live."""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "1")


def assert_eval_case(case: dict, bedrock_client, agent_model_id: str, judge_llm) -> None:
    from tests.case_runner import assert_eval_case as _assert_eval_case

    _assert_eval_case(case, bedrock_client, agent_model_id, judge_llm)


@pytest.fixture(scope="session")
def bedrock_client():
    from agent.bedrock import make_bedrock_client

    return make_bedrock_client()


@pytest.fixture(scope="session")
def agent_model_id() -> str:
    return os.environ.get("BEDROCK_MODEL_ID", "")


@pytest.fixture(scope="session")
def judge_llm():
    from judge.bedrock_llm import BedrockLLM

    return BedrockLLM()


def pytest_sessionstart(session) -> None:
    if os.environ.get("EVALS_LIVE") != "1":
        return
    from judge.report import begin_eval_run

    agent_model = os.environ.get("BEDROCK_MODEL_ID", "")
    judge_model = os.environ.get("BEDROCK_JUDGE_MODEL_ID") or agent_model
    begin_eval_run(agent_model_id=agent_model, judge_model_id=judge_model)


def pytest_sessionfinish(session, exitstatus) -> None:
    if os.environ.get("EVALS_LIVE") != "1":
        return
    from judge.report import get_current_report, write_eval_summary

    report = get_current_report()
    if report is None or not report.results:
        return
    artifacts = write_eval_summary(report)
    terminal = session.config.pluginmanager.get_plugin("terminalreporter")
    if terminal is not None:
        terminal.write_line("")
        terminal.write_line(f"Eval run: {artifacts.run_id}")
        terminal.write_line(f"Summary: results/latest_summary.md")
