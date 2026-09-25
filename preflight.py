"""Check local settings and the Tera MCP endpoint before a live run."""

from __future__ import annotations

import os
import sys

from dotenv import load_dotenv


def _missing(*names: str) -> list[str]:
    return [name for name in names if not os.environ.get(name, "").strip()]


def _require(*names: str) -> None:
    missing = _missing(*names)
    if not missing:
        return
    print("Missing environment variables: " + ", ".join(missing), file=sys.stderr)
    print("Copy .env.example to .env and fill in the bearer token and Bedrock settings.", file=sys.stderr)
    raise SystemExit(2)


def print_tera_tools() -> None:
    """Connect with the bearer token and print the tools Tera publishes."""
    load_dotenv()
    _require("TERA_MCP_URL", "TERA_BEARER_TOKEN")
    from agent.client import list_tera_tools

    try:
        tools = list_tera_tools()
    except Exception as exc:
        print(f"Could not list tools on the Tera MCP endpoint: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if not tools:
        print("Tera MCP connected but published no tools.", file=sys.stderr)
        raise SystemExit(1)
    print(f"Tera MCP tools ({len(tools)}):")
    for tool in tools:
        description = tool["description"].splitlines()[0] if tool["description"] else ""
        suffix = f": {description}" if description else ""
        print(f"  - {tool['name']}{suffix}")


def run_preflight() -> None:
    """Check Bedrock settings, then list Tera tools."""
    load_dotenv()
    _require("TERA_MCP_URL", "TERA_BEARER_TOKEN", "BEDROCK_MODEL_ID")

    import boto3

    if boto3.Session().get_credentials() is None:
        print(
            "No AWS credentials found for Bedrock. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY, "
            "AWS_BEARER_TOKEN_BEDROCK, or a profile in the boto3 credential chain.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    print_tera_tools()


if __name__ == "__main__":
    run_preflight()
