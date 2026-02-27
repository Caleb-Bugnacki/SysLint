"""Diagnostic reporter — formats and prints linting results."""
from __future__ import annotations
import json
import sys
from typing import TextIO

from .diagnostic import Diagnostic, Severity

# ANSI colour codes (disabled when not a TTY or --no-color is set)
_RESET = "\033[0m"
_BOLD = "\033[1m"
_RED = "\033[31m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"
_DIM = "\033[2m"

_SEV_COLOUR = {
    Severity.ERROR: _RED,
    Severity.WARNING: _YELLOW,
    Severity.INFO: _CYAN,
}


class Reporter:
    def __init__(self, fmt: str = "text", color: bool = True, stream: TextIO = sys.stdout) -> None:
        self.fmt = fmt
        self.color = color and stream.isatty()
        self.stream = stream

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def report(self, diags: list[Diagnostic]) -> None:
        if self.fmt == "json":
            self._report_json(diags)
        else:
            self._report_text(diags)

    def summary(self, diags: list[Diagnostic]) -> None:
        errors = sum(1 for d in diags if d.severity == Severity.ERROR)
        warnings = sum(1 for d in diags if d.severity == Severity.WARNING)
        infos = sum(1 for d in diags if d.severity == Severity.INFO)
        if not diags:
            self._print(self._c(_BOLD, "No issues found."))
            return
        parts = []
        if errors:
            parts.append(self._c(_RED, f"{errors} error{'s' if errors != 1 else ''}"))
        if warnings:
            parts.append(self._c(_YELLOW, f"{warnings} warning{'s' if warnings != 1 else ''}"))
        if infos:
            parts.append(self._c(_CYAN, f"{infos} info{'s' if infos != 1 else ''}"))
        self._print(", ".join(parts) + ".")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _report_text(self, diags: list[Diagnostic]) -> None:
        for d in diags:
            sev_colour = _SEV_COLOUR.get(d.severity, "")
            sev_label = self._c(sev_colour, d.severity.value)
            rule = self._c(_DIM, f"[{d.rule_id}]")
            location = self._c(_BOLD, f"{d.filename}:{d.line}:{d.col}")
            self._print(f"{location}: {sev_label} {rule} {d.message}")

    def _report_json(self, diags: list[Diagnostic]) -> None:
        data = [
            {
                "rule": d.rule_id,
                "severity": d.severity.value,
                "message": d.message,
                "file": d.filename,
                "line": d.line,
                "col": d.col,
            }
            for d in diags
        ]
        json.dump(data, self.stream, indent=2)
        self._print("")  # trailing newline

    def _c(self, code: str, text: str) -> str:
        if self.color and code:
            return f"{code}{text}{_RESET}"
        return text

    def _print(self, text: str) -> None:
        print(text, file=self.stream)
