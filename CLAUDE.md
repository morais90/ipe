# Ipê - Claude Development Context

## Project Overview
Ipê is a next-generation OpenAPI code generator built in Python with an obsession for developer experience. Named after the beautiful Brazilian tree, Ipê transforms OpenAPI specifications into beautiful, production-ready code using built-in Jinja2 templates.

## Core Philosophy
- **Developer Experience Above All**: Lightning fast, beautiful CLI output, intelligent defaults
- **Modern & High-Tech**: Rich CLI with progress indicators, syntax highlighting, emojis
- **Exceptionally Documented**: Every feature explained with examples and best practices
- **Zero-Config**: Works perfectly out-of-the-box, customizable when needed

## Technology Stack
- **Runtime**: Python 3.9+
- **CLI Framework**: Typer (with Rich for beautiful output)
- **Template Engine**: Jinja2
- **Package Manager**: uv
- **Testing**: pytest (with pytest-cov, pytest-mock)
- **Code Quality**: ruff (linting + formatting), mypy (type checking)
- **Configuration**: JSON only (pydantic for validation)
- **HTTP**: httpx for modern async HTTP client generation

## Project Structure
```
├── src/ipe/           # Main package
│   ├── cli/           # Typer CLI interface and commands
│   ├── core/          # Core generation logic
│   ├── templates/     # Built-in Jinja2 templates
│   ├── parsers/       # OpenAPI spec parsing (pydantic models)
│   ├── generators/    # Language-specific generators
│   ├── plugins/       # Plugin system with entry points
│   └── utils/         # Shared utilities
├── tests/             # pytest test suite
├── examples/          # Example OpenAPI specs and outputs
└── docs/              # Documentation
```

## CLI Commands
```bash
ipe generate [OPTIONS] SPEC_PATH  # Generate code from OpenAPI spec
ipe init                          # Interactive project setup
ipe validate SPEC                 # Validate OpenAPI specification
ipe generators                    # List available generators
ipe version                       # Show version info
ipe doctor                        # Diagnose issues
```

## Development Commands
```bash
# Install dependencies
uv sync --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check

# Run formatting
uv run ruff format

# Run type checking
uv run mypy src/ipe

# Run all checks
uv run pytest && uv run ruff check && uv run mypy src/ipe
```

## Supported Generators (Planned)
- **Python**: httpx client, Pydantic models, async/sync, type hints (Priority 1)
- **TypeScript**: Axios/Fetch client, full type definitions (Priority 2)
- **JavaScript**: Modern ES6+, optional TypeScript declarations (Priority 3)
- **Go**: Native HTTP client, struct definitions (Future)
- **Rust**: reqwest client, serde models (Future)

## Configuration
- Uses `ipe.json` for project-specific configuration (no global config)
- JSON schema validation with pydantic
- Intelligent defaults for zero-config experience

## Commit Guidelines

### Commit Message Format
```
<type>(<scope>): <subject line (max 50 chars)>

<body wrapped at 72 characters explaining what problem your changes solve and how>
```

### Commit Types
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `chore`: Maintenance tasks
- `test`: Adding or updating tests
- `refactor`: Code refactoring

### Commit Scopes (Always Include When Applicable)
- `config`: Configuration system changes
- `cli`: CLI interface and commands
- `parser`: OpenAPI parsing logic
- `generator`: Code generation engines
- `template`: Template system
- `console`: Rich console and error handling
- `core`: Core utilities and base classes
- `test`: Test-related changes

### Commit Rules
- **Explain the why** - Describe what problem your changes solve and how they solve it
- **Concise yet clear** - Provide meaningful description without unnecessary details
- **Always use scopes** when changes are specific to a module
- **Subject line max 50 characters** - Keep it concise and readable
- **Body wrapped at 72 characters** - Focus on problem and solution
- **Small, frequent commits** - One logical change per commit
- **Use bullets sparingly** - Only when they add real value to understanding
- **No author information** - Never include author tags or co-author lines
- **Stay relevant** - Only include information that relates to the problem being solved

### Good Examples
```
feat(config): add validation for package names

Package names were causing generation failures due to invalid
characters. Implement regex validation to ensure Python naming
conventions and provide helpful error messages.
```

```
fix(console): resolve Rich panel formatting issues

Panel borders were breaking on narrow terminals causing poor
user experience. Fix rendering logic to handle different
terminal sizes gracefully.
```

