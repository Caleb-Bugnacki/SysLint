"""SysML v2 lexer — tokenises source text based on SysMLv2Lexer.g4."""
from __future__ import annotations
from .token_types import Token, TokenType, KEYWORDS


class LexError(Exception):
    def __init__(self, msg: str, line: int, col: int) -> None:
        super().__init__(f"{line}:{col}: {msg}")
        self.line = line
        self.col = col


class Lexer:
    """Converts SysML v2 source text into a list of Tokens.

    Whitespace is skipped; block comments (/* */) and line comments (//) are
    returned as BLOCK_COMMENT / LINE_COMMENT tokens so the parser can attach
    doc blocks to elements.
    """

    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ch(self) -> str | None:
        return self.source[self.pos] if self.pos < len(self.source) else None

    def _peek(self, offset: int = 1) -> str | None:
        p = self.pos + offset
        return self.source[p] if p < len(self.source) else None

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _rest(self) -> str:
        """Characters remaining from current position (after already-consumed char)."""
        return self.source[self.pos:]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while True:
            tok = self._next_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens

    # ------------------------------------------------------------------
    # Core lexing
    # ------------------------------------------------------------------

    def _skip_whitespace(self) -> None:
        while self.pos < len(self.source) and self.source[self.pos] in " \t\r\n":
            self._advance()

    def _next_token(self) -> Token:
        self._skip_whitespace()

        if self.pos >= len(self.source):
            return Token(TokenType.EOF, "", self.line, self.col)

        line, col = self.line, self.col
        ch = self.source[self.pos]

        # Line comment  //
        if ch == "/" and self._peek() == "/":
            start = self.pos
            while self.pos < len(self.source) and self.source[self.pos] != "\n":
                self._advance()
            return Token(TokenType.LINE_COMMENT, self.source[start:self.pos], line, col)

        # Block comment  /* ... */
        if ch == "/" and self._peek() == "*":
            start = self.pos
            self._advance()  # /
            self._advance()  # *
            while self.pos < len(self.source):
                if self.source[self.pos] == "*" and self._peek() == "/":
                    self._advance()  # *
                    self._advance()  # /
                    break
                self._advance()
            return Token(TokenType.BLOCK_COMMENT, self.source[start:self.pos], line, col)

        # Identifiers and keywords
        if ch.isalpha() or ch == "_":
            start = self.pos
            while self.pos < len(self.source) and (
                self.source[self.pos].isalnum() or self.source[self.pos] == "_"
            ):
                self._advance()
            value = self.source[start:self.pos]
            tok_type = KEYWORDS.get(value, TokenType.IDENTIFIER)
            return Token(tok_type, value, line, col)

        # Numeric literals
        if ch.isdigit():
            return self._lex_number(line, col)

        # Real starting with '.'  (e.g. .5)
        if ch == "." and self._peek() and self._peek().isdigit():
            return self._lex_number(line, col)

        # Single-quoted string  '...'
        if ch == "'":
            return self._lex_string("'", TokenType.STRING, line, col)

        # Double-quoted string  "..."
        if ch == '"':
            return self._lex_string('"', TokenType.DOUBLE_STRING, line, col)

        # Operators — consume the first char, then check for compound forms
        self._advance()  # consume ch

        rest = self._rest()  # characters after ch

        if ch == "!":
            if rest.startswith("=="):
                self._advance(); self._advance()
                return Token(TokenType.BANG_EQ_EQ, "!==", line, col)
            if rest.startswith("="):
                self._advance()
                return Token(TokenType.BANG_EQ, "!=", line, col)
            return Token(TokenType.IDENTIFIER, "!", line, col)  # unknown, best-effort

        if ch == ":":
            if rest.startswith(":>"):
                self._advance(); self._advance()
                return Token(TokenType.COLON_COLON_GT, "::>", line, col)
            if rest.startswith(">>"):
                self._advance(); self._advance()
                return Token(TokenType.COLON_GT_GT, ":>>", line, col)
            if rest.startswith(":"):
                self._advance()
                return Token(TokenType.COLON_COLON, "::", line, col)
            if rest.startswith(">"):
                self._advance()
                return Token(TokenType.COLON_GT, ":>", line, col)
            if rest.startswith("="):
                self._advance()
                return Token(TokenType.COLON_EQ, ":=", line, col)
            return Token(TokenType.COLON, ":", line, col)

        if ch == "=":
            if rest.startswith("=="):
                self._advance(); self._advance()
                return Token(TokenType.EQ_EQ_EQ, "===", line, col)
            if rest.startswith("="):
                self._advance()
                return Token(TokenType.EQ_EQ, "==", line, col)
            if rest.startswith(">"):
                self._advance()
                return Token(TokenType.FAT_ARROW, "=>", line, col)
            return Token(TokenType.EQ, "=", line, col)

        if ch == "*":
            if rest.startswith("*"):
                self._advance()
                return Token(TokenType.STAR_STAR, "**", line, col)
            return Token(TokenType.STAR, "*", line, col)

        if ch == "-":
            if rest.startswith(">"):
                self._advance()
                return Token(TokenType.ARROW, "->", line, col)
            return Token(TokenType.MINUS, "-", line, col)

        if ch == ".":
            if rest.startswith("."):
                self._advance()
                return Token(TokenType.DOT_DOT, "..", line, col)
            if rest.startswith("?"):
                self._advance()
                return Token(TokenType.DOT_QUESTION, ".?", line, col)
            return Token(TokenType.DOT, ".", line, col)

        if ch == "<":
            if rest.startswith("="):
                self._advance()
                return Token(TokenType.LE, "<=", line, col)
            return Token(TokenType.LT, "<", line, col)

        if ch == ">":
            if rest.startswith("="):
                self._advance()
                return Token(TokenType.GE, ">=", line, col)
            return Token(TokenType.GT, ">", line, col)

        if ch == "?":
            if rest.startswith("?"):
                self._advance()
                return Token(TokenType.QUESTION_QUESTION, "??", line, col)
            return Token(TokenType.QUESTION, "?", line, col)

        if ch == "@":
            if rest.startswith("@"):
                self._advance()
                return Token(TokenType.AT_AT, "@@", line, col)
            return Token(TokenType.AT_SIGN, "@", line, col)

        # Single-char tokens
        _SINGLE: dict[str, TokenType] = {
            "#": TokenType.HASH, "$": TokenType.DOLLAR, "%": TokenType.PERCENT,
            "&": TokenType.AMP, "(": TokenType.LPAREN, ")": TokenType.RPAREN,
            "+": TokenType.PLUS, ",": TokenType.COMMA, "/": TokenType.SLASH,
            ";": TokenType.SEMI, "[": TokenType.LBRACK, "]": TokenType.RBRACK,
            "^": TokenType.CARET, "{": TokenType.LBRACE, "|": TokenType.PIPE,
            "}": TokenType.RBRACE, "~": TokenType.TILDE,
        }
        if ch in _SINGLE:
            return Token(_SINGLE[ch], ch, line, col)

        # Unknown character — emit as IDENTIFIER so the parser can recover
        return Token(TokenType.IDENTIFIER, ch, line, col)

    def _lex_number(self, line: int, col: int) -> Token:
        start = self.pos
        is_real = False

        # Leading digits (or nothing if we start with '.')
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self._advance()

        # Decimal part
        if self.pos < len(self.source) and self.source[self.pos] == ".":
            next_ch = self._peek()
            if next_ch and next_ch.isdigit():
                is_real = True
                self._advance()  # .
                while self.pos < len(self.source) and self.source[self.pos].isdigit():
                    self._advance()

        # Exponent
        if self.pos < len(self.source) and self.source[self.pos] in "eE":
            is_real = True
            self._advance()
            if self.pos < len(self.source) and self.source[self.pos] in "+-":
                self._advance()
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                self._advance()

        value = self.source[start:self.pos]
        return Token(TokenType.REAL if is_real else TokenType.INTEGER, value, line, col)

    def _lex_string(self, quote: str, tok_type: TokenType, line: int, col: int) -> Token:
        start = self.pos
        self._advance()  # opening quote
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch == "\\":
                self._advance()
                if self.pos < len(self.source):
                    self._advance()
            elif ch == quote:
                self._advance()
                break
            else:
                self._advance()
        return Token(tok_type, self.source[start:self.pos], line, col)
