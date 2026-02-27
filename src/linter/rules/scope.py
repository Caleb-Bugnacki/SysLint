"""Scope lint rules.

W030 — Duplicate name declared in the same scope.
W031 — Import of a namespace that is never referenced in the file.
"""
from __future__ import annotations
from collections import defaultdict
from typing import Optional

from ..ast_nodes import Element, File
from ..diagnostic import Diagnostic, Severity
from .base import BaseRule

# Kinds that define names in a scope
_NAMED_KINDS = {
    "part_def", "action_def", "requirement_def", "attribute_def",
    "port_def", "enum_def", "interface_def", "connection_def",
    "connector_def", "allocation_def", "metadata_def", "behavior_def",
    "function_def", "predicate_def", "calc_def", "analysis_def",
    "state_def", "view_def", "viewpoint_def", "use_case_def",
    "occurrence_def", "class_def", "assoc_def", "classifier_def",
    "datatype_def", "struct_def", "item_def", "type_def",
    "part", "action", "requirement", "attribute", "port", "item",
    "flow", "constraint", "subject",
}


class ScopeRule(BaseRule):

    def check(self, file: File) -> list[Diagnostic]:
        diags: list[Diagnostic] = []
        diags.extend(self._check_duplicates(file.elements, file.filename))
        diags.extend(self._check_unused_imports(file))
        return diags

    # ------------------------------------------------------------------
    # Duplicate names
    # ------------------------------------------------------------------

    def _check_duplicates(
        self, elements: list[Element], filename: str
    ) -> list[Diagnostic]:
        diags: list[Diagnostic] = []
        seen: dict[str, Element] = {}

        for elem in elements:
            if elem.kind in _NAMED_KINDS and elem.name:
                key = elem.name.lower()  # case-insensitive comparison
                if key in seen:
                    first = seen[key]
                    diags.append(self._diag(
                        "W030", Severity.WARNING,
                        f"Duplicate name '{elem.name}' in this scope "
                        f"(first declared at line {first.line}).",
                        filename, elem.line, elem.col,
                    ))
                else:
                    seen[key] = elem

            # Recurse into body (new scope)
            if elem.body:
                diags.extend(self._check_duplicates(elem.body, filename))

        return diags

    # ------------------------------------------------------------------
    # Unused imports
    # ------------------------------------------------------------------

    def _check_unused_imports(self, file: File) -> list[Diagnostic]:
        """Warn when an imported namespace is never referenced in the file."""
        # Collect imports
        imports: list[Element] = []
        self._collect_imports(file.elements, imports)

        if not imports:
            return []

        # Collect all identifiers used in the file (as type_ref / specializes)
        used_names: set[str] = set()
        self._collect_references(file.elements, used_names)

        diags: list[Diagnostic] = []
        for imp in imports:
            if not imp.import_path:
                continue
            # The top-level namespace is the last segment before the star
            parts = imp.import_path.split("::")
            # Use the leaf or root namespace name for matching
            root = parts[0] if parts else ""
            leaf = parts[-1] if parts else ""

            if imp.import_star:
                # namespace import: check if the namespace itself is referenced
                referenced = any(
                    name.startswith(leaf) or name.startswith(root)
                    for name in used_names
                )
            else:
                # membership import: check the leaf name
                referenced = leaf in used_names or imp.import_path in used_names

            if not referenced:
                label = imp.import_path + ("::*" if imp.import_star else "")
                diags.append(self._diag(
                    "W031", Severity.INFO,
                    f"Import '{label}' appears to be unused.",
                    file.filename, imp.line, imp.col,
                ))

        return diags

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _collect_imports(self, elements: list[Element], out: list[Element]) -> None:
        for elem in elements:
            if elem.kind == "import":
                out.append(elem)
            self._collect_imports(elem.body, out)

    def _collect_references(
        self, elements: list[Element], out: set[str]
    ) -> None:
        for elem in elements:
            if elem.type_ref:
                # Add the full ref and each segment
                for part in elem.type_ref.split("::"):
                    out.add(part)
            for spec in elem.specializes:
                for part in spec.split("::"):
                    out.add(part)
            self._collect_references(elem.body, out)
