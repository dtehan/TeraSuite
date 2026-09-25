"""Bedrock agent that answers eval prompts by calling the Tera MCP server."""

from __future__ import annotations

import asyncio
import json
import os
import re
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any

import httpx2
from mcp import Client
from mcp.client.streamable_http import streamable_http_client
from mcp.shared._httpx_utils import create_mcp_http_client
from mcp_types import Implementation

from agent.bedrock import converse_with_retry, make_bedrock_client

_TOOL_NAME = re.compile(r"[^0-9A-Za-z_-]")
_SCHEMA_DROP = {"$schema", "$id", "additionalProperties", "unevaluatedProperties"}


@dataclass
class ToolCallRecord:
    name: str
    input_parameters: dict[str, Any]
    result_preview: str = ""


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    elapsed_seconds: float = 0.0
    steps: int = 0


@dataclass
class AgentResult:
    tool_calls: list[ToolCallRecord] = field(default_factory=list)
    final_response: str = ""
    usage: Usage = field(default_factory=Usage)
    available_tools: list[str] = field(default_factory=list)
    hit_step_limit: bool = False


def build_mcp_headers() -> dict[str, str]:
    """Authorization header for the Tera gateway, plus any extra headers from the env."""
    headers: dict[str, str] = {}
    extra = os.environ.get("TERA_MCP_EXTRA_HEADERS", "").strip()
    if extra:
        parsed = json.loads(extra)
        if not isinstance(parsed, dict):
            raise ValueError("TERA_MCP_EXTRA_HEADERS must be a JSON object")
        headers.update({str(key): str(value) for key, value in parsed.items()})

    token = os.environ.get("TERA_BEARER_TOKEN", "").strip()
    if token:
        # Claude Desktop sends "Authorization: ApiKey <token>". A value that
        # already includes ApiKey or Bearer is sent unchanged.
        if token.lower().startswith(("apikey ", "bearer ")):
            headers["Authorization"] = token
        else:
            scheme = os.environ.get("TERA_AUTH_SCHEME", "ApiKey").strip() or "ApiKey"
            headers["Authorization"] = f"{scheme} {token}"
    return headers


def build_http_client() -> httpx2.AsyncClient:
    """HTTP client whose default headers carry the Tera bearer token."""
    timeout = httpx2.Timeout(
        float(os.environ.get("TERA_MCP_TIMEOUT", "60")),
        read=float(os.environ.get("TERA_MCP_SSE_TIMEOUT", "300")),
    )
    headers = build_mcp_headers()
    verify = os.environ.get("TERA_MCP_VERIFY_SSL", "1").lower() not in {"0", "false", "no"}
    if verify:
        return create_mcp_http_client(headers=headers, timeout=timeout)
    return httpx2.AsyncClient(headers=headers, timeout=timeout, verify=False)


def build_system_prompt(context_mode: str, database: str) -> str:
    """Instructions for the local model. Schema hints depend on the context mode."""
    if context_mode not in {"minimal", "database", "tables"}:
        raise ValueError(f"unknown context mode {context_mode!r}")
    lines = [
        "You are the local driver for the Teradata Tera agent.",
        "Tera is available only through the MCP tools in this conversation.",
        "Answer the user by calling those tools, then relay Tera's answer, including any SQL and rows it returns.",
        "Use read-only tools. Relay a clarifying question or a refusal when that is what Tera returns.",
        "Keep the final answer grounded in tool results.",
    ]
    if context_mode in {"database", "tables"}:
        lines.append(f"The Teradata database name is {database}.")
    return "\n".join(lines)


def build_user_prompt(
    prompt: str,
    *,
    context_mode: str,
    database: str,
    requires_tables: list[str],
) -> str:
    """User message sent to the local agent. The expected answer is never included."""
    if context_mode == "minimal":
        return prompt
    if context_mode == "database":
        return f"Database: {database}\n\n{prompt}"
    if context_mode == "tables":
        tables = ", ".join(requires_tables) if requires_tables else "(none listed)"
        return f"Database: {database}\nRelevant tables: {tables}\n\n{prompt}"
    raise ValueError(f"unknown context mode {context_mode!r}")


def _clean_schema(node: Any) -> Any:
    if isinstance(node, dict):
        return {key: _clean_schema(value) for key, value in node.items() if key not in _SCHEMA_DROP}
    if isinstance(node, list):
        return [_clean_schema(item) for item in node]
    return node


