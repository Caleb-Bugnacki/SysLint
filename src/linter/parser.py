"""SysML v2 recursive-descent parser.

Produces a simplified AST (list of Element nodes) suitable for linting.
The parser is lenient: unknown constructs are skipped with error recovery
so that linting can continue even on partially-invalid files.
"""
from __future__ import annotations
from typing import Optional

from .token_types import Token, TokenType
from .ast_nodes import Element, File

# ---------------------------------------------------------------------------
# Keyword sets used by the parser
# ---------------------------------------------------------------------------

_VISIBILITY = {TokenType.PRIVATE, TokenType.PROTECTED, TokenType.PUBLIC}

_PREFIX_MODIFIERS = {
    TokenType.ABSTRACT, TokenType.REF, TokenType.VAR, TokenType.DERIVED,
    TokenType.ORDERED, TokenType.NONUNIQUE, TokenType.COMPOSITE,
    TokenType.PORTION, TokenType.LIBRARY, TokenType.INDIVIDUAL,
    TokenType.VARIATION, TokenType.VARIANT, TokenType.STANDARD,
    TokenType.CONST, TokenType.CONSTANT,
}

# Keywords that start a named element definition or usage.
# 'USE' is handled specially (followed by 'CASE').
_ELEMENT_KEYWORDS = {
    TokenType.PACKAGE, TokenType.NAMESPACE,
    TokenType.PART, TokenType.ACTION, TokenType.REQUIREMENT,
    TokenType.ATTRIBUTE, TokenType.PORT, TokenType.ENUM,
    TokenType.INTERFACE, TokenType.CONNECTION, TokenType.CONNECTOR,
    TokenType.ALLOCATION, TokenType.METADATA, TokenType.BEHAVIOR,
    TokenType.FUNCTION, TokenType.PREDICATE, TokenType.CALC,
    TokenType.ANALYSIS, TokenType.STATE, TokenType.RENDERING,
    TokenType.VIEW, TokenType.VIEWPOINT, TokenType.OCCURRENCE,
    TokenType.INTERACTION, TokenType.CLASS, TokenType.ASSOC,
    TokenType.CLASSIFIER, TokenType.DATATYPE, TokenType.STRUCT,
    TokenType.ITEM, TokenType.TYPE, TokenType.MULTIPLICITY,
    TokenType.FEATURE, TokenType.FLOW, TokenType.SUCCESSION,
    TokenType.TRANSITION, TokenType.FRAME, TokenType.CONCERN,
    TokenType.STAKEHOLDER, TokenType.CONSTRAINT,
    TokenType.ACTOR, TokenType.SUBJECT, TokenType.OBJECTIVE,
    TokenType.STEP, TokenType.FILTER, TokenType.FORK,
    TokenType.JOIN, TokenType.MERGE, TokenType.DECIDE,
    TokenType.VERIFICATION,
}

# Keywords that introduce inline usages inside bodies but don't follow the
# standard pattern (handled as generic skipped elements).
_BODY_ONLY_KEYWORDS = {
    TokenType.PERFORM, TokenType.EXHIBIT, TokenType.SATISFY,
    TokenType.VERIFY, TokenType.EXPOSE, TokenType.SEND,
    TokenType.ACCEPT, TokenType.ASSERT, TokenType.INCLUDE,
    TokenType.BIND, TokenType.ALIAS, TokenType.DEPENDENCY,
    TokenType.SPECIALIZATION, TokenType.CONJUGATION, TokenType.TYPING,
    TokenType.FEATURING, TokenType.DISJOINING, TokenType.REDEFINES,
    TokenType.SUBSETS, TokenType.MEMBER,
    TokenType.ENTRY, TokenType.DO, TokenType.EXIT,
    TokenType.WHEN, TokenType.ELSE, TokenType.IF,
}

# Sequencing keywords — parsed as thin Element nodes so flow rules can see them
_SEQUENCE_KEYWORDS = {TokenType.FIRST, TokenType.THEN}

# Parameter direction keywords — parsed as feature elements
_DIRECTION_KEYWORDS = {TokenType.IN, TokenType.OUT, TokenType.INOUT}


