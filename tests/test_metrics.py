"""Metric selection does not call Bedrock."""

from deepeval.models.base_model import DeepEvalBaseLLM

from judge.metrics import get_metrics


class FakeJudge(DeepEvalBaseLLM):
    def __init__(self):
        super().__init__(model="fake-judge")

    def load_model(self):
        return self

    def generate(self, *args, **kwargs) -> str:
        return ""

    async def a_generate(self, *args, **kwargs) -> str:
        return ""

    def get_model_name(self) -> str:
        return "fake-judge"


def test_metrics_follow_expected_output_fields():
    judge = FakeJudge()
    full = get_metrics(
        {
            "expected_output": {
                "expected_behavior": "return_data",
                "expected_sql": "SELECT 1",
                "expected_result": {"columns": ["n"], "row_count": 1},
                "expected_explanation_points": ["one row"],
            }
        },
        judge,
    )
    assert [metric.name for metric in full] == [
        "Behavior",
        "SQL Equivalence",
        "Result Shape",
        "Explanation Points",
    ]
    refusal = get_metrics(
        {
            "expected_output": {
                "expected_behavior": "refuse_or_flag_permission",
                "expected_explanation_points": ["refuse"],
            }
        },
        judge,
    )
    assert [metric.name for metric in refusal] == ["Behavior", "Explanation Points"]
