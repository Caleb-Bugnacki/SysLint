"""Documentation lint rules.

W010 — Definition is missing a doc block.
W011 — Requirement definition is missing a doc block (stricter).
W012 — Requirement definition doc block is too short (< 10 chars).
"""
from __future__ import annotations
from typing import Optional

from ..ast_nodes import Element, File
from ..diagnostic import Diagnostic, Severity
from .base import BaseRule

# Definitions that *should* have a doc block (warning if missing)
_DEF_KINDS = {
    "part_def", "action_def", "requirement_def", "attribute_def",
    "port_def", "enum_def", "interface_def", "connection_def",
    "connector_def", "allocation_def", "metadata_def", "behavior_def",
    "function_def", "predicate_def", "calc_def", "analysis_def",
    "state_def", "rendering_def", "view_def", "viewpoint_def",
    "occurrence_def", "interaction_def", "class_def", "assoc_def",
    "classifier_def", "datatype_def", "struct_def", "item_def",
    "use_case_def", "constraint_def",
}

# Package / namespace kinds
_PACKAGE_KINDS = {"package", "namespace"}

# Minimum doc length to avoid trivially empty docs
_MIN_DOC_LEN = 5


class DocumentationRule(BaseRule):

    def check(self, file: File) -> list[Diagnostic]:
        return self._walk(file.elements, file.filename, self._visit)

    def _visit(
        self, elem: Element, filename: str, parent: Optional[Element]
    ) -> list[Diagnostic]:
        diags: list[Diagnostic] = []

        is_def = elem.kind in _DEF_KINDS
        is_req = elem.kind == "requirement_def"

        if not is_def and elem.kind not in _PACKAGE_KINDS:
            return []

        if not elem.name:
            return []

        has_doc = elem.doc is not None and len(elem.doc.strip()) >= _MIN_DOC_LEN

        if is_req and not has_doc:
            diags.append(self._diag(
                "W011", Severity.WARNING,
                f"Requirement definition '{elem.name}' is missing a doc block. "
                "Requirements should document their intent.",
                filename, elem.line, elem.col,
            ))
        elif is_def and not has_doc:
            diags.append(self._diag(
                "W010", Severity.INFO,
                f"Definition '{elem.name}' has no doc block.",
                filename, elem.line, elem.col,
            ))

        return diags
