"""Shared Amazon Bedrock runtime helpers for the agent and the judge."""

from __future__ import annotations

import os
import time
from typing import Any

import boto3
from botocore.exceptions import ClientError

RETRYABLE_CODES = frozenset(
    {
        "ThrottlingException",
        "TooManyRequestsException",
        "ServiceUnavailableException",
        "ModelTimeoutException",
        "ModelNotReadyException",
    }
)


def make_bedrock_client(*, region: str | None = None, endpoint_url: str | None = None):
    """Build a bedrock-runtime client from the standard boto3 credential chain."""
    resolved_region = region or os.environ.get("AWS_REGION", "us-east-1")
    kwargs: dict[str, Any] = {"region_name": resolved_region}
    resolved_endpoint = (endpoint_url if endpoint_url is not None else os.environ.get("BEDROCK_ENDPOINT_URL", "")).strip()
    if resolved_endpoint:
        kwargs["endpoint_url"] = resolved_endpoint
    return boto3.client("bedrock-runtime", **kwargs)


def converse_with_retry(client, /, **kwargs):
    """Call Converse, backing off when Bedrock throttles."""
    delay = 2.0
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            return client.converse(**kwargs)
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "")
            last_error = exc
            if code not in RETRYABLE_CODES or attempt == 4:
                raise
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("Bedrock converse failed") from last_error
