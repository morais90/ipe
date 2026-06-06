# Architecture Specification

## Overview

Ipê follows a **pipeline architecture**: parse OpenAPI → extract a language-agnostic blueprint → render templates. Language support is pluggable via the `LanguageTarget` protocol. Jinja2 handles rendering; `pathlib` handles I/O. No external scaffolding tools.

**v0.1 ships Python only.** The architecture supports additional targets without core changes.

## Pipeline

```
┌───────────────────────────────────────────────────────────┐
│                    SPEC ANALYZER                          │
│  Knows OpenAPI. Knows nothing about languages.            │
├───────────────────────────────────────────────────────────┤
│  Parse + validate + resolve $refs (eager for non-schema,  │
│  lazy for schema) → APIBlueprint                          │
└──────────────────────────┬────────────────────────────────┘
                           │ APIBlueprint
              ┌────────────▼────────────┐
              │     LANGUAGE TARGET     │
              │  Knows its language.    │
              │  Knows nothing about    │
              │  OpenAPI or I/O.        │
              ├─────────────────────────┤
              │ Type resolution,        │
              │ naming, resource        │
              │ grouping, template dir  │
              └────────────┬────────────┘
                           │ context + naming + types (via filters)
              ┌────────────▼────────────┐
              │ TEMPLATE TREE RENDERER  │
              │  Knows Jinja2 + fs.     │
              │  Knows nothing about    │
              │  OpenAPI or languages.  │
              ├─────────────────────────┤
              │ Scan template tree,     │
              │ render each .jinja,     │
              │ write to output dir     │
              └─────────────────────────┘
```

Orchestrated by:

```
┌───────────────────────────────────────────────────────────┐
│                    CODE GENERATOR                         │
│  The pipeline coordinator. Builds the context dict from   │
│  the blueprint, groups operations via the target, hands   │
│  off to the renderer.                                     │
└───────────────────────────────────────────────────────────┘
```

## Generation Flow

```
CLI → CodeGenerator.run(config)
  → SpecAnalyzer.parse(spec_path)        → OpenAPISpec (Pydantic)
  → SpecAnalyzer.extract(spec, config)   → APIBlueprint
  → LanguageTarget.group(operations)     → dict[resource, list[op]]
  → TemplateTreeRenderer.render(...)     → list[Path] written
```

There is no separate `transform` or `plan` step. Type resolution and naming live as **Jinja filters** invoked from templates; the **template tree itself is the render plan**.

## Core Components

### 1. SpecAnalyzer (`core/analyzer.py`)
**Knows OpenAPI. Knows nothing about languages.**

Two responsibilities:

- `parse(spec_path)` — fetch from file or URL, normalize OpenAPI 3.0 → 3.1 quirks (`nullable`, exclusive bounds, `example`), inline non-schema `$ref`s eagerly, validate via Pydantic, bind the schema registry for lazy resolution.
- `extract(spec, config)` — translate the parsed Pydantic OpenAPI models into the language-agnostic `APIBlueprint` (operations, models, auth schemes, metadata).

Type mapping is **not** an analyzer responsibility — each target owns the conversion from OpenAPI types to language-native types.

### 2. LanguageTarget (`targets/base.py`)
**Knows its language. Knows nothing about OpenAPI or I/O.**

A `Protocol` — any class that satisfies it is a valid target. No inheritance required.

| Member | Returns | Purpose |
|---|---|---|
| `name` | `str` | Unique identifier (e.g. `"python"`) |
| `naming` | `NamingConvention` | Language-specific casing |
| `resolve_type(type, format)` | `str` | OpenAPI type → language-native type |
| `group(operations)` | `dict[str, list[Operation]]` | Bucket operations into resources |
| `template_dir` | `Path` | Where this target's `.jinja` files live |
| `get_default_config()` | `dict` | Sensible defaults for the target |

These six members fully define how a language renders an OpenAPI spec. There is no `transform()` or `plan()` — type resolution happens at render time via Jinja filters; the plan is the template tree on disk.

### 3. TargetRegistry (`targets/registry.py`)

Explicit registration of language targets. Built-in targets are imported and registered in `_register_builtins`; third-party targets call `register()`. No filesystem scanning or entry-points discovery in v0.1.

### 4. TemplateTreeRenderer (`core/renderer.py`)
**Knows Jinja2 + filesystem. Knows nothing about OpenAPI or languages.**

The template tree on disk **is** the plan. The renderer walks the target's `template_dir`, renders each `.jinja` file, and writes to output. Three behaviors:

- **Single template** (e.g. `client.py.jinja`) — rendered once with the full context.
- **Repeated template** (`{name}.py.jinja` inside a directory like `models/`) — rendered once per item in the matching context collection. The parent directory name (`models`) maps to the context key.
- **Custom override** — `ChoiceLoader` lets users place a custom template that wins over the built-in.

Filters registered on the Jinja environment expose language semantics to templates:

| Filter | Purpose |
|---|---|
| `class_name`, `method_name`, `field_name`, `module_name` | Target's `NamingConvention` |
| `resolve_type(type, format)` | Target's type resolver |
| `strip_html` | Clean HTML/Markdown from OpenAPI descriptions |
| `pyval` | Render Python literal (`True`/`False`/`None`) |
| `type_imports`, `param_type_imports` | Compute Python imports for used types |

Filters carry **all** language-specific knowledge into templates. Templates stay declarative; targets stay free of I/O.

### 5. CodeGenerator (`core/generator.py`)
**The pipeline coordinator.**

Connects analyzer, target, and renderer. Builds the context dict from `blueprint.model_dump()`, groups operations into resources via the target, and dispatches to the renderer. ~35 lines. Knows nothing about the specifics of any one stage.

## $ref Resolution Strategy

OpenAPI allows `$ref` in many positions (parameters, responses, requestBodies, headers, examples, links, pathItems, schemas). Ipê treats schemas differently from the others:

- **Non-schema `$ref`s**: resolved **eagerly** in `parse_openapi`, before Pydantic validation. The walker (`resolver.resolve_refs`) inlines targets in-place with id-based cycle protection and chained-ref recursion.
- **Schema `$ref`s**: resolved **lazily** at attribute access via `Schema.__getattribute__`. A `ContextVar`-scoped registry holds the bound schemas; reading any non-`ref` field on a Schema whose `ref` is set transparently delegates to the resolved Schema.

The reason for the split: schemas can be recursive (e.g. `Node → Node`), and eager resolution would loop or blow the stack on real-world specs. Non-schema component refs are flat and safe to resolve eagerly, eliminating an entire class of "ref came through empty" bugs at the analyzer boundary.

## Canonical Data Models

This specification is the single source of truth for these models. Other specs reference these definitions, not redefine them.

All models are Pydantic `BaseModel`. Each model that originates from OpenAPI data exposes a `from_*` classmethod for construction from parser models. Targets consume blueprints via `model_dump()`.

### APIBlueprint

Normalized, language-agnostic API representation produced by `SpecAnalyzer.extract`. Parser-agnostic — does not import OpenAPI parser models.

| Field | Type | Description |
|---|---|---|
| api_name | str | From info.title |
| spec_version | str | From info.version |
| spec_description | str? | From info.description |
| base_url | str? | First server URL |
| server_urls | list[str] | All server URLs |
| operations | list[StandardOperation] | Flat list of all operations |
| models | list[StandardModel] | Extracted schema models |
| auth_schemes | list[AuthScheme] | Security schemes |
| module_name | str | Generated module name |
| generated_at | str | ISO timestamp |
| ipe_version | str | Ipê version |
| generator_config | dict | Target-specific config |

### StandardOperation

| Field | Type | Description |
|---|---|---|
| operation_id | str | Unique identifier |
| method | str | GET, POST, PUT, PATCH, DELETE |
| path | str | e.g. `/users/{user_id}` |
| summary | str? | Short description |
| description | str? | Full description |
| tags | list[str] | Grouping tags |
| parameters | list[StandardParameter] | Path, query, header, cookie params |
| request_body | RequestBody? | Request body if present |
| responses | list[Response] | Response definitions |
| security | list[SecurityRequirement] | Required auth schemes |

### StandardParameter

| Field | Type | Description |
|---|---|---|
| name | str | Parameter name |
| location | str | path, query, header, cookie |
| required | bool | Whether required |
| schema_type | str | OpenAPI type |
| description | str? | Description |
| schema_format | str? | e.g. date-time, int64, uuid |
| default | Any? | Default value |

### StandardModel

