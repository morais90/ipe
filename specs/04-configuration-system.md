# Configuration System Specification

## Overview

Ipê uses a single `ipe.json` configuration file as the source of truth for all code generation settings. This file contains all the information needed to generate code from an OpenAPI specification.

## Configuration File: ipe.json

### Basic Structure
```json
{
  "generator": "python",
  "output_dir": "./src/clients",
  "module_name": "api_client",
  "spec_path": "openapi.yaml",
  "generators": {
    "python": {
      "client_library": "httpx",
      "async_support": true,
      "python_version": "3.9"
    },
    "typescript": {
      "client_library": "axios",
      "target": "es2020"
    }
  }
}
```

### Required Fields
- `generator`: Target language/framework for code generation
- `output_dir`: Directory where generated code will be written
- `spec_path`: Path to OpenAPI specification file or URL

### Optional Fields
- `module_name`: Name of the generated module (auto-detected from spec if not provided)
- `generators`: Language-specific configuration options

## Configuration Schema

### Root Configuration
```python
class IpeConfig(BaseModel):
    """Main configuration model"""
    generator: str = "python"
    output_dir: Path
    module_name: Optional[str] = None
    spec_path: str
    generators: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('generator')
    def validate_generator(cls, v):
        supported = ['python', 'typescript']
        if v not in supported:
            raise ValueError(f"Generator '{v}' not supported. Available: {supported}")
        return v
    
    @validator('output_dir')
    def validate_output_dir(cls, v):
        """Ensure output directory path is valid"""
        return Path(v)
    
    @root_validator
    def validate_generator_config(cls, values):
        """Ensure generator-specific config exists for selected generator"""
        generator = values.get('generator', 'python')
        generators = values.get('generators', {})
        
        if generator not in generators:
            # Set default configuration for the generator
            generators[generator] = DefaultGeneratorConfigs.get_default_config(generator)
            values['generators'] = generators
        
        return values
```

### Generator-Specific Configuration

#### Python Generator
```python
class PythonGeneratorConfig(BaseModel):
    """Python-specific configuration"""
    client_library: Literal["httpx", "requests"] = "httpx"
    async_support: bool = True
    python_version: str = "3.9"
    use_pydantic_v2: bool = True
    
    @validator('python_version')
    def validate_python_version(cls, v):
        """Ensure Python version is supported"""
        supported = ['3.9', '3.10', '3.11', '3.12']
        if v not in supported:
            raise ValueError(f"Python version '{v}' not supported")
        return v
```

#### TypeScript Generator  
```python
class TypeScriptGeneratorConfig(BaseModel):
    """TypeScript-specific configuration"""
    client_library: Literal["axios", "fetch"] = "axios"
    target: str = "es2020"
    module_system: Literal["esm", "commonjs"] = "esm"
    strict_mode: bool = True
```

## Configuration Loading

### Single Source Loading
```python
class ConfigManager:
    """Manages configuration loading and validation"""
    
    def load_config(self, config_path: Optional[Path] = None) -> IpeConfig:
        """Load configuration from ipe.json file"""
        config_file = config_path or Path("./ipe.json")
        
        if not config_file.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_file}",
                suggestion="Run 'ipe init' to create a configuration file"
            )
        
        try:
            with open(config_file) as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {config_file}: {e}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load config from {config_file}: {e}")
        
        # Validate and create config object
        return IpeConfig(**config_data)
```

## CLI Integration

### Commands Use Configuration File Only
The CLI commands read from `ipe.json` and do not accept configuration overrides:

```python
# CLI command implementation
@app.command()
def generate(
    spec: Optional[str] = typer.Argument(None, help="OpenAPI spec (overrides config file)"),
    config: Optional[Path] = typer.Option(None, "--config", help="Config file path")
):
    """Generate code from OpenAPI specification"""
    
    # Load configuration
    config_manager = ConfigManager()
    ipe_config = config_manager.load_config(config)
    
    # Allow spec to be provided as CLI argument
    if spec:
        ipe_config.spec_path = spec
    
    # Generate code using configuration
    generate_code(ipe_config)
```

## Auto-Detection and Defaults

### Module Name Auto-Detection
```python
def resolve_module_name(config: IpeConfig, spec: OpenAPISpec) -> str:
    """Resolve module name from config or auto-detect from spec"""
    if config.module_name:
        return config.module_name
    
    # Auto-detect from OpenAPI spec title
    if spec.info.title:
        # Convert "My API" -> "my_api"
        name = to_snake_case(spec.info.title.replace(" API", "").strip())
        return name if name else "api_client"
    
    return "api_client"
```

