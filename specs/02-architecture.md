# Architecture Specification

## Overview

Ipê follows a **pipeline architecture** where the core engine handles OpenAPI parsing, validation, and generation orchestration, while language support is implemented through **pluggable targets**. The renderer uses **Jinja2** for template rendering and **pathlib** for file writing -- no external scaffolding tools required.

**MVP target (v0.1): Python only.** TypeScript and Go are planned for future releases but the architecture supports them from day one.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SPEC ANALYZER                             │
│  Knows: OpenAPI. Knows nothing about languages.             │
├─────────────────────────────────────────────────────────────┤
│  * OpenAPI Parsing & Validation                             │
│  * $ref Resolution & Normalization                          │
│  * Data Extraction → APIBlueprint                           │
└──────────────────────────┬──────────────────────────────────┘
                           │ APIBlueprint
              ┌────────────▼────────────┐
              │    LANGUAGE TARGET      │
              │    (Protocol)           │
              │  Knows: its language.   │
              │  Knows nothing about    │
              │  OpenAPI or I/O.        │
              └────────────┬────────────┘
                           │ list[OutputFile]
              ┌────────────▼────────────┐
              │   TEMPLATE RENDERER     │
              │  Knows: Jinja2 + fs.    │
              │  Knows nothing about    │
              │  OpenAPI or languages.  │
              └─────────────────────────┘
```

Orchestrated by:

```
┌─────────────────────────────────────────────────────────────┐
│                    CODE GENERATOR                            │
│  The pipeline coordinator. Knows nothing about specifics.   │
│  Connects: SpecAnalyzer → LanguageTarget → TemplateRenderer │
└─────────────────────────────────────────────────────────────┘
```

## Generation Pipeline

```
CLI → CodeGenerator.run(config)
  → SpecAnalyzer.parse(spec_path)            → ParsedSpec (OpenAPI Pydantic models)
  → SpecAnalyzer.extract(spec, config)       → APIBlueprint (language-agnostic)
  → LanguageTarget.transform(blueprint)      → dict[str, Any] (language-specific)
  → LanguageTarget.plan(data)                → list[OutputFile] (render instructions)
  → TemplateRenderer.render(plan, out_dir)   → list[Path] (written files)
```

## Core Components

### 1. SpecAnalyzer (`src/ipe/core/analyzer.py`)
**Knows OpenAPI. Knows nothing about languages.**

Parses, validates, resolves $refs, and extracts a language-agnostic `APIBlueprint`.

```python
class SpecAnalyzer:

    def parse(self, spec_path: str) -> ParsedSpec:
        """Parse and validate an OpenAPI specification.

        Loads from local files or URLs, resolves $ref pointers,
        validates OpenAPI 3.0.x / 3.1.x compliance.
        """
        ...

    def extract(self, spec: ParsedSpec, config: IpeConfig) -> APIBlueprint:
        """Extract a language-agnostic API blueprint.

        Converts parsed OpenAPI models into StandardOperation,
        StandardModel, and AuthScheme instances grouped by resource.
        """
        ...
```

The analyzer handles all OpenAPI complexity and provides a clean `APIBlueprint` to language targets. **Type mapping is NOT an analyzer responsibility** -- each target owns the conversion from OpenAPI types to language-native types.

### 2. LanguageTarget (`src/ipe/targets/base.py`)
**Knows its language. Knows nothing about OpenAPI or I/O.**

Protocol-based contract. Any class that satisfies the protocol is a valid target -- no inheritance required.

```python
from typing import Any, Protocol

from pathlib import Path


class NamingConvention(Protocol):
    """Contract for language-specific naming rules."""

    def class_name(self, raw: str) -> str: ...
    def method_name(self, raw: str) -> str: ...
    def field_name(self, raw: str) -> str: ...
    def module_name(self, raw: str) -> str: ...


