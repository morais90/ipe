# Project Overview

## Identity

**Ipê** is a next-generation OpenAPI code generator built in Python with an obsession for developer experience. Named after the stunning Brazilian tree known for its vibrant blooms, Ipê brings the same elegance and reliability to code generation.

## Core Philosophy: Developer Experience Above All

Every decision in Ipê prioritizes the developer experience:

- ⚡ **Lightning Fast**: Sub-second generation for most specs
- 🎨 **Beautiful Output**: Rich CLI with progress indicators and syntax highlighting  
- 🧠 **Intelligent Defaults**: Works perfectly out-of-the-box, customizable when needed
- 📚 **Exceptional Documentation**: Every feature explained with examples
- 🔧 **Extensible**: Protocol-based target system for new languages and custom templates

## Project Mission

Transform OpenAPI specifications into beautiful, production-ready code that developers actually want to use. Eliminate the friction between API specification and client implementation.

## Core Values

### 1. Zero-Config Philosophy
Ipê should work perfectly without any configuration for 80% of use cases. Smart defaults eliminate setup overhead while still providing full customization when needed.

### 2. Beautiful is Better Than Functional
Following Python's philosophy, we prioritize elegant, readable output over purely functional solutions. Generated code should be something developers are proud to use and maintain.

### 3. Fast Feedback Loops
Every interaction should provide immediate, helpful feedback. Whether it's validation errors, generation progress, or success confirmations, users should always know what's happening.

### 4. Progressive Disclosure
Simple commands for simple tasks, powerful options for power users. The CLI should be approachable for beginners while providing advanced capabilities for complex scenarios.

### 5. Production-Ready Output
Generated code must be production-quality with proper error handling, type safety, documentation, and testing considerations built-in.

## Technology Stack Principles

### Modern Python First
- Python 3.9+ as the foundation
- Leverage modern Python features (type hints, dataclasses, async/await)
- Use proven, well-maintained libraries with excellent documentation

### Rich User Experience
- **Typer** for CLI with automatic help generation
- **Rich** for beautiful console output with colors, progress bars, and formatting
- **Pydantic** for robust data validation and settings management

### Template-Based Generation
- **Jinja2** for flexible, maintainable templates
- **pathlib** for file structure generation
- Clear separation between logic and presentation

### Developer Productivity Tools
- **uv** for fast, reliable dependency management
- **ruff** for lightning-fast linting and formatting
- **mypy** for static type checking
- **pytest** for comprehensive testing

## Success Metrics

### User Experience
- First-time users can generate working code in under 60 seconds
- Error messages provide actionable next steps 90% of the time
- Generated code passes language-specific linters without configuration

### Performance  
- Small specs (10 endpoints): <1 second generation time
- Medium specs (50 endpoints): <3 seconds generation time
- Large specs (200+ endpoints): <10 seconds generation time

### Quality
- 90%+ test coverage maintained
- Generated code compiles/runs without modification
- Documentation accuracy verified through automated testing

## Design Principles

### CLI-First Design
The command-line interface is the primary interaction method. All features must be accessible and intuitive from the CLI before considering other interfaces.

### Fail Fast, Fail Clear
When something goes wrong, detect it as early as possible and provide clear, actionable error messages with suggested fixes.

### Convention Over Configuration
Establish sensible defaults based on industry best practices. Users should only need to configure what makes their use case unique.

### Composable Architecture
Design components that can be easily tested, extended, and replaced. Each major feature should work independently while integrating seamlessly.

This overview establishes the foundation for all other specifications. Every feature and implementation decision should align with these core principles and values.