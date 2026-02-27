"""Naming convention lint rules.

W001 — Definition names should use PascalCase.
W002 — Usage/instance names should use camelCase (or snake_case).
W003 — Package/namespace names should use PascalCase.
"""
from __future__ import annotations
import re
from typing import Optional

from ..ast_nodes import Element, File
from ..diagnostic import Diagnostic, Severity
from .base import BaseRule

# Kinds whose *definitions* should be PascalCase
_DEF_KINDS = {
    "part_def", "action_def", "requirement_def", "attribute_def",
    "port_def", "enum_def", "interface_def", "connection_def",
    "connector_def", "allocation_def", "metadata_def", "behavior_def",
    "function_def", "predicate_def", "calc_def", "analysis_def",
    "state_def", "rendering_def", "view_def", "viewpoint_def",
    "occurrence_def", "interaction_def", "class_def", "assoc_def",
    "classifier_def", "datatype_def", "struct_def", "item_def",
    "type_def", "feature_def", "flow_def", "succession_def",
    "transition_def", "frame_def", "concern_def", "stakeholder_def",
    "constraint_def", "use_case_def", "verification_def",
}

# Kinds whose *usages* should be camelCase
_USAGE_KINDS = {
    "part", "action", "requirement", "attribute", "port", "interface",
    "connection", "connector", "allocation", "metadata", "behavior",
    "function", "predicate", "calc", "analysis", "state", "rendering",
    "view", "viewpoint", "occurrence", "interaction", "class", "assoc",
    "classifier", "datatype", "struct", "item", "type", "feature",
    "flow", "succession", "transition", "frame", "concern", "stakeholder",
    "constraint", "use_case",
}

# Package / namespace kinds
_PACKAGE_KINDS = {"package", "namespace"}


def _is_pascal_case(name: str) -> bool:
    """Starts with uppercase letter, contains only alphanumeric chars."""
    return bool(re.match(r"^[A-Z][a-zA-Z0-9]*$", name))


def _is_camel_or_snake(name: str) -> bool:
    """Starts with lowercase letter; allows underscores (snake_case accepted)."""
    return bool(re.match(r"^[a-z][a-zA-Z0-9_]*$", name))


def _is_quoted(name: str) -> bool:
    """Single-quoted restricted names are exempt from naming rules."""
    return name.startswith("'")


class NamingRule(BaseRule):

    def check(self, file: File) -> list[Diagnostic]:
        return self._walk(file.elements, file.filename, self._visit)

    def _visit(
        self, elem: Element, filename: str, parent: Optional[Element]
    ) -> list[Diagnostic]:
        name = elem.name
        if not name or _is_quoted(name):
            return []

        diags: list[Diagnostic] = []

        # Package / namespace
        if elem.kind in _PACKAGE_KINDS:
            if not _is_pascal_case(name):
                diags.append(self._diag(
                    "W003", Severity.WARNING,
                    f"Package/namespace '{name}' should use PascalCase "
                    f"(e.g. '{_to_pascal(name)}').",
                    filename, elem.line, elem.col,
                ))
            return diags

        # Definitions
        if elem.kind in _DEF_KINDS:
            if not _is_pascal_case(name):
                diags.append(self._diag(
                    "W001", Severity.WARNING,
                    f"Definition '{name}' should use PascalCase "
                    f"(e.g. '{_to_pascal(name)}').",
                    filename, elem.line, elem.col,
                ))
            return diags

        # Usages
        if elem.kind in _USAGE_KINDS:
            if not _is_camel_or_snake(name):
                diags.append(self._diag(
                    "W002", Severity.WARNING,
                    f"Usage '{name}' should use camelCase or snake_case "
                    f"(e.g. '{_to_camel(name)}').",
                    filename, elem.line, elem.col,
                ))

        return diags


# ---------------------------------------------------------------------------
# Name conversion helpers (used only in suggestion messages)
# ---------------------------------------------------------------------------

def _to_pascal(name: str) -> str:
    """Best-effort conversion of name to PascalCase."""
    words = re.split(r"[_\s]+", name)
    return "".join(w.capitalize() for w in words if w)


def _to_camel(name: str) -> str:
    """Best-effort conversion of name to camelCase."""
    words = re.split(r"[_\s]+", name)
    if not words:
        return name
    return words[0].lower() + "".join(w.capitalize() for w in words[1:] if w)
