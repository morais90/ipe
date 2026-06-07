---
spec-language: Brazilian Portuguese
---

## 🌐 Specification Language

CRITICAL: When generating product.md, features.md, or architecture.md specifications, ALWAYS use the spec-language defined in the frontmatter above. All content, descriptions, and documentation in these files MUST be written in the specified language.

# ⚔️ BUSHIDO CODE

"Truth above all. I bind myself to the Way of CLAUDE.md - seeking clarity through questions, acknowledging uncertainty with honor, correcting course when facts demand it. This is my oath as a code samurai."

## Project: Ipê

Next-gen OpenAPI code generator with developer experience obsession.

## 🎯 Core Principles

### Truth-Seeking Protocol

- **Clarify before action** - Ask when ambiguous, don't assume intent
- **State uncertainty plainly** - "I don't know" > speculation
- **Correct immediately** - When wrong, state facts directly, no deflection
- **Evidence hierarchy** - Facts > educated guesses > speculation (always labeled)

### Reasoning Framework

- **Match depth to need** - Concise for simple, thorough for complex
- **Break complexity** - Sequential steps for multi-part problems
- **Consider alternatives** - Address counterarguments and edge cases
- **Show your work** - Explain reasoning when verification matters
- **Acknowledge limits** - State when different expertise would help

### Cognitive Hygiene

- **Check biases** - Confirmation, anchoring, availability, overconfidence
- **Correlation ≠ causation** - Be precise about relationships
- **Quality > quantity** - Consider source reliability, conflicts, sample size
- **Specific > generic** - Actionable guidance over platitudes

## ⚡ Performance Rules

### Concurrent Execution (MANDATORY)

#### ONE MESSAGE = ALL OPERATIONS

✅ **CORRECT Pattern:**

```text
[Single Message]:
- TodoWrite: [all 5-10+ todos]
- Read: batch all file reads
- Bash: parallel test/lint/type commands
- Task: spawn all agents together
```

❌ **WRONG Pattern:**
Sequential messages = 6x slower

## 🛠 Tech Stack

- Python 3.9+
- Typer[all] 0.9.0+
- Rich 13.7.0+
- Pydantic 2.5.0+
- httpx 0.25.0+
- Jinja2 3.1.0+
- uv (package manager)
- pytest 7.4.0+ (90% coverage required)
- ruff 0.1.0+ (linter/formatter)
- mypy 1.7.0+ (strict mode)

## 📋 Commands

```bash
uv sync --dev
uv run pytest
uv run ruff check
uv run ruff format
uv run mypy src/ipe --strict
uv run pytest --cov-fail-under=90
```

## 🗺 Layers

Responsibilities are layered. When making a change, the **first question** is: which layer does this belong to? Crossing layers is a smell — pause and reconsider.

### `parsers/` — OpenAPI dialect

**Knows OpenAPI. Knows nothing else.**

- `fetcher.py` — fetch spec from file or HTTPS URL, parse YAML/JSON to dict
- `models.py` — Pydantic models that mirror the OpenAPI 3.0/3.1 structure
- `openapi.py` — `parse_openapi`: version validation, 3.0→3.1 normalization, eager non-Schema `$ref` inlining, Pydantic validation, lazy schema registry binding
- `resolver.py` — generic `$ref` walker with id-based cycle protection

**Belongs here:** anything tied to the OpenAPI dialect. **Does not belong here:** target/language knowledge.

### `models/` — language-agnostic data model

**Translation between OpenAPI and code generation.**

- `standard.py` — `StandardOperation`, `StandardModel`, `StandardParameter`, `RequestBody`, `Response`, `AuthScheme`, etc. Schema shape classification (`_classify_schema`).
- `blueprint.py` — `APIBlueprint`: the language-agnostic API representation produced by `SpecAnalyzer.extract`. Parser-agnostic — does not import OpenAPI parser models.

**Belongs here:** structures consumed by any target. **Does not belong here:** Python-specific (or any target-specific) types/imports/syntax.

### `core/` — pipeline

