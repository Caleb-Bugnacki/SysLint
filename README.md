# SysLint
SysML v2 Linter

A static linter for SysML v2 source files. No external dependencies — pure Python 3.9+.

## Usage

```bash
python src/syslint.py [options] FILE [FILE ...]
```

**Options:**

| Flag | Description |
|------|-------------|
| `--format text\|json` | Output format (default: `text`) |
| `--rules R1,R2,...` | Only emit diagnostics for these rule IDs |
| `--min-severity error\|warning\|info` | Minimum severity to report (default: `info`) |
| `--no-color` | Disable ANSI colour output |

**Exit codes:** `0` = no issues, `1` = warnings/info found, `2` = errors found

### Examples

```bash
# Lint a single file
python src/syslint.py examples/vehicle-model.sysml

# Lint multiple files, warnings and above only
python src/syslint.py --min-severity warning examples/*.sysml

# JSON output, specific rules only
python src/syslint.py --format json --rules W001,W010,W021 examples/camera.sysml

# Disable colour (e.g. in CI)
python src/syslint.py --no-color examples/*.sysml
```

## Rules

| ID | Severity | Description |
|----|----------|-------------|
| W001 | warning | Definition name should use PascalCase (e.g. `part def MyPart`) |
| W002 | warning | Usage/instance name should use camelCase (e.g. `part myPart`) |
| W003 | warning | Package/namespace name should use PascalCase |
| W010 | info | Definition is missing a `doc` block |
| W011 | warning | Requirement definition is missing a `doc` block |
| W020 | info | Definition has an empty body |
| W021 | warning | Requirement definition has no `subject` declaration |
| W022 | info | Requirement definition has no `require constraint` body |
| W023 | info | Part/port/attribute/item usage has no type annotation |
| W030 | warning | Duplicate name declared in the same scope |
| W031 | info | Import appears to be unused |
| I001 | info | Action definition has sub-actions but no `first`/`then` sequencing |

## Architecture

```
src/
  syslint.py               # CLI entry point
  linter/
    token_types.py         # TokenType enum, Token dataclass, keyword map
    lexer.py               # Tokenizer (based on SysMLv2Lexer.g4)
    ast_nodes.py           # Element + File dataclasses
    parser.py              # Recursive-descent parser
    diagnostic.py          # Severity enum + Diagnostic dataclass
    checker.py             # Orchestrates all rules
    reporter.py            # Text and JSON output formatting
    rules/
      naming.py            # W001, W002, W003
      documentation.py     # W010, W011
      structure.py         # W020–W023, I001
      scope.py             # W030, W031

grammar_files/
  SysMLv2Lexer.g4          # ANTLR4 lexer grammar (reference)
  SysMLv2Parser.g4         # ANTLR4 parser grammar (reference)

examples/
  camera.sysml
  toaster-system.sysml
  vehicle-model.sysml
```

The linter uses a hand-rolled tokenizer and recursive-descent parser derived from the official ANTLR4 grammar files. The parser is lenient — it uses error recovery to skip unknown constructs so that linting continues even on partially-invalid files.