### Default Generator Configuration
```python
class DefaultGeneratorConfigs:
    """Default configurations for each generator"""
    
    PYTHON = {
        "client_library": "httpx",
        "async_support": True,
        "python_version": "3.9",
        "use_pydantic_v2": True
    }
    
    TYPESCRIPT = {
        "client_library": "axios",
        "target": "es2020", 
        "module_system": "esm",
        "strict_mode": True
    }
    
    @classmethod
    def get_default_config(cls, generator: str) -> Dict[str, Any]:
        """Get default configuration for a generator"""
        defaults = {
            "python": cls.PYTHON,
            "typescript": cls.TYPESCRIPT
        }
        return defaults.get(generator, {})
```

## Configuration Validation

### Comprehensive Validation
```python
def validate_config_for_generation(config: IpeConfig) -> List[str]:
    """Validate configuration is ready for code generation"""
    errors = []
    
    # Validate spec path
    if config.spec_path.startswith(('http://', 'https://')):
        # URL validation would be done during fetching
        pass
    else:
        spec_path = Path(config.spec_path)
        if not spec_path.exists():
            errors.append(f"OpenAPI specification file not found: {config.spec_path}")
    
    # Validate output directory parent exists
    output_parent = config.output_dir.parent
    if not output_parent.exists():
        errors.append(f"Output parent directory does not exist: {output_parent}")
    
    # Validate generator configuration
    generator_config = config.generators.get(config.generator)
    if not generator_config:
        errors.append(f"No configuration found for generator: {config.generator}")
    
    return errors
```

## Configuration Examples

### Minimal Configuration
```json
{
  "output_dir": "./src/clients",
  "spec_path": "openapi.yaml"
}
```

### Complete Python Configuration
```json
{
  "generator": "python",
  "output_dir": "./src/clients",
  "module_name": "petstore_client",
  "spec_path": "https://petstore3.swagger.io/api/v3/openapi.json",
  "generators": {
    "python": {
      "client_library": "httpx",
      "async_support": true,
      "python_version": "3.11",
      "use_pydantic_v2": true
    }
  }
}
```

### TypeScript Configuration
```json
{
  "generator": "typescript",
  "output_dir": "./src/clients",
  "module_name": "api_client",
  "spec_path": "./api-spec.yaml",
  "generators": {
    "typescript": {
      "client_library": "axios",
      "target": "es2020",
      "module_system": "esm",
      "strict_mode": true
    }
  }
}
```

## Configuration Creation (ipe init)

### Interactive Configuration Setup
```python
def create_config_interactively() -> IpeConfig:
    """Create configuration through interactive prompts"""
    console.print("🌳 Welcome to Ipê! Let's set up your project.")
    
    # Basic prompts
    spec_path = Prompt.ask("OpenAPI specification path or URL")
    output_dir = Prompt.ask("Output directory", default="./src/clients")
    generator = prompt_choice("Generator", ["python", "typescript"])
    
    # Generator-specific prompts
    generator_config = {}
    if generator == "python":
        client_lib = prompt_choice("HTTP client library", ["httpx", "requests"])
        async_support = Confirm.ask("Enable async support", default=True)
        generator_config = {
            "client_library": client_lib,
            "async_support": async_support
        }
    elif generator == "typescript":
        client_lib = prompt_choice("HTTP client library", ["axios", "fetch"])
        generator_config = {
            "client_library": client_lib
        }
    
    config_data = {
        "generator": generator,
        "output_dir": output_dir,
        "spec_path": spec_path,
        "generators": {
            generator: generator_config
        }
    }
    
    # Save to ipe.json
    with open("ipe.json", "w") as f:
        json.dump(config_data, f, indent=2)
    
    console.print("✅ Configuration saved to ipe.json")
    return IpeConfig(**config_data)
```

## Error Handling

### Clear Configuration Errors
```python
class ConfigurationError(IpeError):
    """Configuration validation failed"""
    
    def __init__(self, message: str, suggestion: Optional[str] = None):
        self.suggestion = suggestion
        super().__init__(message)

# Error display
def display_config_error(error: ConfigurationError):
    console.print(f"❌ Configuration Error: {error}")
    if error.suggestion:
        console.print(f"💡 {error.suggestion}")
```

### Example Error Messages
```
❌ Configuration Error: Generator 'java' is not supported

💡 Available generators:
   • python - Generate Python client with httpx
   • typescript - Generate TypeScript client with axios

🔧 Fix: Update your ipe.json:
   {
     "generator": "python"
   }
```

This simplified configuration system ensures that `ipe.json` is the single source of truth for all generation settings, making the system predictable and easy to understand without unnecessary complexity.