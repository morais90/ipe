# Architecture Specification - Kernel-Based Design

## Overview

Ipê follows a **kernel architecture** where the core engine handles OpenAPI parsing, validation, and generation orchestration, while language support is implemented through **pluggable template systems**. This design enables comprehensive multi-language support while maintaining a robust, shared foundation.

## Kernel Architecture Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    IPÊ KERNEL (Core Engine)                 │
├─────────────────────────────────────────────────────────────┤
│  • OpenAPI Parsing & Validation (language-agnostic)        │
│  • Data Extraction & Normalization                         │
│  • Template Context Preparation                            │
│  • Generation Orchestration                                │
└─────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │   TEMPLATE INTERFACE    │
                 │   (Standardized API)    │
                 └────────────┬────────────┘
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
┌───▼───┐                 ┌───▼───┐                 ┌───▼───┐
│Python │                 │TypeScript│              │  Go   │
│Template│                │Template  │              │Template│
│Plugin │                 │Plugin    │              │Plugin │
└───────┘                 └─────────┘              └───────┘
```

## Core Kernel Components

### 1. OpenAPI Engine (`src/ipe/core/kernel.py`)
**Language-agnostic OpenAPI processing**

```python
class OpenAPIKernel:
    """Core engine for OpenAPI specification processing"""
    
    def parse_and_validate(self, spec_path: str) -> ParsedSpec:
        """Parse and validate OpenAPI specification"""
        # Load from local files or URLs
        # Validate OpenAPI 3.x compliance
        # Return normalized representation
        pass
    
    def extract_operations(self, spec: ParsedSpec) -> List[StandardOperation]:
        """Extract operations in language-agnostic format"""
        # Group operations by resource (tags or path analysis)
        # Normalize parameters, request/response bodies
        # Detect standard CRUD patterns
        pass
    
    def extract_models(self, spec: ParsedSpec) -> List[StandardModel]:
        """Extract data models in language-agnostic format"""
        # Parse schema definitions
        # Extract properties and validation rules
        # Handle complex types and references
        pass
    
    def prepare_context(self, spec: ParsedSpec, config: Config) -> TemplateContext:
        """Create standardized template context"""
        # Combine extracted data
        # Add generation metadata
        # Provide language-agnostic representation
        pass
```

The kernel handles all OpenAPI complexity and provides a clean, standardized interface to language templates.

### 2. Template Interface (`src/ipe/templates/base.py`)
**Standardized contract for language templates**

```python
from abc import ABC, abstractmethod

class LanguageTemplate(ABC):
    """Interface for language-specific code generation"""
    
    @property
    @abstractmethod
    def language_name(self) -> str:
        """Unique identifier for this language (e.g., 'python', 'typescript')"""
        pass
    
    @abstractmethod
    def transform_context(self, context: TemplateContext) -> Dict[str, Any]:
        """Transform kernel context to language-specific template data"""
        pass
    
    @abstractmethod
    def get_output_structure(self) -> Dict[str, str]:
        """Define the file structure that will be generated"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate language-specific configuration"""
        pass
    
    @abstractmethod
    def get_default_config(self) -> Dict[str, Any]:
        """Provide default configuration for this language"""
        pass
```

This interface enables any language to be supported while maintaining consistency in the generation process.

### 3. Generation Orchestrator (`src/ipe/core/generation.py`)
**Coordinates kernel and templates**

```python
class GenerationEngine:
    """Orchestrates the complete generation process"""
    
    def __init__(self):
        self.kernel = OpenAPIKernel()
        self.template_registry = TemplateRegistry()
    
    def generate(self, config: IpeConfig) -> GenerationResult:
        """Execute the generation pipeline"""
        
        # 1. Language-agnostic processing
        spec = self.kernel.parse_and_validate(config.spec_path)
        context = self.kernel.prepare_context(spec, config)
        
        # 2. Language-specific processing
        template = self.template_registry.get_template(config.generator)
        template_data = template.transform_context(context)
        
        # 3. Code generation using Copier
        return self._run_copier_generation(
            template.template_directory,
            config.output_dir,
            template_data
        )
```

## Template Plugin System

### Template Directory Structure
Each language is implemented as a self-contained template plugin:

```
src/ipe/templates/
├── base.py                          # Template interface
├── registry.py                      # Template discovery and management
├── python/                          # Python language template
│   ├── plugin.py                    # PythonTemplate implementation
│   ├── copier.yml                   # Copier configuration
│   └── {{module_name}}/             # Generated code structure
│       ├── __init__.py.jinja
│       ├── client.py.jinja
│       ├── models.py.jinja
│       └── exceptions.py.jinja
├── typescript/                      # TypeScript language template
│   ├── plugin.py                    # TypeScriptTemplate implementation
│   ├── copier.yml
│   └── {{module_name}}/
└── go/                             # Go language template
    ├── plugin.py                    # GoTemplate implementation
    ├── copier.yml
    └── {{module_name}}/
