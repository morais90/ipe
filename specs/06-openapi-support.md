# OpenAPI Support Specification

## 1. Overview

OpenAPI parsing is the foundation of the entire Ipê system. Every feature downstream -- validation, data extraction, template rendering, code generation -- depends on a correctly parsed and normalized OpenAPI specification. If this layer is wrong, everything built on top of it is wrong.

This spec defines **what** Ipê supports in terms of OpenAPI specifications, **why** certain decisions were made, **where** each responsibility lives in the codebase, and **when** each component enters the development timeline. It deliberately avoids prescribing implementation details.

**Cross-references:**
- [02-architecture.md](02-architecture.md): Pipeline architecture, `StandardOperation`, `StandardModel`, `APIBlueprint`
- [04-configuration-system.md](04-configuration-system.md): `spec_path` in `ipe.json`
- [05-code-generation.md](05-code-generation.md): How extracted data feeds into templates
- [99-future-features.md](99-future-features.md): Features explicitly deferred from v0.1

---

## 2. Supported Specifications

### OpenAPI 3.0.x (3.0.0 through 3.0.3)

The most widely adopted version. The majority of real-world specs Ipê will encounter are 3.0.x. Full support is required for v0.1.

### OpenAPI 3.1.x (3.1.0+)

The latest major version. Adoption is growing, and Ipê must support it from day one to avoid becoming outdated before release. Key differences that affect code generation:

| Aspect | 3.0.x | 3.1.x |
|--------|-------|-------|
| **JSON Schema** | Extended subset | Full JSON Schema 2020-12 |
| **Nullable** | `nullable: true` property | `type: ["string", "null"]` array syntax |
| **Webhooks** | Not available | Top-level `webhooks` object |
| **PathItem references** | Not a `$ref` target | `pathItem` can be a `$ref` target |
| **`exclusiveMinimum`** | Boolean modifier | Numeric value (JSON Schema alignment) |

Why both versions matter: Ipê must normalize these differences internally so that downstream components (SpecAnalyzer, LanguageTargets) work with a single consistent representation regardless of the source spec version.

### Swagger 2.0 -- Explicitly Not Supported

Ipê does not parse Swagger 2.0 specifications. When a Swagger 2.0 spec is detected, Ipê provides a clear error message:

```
Unsupported specification: Swagger 2.0 detected.

Ipê supports OpenAPI 3.0.x and 3.1.x only.
Convert your spec using: https://converter.swagger.io
```

**Why:** Supporting Swagger 2.0 adds significant complexity with diminishing returns. Mature conversion tools exist, and the OpenAPI ecosystem has moved forward.

---

## 3. Input Sources

### What Ipê Accepts

| Source | Format | Example |
|--------|--------|---------|
| Local file (YAML) | `.yaml`, `.yml` | `ipe generate api.yaml` |
| Local file (JSON) | `.json` | `ipe generate api.json` |
| Remote URL | HTTPS | `ipe generate https://api.example.com/openapi.json` |

### Format Detection

Format is detected from **file content**, not file extension. A file named `spec.json` that contains YAML is parsed as YAML. This prevents subtle errors when extensions are misleading.

Detection strategy:
- Attempt JSON parse first (faster, unambiguous)
- Fall back to YAML parse
- If both fail, report a clear error with the content that could not be parsed

### Remote Fetching

Remote specs are fetched over HTTPS using httpx. HTTP URLs are rejected with a suggestion to use HTTPS. Fetching provides Rich console feedback (download progress, file size, status).

**Where:** `src/ipe/parsers/fetcher.py`

This module is responsible for:
- Resolving the spec source (local path vs URL)
- Fetching remote content with timeout and error handling
- Detecting and returning the parsed content (dict) regardless of source format

---

## 4. Parsing Strategy

### What

Parse an OpenAPI specification (as a raw dict from the fetcher) into a structured, validated set of Pydantic models that represent the OpenAPI document. This is an intermediate representation -- it mirrors the OpenAPI structure, not the generation-ready format.

### Why Pydantic Models (Not a Third-Party OpenAPI Library)

- **Full control over validation messages.** Ipê's core value is developer experience, and error messages are a primary touchpoint. Third-party libraries produce generic, often cryptic errors.
- **Full control over what is supported.** Ipê can progressively add support for OpenAPI features without being blocked by upstream library decisions.
- **Type safety throughout the pipeline.** Pydantic models integrate naturally with mypy strict mode and the rest of the Ipê codebase.
- **No heavy dependencies.** Pydantic is already a core dependency; no additional library needed.

### Where

| Module | Responsibility |
|--------|---------------|
| `src/ipe/parsers/models.py` | Pydantic models representing OpenAPI structures (Info, PathItem, Operation, Schema, etc.) |
| `src/ipe/parsers/openapi.py` | Main parser: takes a dict, returns validated Pydantic models. Handles version detection and normalization between 3.0.x and 3.1.x |