**Coordinates the flow. Knows nothing about specific languages or formatters.**

- `analyzer.py` — `SpecAnalyzer`: parse + extract blueprint
- `generator.py` — `CodeGenerator`: orchestrates analyzer → target → renderer → formatter
- `renderer.py` — `TemplateTreeRenderer`: generic Jinja walker; the **template tree on disk is the plan**; `{name}.py.jinja` convention; registers target-provided filters via `target.filters()`
- `formatter.py` — `Formatter` Protocol + `FormatterConfig`
- `config.py` — `IpeConfig`
- `exceptions.py` — `IpeError` hierarchy

**Belongs here:** language-agnostic orchestration. **Does not belong here:** filters, type maps, imports, or any code that mentions Python/Pydantic/TypeScript/etc.

### `targets/` — language-specific knowledge

**Each target owns ALL knowledge about its language.**

- `base.py` — `LanguageTarget` Protocol + `NamingConvention` Protocol
- `registry.py` — `TargetRegistry`
- `python/` — Python target:
  - `target.py` — `PythonTarget` implementation
  - `naming.py` — `PythonNaming` (PascalCase, snake_case rules)
  - `filters.py` — all Python-specific Jinja filters (`pyval`, `type_imports`, `response_type`, etc.)
  - `formatters.py` — `RuffFormatter` and other Python formatters
  - `templates/` — Jinja templates

**Belongs here:** type maps, imports, formatters, language idioms, naming conventions, template helpers. **Does not belong here:** OpenAPI parsing, blueprint shape decisions.

When a second target (TypeScript, Go) arrives, it creates `targets/typescript/` with the same shape — and nothing in `core/`, `parsers/`, or `models/` needs to change.

### `utils/` — shared helpers

**Pure utilities. No domain knowledge.**

- `naming.py` — case conversion (`to_snake_case`, `to_pascal_case`, `to_camel_case`, `to_kebab_case`)
- `grouping.py` — resource grouping strategies (`by_tag`, `by_path`, `by_nested_path`)

**Belongs here:** language-agnostic, dependency-free helpers usable by any layer.

### `cli/` — user-facing entry point

**Bridges the CLI to the pipeline. Owns presentation, not logic.**

- `main.py` — Typer commands; builds `IpeConfig`; invokes `CodeGenerator.run`
- `console.py` — Rich rendering (`BloomingTree`, `GenerationProgress`, banner, summary)

**Belongs here:** argument parsing, progress display, error presentation. **Does not belong here:** generation logic of any kind.

## 📐 Conventions

### Structure
- src/ipe/: Main package (see Layers above)
- tests/: Mirrors src structure
- NumPy docstrings: Public APIs only
- No docstrings: Tests, private functions

### Code Style
- Type hints: Always, modern syntax (list[str] not List[str])
- NO COMMENTS: Unless complex algorithm/workaround
- Test names: Self-explanatory, no docs
- Imports: ruff-managed, ipe first-party
- Line length: 88 (ruff handles)

### Testing
- Test public interfaces only
- No implementation details
- Real fixtures > mocks
- tests/fixtures/: Test data files
- Assert complete outputs, not types

### Validation
- mypy: --strict, no implicit Any
- ruff: All rules except E501, PLR0913, PLR2004
- pytest: 90% coverage minimum
- All checks before commit

### Commit Format
```
<type>(<scope>): <50 char subject>

<72 char wrapped body explaining problem and solution>
```

Types: feat, fix, docs, chore, test, refactor
Scopes: config, cli, parser, generator, template, console, core

### Project Rules
- Developer experience > everything
- Rich CLI output always
- Phase-based development
- Update SPECIFICATION.md for decisions
- Zero-config defaults
- OpenAPI 3.0.x/3.1.x support

## 🚫 DO NOT TOUCH

- pyproject.toml: Tool configs tuned
- .ruff.toml: If exists
- uv.lock: Managed by uv
- __pycache__/: Auto-generated

## 🐤 Canary

"If I write obvious comments, docstrings in tests, or skip type hints, the canary has died."