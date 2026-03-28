# Configuration System Specification

## Overview

Ipê uses `ipe.json` as the source of truth for **project-level** code generation settings -- things that rarely change between runs. CLI arguments provide **execution-level** overrides for values that may vary per invocation.

### Resolution Priority

```
CLI arguments  >  ipe.json  >  smart defaults
```

A CLI flag always wins. `ipe.json` wins over built-in defaults. Smart defaults ensure the tool works with minimal configuration. This three-tier chain keeps every usage scenario -- from quick one-off generation to fully configured projects -- working without friction.

## What Lives Where

### Project settings (ipe.json)

Settings that define the project and stay stable across runs:

| Field | Description |
|---|---|
| `target` | Language target (e.g. `"python"`) |
| `module_name` | Name of the generated module |
| `spec_path` | Default path or URL to OpenAPI spec |
| `output_dir` | Default output directory |
| `targets.python.*` | Target-specific config (client_library, async_support, python_version) |
| `template_dir` | Custom template directory (v0.2+) |

### CLI-only flags

Flags that only make sense at execution time:

| Flag | Description |
|---|---|
| `--config` | Path to an alternative config file (default: `./ipe.json`) |

### Both (CLI overrides ipe.json)

Values that live in `ipe.json` as defaults but can be overridden per run:

| CLI arg | Overrides field |
|---|---|
| `SPEC` (positional) | `spec_path` |
| `--output` | `output_dir` |
| `--target` | `target` |
| `--module-name` | `module_name` |

## Configuration File: ipe.json

### Basic Structure

```json
{
  "target": "python",
  "output_dir": "./src/clients",
  "module_name": "api_client",
  "spec_path": "openapi.yaml",
  "targets": {
    "python": {
      "client_library": "httpx",
      "async_support": true,
      "python_version": "3.9"
    }
  }
}
```

### Required Fields

- `spec_path`: Path to OpenAPI specification file or URL

### Optional Fields

- `target`: Language target for code generation (default: `"python"`)
- `output_dir`: Directory where generated code will be written (default: `"./output"`)
- `module_name`: Name of the generated module (auto-detected from spec if omitted)
- `targets`: Target-specific configuration options
- `template_dir`: Path to custom Jinja2 templates directory (v0.2+)

## Configuration Schema

### Root Configuration

```python
class IpeConfig(BaseModel):
    target: str = "python"
    output_dir: Path = Path("./output")
    module_name: str | None = None
    spec_path: str = ""
    targets: dict[str, dict[str, Any]] = Field(default_factory=dict)
    template_dir: Path | None = None

    @field_validator("output_dir", mode="before")
    @classmethod
    def coerce_output_dir(cls, v: Any) -> Path:
        return Path(v)

    @field_validator("template_dir", mode="before")
    @classmethod
    def coerce_template_dir(cls, v: Any) -> Path | None:
        if v is None:
            return None
        return Path(v)

    @model_validator(mode="after")
    def ensure_target_config(self) -> "IpeConfig":
        if self.target not in self.targets:
            registry = TargetRegistry()
            target = registry.get(self.target)
            self.targets[self.target] = target.get_default_config()
        return self
```

Target validation is **not** hardcoded in the config model. The `TargetRegistry` is the single source of truth for which targets are available. If a target is not registered, `registry.get()` raises `UnsupportedLanguageError` with the list of available targets.

### Target-Specific Configuration