```
refactor(generator): eliminate code duplication in operation processing

Operation data preparation was duplicated in two methods causing
maintenance issues. Extract shared logic to single method.
```

### Bad Examples
```
# Missing why/problem context
feat(config): add package name validation

# Including irrelevant information
test(config): add comprehensive validation tests

Achieves 95% coverage with 15 new test cases covering
edge cases including path normalization and CLI overrides.

🤖 Generated with [Claude Code](https://claude.ai/code)
Co-Authored-By: Claude <noreply@anthropic.com>

# Too generic - doesn't explain the problem
chore: updates

# Unnecessary bullets that don't add value
fix(parser): resolve validation errors

- Fix null pointer exception
- Update error messages
- Add better logging
```

## Key Files
- `SPECIFICATION.md`: Complete technical specification with development plan and current status
- `README.md`: Project introduction and usage
- `pyproject.toml`: Project configuration with all dependencies
- `src/ipe/`: Main package source code

## Code Quality & Developer Experience Standards

### Amazing Developer Experience Philosophy
- **CLI Experience**: Beautiful, intuitive, helpful interface with Rich output
- **Code Readability**: Code should read like well-written prose
- **Documentation**: Crystal clear, accessible to non-native English speakers
- **Validation**: Bullet-proof project through comprehensive tooling

### Code Standards

#### Comments Policy
- **Never write obvious comments** - Code should be self-explanatory through clear naming
- **Only comment when absolutely necessary**: Complex algorithms, business logic, or counterintuitive decisions that cannot be expressed through better code structure
- **Examples of prohibited comments**:
  - `# Set user to None` → just write `user = None`
  - `# Loop through items` → just write `for item in items:`
  - `# Import required modules` → imports are self-evident
- **Examples of acceptable comments**:
  - `# Using exponential backoff to handle API rate limiting gracefully`
  - `# Workaround for OpenAPI spec bug where responses.default is sometimes missing`
  - `# Performance optimization: cache compiled regex patterns for hot path`

#### Docstring Standards (NumPy Convention)
- **Never write docstrings in test files** - Test names should be descriptive enough
- **Always write docstrings for public APIs** - All public functions, classes, and methods
- **Private functions may skip docstrings** if the function name and type hints make the purpose clear
- **Focus on behavior, not implementation** - Explain what the function does, not how it does it
```python
def generate_client(spec_path: Path, config: Config) -> GeneratedCode:
    """Generate API client from OpenAPI specification.

    Parameters
    ----------
    spec_path : Path
        Path to the OpenAPI specification file (YAML or JSON)
    config : Config
        Configuration object containing generation settings

    Returns
    -------
    GeneratedCode
        Object containing all generated files and metadata

    Raises
    ------
    ValidationError
        If the OpenAPI specification is invalid
    FileNotFoundError
        If the specification file cannot be found

    Examples
    --------
    >>> config = Config(generator="python", output_dir="./client")
    >>> result = generate_client(Path("api.yaml"), config)
    >>> print(f"Generated {len(result.files)} files")
    """
```

#### Documentation Requirements
- **Complete**: Document all public APIs, parameters, return values, exceptions
- **Clear English**: Simple vocabulary, short sentences, active voice
- **No Jargon**: Explain technical terms or use simpler alternatives
- **Examples**: Include usage examples for complex functions
- **Non-native Friendly**: Avoid idioms, cultural references, complex grammar

#### Type Hints
- **Always use type hints** for all function signatures
- **Use modern typing**: `list[str]` instead of `List[str]` (Python 3.9+)
- **Be specific**: `Literal["python", "typescript"]` instead of `str`
- **Document complex types**: Use TypedDict or dataclasses for structured data

### Code Validation & Tooling

#### Pre-commit Validation
```bash
# Type checking (strict mode)
uv run mypy src/ipe --strict

# Linting and formatting
uv run ruff check src/ipe
uv run ruff format src/ipe

# Documentation validation
uv run python -m doctest src/ipe/**/*.py

# Test coverage
uv run pytest --cov=src/ipe --cov-report=term-missing --cov-fail-under=90
```