class LanguageTarget(Protocol):
    """Contract for language-specific code generation.

    Each implementation is responsible for:
    - Transforming the APIBlueprint into language-specific template data
    - Mapping OpenAPI types to language-native types
    - Planning which files to generate and with what data
    """

    @property
    def name(self) -> str:
        """Unique identifier (e.g., 'python', 'typescript')."""
        ...

    @property
    def naming(self) -> NamingConvention:
        """Naming convention for this language."""
        ...

    def transform(self, blueprint: APIBlueprint) -> dict[str, Any]:
        """Transform API blueprint into language-specific template data.

        This is where type mapping happens. The target converts
        OpenAPI types (string, integer, array, etc.) into language-native
        types (str, int, list[T], etc.).
        """
        ...

    def plan(self, data: dict[str, Any]) -> list[OutputFile]:
        """Plan which files to generate.

        Returns a list of OutputFile instructions. Each instruction
        specifies which template to render, where to write it,
        and what data to pass. The target decides everything about
        the output structure -- the renderer just executes.
        """
        ...

    def get_template_dir(self) -> Path:
        """Return the directory containing .jinja template files."""
        ...

    def validate_config(self, config: dict[str, Any]) -> bool:
        """Validate language-specific configuration."""
        ...

    def get_default_config(self) -> dict[str, Any]:
        """Provide default configuration for this language."""
        ...
```

### 3. TargetRegistry (`src/ipe/targets/registry.py`)
**Explicit registration of language targets**

```python
class TargetRegistry:

    def __init__(self) -> None:
        self._targets: dict[str, LanguageTarget] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        from ipe.targets.python.target import PythonTarget

        self.register(PythonTarget())

    def register(self, target: LanguageTarget) -> None:
        """Register a language target."""
        self._targets[target.name] = target

    def get(self, language: str) -> LanguageTarget:
        """Retrieve target for specified language."""
        if language not in self._targets:
            raise UnsupportedLanguageError(
                language, available=list(self._targets)
            )
        return self._targets[language]

    def list_languages(self) -> list[str]:
        """Get list of all registered languages."""
        return list(self._targets.keys())
```

No filesystem scanning or dynamic discovery. Built-in targets are imported explicitly; third-party targets call `register()`.

### 4. TemplateRenderer (`src/ipe/core/renderer.py`)
**Knows Jinja2 + filesystem. Knows nothing about OpenAPI or languages.**

Executes a list of `OutputFile` instructions. Does not decide what to render or where -- that's the target's job.

```python
from pathlib import Path

from jinja2 import ChoiceLoader, Environment, FileSystemLoader


