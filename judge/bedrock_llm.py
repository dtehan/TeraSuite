"""DeepEval LLM wrapper backed by Amazon Bedrock (Converse API)."""

from __future__ import annotations

import asyncio
import os
from typing import Any

from deepeval.models.base_model import DeepEvalBaseLLM

from agent.bedrock import converse_with_retry, make_bedrock_client


class BedrockLLM(DeepEvalBaseLLM):
    """Anthropic Claude on Bedrock, used as the deepeval judge."""

    def __init__(self, model_id: str | None = None, bedrock_client=None):
        self.model_id = model_id or os.environ.get("BEDROCK_JUDGE_MODEL_ID") or os.environ.get(
            "BEDROCK_MODEL_ID", ""
        )
        self._client = bedrock_client or self._build_client()
        self.input_tokens = 0
        self.output_tokens = 0
        super().__init__(model=self.model_id or "bedrock-judge")

    def _build_client(self):
        judge_endpoint = os.environ.get("BEDROCK_JUDGE_ENDPOINT_URL", "").strip()
        return make_bedrock_client(
            region=os.environ.get("BEDROCK_JUDGE_REGION") or None,
            endpoint_url=judge_endpoint or None,
        )

    def load_model(self):
        return self._client

    def get_model_name(self) -> str:
        return self.model_id or "bedrock-judge"

    def _complete(self, prompt: str, schema: Any = None) -> Any:
        if not self.model_id:
            raise RuntimeError("BEDROCK_MODEL_ID or BEDROCK_JUDGE_MODEL_ID is not set.")
        response = converse_with_retry(
            self._client,
            modelId=self.model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={
                "maxTokens": int(os.environ.get("JUDGE_MAX_OUTPUT_TOKENS", "2048")),
                "temperature": 0,
            },
        )
        usage = response.get("usage") or {}
        self.input_tokens += int(usage.get("inputTokens") or 0)
        self.output_tokens += int(usage.get("outputTokens") or 0)
        blocks = response["output"]["message"]["content"]
        text = "".join(block.get("text", "") for block in blocks if isinstance(block, dict))
        if schema is None:
            return text
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return schema.model_validate_json(text[start:end])
        except Exception:
            return text

    def generate(self, prompt: str, schema: Any = None) -> Any:
        return self._complete(prompt, schema)

    async def a_generate(self, prompt: str, schema: Any = None) -> Any:
        return await asyncio.to_thread(self._complete, prompt, schema)