#### Tool Configuration for Bullet-proof Code
- **MyPy**: Strict mode with no implicit Any, no untyped defs
- **Ruff**: Comprehensive linting with error on all issues
- **Pytest**: Minimum 90% coverage, strict test discovery
- **Pre-commit hooks**: Automated validation on every commit

### Testing Standards

#### Core Testing Principles
- **Test public interfaces only** - Never assert on private methods; test outputs and side effects
- **No comments or docstrings in tests** - Test names must be self-explanatory
- **Simple and clear** - Tests are living documentation, prioritize readability
- **Avoid loops in assertions** - Flatten results or format data for direct comparison
- **Use real fixtures over mocks** - Create fixture files instead of mocking when possible
- **Test complete outputs** - Assert entire results to catch silent changes, not just key presence or types

#### Test Structure Requirements
```python
# Good - Clear, direct, complete testing
def test_convert_openapi_types_to_python():
    result = convert_openapi_type_to_python("string")
    assert result == "str"

def test_template_data_extracts_complete_operations():
    spec = OpenAPISpec.from_file("tests/fixtures/api.json")
    config = IpeConfig(module_name="test_client")

    template_data = TemplateData(spec, config)

    expected_operations = [
        {"path": "/users", "method": "get", "operation_id": "getUsers"},
        {"path": "/users", "method": "post", "operation_id": "createUser"}
    ]
    assert template_data.data["operations"] == expected_operations

# Bad - Testing implementation details
def test_extract_module_path_internal_logic():  # Don't test private methods
    assert template_data._extract_module_path("/users") == "users"  # Avoid this

# Bad - Useless assertions
def test_operations_is_list():  # Don't test types
    assert isinstance(template_data.data["operations"], list)  # Avoid this
```

#### Fixture and Data Management
- **Create fixture files** for test data in `tests/fixtures/` directory
- **Use pytest.fixture** for complex setup, but prefer real data files
- **Avoid mocks** unless testing external dependencies (HTTP calls, file system)
- **Use temporary directories** for file output tests with pytest's `tmp_path`
- **Real scenarios over artificial data** - Use actual OpenAPI specs and realistic inputs

#### Test Organization
```python
# Organize by functionality, not by implementation structure
class TestTypeConversion:           # Utility functions
class TestTemplateDataExtraction:   # Core data processing
class TestCodeGeneration:          # End-to-end scenarios
```

#### Test Categories
- **Unit Tests**: Individual functions and classes with real data
- **Integration Tests**: Component interactions and data flow
- **CLI Tests**: Complete command workflows using actual CLI commands
- **Error Handling Tests**: Exception scenarios and error messages

## Critical Thinking and Feedback

**IMPORTANT: Always critically evaluate and challenge user suggestions, even when they seem reasonable.**

### Analytical Approach Guidelines
- **Question assumptions**: Don't just accept requests - analyze if there are better approaches or if the underlying problem is correctly identified
- **Offer alternative perspectives**: Suggest different solutions, point out potential issues, or propose more efficient implementations
- **Challenge organizational decisions**: If something doesn't fit logically within the codebase structure or violates established patterns, speak up and explain why
- **Point out inconsistencies**: Help catch logical errors, contradictory requirements, or components that seem misplaced
- **Evaluate impact**: Consider how changes affect user experience, maintainability, performance, and long-term architecture

### Why Critical Feedback Matters
This analytical approach helps improve decision-making and ensures robust, well-thought-out solutions. Being agreeable without analysis is less valuable than being thoughtful and constructively challenging. The goal is to build the best possible solution, not just implement requests as given.

### Examples of Good Critical Thinking
- Questioning whether a new command is necessary or if existing functionality could be extended
- Suggesting simpler solutions when complex ones are proposed
- Pointing out when a feature might confuse users or create maintenance burden
- Recommending architectural improvements that align with project goals
- Identifying when requirements conflict with established design principles

## Important Notes
- Focus on developer experience in every decision (CLI + code reading)
- Use Rich for beautiful CLI output with emojis and progress bars
- Follow Python best practices with full type hints and strict validation
- Maintain comprehensive test coverage (target: 90%+)
- Generate clean, modern, production-ready code
- Support OpenAPI 3.0.x and 3.1.x specifications
- **Always update SPECIFICATION.md with important decisions**
- **Follow the phase-based development plan strictly**
- **Test each component before moving to the next**
- **Validate code quality with every change**