Target-specific config schemas are defined by each `LanguageTarget` implementation. See [02-architecture.md](02-architecture.md#target-implementation-example-python) for the Python target's `get_default_config()` and `validate_config()`.

## Configuration Loading

### ConfigManager

```python
class ConfigManager:
    def load_config(self, config_path: Path | None = None) -> IpeConfig:
        config_file = config_path or Path("./ipe.json")

        if not config_file.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_file}",
                suggestion="Run 'ipe init' to create a configuration file",
            )

        try:
            with open(config_file) as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {config_file}: {e}")
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load config from {config_file}: {e}"
            )

        return IpeConfig(**config_data)
```

## CLI Integration

### Resolution Logic

The `generate` command merges CLI arguments with the loaded config following the priority chain:

```python
@app.command()
def generate(
    spec: str | None = typer.Argument(
        None, help="OpenAPI spec path or URL (overrides config spec_path)"
    ),
    config: Path | None = typer.Option(
        None, "--config", help="Path to config file"
    ),
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Output directory (overrides config output_dir)"
    ),
    target: str | None = typer.Option(
        None, "--target", "-t", help="Language target (overrides config target)"
    ),
    module_name: str | None = typer.Option(
        None, "--module-name", "-m", help="Module name (overrides config module_name)"
    ),
) -> None:
    config_manager = ConfigManager()
    ipe_config = config_manager.load_config(config)

    # Resolution: CLI args > ipe.json > defaults
    final_spec = spec or ipe_config.spec_path
    final_output = output or ipe_config.output_dir
    final_target = target or ipe_config.target or "python"
    final_module_name = module_name or ipe_config.module_name

    if not final_spec:
        raise ConfigurationError(
            "No spec provided",
            suggestion="Pass a spec as argument or set spec_path in ipe.json",
        )

    # Apply resolved values
    ipe_config.spec_path = final_spec
    ipe_config.output_dir = final_output
    ipe_config.target = final_target
    if final_module_name:
        ipe_config.module_name = final_module_name

    generator = CodeGenerator()
    generator.run(ipe_config)
```

## Auto-Detection and Defaults

### Module Name Auto-Detection

```python
def resolve_module_name(config: IpeConfig, spec: ParsedSpec) -> str:
    if config.module_name:
        return config.module_name

    if spec.info.title:
        name = to_snake_case(spec.info.title.replace(" API", "").strip())
        return name if name else "api_client"

    return "api_client"
```

## Configuration Validation

### Pre-Generation Validation

```python
def validate_config_for_generation(config: IpeConfig) -> list[str]:
    errors: list[str] = []

    if config.spec_path.startswith(("http://", "https://")):
        pass  # URL reachability checked at fetch time
    else:
        spec_path = Path(config.spec_path)
        if not spec_path.exists():
            errors.append(
                f"OpenAPI specification file not found: {config.spec_path}"
            )

    output_parent = config.output_dir.parent
    if not output_parent.exists():
        errors.append(
            f"Output parent directory does not exist: {output_parent}"
        )

    if config.template_dir and not config.template_dir.is_dir():
        errors.append(
            f"Template directory does not exist: {config.template_dir}"
        )

    return errors
```

## Configuration Examples

### Minimal Configuration

```json
{
  "spec_path": "openapi.yaml"
}
```

### Complete Python Configuration

```json
{
  "target": "python",
  "output_dir": "./src/clients",
  "module_name": "petstore_client",
  "spec_path": "https://petstore3.swagger.io/api/v3/openapi.json",
  "targets": {
    "python": {
      "client_library": "httpx",
      "async_support": true,
      "python_version": "3.11",
      "use_pydantic_v2": true
    }
  }
}
```

### Custom Templates (v0.2+)

```json
{
  "target": "python",
  "output_dir": "./src/clients",
  "spec_path": "openapi.yaml",
  "template_dir": "./company-templates/python/"
}
```

## Configuration Creation (ipe init)

### Interactive Configuration Setup

```python
def create_config_interactively() -> IpeConfig:
    console.print("[bold]Welcome to Ipê! Let's set up your project.[/bold]")

    spec_path = Prompt.ask("OpenAPI specification path or URL")
    output_dir = Prompt.ask("Output directory", default="./src/clients")

    registry = TargetRegistry()
    target = prompt_choice("Language target", registry.list_languages())

    config_data = {
        "target": target,
        "output_dir": output_dir,
        "spec_path": spec_path,
    }

    with open("ipe.json", "w") as f:
        json.dump(config_data, f, indent=2)

    console.print("[green]Configuration saved to ipe.json[/green]")
    return IpeConfig(**config_data)
```

## Error Handling

### ConfigurationError

```python
class ConfigurationError(IpeError):
    def __init__(self, message: str, suggestion: str | None = None) -> None:
        self.suggestion = suggestion
        super().__init__(message)
```

### Example Error Messages

```
Configuration Error: Target 'java' is not supported

  Available targets:
    - python  Generate Python client with httpx

  Fix: Update your ipe.json:
    {
      "target": "python"
    }
```