### Key Decision: Two-Stage Processing

1. **Stage 1 (Parser):** Raw dict --> OpenAPI Pydantic models (this spec, `parsers/`)
2. **Stage 2 (SpecAnalyzer):** OpenAPI Pydantic models --> `APIBlueprint` containing `StandardOperation` / `StandardModel` (see [02-architecture.md](02-architecture.md), `core/analyzer.py`)

This separation keeps OpenAPI-specific logic isolated from the language-agnostic `APIBlueprint` that feeds into LanguageTargets.

---

## 5. $ref Resolution

### What

Resolve all JSON Reference (`$ref`) pointers in the specification before any other processing occurs. After resolution, the working document contains no `$ref` nodes -- all references are replaced with the content they point to.

### Why Inline Resolution

- Simplifies every downstream component: parser, validator, and analyzer never need to handle `$ref` logic
- Makes the full document self-contained and predictable
- Enables clear error reporting with resolved paths

### Supported Reference Types

| Reference Type | Example | v0.1 Support |
|----------------|---------|--------------|
| Local (same document) | `#/components/schemas/User` | Yes |
| Relative file | `./models/user.yaml#/User` | No (future) |
| Remote URL | `https://example.com/schemas.yaml#/User` | No (future) |

### Circular Reference Detection

Circular references (e.g., `User` has a property `manager` of type `User`) must be detected and reported with a clear error:

```
Circular reference detected:
  #/components/schemas/User
    -> #/components/schemas/User/properties/manager
    -> #/components/schemas/User

Circular $ref chains cannot be fully resolved inline.
Consider restructuring your schema to break the cycle.
```

**Why strict handling:** This applies to the eager inlining of non-schema `$ref`s (parameters, responses), where a cycle cannot be expanded in place. Schema `$ref`s are never inlined — they bind lazily — so circular *model* references (e.g. `User.manager: User`, or mutually recursive schemas) are fully supported: the generated models reference each other through `TYPE_CHECKING` imports and resolve at runtime via `model_rebuild`.

**Where:** `src/ipe/parsers/resolver.py`

---

## 6. Validation

### What

Validate that the OpenAPI specification is both structurally correct and sufficient for code generation.

### Why Two Validation Levels

Not every valid OpenAPI document produces good generated code. Ipê validates at two levels:

#### Level 1: Structural Validation

The document conforms to the OpenAPI specification. Required fields are present, types are correct, enums contain valid values.

Examples:
- `info.title` is present and non-empty
- `paths` contains at least one path
- Each operation has a valid HTTP method
- Response status codes are valid

#### Level 2: Generation Validation

The document contains enough information for Ipê to generate useful code. This is stricter than OpenAPI compliance -- it ensures generation quality.

Examples:
- Operations have `operationId` (required for method naming)
- Response `200`/`201` has a schema (required for return types)
- Request bodies have `content` with at least one media type
- Schema properties have types defined

**Why this distinction matters:** A spec can be valid OpenAPI but still produce poor generated code (e.g., operations without `operationId` force Ipê to generate ugly method names). Generation validation catches these early and provides actionable guidance.

### Error Reporting

Every validation error includes three components:

1. **Location:** JSON path within the spec (e.g., `$.paths./users.get.responses.200`)
2. **Problem:** What is wrong
3. **Suggestion:** How to fix it

```
Validation Warning at $.paths./users/{id}.get:
  Missing 'operationId' field.
  Without operationId, the generated method name will be derived from
  the path and HTTP method (e.g., 'get_users_id'), which may not be ideal.
  Add: operationId: getUserById
```

### Severity Levels

| Severity | Behavior | Example |
|----------|----------|---------|
| **Error** | Blocks generation | Missing `info`, invalid schema type |
| **Warning** | Generation proceeds, output may be suboptimal | Missing `operationId`, missing `description` |

Warnings are displayed but do not prevent generation. Errors halt the process.

**Where:** Validation logic lives within `src/ipe/parsers/openapi.py` (structural) and `src/ipe/core/analyzer.py` (generation-level).

---

## 7. Data Extraction

### What

Transform the validated OpenAPI Pydantic models into an `APIBlueprint` containing language-agnostic `StandardOperation`, `StandardModel`, and `AuthScheme` instances defined in [02-architecture.md](02-architecture.md). This is the bridge between "OpenAPI world" and "generation world."

### Where

`src/ipe/core/analyzer.py` -- the SpecAnalyzer orchestrates all extraction. It receives parsed OpenAPI models and produces an `APIBlueprint`.

### Key Extractions

#### Operations (from `paths`)

- Each path + HTTP method combination becomes one `StandardOperation`
- Operations are grouped by tags (primary) or path analysis (fallback)
- Parameters are categorized: path, query, header, cookie
- Request body and response schemas are extracted and linked to models

