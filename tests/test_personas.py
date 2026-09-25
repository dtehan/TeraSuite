"""Live eval entry. Collected cases follow EVALS_* filters set by run_evals.py."""

from __future__ import annotations

import pytest

from tests.case_loader import load_all_cases
from tests.conftest import assert_eval_case


def _selected_cases():
    cases = load_all_cases()
    if cases:
        return cases
    return [
        pytest.param(
            {"id": "NO-CASES"},
            marks=pytest.mark.skip(reason="no eval cases matched EVALS_PERSONA / EVALS_CATEGORY / EVALS_CASE_ID"),
        )
    ]


@pytest.mark.live
@pytest.mark.parametrize("case", _selected_cases(), ids=lambda case: case["id"])
def test_eval_case(case, bedrock_client, agent_model_id, judge_llm):
    assert_eval_case(case, bedrock_client, agent_model_id, judge_llm)
