"""AST node types for the SysML v2 linter."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Element:
    """A single SysML v2 element (definition or usage)."""

    # Element kind: e.g. 'part_def', 'part', 'action_def', 'package',
    # 'requirement_def', 'import', 'doc', 'comment', 'constraint', etc.
    kind: str

    # True when the 'def' keyword was present (i.e. this is a definition)
    is_def: bool

    # The declared name (IDENTIFIER or STRING), if present
    name: Optional[str]

    # Type annotation after ':', e.g. 'Engine' in 'part engine : Engine'
    type_ref: Optional[str]

    # Specialisation(s) after ':>' or 'specializes'
    specializes: list[str] = field(default_factory=list)

    # Multiplicity string, e.g. '[4]' or '[1..*]'
    multiplicity: Optional[str] = None

    # Nested body elements (children inside '{ ... }')
    body: list[Element] = field(default_factory=list)

    # Extracted doc text (from a 'doc /* ... */' child or leading block comment)
    doc: Optional[str] = None

    # Visibility and other prefix modifiers ('private', 'abstract', etc.)
    modifiers: list[str] = field(default_factory=list)

    # Source location
    line: int = 0
    col: int = 0

    # For import elements
    import_path: Optional[str] = None
    import_star: bool = False


@dataclass
class File:
    """Root of the AST for a single SysML v2 source file."""
    filename: str
    elements: list[Element] = field(default_factory=list)
