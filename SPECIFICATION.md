# Ipê - Technical Specification

*A next-generation OpenAPI code generator with an obsession for developer experience*

## Overview

This document serves as the entry point to Ipê's complete technical specification. For detailed information on specific domains, see the organized specifications in the `specs/` directory.

**Quick Navigation:**
- [📋 Complete Specifications](specs/README.md) - Organized specification index
- [🌳 Project Overview](specs/01-project-overview.md) - Vision and core philosophy
- [🏗️ Architecture](specs/02-architecture.md) - System design and data flow
- [💻 CLI Interface](specs/03-cli-interface.md) - Command-line interface specification
- [⚙️ Configuration](specs/04-configuration-system.md) - Settings and configuration management
- [🔧 Code Generation](specs/05-code-generation.md) - Template-based generation system

## What is Ipê?

Ipê is a blazingly fast, developer-first Python CLI tool that transforms OpenAPI specifications into beautiful, production-ready code. Named after the stunning Brazilian tree known for its vibrant blooms, Ipê brings the same elegance and reliability to code generation.

## Core Philosophy: Developer Experience Above All

- ⚡ **Lightning Fast**: Sub-second generation for most specs
- 🎨 **Beautiful Output**: Rich CLI with progress indicators and syntax highlighting
- 🧠 **Intelligent Defaults**: Works perfectly out-of-the-box, customizable when needed
- 📚 **Exceptional Documentation**: Every feature explained with examples
- 🔧 **Simple & Clean**: Single configuration file, focused feature set

## Quick Start

### Installation
```bash
pip install ipe
```

### Basic Usage
```bash
# Initialize project configuration
ipe init

# Generate code from OpenAPI spec
ipe generate openapi.yaml --output ./src/clients/
```

### Generated Client Usage
```python
from petstore.client import PetStoreClient

client = PetStoreClient(api_key="your-api-key")

# Resource-based organization with full type safety
try:
    users = client.users.list(status="active")
    new_user = client.users.create(name="John", email="john@example.com")
    
    # Auto-pagination
    for user in client.users.list_iter():
        print(user.name)

except PetStoreClient.RateLimitError:
    print("Rate limited")
except PetStoreClient.ValidationError as e:
    print(f"Invalid input: {e.details}")
```

## Current Status

**MVP Phase**: Focus on essential Python module generation with excellent developer experience.

### ✅ Completed (Phase 1-2)
- Configuration system with `ipe.json`
- Error handling with Rich console output
- OpenAPI parser with Pydantic models
- Basic CLI structure with Typer
- Template system foundation

### 🚧 In Progress (Phase 3)
- **Kernel Engine**: Core OpenAPI processing and validation
- **Template Plugin Interface**: Standardized contract for language support
- **Python Template Plugin**: Resource-based client generation
- **Template Registry**: Plugin discovery and management system

### ⏳ Planned (Phase 4-5)
- Complete CLI implementation with kernel integration
- Enhanced error messages and progress indicators
- **TypeScript Template Plugin**: Second language to validate architecture
- Integration testing and multi-language support validation

## Technology Stack

- **Runtime**: Python 3.9+
- **Architecture**: Kernel engine with pluggable template system
- **CLI Framework**: Typer with Rich for beautiful output
- **Template Engine**: Copier + Jinja2 for language-specific generation
- **Configuration**: Single `ipe.json` file with Pydantic validation
- **OpenAPI Processing**: Pydantic models with comprehensive validation
- **Generated Clients**: httpx for Python (language-specific for others)
- **Testing**: pytest with comprehensive coverage
- **Code Quality**: ruff (linting + formatting), mypy (type checking)

## Development Principles

### Kernel-First Strategy
We prioritize building a robust kernel foundation that can support any language:
- **Kernel Foundation**: Rock-solid OpenAPI parsing, validation, and data normalization
- **Plugin Architecture**: Clean interface between kernel and language templates  
- **Python Template**: First template plugin to validate kernel design
- **Essential Commands**: `generate`, `init`, `version` only for MVP
- **Single Configuration**: `ipe.json` file as the source of truth

### Quality Standards
- **Strong typing**: Full type hints with mypy strict mode
- **Comprehensive testing**: 90%+ test coverage
- **Beautiful code**: Generated code should be production-ready
- **Resource-based clients**: Clean, intuitive API organization
- **Client-side validation**: Fail fast with helpful error messages

## Generated Code Features

**Excellent Developer Experience:**
- Resource-based organization (`client.users.list()`, `client.pets.create()`)
- Strong type safety with comprehensive type hints
- Client-side validation with helpful error messages
- Idiomatic code that follows language best practices

**See [Code Generation Specification](specs/05-code-generation.md) for complete details.**

## Architecture Overview

**Kernel-based architecture:** Language-agnostic OpenAPI processing core with pluggable language templates.

```
OpenAPI Spec → Kernel Engine → Template Plugins → Generated Clients
```

- **Kernel**: Handles parsing, validation, and data normalization
- **Templates**: Language-specific code generation (Python, TypeScript, Go, etc.)  
- **Output**: Resource-based, strongly-typed API clients

**See [Architecture Specification](specs/02-architecture.md) for detailed design.**

## Future Enhancements

The kernel architecture enables expansion to multiple languages and advanced features:

- **Additional Languages**: TypeScript, Go, Rust, Java support
- **Built-in Extensions**: Testing, CLI wrappers, framework integrations  
- **Advanced Features**: Package output, watch mode, enhanced validation

**See [Future Features](specs/99-future-features.md) for complete roadmap.**

## Contributing

Start with the [Project Overview](specs/01-project-overview.md) to understand our vision, then review the [Architecture](specs/02-architecture.md) and current development status. All contributions should maintain focus on exceptional developer experience and code quality.

## Documentation Structure

Each specification in the `specs/` directory focuses on a single domain and serves as the definitive source of truth for that area:

- [Project Overview](specs/01-project-overview.md) - Vision and philosophy
- [Architecture](specs/02-architecture.md) - Kernel-based system design  
- [CLI Interface](specs/03-cli-interface.md) - Command-line interface
- [Configuration](specs/04-configuration-system.md) - Settings management
- [Code Generation](specs/05-code-generation.md) - Template-based generation
- [Future Features](specs/99-future-features.md) - Planned enhancements

This organization ensures specifications remain focused, maintainable, and serve as reliable implementation guidance.