class TemplateRenderer:

    def __init__(
        self, template_dir: Path, custom_dir: Path | None = None
    ) -> None:
        loaders: list[FileSystemLoader] = []
        if custom_dir is not None:
            loaders.append(FileSystemLoader(str(custom_dir)))
        loaders.append(FileSystemLoader(str(template_dir)))

        self._env = Environment(
            loader=ChoiceLoader(loaders),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render(
        self,
        plan: list[OutputFile],
        output_dir: Path,
    ) -> list[Path]:
        """Execute a render plan. Returns list of written file paths."""
        written: list[Path] = []

        for output_file in plan:
            target_path = output_dir / output_file.output_path
            target_path.parent.mkdir(parents=True, exist_ok=True)

            template = self._env.get_template(output_file.template)
            content = template.render(output_file.context)
            target_path.write_text(content, encoding="utf-8")
            written.append(target_path)

        return written

    def dry_run(self, plan: list[OutputFile], output_dir: Path) -> list[Path]:
        """Preview which files would be written without writing them."""
        return [output_dir / f.output_path for f in plan]
```

### 5. CodeGenerator (`src/ipe/core/generator.py`)
**The pipeline coordinator. Knows nothing about specifics.**

Connects SpecAnalyzer, LanguageTarget, and TemplateRenderer in sequence.

```python
class CodeGenerator:

    def __init__(self) -> None:
        self.analyzer = SpecAnalyzer()
        self.registry = TargetRegistry()

    def run(self, config: IpeConfig) -> GenerationResult:
        """Execute the full generation pipeline."""
        # 1. Analyze OpenAPI spec → language-agnostic blueprint
        spec = self.analyzer.parse(config.spec_path)
        blueprint = self.analyzer.extract(spec, config)

        # 2. Transform blueprint → language-specific data + render plan
        target = self.registry.get(config.target)
        data = target.transform(blueprint)
        plan = target.plan(data)

        # 3. Render templates → files on disk
        renderer = TemplateRenderer(
            template_dir=target.get_template_dir(),
            custom_dir=config.template_dir,
        )
        written_files = renderer.render(plan, config.output_dir)

        return GenerationResult(files=written_files, target=target.name)
```

## Canonical Data Models

**This specification is the single source of truth for all data models below.** Other specs (03-cli, 04-config, 05-codegen, 06-openapi) must reference these definitions, not redefine them.

### OutputFile

The instruction that connects LanguageTarget to TemplateRenderer:

```python
@dataclass
class OutputFile:
    """A single file to be rendered and written."""

    template: str           # which .jinja template to use
    output_path: str        # where to write (relative to output_dir)
    context: dict[str, Any] # data for this specific render
```

### APIBlueprint (Language-Agnostic)

```python
@dataclass
class APIBlueprint:
    """Normalized API representation produced by SpecAnalyzer."""

    # Specification metadata
    api_name: str
    spec_version: str
    spec_description: str | None
    base_url: str | None
    server_urls: list[str]

    # Extracted data (flat, for direct access)
    operations: list[StandardOperation]
    models: list[StandardModel]
    auth_schemes: list[AuthScheme]

    # Grouped by resource (for targets that need it)
    resources: dict[str, list[StandardOperation]]

    # Generation metadata
    module_name: str
    generated_at: str
    ipe_version: str
    generator_config: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict for Jinja2 consumption."""
        ...
```

### StandardOperation

```python
@dataclass
class StandardOperation:
    operation_id: str
    method: str          # GET, POST, PUT, PATCH, DELETE
    path: str            # /users/{user_id}
    summary: str | None
    description: str | None
    tags: list[str]
    parameters: list[StandardParameter]
    request_body: RequestBody | None
    responses: list[Response]
    security: list[SecurityRequirement]
```

### StandardParameter

```python
@dataclass
class StandardParameter:
    name: str
    location: str        # path, query, header, cookie
    required: bool
    description: str | None
    schema_type: str     # OpenAPI type: string, integer, boolean, etc.
    schema_format: str | None  # date-time, int64, uuid, etc.
    default: Any | None
```

### StandardModel

```python
@dataclass
class StandardModel:
    name: str
    description: str | None
    properties: list[StandardProperty]
    required_fields: list[str]
    validation_rules: list[ValidationRule]
```

### StandardProperty

```python
@dataclass
class StandardProperty:
    name: str
    description: str | None
    schema_type: str          # OpenAPI type
    schema_format: str | None
    required: bool
    nullable: bool
    default: Any | None
    enum_values: list[Any] | None
```

### RequestBody

```python
@dataclass
class RequestBody:
    required: bool
    description: str | None
    content_types: list[str]  # application/json, multipart/form-data, etc.
    schema_type: str          # OpenAPI type or $ref model name
    schema_format: str | None
```

### Response

```python
@dataclass
class Response:
    status_code: str          # "200", "404", "default"
    description: str | None
    content_type: str | None
    schema_type: str | None
    schema_format: str | None
```

### AuthScheme

```python
@dataclass
class AuthScheme:
    name: str
    type: str                 # apiKey, http, oauth2, openIdConnect
    scheme: str | None        # bearer, basic (for type=http)
    location: str | None      # header, query, cookie (for type=apiKey)
    header_name: str | None   # X-API-Key, Authorization, etc.
```

### ValidationRule

```python
@dataclass
class ValidationRule:
    rule_type: str            # min_length, max_length, pattern, minimum, etc.
    value: Any                # The constraint value
```

### SecurityRequirement

```python
@dataclass
class SecurityRequirement:
    scheme_name: str
    scopes: list[str]
```

## NamingConvention Protocol

Each language target provides a `NamingConvention` that handles language-specific naming rules. This is composition, not inheritance -- targets use it, they're not forced into a hierarchy.

```python
class PythonNaming:
    """Python naming conventions: snake_case methods, PascalCase classes."""

    def class_name(self, raw: str) -> str:
        return to_pascal_case(raw)

    def method_name(self, raw: str) -> str:
        return to_snake_case(raw)

    def field_name(self, raw: str) -> str:
        return to_snake_case(raw)

    def module_name(self, raw: str) -> str:
        return to_snake_case(raw)


class TypeScriptNaming:
    """TypeScript naming: camelCase methods, PascalCase classes."""

    def class_name(self, raw: str) -> str:
        return to_pascal_case(raw)

    def method_name(self, raw: str) -> str:
        return to_camel_case(raw)

    def field_name(self, raw: str) -> str:
        return to_camel_case(raw)

    def module_name(self, raw: str) -> str:
        return to_kebab_case(raw)
```

Utility functions (`to_snake_case`, `to_pascal_case`, etc.) live in `src/ipe/utils/naming.py`.

## Target Implementation Example (Python)

```python
class PythonTarget:
    """Python language target for code generation."""

    TYPE_MAP: ClassVar[dict[tuple[str, str | None], str]] = {
        ("string", None): "str",
        ("string", "date-time"): "datetime",
        ("string", "date"): "date",
        ("string", "uuid"): "UUID",
        ("string", "binary"): "bytes",
        ("integer", None): "int",
        ("integer", "int64"): "int",
        ("number", None): "float",
        ("number", "double"): "float",
        ("boolean", None): "bool",
        ("array", None): "list",
        ("object", None): "dict[str, Any]",
    }

    def __init__(self) -> None:
        self._naming = PythonNaming()

    @property
    def name(self) -> str:
        return "python"

    @property
    def naming(self) -> PythonNaming:
        return self._naming

    def transform(self, blueprint: APIBlueprint) -> dict[str, Any]:
        return {
            **blueprint.to_dict(),
            "python_models": self._transform_models(blueprint.models),
            "python_operations": self._transform_operations(blueprint.operations),
            "error_mappings": self._get_error_mappings(),
        }

    def plan(self, data: dict[str, Any]) -> list[OutputFile]:
        module = data["module_name"]
        files = [
            OutputFile("__init__.py.jinja", f"{module}/__init__.py", data),
            OutputFile("client.py.jinja", f"{module}/client.py", data),
            OutputFile("exceptions.py.jinja", f"{module}/exceptions.py", data),
            OutputFile("auth.py.jinja", f"{module}/auth.py", data),
            OutputFile(
                "models/__init__.py.jinja",
                f"{module}/models/__init__.py",
                data,
            ),
            OutputFile(
                "resources/__init__.py.jinja",
                f"{module}/resources/__init__.py",
                data,
            ),
        ]

        # Per-resource files
        for resource_name, ops in data["resources"].items():
            resource_data = {**data, "resource_name": resource_name, "operations": ops}
            files.append(OutputFile(
                "resources/resource.py.jinja",
                f"{module}/resources/{resource_name}.py",
                resource_data,
            ))

        # Per-model files
        for group_name, models in data.get("model_groups", {}).items():
            model_data = {**data, "group_name": group_name, "models": models}
            files.append(OutputFile(
                "models/model.py.jinja",
                f"{module}/models/{group_name}.py",
                model_data,
            ))

        return files

    def get_template_dir(self) -> Path:
        return Path(__file__).parent / "templates"

    def validate_config(self, config: dict[str, Any]) -> bool:
        ...

    def get_default_config(self) -> dict[str, Any]:
        return {
            "client_library": "httpx",
            "async_support": True,
            "python_version": "3.9",
            "use_pydantic_v2": True,
        }

    def _get_error_mappings(self) -> dict[int, str]:
        return {
            400: "BadRequestError",
            401: "UnauthorizedError",
            403: "ForbiddenError",
            404: "NotFoundError",
            409: "ConflictError",
            422: "ValidationError",
            429: "RateLimitError",
            500: "InternalServerError",
            502: "BadGatewayError",
            503: "ServiceUnavailableError",
        }
```

## Template Customization (v0.2+)

Users can override individual Jinja2 templates without forking the entire target. This is configured via the `template_dir` field in `ipe.json`.

### How It Works

1. User sets `template_dir` in `ipe.json`:

```json
{
  "target": "python",
  "template_dir": "./my-templates"
}
```

2. The `TemplateRenderer` uses Jinja2 `ChoiceLoader` to check the custom directory first, then fall back to the built-in templates (see TemplateRenderer implementation above).

### Partial Override

Users only need to provide the templates they want to customize:

```
my-templates/
└── client.py.jinja    # Custom client template
                       # models/, exceptions.py.jinja, etc.
                       # inherited from built-in target
```

## Module Organization

```
src/ipe/
├── __init__.py                      # Public API exports
├── cli/                             # Command-line interface
│   ├── main.py                      # CLI application and routing
│   └── console.py                   # Rich console utilities
├── core/                            # PIPELINE COMPONENTS
│   ├── __init__.py
│   ├── analyzer.py                  # SpecAnalyzer (OpenAPI → APIBlueprint)
│   ├── generator.py                 # CodeGenerator (pipeline coordinator)
│   ├── renderer.py                  # TemplateRenderer (Jinja2 + pathlib)
│   ├── config.py                    # Configuration management
│   └── exceptions.py                # Core exception hierarchy
├── parsers/                         # OpenAPI specification parsing
│   ├── __init__.py
│   ├── openapi.py                   # Main OpenAPI parser
│   ├── models.py                    # Pydantic models for OpenAPI structures
│   ├── resolver.py                  # $ref resolution
│   └── fetcher.py                   # URL and file fetching
├── targets/                         # LANGUAGE TARGET SYSTEM
│   ├── __init__.py
│   ├── base.py                      # LanguageTarget + NamingConvention Protocols
│   ├── registry.py                  # TargetRegistry with register()
│   └── python/                      # Python target (v0.1)
│       ├── target.py                # PythonTarget implementation
│       ├── naming.py                # PythonNaming implementation
│       └── templates/               # Jinja2 .jinja files
├── models/                          # Shared data models
│   ├── __init__.py
│   ├── blueprint.py                 # APIBlueprint, OutputFile
│   └── standard.py                  # StandardOperation, StandardModel, etc.
└── utils/                           # Shared utilities
    └── naming.py                    # to_snake_case, to_pascal_case, etc.
```

## Architecture Benefits

### Separation of Concerns
- **SpecAnalyzer**: Handles OpenAPI complexity once for all languages
- **LanguageTarget**: Focuses on language-specific code generation and type mapping
- **TemplateRenderer**: Handles Jinja2 rendering and disk I/O
- **CodeGenerator**: Coordinates the pipeline without knowing details

### Language Extensibility
- Add new languages by implementing the `LanguageTarget` Protocol and calling `registry.register()`
- No inheritance required -- structural subtyping via Protocol
- Each target is self-contained and independently developed

### Testability
- Each component testable in isolation
- Protocol-based design enables easy test doubles
- `dry_run()` on TemplateRenderer enables output preview without I/O

### Future-Proofing
- New OpenAPI features added to SpecAnalyzer automatically benefit all languages
- `register()` API enables third-party and community-contributed targets
- `ChoiceLoader` enables template customization without forking

## Implementation Strategy

### Phase 1: Foundation + Python (v0.1)
Build the pipeline with Python as the sole built-in target. This validates the architecture end-to-end: parsing, blueprint extraction, type mapping, Jinja2 rendering, and file writing.

### Phase 2: Template Customization + TypeScript (v0.2+)
Add `ChoiceLoader`-based template customization and the TypeScript target to validate that the design handles diverse language requirements.

### Phase 3: Ecosystem Expansion (v0.3+)
Additional language targets (Go, Rust) and community contributions via `register()`. Entry_points discovery for pip-installable targets.
