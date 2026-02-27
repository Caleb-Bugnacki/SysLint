#!/usr/bin/env python3
"""SysLint — SysML v2 Linter CLI.

Usage:
    syslint.py [options] FILE [FILE ...]

Options:
    --format  text|json          Output format (default: text)
    --rules   R1,R2,...          Only emit diagnostics for these rule IDs
    --min-severity  error|warning|info
                                 Minimum severity to report (default: info)
    --no-color                   Disable ANSI colour output
    -h, --help                   Show this help and exit

Exit codes:
    0  No issues found
    1  Warnings (or info) found but no errors
    2  Errors found
"""
from __future__ import annotations
import argparse
import os
import sys

# Allow running as  python src/syslint.py  from the project root
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from linter.lexer import Lexer
from linter.parser import Parser
from linter.checker import check_file
from linter.diagnostic import Severity
from linter.reporter import Reporter


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="syslint",
        description="SysML v2 linter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="SysML v2 source files to lint")
    p.add_argument(
        "--format", dest="fmt", choices=("text", "json"), default="text",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--rules", dest="rules", default=None,
        help="Comma-separated rule IDs to enable (e.g. W001,W010). Default: all",
    )
    p.add_argument(
        "--min-severity", dest="min_severity",
        choices=("error", "warning", "info"), default="info",
        help="Minimum severity level to report (default: info)",
    )
    p.add_argument(
        "--no-color", dest="no_color", action="store_true",
        help="Disable ANSI colour output",
    )
    return p.parse_args()


def _lint_file(path: str, rule_ids: set[str] | None) -> list:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            source = fh.read()
    except OSError as exc:
        print(f"syslint: cannot read '{path}': {exc}", file=sys.stderr)
        return []

    tokens = Lexer(source).tokenize()
    ast = Parser(tokens, filename=path).parse()
    return check_file(ast, rule_ids=rule_ids)


def main() -> int:
    args = _parse_args()

    rule_ids: set[str] | None = None
    if args.rules:
        rule_ids = {r.strip() for r in args.rules.split(",")}

    min_order = {"error": 0, "warning": 1, "info": 2}[args.min_severity]

    reporter = Reporter(
        fmt=args.fmt,
        color=not args.no_color,
        stream=sys.stdout,
    )

    all_diags = []
    for path in args.files:
        diags = _lint_file(path, rule_ids)
        # Filter by minimum severity
        diags = [d for d in diags if d.severity.order <= min_order]
        all_diags.extend(diags)

    reporter.report(all_diags)

    if args.fmt == "text":
        print()
        reporter.summary(all_diags)

    has_errors = any(d.severity == Severity.ERROR for d in all_diags)
    has_warnings_or_info = bool(all_diags)

    if has_errors:
        return 2
    if has_warnings_or_info:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