A named schema from `components/schemas`. Array schemas are skipped (they're type aliases).

| Field | Type | Description |
|---|---|---|
| name | str | Schema name |
| description | str? | Description |
| properties | list[StandardProperty] | Model fields |
| required_fields | list[str] | Required field names |
| validation_rules | list[ValidationRule] | Constraints from schema |

### StandardProperty

| Field | Type | Description |
|---|---|---|
| name | str | Field name |
| schema_type | str | OpenAPI type |
| description | str? | Description |
| schema_format | str? | Format hint |
| required | bool | Whether required |
| nullable | bool | Whether nullable |
| default | Any? | Default value |
| enum_values | list[Any]? | Allowed values |

### RequestBody

| Field | Type | Description |
|---|---|---|
| required | bool | Whether required |
| content_types | list[str] | e.g. application/json |
| schema_type | str | OpenAPI type or model name |
| description | str? | Description |
| schema_format | str? | Format hint |

### Response

| Field | Type | Description |
|---|---|---|
| status_code | str | "200", "404", "default" |
| description | str? | Description |
| content_type | str? | Media type |
| schema_type | str? | Response body type |
| schema_format | str? | Format hint |

### AuthScheme

| Field | Type | Description |
|---|---|---|
| name | str | Scheme identifier |
| type | str | apiKey, http, oauth2, openIdConnect |
| scheme | str? | bearer, basic (for type=http) |
| location | str? | header, query, cookie (for type=apiKey) |
| header_name | str? | e.g. X-API-Key, Authorization |

### ValidationRule

| Field | Type | Description |
|---|---|---|
| rule_type | str | min_length, pattern, minimum, etc. |
| value | Any | Constraint value |

### SecurityRequirement

| Field | Type | Description |
|---|---|---|
| scheme_name | str | References an AuthScheme |
| scopes | list[str] | Required OAuth scopes (empty for non-oauth) |

## NamingConvention Protocol

Each target provides a `NamingConvention` that handles language-specific casing. Composition, not inheritance — targets use it, they're not forced into a hierarchy.

The Protocol requires four methods that map a raw OpenAPI identifier to its language's preferred casing:

- `class_name(raw)` — class/type declarations
- `method_name(raw)` — operation methods
- `field_name(raw)` — model fields and parameters
- `module_name(raw)` — file/module identifiers

Python uses snake_case for everything except classes (PascalCase). Naming utility functions (`to_snake_case`, `to_pascal_case`, `to_camel_case`, `to_kebab_case`) live in `utils/naming.py` and are shared across targets.

## Resource Grouping

Operations are grouped into resources (Python classes, TypeScript modules, etc.) by the target's `group()` method. `utils/grouping.py` provides three reusable strategies:

| Strategy | Bucket key | Example |
|---|---|---|
| `by_tag` | First operation tag, with path fallback | `Customers`, `Charges` |
| `by_path` | First non-parameter path segment | `customers` for `/customers/{id}` |
| `by_nested_path` | Dotted path segments | `customers.subscriptions` for `/customers/{id}/subscriptions` |

The Python target currently uses `by_nested_path` (one file per nested resource).

## Template Customization

Users can override individual Jinja templates without forking the target. Configured via `template_dir` in `ipe.json`:

```json
{
  "target": "python",
  "template_dir": "./my-templates"
}
```

The renderer uses Jinja2 `ChoiceLoader`: the custom directory is checked first, built-in templates serve as fallback. Users only need to provide the templates they want to customize — the rest inherits from the target.

## Module Organization

```
src/ipe/
├── __init__.py
├── cli/                       # Command-line interface
│   ├── main.py                # Typer commands
│   └── console.py             # Rich console output
├── core/                      # Pipeline components
│   ├── analyzer.py            # SpecAnalyzer
│   ├── generator.py           # CodeGenerator
│   ├── renderer.py            # TemplateTreeRenderer + Jinja filters
│   ├── config.py              # IpeConfig
│   └── exceptions.py          # Exception hierarchy
├── parsers/                   # OpenAPI parsing
│   ├── openapi.py             # parse_openapi + 3.0→3.1 normalization
│   ├── models.py              # Pydantic OpenAPI models
│   ├── resolver.py            # resolve_refs walker with ref_filter
│   └── fetcher.py             # Local / HTTPS spec fetching
├── targets/                   # Language target system
│   ├── base.py                # LanguageTarget + NamingConvention Protocols
│   ├── registry.py            # TargetRegistry
│   └── python/                # Python target (v0.1)
│       ├── target.py          # PythonTarget
│       ├── naming.py          # PythonNaming
│       └── templates/         # Jinja .jinja files
├── models/                    # Shared data models
│   ├── blueprint.py           # APIBlueprint
│   └── standard.py            # StandardOperation, StandardModel, ...
└── utils/
    ├── naming.py              # Casing helpers
    └── grouping.py            # Resource grouping strategies
```

## Architecture Benefits

**Separation of concerns**

- `SpecAnalyzer` handles OpenAPI complexity once for all languages.
- `LanguageTarget` carries language-specific decisions without touching parsing or I/O.
- `TemplateTreeRenderer` handles rendering and disk I/O without knowing the language.
- `CodeGenerator` coordinates without owning details.

**Language extensibility**

- New languages implement the `LanguageTarget` Protocol and call `registry.register()`.
- Protocol-based design — no inheritance required.
- Each target is self-contained: its templates, naming, and type resolution live under `targets/<name>/`.

**Template-tree-as-plan**

- The directory of `.jinja` files is the render plan. No separate plan object, no `OutputFile`.
- `{name}.py.jinja` convention handles repeated templates (one per item in a collection).
- Lower coupling: adding a new generated file means dropping a `.jinja` in the template tree.

**Testability**

- Each component testable in isolation.
- Protocol-based contracts make test doubles trivial.
- Golden-file tests at the CLI boundary catch regressions across the full pipeline.

## Implementation Status

| Phase | Scope | Status |
|---|---|---|
| 1 — Foundation + Python | Pipeline, Python target, CLI | Done (v0.1) |
| 2 — Template customization + TypeScript | `ChoiceLoader` overrides, second target | Customization done; TS target pending |
| 3 — Ecosystem | Additional targets (Go, Rust), entry_points discovery | Planned |
