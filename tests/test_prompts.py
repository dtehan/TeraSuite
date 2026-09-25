"""Prompt-builder and bearer-header tests. No network calls."""

from __future__ import annotations

import asyncio
import json

import pytest

from agent.client import build_http_client, build_mcp_headers, build_system_prompt, build_user_prompt


def test_api_key_header_adds_prefix(monkeypatch):
    monkeypatch.setenv("TERA_BEARER_TOKEN", "secret-token")
    monkeypatch.delenv("TERA_AUTH_SCHEME", raising=False)
    monkeypatch.delenv("TERA_MCP_EXTRA_HEADERS", raising=False)
    assert build_mcp_headers()["Authorization"] == "ApiKey secret-token"


def test_auth_header_keeps_existing_scheme(monkeypatch):
    monkeypatch.delenv("TERA_MCP_EXTRA_HEADERS", raising=False)
    monkeypatch.setenv("TERA_BEARER_TOKEN", "ApiKey already")
    assert build_mcp_headers()["Authorization"] == "ApiKey already"
    monkeypatch.setenv("TERA_BEARER_TOKEN", "Bearer already")
    assert build_mcp_headers()["Authorization"] == "Bearer already"


def test_extra_headers_do_not_replace_authorization(monkeypatch):
    monkeypatch.setenv("TERA_BEARER_TOKEN", "real-token")
    monkeypatch.delenv("TERA_AUTH_SCHEME", raising=False)
    monkeypatch.setenv("TERA_MCP_EXTRA_HEADERS", '{"Authorization": "nope", "x-team": "evals"}')
    headers = build_mcp_headers()
    assert headers["Authorization"] == "ApiKey real-token"
    assert headers["x-team"] == "evals"


def test_invalid_extra_headers(monkeypatch):
    monkeypatch.setenv("TERA_MCP_EXTRA_HEADERS", "not-json")
    monkeypatch.delenv("TERA_BEARER_TOKEN", raising=False)
    with pytest.raises(json.JSONDecodeError):
        build_mcp_headers()


def test_http_client_carries_bearer(monkeypatch):
    monkeypatch.setenv("TERA_BEARER_TOKEN", "secret-token")
    monkeypatch.delenv("TERA_AUTH_SCHEME", raising=False)
    monkeypatch.delenv("TERA_MCP_EXTRA_HEADERS", raising=False)
    client = build_http_client()

    async def _close():
        try:
            assert client.headers["authorization"] == "ApiKey secret-token"
        finally:
            await client.aclose()

    asyncio.run(_close())


def test_user_prompt_modes_hide_the_answer():
    prompt = "How many orders?"
    assert (
        build_user_prompt(prompt, context_mode="minimal", database="TeraTestingDB", requires_tables=["Orders"])
        == prompt
    )
    database_prompt = build_user_prompt(
        prompt, context_mode="database", database="TeraTestingDB", requires_tables=["Orders"]
    )
    assert "TeraTestingDB" in database_prompt
    assert "Orders" not in database_prompt
    tables_prompt = build_user_prompt(
        prompt, context_mode="tables", database="TeraTestingDB", requires_tables=["Orders", "OrderLine"]
    )
    assert "Orders" in tables_prompt
    assert "OrderLine" in tables_prompt
    assert "SELECT" not in tables_prompt
    assert "expected_sql" not in build_system_prompt("tables", "TeraTestingDB")


def test_minimal_system_prompt_omits_database():
    assert "TeraTestingDB" not in build_system_prompt("minimal", "TeraTestingDB")
    assert "TeraTestingDB" in build_system_prompt("database", "TeraTestingDB")
