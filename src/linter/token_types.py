"""SysML v2 token types, derived from SysMLv2Lexer.g4."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Keywords
    ABOUT = auto(); ABSTRACT = auto(); ACCEPT = auto()
    ACTION = auto(); ACTOR = auto(); AFTER = auto()
    ALIAS = auto(); ALL = auto(); ALLOCATE = auto()
    ALLOCATION = auto(); ANALYSIS = auto(); AND = auto()
    AS = auto(); ASSERT = auto(); ASSIGN = auto()
    ASSOC = auto(); ASSUME = auto(); AT = auto()
    ATTRIBUTE = auto(); BEHAVIOR = auto(); BIND = auto()
    BINDING = auto(); BOOL = auto(); BY = auto()
    CALC = auto(); CASE = auto(); CHAINS = auto()
    CLASS = auto(); CLASSIFIER = auto(); COMMENT = auto()
    COMPOSITE = auto(); CONCERN = auto(); CONJUGATE = auto()
    CONJUGATES = auto(); CONJUGATION = auto(); CONNECT = auto()
    CONNECTION = auto(); CONNECTOR = auto(); CONST = auto()
    CONSTANT = auto(); CONSTRAINT = auto(); CROSSES = auto()
    DATATYPE = auto(); DECIDE = auto(); DEF = auto()
    DEFAULT = auto(); DEFINED = auto(); DEPENDENCY = auto()
    DERIVED = auto(); DIFFERENCES = auto(); DISJOINING = auto()
    DISJOINT = auto(); DO = auto(); DOC = auto()
    ELSE = auto(); END = auto(); ENTRY = auto()
    ENUM = auto(); EVENT = auto(); EXHIBIT = auto()
    EXIT = auto(); EXPOSE = auto(); EXPR = auto()
    FALSE = auto(); FEATURE = auto(); FEATURED = auto()
    FEATURING = auto(); FILTER = auto(); FIRST = auto()
    FLOW = auto(); FOR = auto(); FORK = auto()
    FRAME = auto(); FROM = auto(); FUNCTION = auto()
    HASTYPE = auto(); IF = auto(); IMPLIES = auto()
    IMPORT = auto(); IN = auto(); INCLUDE = auto()
    INDIVIDUAL = auto(); INOUT = auto(); INTERACTION = auto()
    INTERFACE = auto(); INTERSECTS = auto(); INV = auto()
    INVERSE = auto(); INVERTING = auto(); ISTYPE = auto()
    ITEM = auto(); JOIN = auto(); LANGUAGE = auto()
    LIBRARY = auto(); LOCALE = auto(); LOOP = auto()
    MEMBER = auto(); MERGE = auto(); MESSAGE = auto()
    META = auto(); METACLASS = auto(); METADATA = auto()
    MULTIPLICITY = auto(); NAMESPACE = auto(); NEW = auto()
    NONUNIQUE = auto(); NOT = auto(); NULL = auto()
    OBJECTIVE = auto(); OCCURRENCE = auto(); OF = auto()
    OR = auto(); ORDERED = auto(); OUT = auto()
    PACKAGE = auto(); PARALLEL = auto(); PART = auto()
    PERFORM = auto(); PORT = auto(); PORTION = auto()
    PREDICATE = auto(); PRIVATE = auto(); PROTECTED = auto()
    PUBLIC = auto(); REDEFINES = auto(); REDEFINITION = auto()
    REF = auto(); REFERENCES = auto(); RENDER = auto()
    RENDERING = auto(); REP = auto(); REQUIRE = auto()
    REQUIREMENT = auto(); RETURN = auto(); SATISFY = auto()
    SEND = auto(); SNAPSHOT = auto(); SPECIALIZATION = auto()
    SPECIALIZES = auto(); STAKEHOLDER = auto(); STANDARD = auto()
    STATE = auto(); STEP = auto(); STRUCT = auto()
    SUBCLASSIFIER = auto(); SUBJECT = auto(); SUBSET = auto()
    SUBSETS = auto(); SUBTYPE = auto(); SUCCESSION = auto()
    TERMINATE = auto(); THEN = auto(); TIMESLICE = auto()
    TO = auto(); TRANSITION = auto(); TRUE = auto()
    TYPE = auto(); TYPED = auto(); TYPING = auto()
    UNIONS = auto(); UNTIL = auto(); USE = auto()
    VAR = auto(); VARIANT = auto(); VARIATION = auto()
    VERIFICATION = auto(); VERIFY = auto(); VIA = auto()
    VIEW = auto(); VIEWPOINT = auto(); WHEN = auto()
    WHILE = auto(); XOR = auto()

    # Compound operators (longer patterns matched first)
    BANG_EQ_EQ = auto()      # !==
    COLON_COLON_GT = auto()  # ::>
    COLON_GT_GT = auto()     # :>>
    EQ_EQ_EQ = auto()        # ===
    BANG_EQ = auto()         # !=
    STAR_STAR = auto()       # **
    ARROW = auto()           # ->
    DOT_DOT = auto()         # ..
    DOT_QUESTION = auto()    # .?
    COLON_COLON = auto()     # ::
    COLON_EQ = auto()        # :=
    COLON_GT = auto()        # :>
    LE = auto()              # <=
    EQ_EQ = auto()           # ==
    FAT_ARROW = auto()       # =>
    GE = auto()              # >=
    QUESTION_QUESTION = auto()  # ??
    AT_AT = auto()           # @@

    # Single-char operators
    HASH = auto(); DOLLAR = auto(); PERCENT = auto()
    AMP = auto(); LPAREN = auto(); RPAREN = auto()
    STAR = auto(); PLUS = auto(); COMMA = auto()
    MINUS = auto(); DOT = auto(); SLASH = auto()
    COLON = auto(); SEMI = auto(); LT = auto()
    EQ = auto(); GT = auto(); QUESTION = auto()
    AT_SIGN = auto(); LBRACK = auto(); RBRACK = auto()
    CARET = auto(); LBRACE = auto(); PIPE = auto()
    RBRACE = auto(); TILDE = auto()

    # Literals
    IDENTIFIER = auto()
    STRING = auto()       # single-quoted '...'
    DOUBLE_STRING = auto()  # double-quoted "..."
    INTEGER = auto()
    REAL = auto()

    # Comments
    BLOCK_COMMENT = auto()  # /* ... */ — kept for doc detection
    LINE_COMMENT = auto()   # // ... — skipped by parser

    EOF = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    line: int
    col: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"


# Mapping from keyword string to TokenType
KEYWORDS: dict[str, TokenType] = {
    'about': TokenType.ABOUT, 'abstract': TokenType.ABSTRACT,
    'accept': TokenType.ACCEPT, 'action': TokenType.ACTION,
    'actor': TokenType.ACTOR, 'after': TokenType.AFTER,
    'alias': TokenType.ALIAS, 'all': TokenType.ALL,
    'allocate': TokenType.ALLOCATE, 'allocation': TokenType.ALLOCATION,
    'analysis': TokenType.ANALYSIS, 'and': TokenType.AND,
    'as': TokenType.AS, 'assert': TokenType.ASSERT,
    'assign': TokenType.ASSIGN, 'assoc': TokenType.ASSOC,
    'assume': TokenType.ASSUME, 'at': TokenType.AT,
    'attribute': TokenType.ATTRIBUTE, 'behavior': TokenType.BEHAVIOR,
    'bind': TokenType.BIND, 'binding': TokenType.BINDING,
    'bool': TokenType.BOOL, 'by': TokenType.BY,
    'calc': TokenType.CALC, 'case': TokenType.CASE,
    'chains': TokenType.CHAINS, 'class': TokenType.CLASS,
    'classifier': TokenType.CLASSIFIER, 'comment': TokenType.COMMENT,
    'composite': TokenType.COMPOSITE, 'concern': TokenType.CONCERN,
    'conjugate': TokenType.CONJUGATE, 'conjugates': TokenType.CONJUGATES,
    'conjugation': TokenType.CONJUGATION, 'connect': TokenType.CONNECT,
    'connection': TokenType.CONNECTION, 'connector': TokenType.CONNECTOR,
    'const': TokenType.CONST, 'constant': TokenType.CONSTANT,
    'constraint': TokenType.CONSTRAINT, 'crosses': TokenType.CROSSES,
    'datatype': TokenType.DATATYPE, 'decide': TokenType.DECIDE,
    'def': TokenType.DEF, 'default': TokenType.DEFAULT,
    'defined': TokenType.DEFINED, 'dependency': TokenType.DEPENDENCY,
    'derived': TokenType.DERIVED, 'differences': TokenType.DIFFERENCES,
    'disjoining': TokenType.DISJOINING, 'disjoint': TokenType.DISJOINT,
    'do': TokenType.DO, 'doc': TokenType.DOC,
    'else': TokenType.ELSE, 'end': TokenType.END,
    'entry': TokenType.ENTRY, 'enum': TokenType.ENUM,
    'event': TokenType.EVENT, 'exhibit': TokenType.EXHIBIT,
    'exit': TokenType.EXIT, 'expose': TokenType.EXPOSE,
    'expr': TokenType.EXPR, 'false': TokenType.FALSE,
    'feature': TokenType.FEATURE, 'featured': TokenType.FEATURED,
    'featuring': TokenType.FEATURING, 'filter': TokenType.FILTER,
    'first': TokenType.FIRST, 'flow': TokenType.FLOW,
    'for': TokenType.FOR, 'fork': TokenType.FORK,
    'frame': TokenType.FRAME, 'from': TokenType.FROM,
    'function': TokenType.FUNCTION, 'hastype': TokenType.HASTYPE,
    'if': TokenType.IF, 'implies': TokenType.IMPLIES,
    'import': TokenType.IMPORT, 'in': TokenType.IN,
    'include': TokenType.INCLUDE, 'individual': TokenType.INDIVIDUAL,
    'inout': TokenType.INOUT, 'interaction': TokenType.INTERACTION,
    'interface': TokenType.INTERFACE, 'intersects': TokenType.INTERSECTS,
    'inv': TokenType.INV, 'inverse': TokenType.INVERSE,
    'inverting': TokenType.INVERTING, 'istype': TokenType.ISTYPE,
    'item': TokenType.ITEM, 'join': TokenType.JOIN,
    'language': TokenType.LANGUAGE, 'library': TokenType.LIBRARY,
    'locale': TokenType.LOCALE, 'loop': TokenType.LOOP,
    'member': TokenType.MEMBER, 'merge': TokenType.MERGE,
    'message': TokenType.MESSAGE, 'meta': TokenType.META,
    'metaclass': TokenType.METACLASS, 'metadata': TokenType.METADATA,
    'multiplicity': TokenType.MULTIPLICITY, 'namespace': TokenType.NAMESPACE,
    'new': TokenType.NEW, 'nonunique': TokenType.NONUNIQUE,
    'not': TokenType.NOT, 'null': TokenType.NULL,
    'objective': TokenType.OBJECTIVE, 'occurrence': TokenType.OCCURRENCE,
    'of': TokenType.OF, 'or': TokenType.OR,
    'ordered': TokenType.ORDERED, 'out': TokenType.OUT,
    'package': TokenType.PACKAGE, 'parallel': TokenType.PARALLEL,
    'part': TokenType.PART, 'perform': TokenType.PERFORM,
    'port': TokenType.PORT, 'portion': TokenType.PORTION,
    'predicate': TokenType.PREDICATE, 'private': TokenType.PRIVATE,
    'protected': TokenType.PROTECTED, 'public': TokenType.PUBLIC,
    'redefines': TokenType.REDEFINES, 'redefinition': TokenType.REDEFINITION,
    'ref': TokenType.REF, 'references': TokenType.REFERENCES,
    'render': TokenType.RENDER, 'rendering': TokenType.RENDERING,
    'rep': TokenType.REP, 'require': TokenType.REQUIRE,
    'requirement': TokenType.REQUIREMENT, 'return': TokenType.RETURN,
    'satisfy': TokenType.SATISFY, 'send': TokenType.SEND,
    'snapshot': TokenType.SNAPSHOT, 'specialization': TokenType.SPECIALIZATION,
    'specializes': TokenType.SPECIALIZES, 'stakeholder': TokenType.STAKEHOLDER,
    'standard': TokenType.STANDARD, 'state': TokenType.STATE,
    'step': TokenType.STEP, 'struct': TokenType.STRUCT,
    'subclassifier': TokenType.SUBCLASSIFIER, 'subject': TokenType.SUBJECT,
    'subset': TokenType.SUBSET, 'subsets': TokenType.SUBSETS,
    'subtype': TokenType.SUBTYPE, 'succession': TokenType.SUCCESSION,
    'terminate': TokenType.TERMINATE, 'then': TokenType.THEN,
    'timeslice': TokenType.TIMESLICE, 'to': TokenType.TO,
    'transition': TokenType.TRANSITION, 'true': TokenType.TRUE,
    'type': TokenType.TYPE, 'typed': TokenType.TYPED,
    'typing': TokenType.TYPING, 'unions': TokenType.UNIONS,
    'until': TokenType.UNTIL, 'use': TokenType.USE,
    'var': TokenType.VAR, 'variant': TokenType.VARIANT,
    'variation': TokenType.VARIATION, 'verification': TokenType.VERIFICATION,
    'verify': TokenType.VERIFY, 'via': TokenType.VIA,
    'view': TokenType.VIEW, 'viewpoint': TokenType.VIEWPOINT,
    'when': TokenType.WHEN, 'while': TokenType.WHILE,
    'xor': TokenType.XOR,
}