def _tool_input_schema(tool) -> dict[str, Any]:
    raw = getattr(tool, "input_schema", None)
    if raw is None:
        raw = getattr(tool, "inputSchema", None)
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump(mode="json", exclude_none=True)
    if not isinstance(raw, dict):
        raw = {}
    schema = _clean_schema(raw)
    if schema.get("type") != "object":
        schema["type"] = "object"
    schema.setdefault("properties", {})
    return schema


def _bedrock_tools(tools: list) -> tuple[list[dict], dict[str, str]]:
    used: set[str] = set()
    mapping: dict[str, str] = {}
    specs: list[dict] = []
    for tool in tools:
        original = tool.name
        sanitized = _TOOL_NAME.sub("_", original)[:64] or "tool"
        base = sanitized
        suffix_n = 2
        while sanitized in used:
            suffix = f"_{suffix_n}"
            sanitized = base[: 64 - len(suffix)] + suffix
            suffix_n += 1
        used.add(sanitized)
        mapping[sanitized] = original
        description = (getattr(tool, "description", None) or "Tera MCP tool").strip()[:1024]
        specs.append(
            {
                "toolSpec": {
                    "name": sanitized,
                    "description": description,
                    "inputSchema": {"json": _tool_input_schema(tool)},
                }
            }
        )
    return specs, mapping


def _extract_text(content_blocks: list[dict]) -> str:
    parts: list[str] = []
    for block in content_blocks:
        if isinstance(block, dict) and block.get("text"):
            parts.append(block["text"])
    return "".join(parts)


def _iter_tool_uses(content_blocks: list[dict]):
    for block in content_blocks:
        if not isinstance(block, dict) or "toolUse" not in block:
            continue
        tool_use = block["toolUse"]
        yield tool_use["name"], tool_use.get("input") or {}, tool_use["toolUseId"]


def _result_text(mcp_result) -> str:
    chunks: list[str] = []
    if getattr(mcp_result, "is_error", False):
        chunks.append("Tool error")
    for block in getattr(mcp_result, "content", None) or []:
        text = getattr(block, "text", None)
        if text:
            chunks.append(text)
        elif hasattr(block, "model_dump"):
            chunks.append(json.dumps(block.model_dump(mode="json", exclude_none=True), default=str))
        else:
            chunks.append(str(block))
    structured = getattr(mcp_result, "structured_content", None)
    if structured:
        chunks.append(json.dumps(structured, default=str))
    return "\n".join(chunks)


