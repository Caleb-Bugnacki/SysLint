"""Diagnostic (lint result) types."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    @property
    def order(self) -> int:
        return {"error": 0, "warning": 1, "info": 2}[self.value]


@dataclass(frozen=True, order=False)
class Diagnostic:
    rule_id: str
    severity: Severity
    message: str
    filename: str
    line: int
    col: int

    def __lt__(self, other: "Diagnostic") -> bool:
        return (self.filename, self.line, self.col) < (other.filename, other.line, other.col)
