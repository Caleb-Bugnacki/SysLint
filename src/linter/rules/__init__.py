"""Lint rule registry."""
from .naming import NamingRule
from .documentation import DocumentationRule
from .structure import StructureRule
from .scope import ScopeRule

ALL_RULES = [NamingRule, DocumentationRule, StructureRule, ScopeRule]
