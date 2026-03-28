# Future Features

This document outlines planned features and enhancements for future releases of Ipê. These are explicitly **out of scope for v0.1** (MVP), which focuses on Python client generation from a single OpenAPI spec as an embedded module.

## v0.1 MVP Scope (for reference)

What ships in v0.1:
- Python target only (httpx + Pydantic)
- Embedded module output (not standalone package)
- Authentication: API key, Bearer token, Basic auth
- OpenAPI 3.0.x and 3.1.x support
- CLI: `generate`, `init`, `version`
- Configuration via `ipe.json`

Everything below is **post-MVP**.

---

## Template Customization (v0.2)

### Custom Template Directory
Users can provide their own Jinja2 templates to customize generated output, enabling company-specific code standards and patterns.

```json
{
  "target": "python",
  "template_dir": "./company-templates/python/"
}
```

**Partial override** is supported — override only `client.py.jinja` and inherit the rest from built-in templates. Uses Jinja2 `ChoiceLoader` for resolution: custom directory first, fallback to built-in.

See [02-architecture.md](02-architecture.md) for the template customization architecture.

### Installable Target Plugins
Third-party targets installable via pip:

```bash
pip install ipe-kotlin-target
ipe generate api.yaml --target kotlin
```

Enabled by `entry_points` discovery in the TargetRegistry.

---

## Additional Language Targets (v0.2+)

### TypeScript Target
- Client libraries: axios, fetch
- Module systems: ESM, CommonJS
- Strict TypeScript mode

### Go Target
- Standard library `net/http` or third-party clients
- Struct tags and interface generation

### Additional Languages
- Rust, Kotlin, Swift — based on community demand

---

## Built-in Extension System (v0.2+)

### Core Concept
Users select which extensions to include in generated output. All extensions are maintained as part of the core project.

```json
{
  "extensions": [
    "testing",
    "cli_wrapper",
    "fastapi_integration"
  ]
}
```

### Python Extensions

#### Testing Extension
Generates complete test suites:
- Mock server setup
- Model validation tests
- Authentication and error handling tests
- Integration test examples

#### CLI Wrapper Extension
Generates a CLI wrapper for the API client using Click/Typer.

#### FastAPI Integration Extension
Generates FastAPI dependencies and proxy endpoints for the API client.

#### Auto-Pagination Extension
Iterator patterns for paginated endpoints:

```python
for user in client.users.list_iter(status="active"):
    process(user)
```

### TypeScript Extensions

#### React Integration
React Query hooks for API operations.

#### Vue Integration
Vue.js composables for API integration.

---

## Package Output Type (v0.2+)

Generate standalone, publishable packages instead of embedded modules:

```bash
ipe generate api.yaml --output-type package --package-name my-api-sdk
```

Generated structure:
```
my-api-sdk/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/my_api_sdk/
│   ├── __init__.py
│   ├── client.py
│   └── models/
└── examples/
    └── basic_usage.py
```

---

## Advanced OpenAPI Support (v0.3+)

### Discriminated Unions
Full support for oneOf/anyOf with discriminator fields.

### Complex Schema Patterns
- Nested allOf/oneOf/anyOf combinations
- Schema composition and inheritance
- Complex property dependencies

### Multi-file Specs
Support for specs split across multiple files with relative $ref resolution.

### Webhooks
Support for OpenAPI 3.1 webhook definitions.

---

## Advanced Authentication (v0.3+)

- OAuth2 flows (authorization code, client credentials, etc.)
- OpenID Connect integration
- Automatic token refresh logic
- Mutual TLS authentication

---

## Performance Features (v0.3+)

### Connection Pooling
Configurable connection pool settings in generated clients.

### Retry Logic with Backoff
Configurable retry strategies with exponential backoff.

### Response Caching
Intelligent caching based on HTTP semantics (Cache-Control, ETags).

---

## Development Workflow Features (v0.3+)

### Watch Mode
Auto-regeneration when OpenAPI spec changes:
```bash
ipe generate --watch
```

### Validation Command
Standalone specification validation:
```bash
ipe validate api.yaml
```

### Target Discovery
List available targets:
```bash
ipe targets
```

### Diagnostic Tool
```bash
ipe doctor
```

---

## Template Hooks System (v0.4+)

Pre and post-generation hooks for advanced customization:

```
targets/{language}/hooks/
├── pre_gen.py
└── post_gen.py
```

---

## Implementation Timeline

| Phase | Version | Features |
|-------|---------|----------|
| Template Customization | v0.2 | Custom template_dir, partial override |
| Core Extensions | v0.2 | Auto-pagination, testing extension, package output |
| Additional Languages | v0.2+ | TypeScript, Go targets |
| Framework Integrations | v0.3 | React/Vue/FastAPI, CLI wrapper, docs generation |
| Advanced Features | v0.3+ | Advanced auth, performance, complex schemas |
| Hooks System | v0.4+ | Pre/post generation hooks, advanced customization |