def _require_setting(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not set. Add it to .env (see .env.example).")
    return value


@asynccontextmanager
async def _tera_client():
    url = _require_setting("TERA_MCP_URL")
    if not os.environ.get("TERA_BEARER_TOKEN", "").strip():
        raise RuntimeError("TERA_BEARER_TOKEN is not set. Add it to .env (see .env.example).")
    http_client = build_http_client()
    transport = streamable_http_client(url, http_client=http_client)
    mode = os.environ.get("TERA_MCP_MODE", "legacy").strip() or "legacy"
    read_timeout = float(os.environ.get("TERA_MCP_SSE_TIMEOUT", "300"))
    async with http_client:
        async with Client(
            transport,
            read_timeout_seconds=read_timeout,
            mode=mode,
            cache=None,
            client_info=Implementation(name="tera-agent-evals", version="0.1.0"),
        ) as tera:
            yield tera


async def _list_all_tools(tera: Client) -> list:
    tools = []
    cursor = None
    while True:
        page = await tera.list_tools(cursor=cursor) if cursor else await tera.list_tools()
        tools.extend(page.tools)
        cursor = page.next_cursor
        if not cursor:
            return tools


def _truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n... [truncated]"


async def _run_agent_async(
    *,
    prompt: str,
    model_id: str,
    bedrock_client,
    context_mode: str,
    database: str,
    requires_tables: list[str],
    max_steps: int,
) -> AgentResult:
    started = time.perf_counter()
    usage = Usage()
    system_prompt = build_system_prompt(context_mode, database)
    user_prompt = build_user_prompt(
        prompt,
        context_mode=context_mode,
        database=database,
        requires_tables=requires_tables,
    )
    max_output = int(os.environ.get("AGENT_MAX_OUTPUT_TOKENS", "4096"))
    temperature = float(os.environ.get("AGENT_TEMPERATURE", "0"))
    result_limit = int(os.environ.get("MAX_TOOL_RESULT_CHARS", "8000"))

    async with _tera_client() as tera:
        instructions = (getattr(tera, "instructions", None) or "").strip()
        if instructions:
            system_prompt += "\n\nTera server instructions:\n" + _truncate(instructions, 6000)
        tools = await _list_all_tools(tera)
        bedrock_tools, name_map = _bedrock_tools(tools)
        available = [tool.name for tool in tools]
        messages: list[dict] = [{"role": "user", "content": [{"text": user_prompt}]}]
        tool_calls: list[ToolCallRecord] = []
        final_response = ""
        hit_step_limit = False

        for _ in range(max_steps):
            kwargs: dict[str, Any] = {
                "modelId": model_id,
                "system": [{"text": system_prompt}],
                "messages": messages,
                "inferenceConfig": {"maxTokens": max_output, "temperature": temperature},
            }
            if bedrock_tools:
                kwargs["toolConfig"] = {"tools": bedrock_tools, "toolChoice": {"auto": {}}}
            response = await asyncio.to_thread(converse_with_retry, bedrock_client, **kwargs)
            step_usage = response.get("usage") or {}
            usage.input_tokens += int(step_usage.get("inputTokens") or 0)
            usage.output_tokens += int(step_usage.get("outputTokens") or 0)
            usage.steps += 1

            stop_reason = response.get("stopReason", "")
            output_message = response["output"]["message"]
            messages.append(output_message)
            content = output_message.get("content", [])

            if stop_reason == "tool_use":
                tool_results = []
                for tool_name, tool_input, tool_use_id in _iter_tool_uses(content):
                    if isinstance(tool_input, str):
                        try:
                            tool_input = json.loads(tool_input)
                        except json.JSONDecodeError:
                            tool_input = {"value": tool_input}
                    if not isinstance(tool_input, dict):
                        tool_input = {"value": tool_input}
                    original_name = name_map.get(tool_name, tool_name)
                    try:
                        mcp_result = await tera.call_tool(original_name, tool_input)
                        result_text = _result_text(mcp_result)
                    except Exception as exc:
                        result_text = f"Tool error: {exc}"
                    preview = _truncate(result_text, result_limit)
                    tool_calls.append(
                        ToolCallRecord(
                            name=original_name,
                            input_parameters=tool_input,
                            result_preview=preview,
                        )
                    )
                    tool_results.append(
                        {
                            "toolResult": {
                                "toolUseId": tool_use_id,
                                "content": [{"text": preview}],
                            }
                        }
                    )
                if not tool_results:
                    final_response = _extract_text(content)
                    break
                messages.append({"role": "user", "content": tool_results})
                continue

            final_response = _extract_text(content)
            break
        else:
            hit_step_limit = True

    usage.total_tokens = usage.input_tokens + usage.output_tokens
    usage.elapsed_seconds = round(time.perf_counter() - started, 3)
    return AgentResult(
        tool_calls=tool_calls,
        final_response=final_response,
        usage=usage,
        available_tools=available,
        hit_step_limit=hit_step_limit,
    )


def run_agent(
    prompt: str,
    *,
    model_id: str | None = None,
    bedrock_client=None,
    context_mode: str | None = None,
    database: str | None = None,
    requires_tables: list[str] | None = None,
    max_steps: int | None = None,
) -> AgentResult:
    """Run one eval prompt through Bedrock and the Tera MCP endpoint."""
    resolved_model = model_id or os.environ.get("BEDROCK_MODEL_ID", "").strip()
    if not resolved_model:
        raise RuntimeError("BEDROCK_MODEL_ID is not set. Add it to .env (see .env.example).")
    if bedrock_client is None:
        bedrock_client = make_bedrock_client()
    resolved_mode = context_mode or os.environ.get("CONTEXT_MODE", "database")
    resolved_db = database or os.environ.get("TERA_DATABASE", "TeraTestingDB")
    resolved_steps = max_steps or int(os.environ.get("AGENT_MAX_STEPS", "8"))
    return asyncio.run(
        _run_agent_async(
            prompt=prompt,
            model_id=resolved_model,
            bedrock_client=bedrock_client,
            context_mode=resolved_mode,
            database=resolved_db,
            requires_tables=requires_tables or [],
            max_steps=resolved_steps,
        )
    )


def list_tera_tools() -> list[dict[str, str]]:
    """Connect to Tera and return the tool name and description of each tool."""

    async def _list() -> list[dict[str, str]]:
        async with _tera_client() as tera:
            tools = await _list_all_tools(tera)
            return [{"name": tool.name, "description": (tool.description or "").strip()} for tool in tools]

    return asyncio.run(_list())
