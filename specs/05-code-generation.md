# Code Generation Specification

## Overview

This spec defines **what** Ipê generates and **why** — the qualities, structure, and conventions of the generated code. For **how** the pipeline works (SpecAnalyzer, LanguageTarget, TemplateTreeRenderer), see [02-architecture.md](02-architecture.md).

Data models used in generation (APIBlueprint, StandardOperation, StandardModel, etc.) are defined in [02-architecture.md](02-architecture.md#canonical-data-models).

## Quality Principles

### 1. Resource-Based Client Organization
API operations are grouped into resources that mirror the API's path structure, creating intuitive client interfaces.

### 2. Strong Type Safety
Generated code carries comprehensive type annotations so static analysis catches errors before runtime.

### 3. Idiomatic Code
Output follows the conventions, patterns, and best practices of the target language. It should read as if written by an experienced developer.

### 4. Forward Compatibility
Generated clients handle unknown fields gracefully and tolerate evolving APIs without breaking.

### 5. Lint-Clean by Default
Output passes the target language's standard linter without configuration (Python: `ruff` clean).

## Developer Experience

The generated client provides an intuitive, discoverable surface that feels natural in the target language.

```python
from florada_payments.client import FloradaPaymentsClient

client = FloradaPaymentsClient(api_key="your-key")

# Resource-based access
charges = client.charges.list_charges(status="succeeded", limit=50)
charge = client.charges.get_charge(charge_id="ch_123")

# Nested resources are flattened with underscores
subscriptions = client.customers_subscriptions.list_subscriptions(
    customer_id="cu_456"
)
```

## v0.1 Generated Structure (Python)

```
florada_payments/
├── __init__.py                # Re-exports the client class
├── client.py                  # Main client with resource accessors
├── exceptions.py              # Exception hierarchy
├── models/
│   ├── __init__.py            # Lazy imports via __getattr__
│   ├── charge.py              # One file per schema
│   ├── create_charge_request.py
│   ├── customer.py
│   └── ...
└── resources/
    ├── __init__.py            # Sorted resource imports
    ├── charges.py             # One file per resource
    ├── customers.py
    └── ...
```

**One schema → one file.** Each model lives in its own module under `models/`. Lazy imports in `models/__init__.py` keep imports cheap.

**One resource → one file.** Resources are grouped by nested path (see below), one file each under `resources/`.

## Resource Grouping

Operations are grouped using **`by_nested_path`** (from `utils/grouping.py`). The bucket key is the dotted concatenation of non-parameter path segments; the resource file is the bucket key with dots replaced by underscores.

| Path | Bucket key | File |
|---|---|---|
| `GET /charges` | `charges` | `resources/charges.py` |
| `GET /charges/{id}` | `charges` | `resources/charges.py` |
| `POST /charges/{id}/capture` | `charges.capture` | `resources/charges_capture.py` |
| `GET /customers/{id}/subscriptions` | `customers.subscriptions` | `resources/customers_subscriptions.py` |

This produces fine-grained resources that map directly onto the URL hierarchy. Each resource class on the client (`client.customers_subscriptions`) corresponds to exactly one bucket.

OpenAPI tags are not currently used for grouping; the `by_tag` strategy exists in `utils/grouping.py` but is not the default. Targets can pick a different strategy without changing the renderer.

## Method Naming

Method names come from the operation's `operationId` run through the target's `NamingConvention.method_name`. For Python that's `snake_case` with a trailing underscore on Python keywords.

| operationId | Generated method |
|---|---|
| `listCharges` | `list_charges` |
| `getCharge` | `get_charge` |
| `createCharge` | `create_charge` |
| `captureCharge` | `capture_charge` |

Ipê does not currently infer CRUD verbs from HTTP method + path shape — it trusts the `operationId`. Specs without `operationId`s get a synthesized fallback (`{method}_{path_segments}`).

## Generated Exception Hierarchy

A fixed hierarchy is generated regardless of the spec. All exceptions inherit from `{ApiName}Error`, which carries `message`, `status_code`, and `response`.

```python
class FloradaPaymentsError(Exception):
    def __init__(self, message, status_code=None, response=None): ...

class BadRequestError(FloradaPaymentsError): pass
class UnauthorizedError(FloradaPaymentsError): pass
class ForbiddenError(FloradaPaymentsError): pass
class NotFoundError(FloradaPaymentsError): pass
class ConflictError(FloradaPaymentsError): pass
class ValidationError(FloradaPaymentsError): pass
class RateLimitError(FloradaPaymentsError): pass
class InternalServerError(FloradaPaymentsError): pass
```

The generated `client.py` uses `response.raise_for_status()` from httpx; the exception classes exist for downstream code to catch, but Ipê does not yet wire status codes to these classes automatically. Spec-driven mapping (only generating classes for status codes actually present in the spec, and dispatching to them on failed responses) is on the roadmap.

## Authentication

v0.1 supports **bearer-token auth inline in the client constructor**. The generated `client.py` accepts an `api_key` kwarg and sets `Authorization: Bearer <key>` on the underlying httpx client.

A dedicated `auth.py` module with pluggable handlers for API key, Basic, and OAuth2 flows is on the roadmap.

## Models

Each schema in `components/schemas` becomes a Pydantic `BaseModel` in its own file under `models/`. Field rendering rules:

- **Required + non-nullable**: `name: type`
- **Required + nullable**: `name: type | None`
- **Optional with default**: `name: type = <default>` (or `name: type | None = <default>` if nullable)
- **Optional without default**: `name: type | None = None`

Defaults render via the `pyval` Jinja filter (Python `repr`), so booleans, `None`, and strings round-trip correctly. Imports for `UUID`, `datetime`, `date`, and `Any` are computed automatically by the `type_imports` filter based on the resolved property types.

Schemas with `type: array` are skipped — they're treated as type aliases, not standalone models.

## Resource Files

Each resource file declares a `{Name}Resource` class that holds a reference to the shared `httpx.Client`. Operation methods:

- Take typed parameters (path params first, then query params with defaults).
- Build the URL via `.format(...)` for path params.
- Issue the request with `self._client.request(method, url, params=...)`.
- Call `response.raise_for_status()` and return `response.json()`.

Return types are currently `Any`. Typed responses tied to schema models are on the roadmap.

Operation docstrings carry the OpenAPI `summary`, `description`, and parameter descriptions, stripped of HTML/Markdown via the `strip_html` filter.

## Template Directory

Each target's templates are self-contained. The Python target's tree:

```
targets/python/templates/
├── __init__.py.jinja
├── client.py.jinja
├── exceptions.py.jinja
├── models/
│   ├── __init__.py.jinja
│   └── {name}.py.jinja        # Rendered once per model
└── resources/
    ├── __init__.py.jinja
    └── {name}.py.jinja        # Rendered once per resource
```

The `{name}.py.jinja` convention tells the renderer to repeat the template once per item in the matching context collection. See [02-architecture.md](02-architecture.md#4-templatetreerenderer-corerendererpy) for the convention's semantics.

## Quality Standards

### Checklist

- Every generated module compiles as valid Python.
- Every function parameter and return value is type-annotated.
- Model fields declare defaults or are marked required.
- Re-export `__init__.py` files provide a clean public surface (lazy for models).
- Exception classes carry `status_code` and `response` for debugging.
- Output passes `ruff` without configuration.

### Verified by Tests

Golden-file tests at the CLI boundary compare the full generated tree against `tests/fixtures/expected/florada/python/`. Any drift in generated output fails CI.

## Roadmap

Beyond v0.1, in rough priority order:

| Feature | Notes |
|---|---|
| Typed responses | Map response bodies to schema models, return `Pet` instead of `Any`. |
| Async client | `AsyncClient` variant generated alongside the sync one. |
| Status-code-driven exceptions | Only generate classes for codes in the spec; dispatch via response status. |
| Full `auth.py` module | API key, Basic, OAuth2 handlers as composable classes. |
| File upload methods | Detect `multipart/form-data` operations, expose `BinaryIO` parameters. |
| Tag-based grouping option | Make the grouping strategy configurable per target. |
| TypeScript target | Validate the target Protocol against a second language. |