```

### Language Template Implementation

```python
class PythonTemplate(LanguageTemplate):
    """Python code generation template"""
    
    @property
    def language_name(self) -> str:
        return "python"
    
    def transform_context(self, context: TemplateContext) -> Dict[str, Any]:
        """Add Python-specific transformations"""
        return {
            **context.to_dict(),
            
            # Resource-based organization
            "resources": self._organize_by_resources(context.operations),
            
            # Python-specific naming and types
            "python_models": self._transform_models(context.models),
            "python_operations": self._transform_operations(context.operations),
            
            # Error handling configuration
            "error_mappings": self._get_error_mappings(),
        }
    
    def _organize_by_resources(self, operations: List[StandardOperation]):
        """Group operations by resource for intuitive client organization"""
        # Implementation details for resource grouping
        pass
    
    def _transform_models(self, models: List[StandardModel]):
        """Convert to Python-specific model representations"""
        # Implementation details for model transformation
        pass
```

## Standardized Data Models

### Template Context (Language Agnostic)
```python
@dataclass
class TemplateContext:
    """Normalized data provided by kernel to all templates"""
    
    # Specification metadata
    module_name: str
    spec_title: str
    spec_version: str
    spec_description: Optional[str]
    base_url: Optional[str]
    
    # Extracted OpenAPI data
    operations: List[StandardOperation]
    models: List[StandardModel]
    auth_schemes: List[AuthScheme]
    
    # Generation metadata
    generated_at: str
    ipe_version: str
    generator_config: Dict[str, Any]

@dataclass
class StandardOperation:
    """Language-agnostic operation representation"""
    operation_id: str
    method: str
    path: str
    summary: Optional[str]
    description: Optional[str]
    tags: List[str]
    parameters: List[StandardParameter]
    request_body: Optional[RequestBody]
    responses: List[Response]
    security: List[SecurityRequirement]

@dataclass
class StandardModel:
    """Language-agnostic model representation"""
    name: str
    description: Optional[str]
    properties: List[StandardProperty]
    required_fields: List[str]
    validation_rules: List[ValidationRule]
```

## Template Discovery and Management

```python
class TemplateRegistry:
    """Discovers and manages language template plugins"""
    
    def __init__(self):
        self._templates = {}
        self._discover_templates()
    
    def _discover_templates(self):
        """Automatically discover available template plugins"""
        template_dirs = (Path(__file__).parent / "templates").glob("*/")
        
        for template_dir in template_dirs:
            plugin_file = template_dir / "plugin.py"
            if plugin_file.exists():
                plugin = self._load_plugin(plugin_file)
                self._templates[plugin.language_name] = plugin
    
    def get_template(self, language: str) -> LanguageTemplate:
        """Retrieve template plugin for specified language"""
        if language not in self._templates:
            raise UnsupportedLanguageError(f"No template available for {language}")
        return self._templates[language]
    
    def list_supported_languages(self) -> List[str]:
        """Get list of all supported languages"""
        return list(self._templates.keys())
```

## Module Organization

```
src/ipe/
├── __init__.py                      # Public API exports
├── cli/                             # Command-line interface
│   ├── main.py                      # CLI application and routing
│   └── console.py                   # Rich console utilities
├── core/                            # KERNEL COMPONENTS
│   ├── __init__.py
│   ├── kernel.py                    # OpenAPI processing engine
│   ├── generation.py                # Generation orchestrator
│   ├── config.py                    # Configuration management
│   └── exceptions.py                # Core exception hierarchy
├── parsers/                         # OpenAPI specification parsing
│   ├── __init__.py
│   ├── openapi.py                   # Main OpenAPI parser
│   ├── models.py                    # Pydantic models for OpenAPI
│   └── fetcher.py                   # URL and file fetching
├── templates/                       # TEMPLATE PLUGIN SYSTEM
│   ├── __init__.py
│   ├── base.py                      # Template interface definition
│   ├── registry.py                  # Template discovery and management
│   ├── python/                      # Python template plugin
│   ├── typescript/                  # TypeScript template plugin
│   └── go/                          # Go template plugin
└── utils/                           # Shared utilities
    ├── naming.py                    # Naming convention utilities
    └── types.py                     # Type mapping utilities
```

## Architecture Benefits

### Separation of Concerns
- **Kernel**: Handles OpenAPI complexity once for all languages
- **Templates**: Focus purely on language-specific code generation
- **Interface**: Clean contract between components

### Language Extensibility
- Add new languages without modifying kernel code
- Each template is self-contained and independently developed
- Consistent generation process across all languages

### Maintainability
- Core OpenAPI bugs fixed once benefit all languages  
- Language-specific issues isolated to individual templates
- Clear boundaries enable independent development

### Quality Assurance
- Kernel thoroughly tested provides reliable foundation
- Template-specific tests focus on generated code quality
- Consistent validation across all supported languages

### Future-Proofing
- New OpenAPI features added to kernel automatically benefit all languages
- Template format can evolve without breaking existing templates
- Natural foundation for community-contributed templates

## Implementation Strategy

The kernel architecture enables a phased approach to implementation:

### Phase 1: Kernel Foundation
Build robust kernel with Python template to validate the architecture.

### Phase 2: Multi-Language Validation  
Add TypeScript template to ensure kernel design handles diverse language requirements.

### Phase 3: Ecosystem Expansion
Additional language templates and community contributions.

This architecture provides a solid foundation for comprehensive multi-language OpenAPI code generation while maintaining consistency, quality, and developer experience across all supported languages.