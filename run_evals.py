"""
Run the YAML eval suites against the Teradata Tera agent.

Examples:
    uv run python run_evals.py --list-cases
    uv run python run_evals.py --list-tools
    uv run python run_evals.py --persona business_user --case BU-001
    uv run python run_evals.py --category edge --limit 5
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv

from judge.report import format_run_index, load_latest_pointer
from tests.case_loader import load_all_cases, persona_names

CONTEXT_MODES = ("minimal", "database", "tables")
CATEGORIES = ("typical", "edge")


def _print_cases(cases: list[dict]) -> None:
    print(f"{'ID':<12} {'Persona':<22} {'Category':<10} Behavior")
    for case in cases:
        behavior = (case.get("expected_output") or {}).get("expected_behavior", "")
        print(f"{case['id']:<12} {case['persona']:<22} {case['category']:<10} {behavior}")
    print(f"\n{len(cases)} case(s)")


def _selected(args: argparse.Namespace) -> list[dict]:
    return load_all_cases(
        persona=args.persona,
        category=args.category,
        case_id=args.case,
        limit=args.limit,
        apply_env=False,
    )


def main() -> None:
    load_dotenv()
    os.environ.setdefault("DEEPEVAL_TELEMETRY_OPT_OUT", "1")

    parser = argparse.ArgumentParser(description="Run Tera agent evals with deepeval")
    parser.add_argument("--persona", choices=persona_names(), help="Run one persona file")
    parser.add_argument("--category", choices=CATEGORIES, help="Run typical or edge cases")
    parser.add_argument("--case", help="Run a single case id, for example BU-001")
    parser.add_argument("--limit", type=int, help="Run at most this many cases after filtering")
    parser.add_argument(
        "--context",
        choices=CONTEXT_MODES,
        default=os.environ.get("CONTEXT_MODE", "database"),
        help="How much schema context the local agent sees (default: database)",
    )
    parser.add_argument("--run-label", help="Suffix added to the results directory name")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose pytest output")
    parser.add_argument("--skip-preflight", action="store_true", help="Skip the Tera MCP and Bedrock check")
    parser.add_argument("--list-cases", action="store_true", help="Print the cases that match the filters and exit")
    parser.add_argument("--list-tools", action="store_true", help="Connect to Tera and print its MCP tools")
    parser.add_argument("--list-runs", action="store_true", help="List recent eval runs and exit")
    args = parser.parse_args()

    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")

    if args.list_runs:
        print(format_run_index())
        pointer = load_latest_pointer()
        if pointer:
            print("")
            print(f"Latest run: {pointer.get('run_id')}")
            print(f"Summary: results/{pointer.get('summary_md')}")
        sys.exit(0)

    if args.list_cases:
        cases = _selected(args)
        if not cases:
            print("No cases matched those filters.", file=sys.stderr)
            sys.exit(2)
        _print_cases(cases)
        sys.exit(0)

    if args.list_tools:
        from preflight import print_tera_tools

        print_tera_tools()
        sys.exit(0)

    cases = _selected(args)
    if not cases:
        print("No cases matched those filters.", file=sys.stderr)
        sys.exit(2)

    if not args.skip_preflight:
        from preflight import run_preflight

        run_preflight()

    os.environ["EVALS_LIVE"] = "1"
    os.environ["CONTEXT_MODE"] = args.context
    if args.persona:
        os.environ["EVALS_PERSONA"] = args.persona
    else:
        os.environ.pop("EVALS_PERSONA", None)
    if args.category:
        os.environ["EVALS_CATEGORY"] = args.category
    else:
        os.environ.pop("EVALS_CATEGORY", None)
    if args.case:
        os.environ["EVALS_CASE_ID"] = args.case
    else:
        os.environ.pop("EVALS_CASE_ID", None)
    if args.limit is not None:
        os.environ["EVALS_LIMIT"] = str(args.limit)
    else:
        os.environ.pop("EVALS_LIMIT", None)
    if args.run_label:
        os.environ["EVALS_RUN_LABEL"] = args.run_label
    else:
        os.environ.pop("EVALS_RUN_LABEL", None)

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_personas.py",
        "-m",
        "live",
        "-o",
        "addopts=",
        "--tb=short",
    ]
    if args.verbose:
        cmd.append("-vv")
    print(f"Running {len(cases)} case(s) with context mode {args.context}")
    print(f"Command: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    if result.returncode in {0, 1}:
        pointer = load_latest_pointer()
        if pointer:
            print("")
            print(f"Eval run: {pointer.get('run_id')}")
            print(f"Summary: results/{pointer.get('summary_md')}")
            print("Latest copy: results/latest_summary.md")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