class Parser:
    """Parse a flat token list into a File AST."""

    def __init__(self, tokens: list[Token], filename: str = "") -> None:
        # Keep block comments so we can attach doc strings; skip line comments.
        self._tokens = [t for t in tokens if t.type != TokenType.LINE_COMMENT]
        self._pos = 0
        self.filename = filename
        self.errors: list[str] = []

    # ------------------------------------------------------------------
    # Token stream helpers
    # ------------------------------------------------------------------

    def _cur(self) -> Token:
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return Token(TokenType.EOF, "", 0, 0)

    def _peek(self, offset: int = 1) -> Token:
        p = self._pos + offset
        if p < len(self._tokens):
            return self._tokens[p]
        return Token(TokenType.EOF, "", 0, 0)

    def _advance(self) -> Token:
        tok = self._cur()
        self._pos += 1
        return tok

    def _eat(self, *types: TokenType) -> Optional[Token]:
        if self._cur().type in types:
            return self._advance()
        return None

    def _at(self, *types: TokenType) -> bool:
        return self._cur().type in types

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def parse(self) -> File:
        elements = self._parse_body(top_level=True)
        return File(filename=self.filename, elements=elements)

    # ------------------------------------------------------------------
    # Body / element lists
    # ------------------------------------------------------------------

    def _parse_body(self, top_level: bool = False) -> list[Element]:
        elements: list[Element] = []
        while True:
            if self._at(TokenType.EOF):
                break
            if not top_level and self._at(TokenType.RBRACE):
                break

            # Collect any pending block comment (potential doc for next element)
            pending_comment: Optional[Token] = None
            while self._at(TokenType.BLOCK_COMMENT):
                pending_comment = self._advance()

            if self._at(TokenType.EOF):
                break
            if not top_level and self._at(TokenType.RBRACE):
                break

            elem = self._parse_element(pending_comment)
            if elem is not None:
                elements.append(elem)
        return elements

    # ------------------------------------------------------------------
    # Single element
    # ------------------------------------------------------------------

    def _parse_element(self, pending_comment: Optional[Token] = None) -> Optional[Element]:
        """Try to parse one element from the current position."""
        if self._eat(TokenType.SEMI):
            return None

        line, col = self._cur().line, self._cur().col

        # ----------------------------------------------------------------
        # Collect visibility and prefix modifiers
        # ----------------------------------------------------------------
        modifiers: list[str] = []
        if self._cur().type in _VISIBILITY:
            modifiers.append(self._advance().value)
        while self._cur().type in _PREFIX_MODIFIERS:
            modifiers.append(self._advance().value)

        # After modifiers: skip stray ':>>', ':>' subsetting/redefining lines
        if self._at(TokenType.COLON_GT_GT, TokenType.COLON_COLON_GT, TokenType.COLON_GT):
            return self._skip_to_end(line, col)

        # ----------------------------------------------------------------
        # Special elements
        # ----------------------------------------------------------------

        # import
        if self._at(TokenType.IMPORT):
            return self._parse_import(line, col, modifiers)

        # doc  /* ... */
        if self._at(TokenType.DOC):
            return self._parse_doc(line, col, pending_comment)

        # comment [about ...]  /* ... */
        if self._at(TokenType.COMMENT):
            return self._parse_comment_kw(line, col)

        # require constraint { ... }  /  assume constraint { ... }
        if self._at(TokenType.REQUIRE, TokenType.ASSUME):
            return self._parse_require_or_assume(line, col, modifiers)

        # Sequencing keywords  first name; / then name;
        if self._cur().type in _SEQUENCE_KEYWORDS:
            kw = self._advance().value
            seq_name = self._parse_name_token()
            self._eat(TokenType.SEMI)
            return Element(kind=kw, is_def=False, name=seq_name, type_ref=None,
                           line=line, col=col)

        # return name : Type ;  — treated as an output parameter
        if self._eat(TokenType.RETURN):
            ret_name = self._parse_name_token()
            ret_type: Optional[str] = None
            if self._eat(TokenType.COLON):
                ret_type = self._parse_qualified_name()
            self._eat(TokenType.SEMI)
            return Element(kind="return_param", is_def=False, name=ret_name,
                           type_ref=ret_type, modifiers=["return"], line=line, col=col)

        # IN / OUT / INOUT — direction prefix for parameters/features
        direction: Optional[str] = None
        if self._at(TokenType.IN, TokenType.OUT, TokenType.INOUT):
            direction = self._advance().value
            modifiers.append(direction)

        # use case [def]  — two-keyword construct
        if self._at(TokenType.USE) and self._peek().type == TokenType.CASE:
            return self._parse_use_case(line, col, modifiers, pending_comment)

        # Body-only keywords (first, then, perform, …) — quick skip
        if self._cur().type in _BODY_ONLY_KEYWORDS:
            return self._skip_to_end(line, col)

        # Metadata usage:  @TypeName ...  or  @@TypeName ...
        if self._at(TokenType.AT_SIGN, TokenType.AT_AT):
            return self._skip_to_end(line, col)

        # ----------------------------------------------------------------
        # General element
        # ----------------------------------------------------------------
        if self._cur().type not in _ELEMENT_KEYWORDS:
            # If a direction modifier was consumed (in/out/inout), the next token
            # might be a plain IDENTIFIER parameter:  in paramName : Type ;
            if direction is not None and self._at(TokenType.IDENTIFIER):
                param_name = self._advance().value
                param_type: Optional[str] = None
                if self._eat(TokenType.COLON):
                    param_type = self._parse_qualified_name()
                mult: Optional[str] = None
                if self._at(TokenType.LBRACK):
                    mult = self._parse_multiplicity()
                self._eat(TokenType.SEMI)
                return Element(kind="parameter", is_def=False, name=param_name,
                               type_ref=param_type, multiplicity=mult,
                               modifiers=modifiers, line=line, col=col)
            # Unknown token — skip it and try to recover
            if not self._at(TokenType.EOF, TokenType.RBRACE):
                self._advance()
            return None

        primary = self._advance()
        is_def = self._eat(TokenType.DEF) is not None
        kind = primary.value + ("_def" if is_def else "")

        # Parse identification  [< alias >] name
        name = self._parse_identification()

        elem = Element(
            kind=kind,
            is_def=is_def,
            name=name,
            type_ref=None,
            modifiers=modifiers,
            line=line,
            col=col,
        )

        # Attach pending block comment as doc if no inline doc yet
        if pending_comment is not None:
            elem.doc = _strip_comment(pending_comment.value)

        self._parse_element_tail(elem)
        return elem

    # ------------------------------------------------------------------
    # Element tail: type annotation, specialisations, body/semicolon
    # ------------------------------------------------------------------

    def _parse_element_tail(self, elem: Element) -> None:
        """Parse everything after the element name."""

        # Type annotation   : TypeName [multiplicity]
        if self._eat(TokenType.COLON):
            # Skip 'typed by' alternative spellings
            self._eat(TokenType.TYPED)
            elem.type_ref = self._parse_qualified_name()
            if self._at(TokenType.LBRACK):
                elem.multiplicity = self._parse_multiplicity()

        # Specialisation  :> TypeRef, …  or  specializes TypeRef, …
        if self._at(TokenType.COLON_GT) or self._at(TokenType.SPECIALIZES):
            self._advance()
            elem.specializes.append(self._parse_qualified_name())
            while self._eat(TokenType.COMMA):
                elem.specializes.append(self._parse_qualified_name())

        # Redefinition :>> name — skip the value
        if self._at(TokenType.COLON_GT_GT) or self._at(TokenType.REDEFINES):
            self._advance()
            self._parse_qualified_name()  # consume the redefined name

        # Multiplicity if not already consumed
        if elem.multiplicity is None and self._at(TokenType.LBRACK):
            elem.multiplicity = self._parse_multiplicity()

        # Default value  = expr ;
        if self._eat(TokenType.EQ):
            self._skip_expression()
            return

        # Body  { ... }
        if self._eat(TokenType.LBRACE):
            children = self._parse_body(top_level=False)
            elem.body = children
            # Extract doc from the first DOC child if not already set
            for child in children:
                if child.kind == "doc" and elem.doc is None:
                    elem.doc = child.doc
                    break
            self._eat(TokenType.RBRACE)
            return

        # Semicolon terminator
        self._eat(TokenType.SEMI)

    # ------------------------------------------------------------------
    # Special element parsers
    # ------------------------------------------------------------------

    def _parse_import(self, line: int, col: int, modifiers: list[str]) -> Element:
        self._advance()  # IMPORT
        self._eat(TokenType.ALL)
        path_parts: list[str] = []

        # qualified name   A::B::C
        name = self._parse_name_token()
        if name:
            path_parts.append(name)
        while self._eat(TokenType.COLON_COLON):
            n = self._parse_name_token()
            if n:
                path_parts.append(n)

        is_star = False
        # namespace import:  ...::*
        # (the COLON_COLON was already consumed above)
        if path_parts and path_parts[-1] == "*":
            is_star = True
            path_parts.pop()

        # Alternatively the last token might be STAR
        if self._eat(TokenType.STAR):
            is_star = True

        path = "::".join(path_parts)

        # Relationship body  ;  or  { }
        if self._eat(TokenType.LBRACE):
            self._skip_block()
        else:
            self._eat(TokenType.SEMI)

        return Element(
            kind="import",
            is_def=False,
            name=None,
            type_ref=None,
            modifiers=modifiers,
            line=line,
            col=col,
            import_path=path,
            import_star=is_star,
        )

    def _parse_doc(self, line: int, col: int, pending: Optional[Token]) -> Element:
        self._advance()  # DOC
        # Optional identification (ignored for linting purposes)
        self._eat_identification()
        # Optional  locale "..."
        if self._eat(TokenType.LOCALE):
            self._eat(TokenType.DOUBLE_STRING)
        # The block comment is the actual doc text
        doc_text: Optional[str] = None
        if self._at(TokenType.BLOCK_COMMENT):
            doc_text = _strip_comment(self._advance().value)
        elif pending is not None:
            doc_text = _strip_comment(pending.value)
        return Element(
            kind="doc",
            is_def=False,
            name=None,
            type_ref=None,
            doc=doc_text,
            line=line,
            col=col,
        )

    def _parse_comment_kw(self, line: int, col: int) -> Element:
        self._advance()  # COMMENT keyword
        # Optional identification
        self._eat_identification()
        # Optional  about  Name, Name, …
        if self._eat(TokenType.ABOUT):
            self._parse_qualified_name()
            while self._eat(TokenType.COMMA):
                self._parse_qualified_name()
        # Optional  locale "..."
        if self._eat(TokenType.LOCALE):
            self._eat(TokenType.DOUBLE_STRING)
        # Block comment body
        doc_text: Optional[str] = None
        if self._at(TokenType.BLOCK_COMMENT):
            doc_text = _strip_comment(self._advance().value)
        return Element(
            kind="comment",
            is_def=False,
            name=None,
            type_ref=None,
            doc=doc_text,
            line=line,
            col=col,
        )

    def _parse_require_or_assume(
        self, line: int, col: int, modifiers: list[str]
    ) -> Optional[Element]:
        kw = self._advance().value  # 'require' or 'assume'
        if self._eat(TokenType.CONSTRAINT):
            elem = Element(
                kind="require_constraint",
                is_def=False,
                name=None,
                type_ref=None,
                modifiers=modifiers,
                line=line,
                col=col,
            )
            # Body  { expr }  or  ;
            if self._eat(TokenType.LBRACE):
                self._skip_block()
            else:
                self._eat(TokenType.SEMI)
            return elem
        # 'require' used in other contexts — skip to next boundary
        return self._skip_to_end(line, col)

    def _parse_use_case(
        self, line: int, col: int, modifiers: list[str], pending: Optional[Token]
    ) -> Element:
        self._advance()  # USE
        self._advance()  # CASE
        is_def = self._eat(TokenType.DEF) is not None
        name = self._parse_identification()
        elem = Element(
            kind="use_case_def" if is_def else "use_case",
            is_def=is_def,
            name=name,
            type_ref=None,
            modifiers=modifiers,
            line=line,
            col=col,
        )
        if pending is not None:
            elem.doc = _strip_comment(pending.value)
        self._parse_element_tail(elem)
        return elem

    # ------------------------------------------------------------------
    # Sub-parsers for names, types, multiplicity
    # ------------------------------------------------------------------

    def _parse_identification(self) -> Optional[str]:
        """Parse optional  [< alias >] name."""
        # < alias_name > name
        if self._eat(TokenType.LT):
            self._parse_name_token()  # alias
            self._eat(TokenType.GT)
        return self._parse_name_token()

    def _eat_identification(self) -> None:
        if self._eat(TokenType.LT):
            self._parse_name_token()
            self._eat(TokenType.GT)
        self._parse_name_token()

    def _parse_name_token(self) -> Optional[str]:
        """Consume an IDENTIFIER or single-quoted STRING and return its value."""
        if self._at(TokenType.IDENTIFIER):
            return self._advance().value
        if self._at(TokenType.STRING):
            return self._advance().value.strip("'")
        return None

    def _parse_qualified_name(self) -> str:
        """Parse A::B::C (or A.B.C) and return as a string."""
        parts: list[str] = []
        tok = self._parse_name_token()
        if tok:
            parts.append(tok)
        while self._at(TokenType.COLON_COLON, TokenType.DOT):
            self._advance()
            seg = self._parse_name_token()
            if seg:
                parts.append(seg)
            elif self._eat(TokenType.STAR):
                parts.append("*")
        return "::".join(parts)

    def _parse_multiplicity(self) -> str:
        """Parse  [ lower .. upper ]  or  [ n ]  and return the bracket text."""
        if not self._eat(TokenType.LBRACK):
            return ""
        parts: list[str] = []
        while not self._at(TokenType.RBRACK, TokenType.EOF):
            tok = self._advance()
            parts.append(tok.value)
        self._eat(TokenType.RBRACK)
        return "[" + "".join(parts) + "]"

    # ------------------------------------------------------------------
    # Error recovery helpers
    # ------------------------------------------------------------------

    def _skip_to_end(self, line: int, col: int) -> None:
        """Skip tokens until we reach ';', '{', or '}' (or EOF)."""
        while not self._at(TokenType.SEMI, TokenType.LBRACE,
                            TokenType.RBRACE, TokenType.EOF):
            self._advance()
        if self._eat(TokenType.SEMI):
            return
        if self._eat(TokenType.LBRACE):
            self._skip_block()
        return None

    def _skip_expression(self) -> None:
        """Skip tokens making up a value expression (stops at ';' or '}')."""
        depth = 0
        while not self._at(TokenType.EOF):
            if self._at(TokenType.LBRACE, TokenType.LPAREN, TokenType.LBRACK):
                depth += 1
                self._advance()
            elif self._at(TokenType.RBRACE, TokenType.RPAREN, TokenType.RBRACK):
                if depth == 0:
                    break
                depth -= 1
                self._advance()
            elif self._at(TokenType.SEMI) and depth == 0:
                self._advance()
                break
            else:
                self._advance()

    def _skip_block(self) -> None:
        """Skip tokens until the matching '}' (assumes '{' was already consumed)."""
        depth = 1
        while not self._at(TokenType.EOF) and depth > 0:
            if self._eat(TokenType.LBRACE):
                depth += 1
            elif self._eat(TokenType.RBRACE):
                depth -= 1
            else:
                self._advance()


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _strip_comment(text: str) -> str:
    """Strip /* and */ from a block comment and trim whitespace."""
    s = text.strip()
    if s.startswith("/*"):
        s = s[2:]
    if s.endswith("*/"):
        s = s[:-2]
    # Remove leading '*' on each line (JavaDoc style)
    lines = [ln.strip().lstrip("*").strip() for ln in s.splitlines()]
    return "\n".join(ln for ln in lines if ln).strip()
