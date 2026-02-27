"""Checker — runs all enabled lint rules against a parsed File."""
from __future__ import annotations

from .ast_nodes import File
from .diagnostic import Diagnostic
from .rules import ALL_RULES
from .rules.base import BaseRule


def check_file(file: File, rule_ids: set[str] | None = None) -> list[Diagnostic]:
    """Run all (or a subset of) lint rules and return sorted diagnostics.

    Args:
        file:      Parsed AST.
        rule_ids:  If given, only rules whose diagnostic IDs appear in the set
                   are emitted.  Pass ``None`` to run everything.
    """
    diags: list[Diagnostic] = []
    for rule_cls in ALL_RULES:
        rule: BaseRule = rule_cls()
        rule_diags = rule.check(file)
        if rule_ids is not None:
            rule_diags = [d for d in rule_diags if d.rule_id in rule_ids]
        diags.extend(rule_diags)
    return sorted(diags)