#### Models (from `components/schemas`)

- Each named schema becomes one `StandardModel`
- Properties include type information, required status, validation constraints
- Enum values are extracted as distinct enum types
- Composition (`allOf`, `oneOf`, `anyOf`) is resolved into concrete model structures

#### Authentication (from `components/securitySchemes`)

- Supported in v0.1: `apiKey`, `http` (bearer, basic)
- Each scheme becomes an `AuthScheme` with enough information for targets to generate auth handling
- Security requirements on operations are linked to the corresponding scheme

#### Server URLs

- The first server URL becomes the default `base_url`
- Server variables are resolved to their default values
- If no servers are defined, no default `base_url` is set (the user must provide one)

---

## 8. Error Handling

Every error that surfaces to the user must be actionable. Cryptic stack traces are a failure of developer experience.

### Error Categories

| Category | Source | User-Facing Behavior |
|----------|--------|---------------------|
| **Fetch errors** | `fetcher.py` | Network issue described with suggestion (check URL, check connectivity, retry) |
| **Parse errors** | `openapi.py` | Invalid YAML/JSON with file location; invalid OpenAPI structure with JSON path |
| **Resolution errors** | `resolver.py` | Broken `$ref` with the reference path and what it pointed to |
| **Validation errors** | `openapi.py`, `analyzer.py` | Grouped by severity, each with location + problem + suggestion |
| **Unsupported features** | Throughout | Clear message stating what is not yet supported, with reference to future plans |

### Network Error Specifics

| Error | Message Pattern |
|-------|----------------|
| DNS failure | "Could not resolve host: {host}. Check the URL spelling." |
| Connection timeout | "Connection timed out after {n}s. The server may be down or the URL incorrect." |
| SSL error | "SSL certificate verification failed for {host}. If this is expected, this is not currently supported." |
| HTTP 4xx/5xx | "Server returned {status}: {reason}. Ensure the URL points to a valid OpenAPI specification." |

### Error Presentation

All errors are rendered through Rich console formatting (see [03-cli-interface.md](03-cli-interface.md) for output examples). Errors include:
- A clear header indicating the error type
- The specific problem with context
- An actionable suggestion when possible

---

## 9. Limitations (v0.1)

These features are explicitly out of scope for the initial release. They are documented here to set expectations and in [99-future-features.md](99-future-features.md) as future enhancements.

| Feature | Why Deferred |
|---------|-------------|
| **Links / Callbacks** | Rarely used in practice; adds significant parser complexity |
| **Webhooks** | OpenAPI 3.1 feature; requires different generation paradigm (server-side) |
| **Multi-file specs** | Requires relative/remote `$ref` resolution; single-file covers most use cases |
| **Swagger 2.0 conversion** | Conversion tools already exist; maintaining a converter is out of scope |
| **Circular schema support** | Requires lazy resolution strategy; clear error is provided instead |
| **XML content types** | JSON is the dominant format; XML support adds complexity with low demand |
| **`discriminator` mapping** | Complex union type handling deferred to post-MVP |

---

## 10. Phase & Timeline

### Position in Development Plan

OpenAPI support is **Phase 3** in the Ipê development roadmap.

| Phase | Focus | Status |
|-------|-------|--------|
| Phase 1 | Project setup, tooling, CI | Complete |
| Phase 2 | Configuration, CLI skeleton, exceptions | Complete |
| **Phase 3** | **OpenAPI parsing, validation, resolution** | **This spec** |
| Phase 4 | SpecAnalyzer (data extraction, APIBlueprint) | Depends on Phase 3 |
| Phase 5 | Target system and code generation | Depends on Phase 4 |

### Component Build Order

Components within Phase 3 are built in dependency order:

```
models.py          Define Pydantic models for OpenAPI structures
    |
    v
fetcher.py         Fetch and detect format of spec sources
    |
    v
resolver.py        Resolve all $ref pointers
    |
    v
openapi.py         Parse raw dict into validated Pydantic models
```

**Why this order:**
- `models.py` first because every other component depends on the type definitions
- `fetcher.py` next because it provides the raw input
- `resolver.py` before the main parser because resolution must happen before structural validation
- `openapi.py` last because it integrates all the above into the public parsing interface

### Phase 3 Exit Criteria

Phase 3 is complete when:
- A local YAML or JSON OpenAPI 3.0.x spec can be parsed into validated Pydantic models
- A local OpenAPI 3.1.x spec can be parsed with version-specific normalization
- Remote specs can be fetched via HTTPS and parsed identically to local files
- All local `$ref` pointers are resolved inline
- Circular references are detected and reported
- Structural and generation validation produce grouped, actionable errors
- Swagger 2.0 specs are rejected with a clear message
- All components have 90%+ test coverage
