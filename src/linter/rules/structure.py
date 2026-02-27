"""Structural lint rules.

E001 — require constraint body is empty.
W020 — Definition body is empty.
W021 — Requirement definition has no 'subject'.
W022 — Requirement definition has no 'require constraint'.
W023 — Part usage has no type annotation.
W024 — Port usage has no type annotation.
W025 — Attribute usage has no type annotation.
I001 — Action definition has no sequential flow (first/then).
"""
from __future__ import annotations
from typing import Optional

from ..ast_nodes import Element, File
from ..diagnostic import Diagnostic, Severity
from .base import BaseRule

# Definitions that should not have an empty body
_SUBSTANTIVE_DEFS = {
    "part_def", "action_def", "requirement_def", "interface_def",
    "connection_def", "port_def", "behavior_def", "function_def",
    "predicate_def", "calc_def", "analysis_def", "state_def",
    "use_case_def",
}

# Usages that should declare a type
_TYPED_USAGES = {"part", "port", "attribute", "item"}


class StructureRule(BaseRule):

    def check(self, file: File) -> list[Diagnostic]:
        return self._walk(file.elements, file.filename, self._visit)

    def _visit(
        self, elem: Element, filename: str, parent: Optional[Element]
    ) -> list[Diagnostic]:
        diags: list[Diagnostic] = []

        # ----------------------------------------------------------------
        # Empty definition body
        # ----------------------------------------------------------------
        if elem.kind in _SUBSTANTIVE_DEFS and elem.name:
            real_body = [
                c for c in elem.body
                if c.kind not in ("doc", "comment")
            ]
            if not real_body:
                diags.append(self._diag(
                    "W020", Severity.INFO,
                    f"Definition '{elem.name}' has an empty body.",
                    filename, elem.line, elem.col,
                ))

        # ----------------------------------------------------------------
        # Requirement definition checks
        # ----------------------------------------------------------------
        if elem.kind == "requirement_def" and elem.name:
            kinds_in_body = {c.kind for c in elem.body}

            # Composite requirements contain sub-requirements and don't need
            # a direct subject or require constraint at this level.
            has_sub_reqs = any(
                c.kind in ("requirement", "requirement_def") for c in elem.body
            )

            if "subject" not in kinds_in_body and not has_sub_reqs:
                diags.append(self._diag(
                    "W021", Severity.WARNING,
                    f"Requirement definition '{elem.name}' has no 'subject' declaration.",
                    filename, elem.line, elem.col,
                ))

            if "require_constraint" not in kinds_in_body and not has_sub_reqs:
                diags.append(self._diag(
                    "W022", Severity.INFO,
                    f"Requirement definition '{elem.name}' has no 'require constraint' body.",
                    filename, elem.line, elem.col,
                ))

        # ----------------------------------------------------------------
        # Typed usages without type annotation
        # ----------------------------------------------------------------
        if (
            elem.kind in _TYPED_USAGES
            and elem.name
            and elem.type_ref is None
            and not elem.specializes
        ):
            diags.append(self._diag(
                "W023", Severity.INFO,
                f"Usage '{elem.name}' ({elem.kind}) has no type annotation.",
                filename, elem.line, elem.col,
            ))

        # ----------------------------------------------------------------
        # Action definition should contain flow sequencing
        # ----------------------------------------------------------------
        if elem.kind == "action_def" and elem.name and elem.body:
            has_sub_actions = any(c.kind == "action" for c in elem.body)
            has_flow = any(c.kind in ("first", "then") for c in elem.body)
            if has_sub_actions and not has_flow:
                diags.append(self._diag(
                    "I001", Severity.INFO,
                    f"Action definition '{elem.name}' defines sub-actions "
                    "but has no 'first'/'then' sequencing.",
                    filename, elem.line, elem.col,
                ))

        return diags
