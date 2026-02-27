"""Abstract base class for all lint rules."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from ..ast_nodes import Element, File
from ..diagnostic import Diagnostic, Severity


class BaseRule(ABC):
    """Each rule receives a File and returns a list of Diagnostics."""

    @abstractmethod
    def check(self, file: File) -> list[Diagnostic]:
        ...

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _diag(
        self,
        rule_id: str,
        severity: Severity,
        message: str,
        filename: str,
        line: int,
        col: int,
    ) -> Diagnostic:
        return Diagnostic(
            rule_id=rule_id,
            severity=severity,
            message=message,
            filename=filename,
            line=line,
            col=col,
        )

    def _walk(
        self,
        elements: list[Element],
        filename: str,
        visitor,  # callable(elem, filename, parent) -> list[Diagnostic]
        parent: Optional[Element] = None,
    ) -> list[Diagnostic]:
        diags: list[Diagnostic] = []
        for elem in elements:
            diags.extend(visitor(elem, filename, parent))
            diags.extend(self._walk(elem.body, filename, visitor, parent=elem))
        return diags
