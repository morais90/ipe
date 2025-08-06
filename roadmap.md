# Ipê Development Roadmap - Parallel Task Distribution with Spec Validation

## 📋 Overview
This roadmap identifies tasks for parallel execution using multiple agents. Each task includes mandatory validation steps and verification against project specifications.

## 🚨 MANDATORY FOR EVERY TASK
**Core Validation (applies to ALL tasks):**
- ✅ Code is fully functional
- ✅ `uv run pytest` - All tests pass
- ✅ `uv run ruff check` - No linting errors
- ✅ `uv run ruff format --check` - Code is formatted
- ✅ `uv run mypy src/ipe --strict` - No type errors
- ✅ Test coverage ≥ 90% for new code
- 📋 **SPEC COMPLIANCE**: Verify implementation matches specifications

---

## Phase 1: Project Foundation (Sequential - 1 Agent)
**Must be completed before other phases**

### Task 1.1: Create pyproject.toml
**Spec Reference:** `SPECIFICATION.md` - Technology Stack section
**Description:** Set up Python project configuration
**Files:** `pyproject.toml`
**Dependencies:** None
**Validation Against Spec:**
- ✅ Python 3.9+ requirement (per spec)
- ✅ All specified dependencies included:
  - Runtime: typer[all], rich, pydantic, httpx, jinja2, copier
  - Dev: pytest, pytest-cov, pytest-mock, ruff, mypy
- ✅ Package manager: uv (as specified)
- ✅ Entry point: `ipe` CLI command
- ✅ All core validation passes

### Task 1.2: Create package structure
**Spec Reference:** `specs/02-architecture.md` - Module Organization
**Description:** Basic package with __init__.py
**Files:** `src/ipe/__init__.py`, `src/ipe/py.typed`
**Dependencies:** Task 1.1
**Validation Against Spec:**
- ✅ Structure matches spec exactly:
  ```
  src/ipe/
  ├── __init__.py
  ├── cli/
  ├── core/
  ├── parsers/
  ├── templates/
  └── utils/
  ```
- ✅ Package includes py.typed for type hints
- ✅ `python -c "import ipe; print(ipe.__version__)"` works
- ✅ All core validation passes

---

## Phase 2: Core Infrastructure (🔀 PARALLEL - 3 Agents)

### 🔀 Task 2.1: Configuration System (Agent 1)
**Spec Reference:** `specs/04-configuration-system.md`
**Description:** Build configuration loading and validation
**Files:** 
- `src/ipe/core/__init__.py`
- `src/ipe/core/config.py`
- `tests/core/test_config.py`
**Dependencies:** Phase 1 complete
**Validation Against Spec:**
- ✅ Single `ipe.json` file (no global config)
- ✅ Required fields per spec:
  - `module_name`: Package name
  - `generator`: Target language
  - `output_dir`: Output directory
- ✅ JSON schema validation with pydantic
- ✅ Intelligent defaults as specified
- ✅ Can load valid ipe.json
- ✅ Validation errors are descriptive
- ✅ Edge cases tested
- ✅ All core validation passes

### 🔀 Task 2.2: Console & CLI Foundation (Agent 2)
**Spec Reference:** `specs/03-cli-interface.md` - User Experience Design
**Description:** Rich console utilities and basic CLI
**Files:**
- `src/ipe/cli/__init__.py`
- `src/ipe/cli/main.py`
- `src/ipe/cli/console.py`
- `tests/cli/test_console.py`
**Dependencies:** Phase 1 complete
**Validation Against Spec:**
- ✅ Rich console with emojis (🌳, ✅, ❌, 📋, etc.)
- ✅ Progress indicators as specified
- ✅ Beautiful error formatting per examples
- ✅ Exit codes match specification (0-5)
- ✅ `ipe version` shows formatted output
- ✅ `ipe --help` works
- ✅ Console helpers tested
- ✅ All core validation passes

### 🔀 Task 2.3: Exception System (Agent 3)
**Spec Reference:** `CLAUDE.md` - Code Quality Standards
**Description:** Complete error hierarchy
**Files:**
- `src/ipe/core/exceptions.py`
- `tests/core/test_exceptions.py`
**Dependencies:** Phase 1 complete
**Validation Against Spec:**
- ✅ User-friendly messages (non-native English friendly)
- ✅ Helpful suggestions included
- ✅ Base `IpeError` hierarchy
- ✅ Specific exceptions: ValidationError, GenerationError, ConfigError
- ✅ All exceptions have user-friendly messages
- ✅ Exception inheritance tested
- ✅ All core validation passes

---

## Phase 3: OpenAPI Foundation (Mixed Sequential/Parallel)

### Task 3.1: OpenAPI Models (Sequential - 1 Agent)
**Spec Reference:** `specs/02-architecture.md` - Standardized Data Models
**Description:** Pydantic models for OpenAPI spec
**Files:**
- `src/ipe/parsers/__init__.py`
- `src/ipe/parsers/models.py`
- `tests/parsers/test_models.py`
**Dependencies:** Phase 2 complete
**Validation Against Spec:**
- ✅ Pydantic models for OpenAPI 3.0.x and 3.1.x
- ✅ Models match spec data structures:
  - StandardOperation
  - StandardModel
  - StandardParameter
  - StandardProperty
- ✅ Models parse Petstore spec
- ✅ Validation works correctly
- ✅ All core validation passes

### 🔀 Parallel Tasks After 3.1:

#### 🔀 Task 3.2: Spec Fetcher (Agent 1)
**Spec Reference:** `specs/03-cli-interface.md` - Spec Source Support
**Description:** Load specs from files/URLs
**Files:**
- `src/ipe/parsers/fetcher.py`
- `tests/parsers/test_fetcher.py`
- `tests/fixtures/petstore.yaml`
**Dependencies:** Task 3.1
**Validation Against Spec:**
- ✅ Local file support (YAML/JSON)
- ✅ URL fetching with httpx
- ✅ Auto-detection of format
- ✅ Progress feedback for URL fetching
- ✅ Loads YAML/JSON files
- ✅ Fetches from URLs
- ✅ Error handling tested
- ✅ All core validation passes

#### 🔀 Task 3.3: OpenAPI Parser (Agent 2)
**Spec Reference:** `SPECIFICATION.md` - Current Status
**Description:** Parse and validate specs
**Files:**
- `src/ipe/parsers/openapi.py`
- `tests/parsers/test_openapi.py`
**Dependencies:** Task 3.1
**Validation Against Spec:**
- ✅ OpenAPI 3.0.x and 3.1.x support
- ✅ Comprehensive validation
- ✅ Clear error messages with line numbers
- ✅ Parses complete specs
- ✅ Validation messages helpful
- ✅ All core validation passes

---

## Phase 4: Kernel Engine (Sequential - 1 Agent)
**Critical path - must be done carefully**

### Task 4.1: Kernel Foundation
**Spec Reference:** `specs/02-architecture.md` - Core Kernel Components
**Description:** Core processing engine
**Files:**
- `src/ipe/core/kernel.py`
- `tests/core/test_kernel.py`
**Dependencies:** Phase 3 complete
**Validation Against Spec:**
- ✅ Implements `OpenAPIKernel` class as specified
- ✅ Methods match spec interface:
  - `parse_and_validate()`
  - `extract_operations()`
  - `extract_models()`
  - `prepare_context()`
- ✅ Resource grouping by tags/paths
- ✅ Language-agnostic processing
- ✅ Extracts operations correctly
- ✅ Extracts models correctly
- ✅ All core validation passes

### Task 4.2: Template Interface
**Spec Reference:** `specs/02-architecture.md` - Template Interface
**Description:** Plugin contract definition
**Files:**
- `src/ipe/templates/__init__.py`
- `src/ipe/templates/base.py`
- `tests/templates/test_base.py`
**Dependencies:** Task 4.1
**Validation Against Spec:**
- ✅ `LanguageTemplate` ABC matches spec exactly
- ✅ Required methods:
  - `language_name` property
  - `transform_context()`
  - `get_output_structure()`
  - `validate_config()`
  - `get_default_config()`
- ✅ `TemplateContext` model as specified
- ✅ Interface is clear and complete
- ✅ Context model comprehensive
- ✅ All core validation passes

---

## Phase 5: Template System (🔀 PARALLEL - 4 Agents)

### 🔀 Task 5.1: Python Plugin (Agent 1)
**Spec Reference:** `specs/05-code-generation.md` - Python Template
**Description:** Python template implementation
**Files:**
- `src/ipe/templates/python/__init__.py`
- `src/ipe/templates/python/plugin.py`
- `tests/templates/python/test_plugin.py`
**Dependencies:** Task 4.2
**Validation Against Spec:**
- ✅ Resource-based organization
- ✅ Implements `PythonTemplate` class
- ✅ Context transformation for Python
- ✅ httpx client generation
- ✅ Transforms context correctly
- ✅ Python-specific logic tested
- ✅ All core validation passes

### 🔀 Task 5.2: Client Template (Agent 2)
**Spec Reference:** `specs/05-code-generation.md` - Generated Code Features
**Description:** Jinja template for client.py
**Files:**
- `src/ipe/templates/python/{{module_name}}/client.py.jinja`
- `src/ipe/templates/python/{{module_name}}/__init__.py.jinja`
- `tests/templates/python/test_client_template.py`
**Dependencies:** Task 4.2
**Validation Against Spec:**
- ✅ Resource-based API (`client.users.list()`)
- ✅ Auto-pagination support
- ✅ Structured error handling
- ✅ Type hints throughout
- ✅ Generates valid Python code
- ✅ Resource organization correct
- ✅ All core validation passes

### 🔀 Task 5.3: Models Template (Agent 3)
**Spec Reference:** `SPECIFICATION.md` - Generated Code Features
**Description:** Jinja template for models
**Files:**
- `src/ipe/templates/python/{{module_name}}/models.py.jinja`
- `tests/templates/python/test_models_template.py`
**Dependencies:** Task 4.2
**Validation Against Spec:**
- ✅ Pydantic models with validation
- ✅ Client-side validation
- ✅ Comprehensive type hints
- ✅ Idiomatic Python code
- ✅ Type hints correct
- ✅ All core validation passes

### 🔀 Task 5.4: Generation Engine (Agent 4)
**Spec Reference:** `specs/02-architecture.md` - Generation Orchestrator
**Description:** Orchestration and file writing
**Files:**
- `src/ipe/core/generation.py`
- `src/ipe/templates/registry.py`
- `tests/core/test_generation.py`
**Dependencies:** Task 4.2
**Validation Against Spec:**
- ✅ Implements `GenerationEngine` class
- ✅ Coordinates kernel and templates
- ✅ Uses Copier for generation
- ✅ Template registry system
- ✅ End-to-end generation works
- ✅ Files written correctly
- ✅ All core validation passes

---

## Phase 6: CLI Commands (🔀 PARALLEL - 2 Agents)

### 🔀 Task 6.1: Generate Command (Agent 1)
**Spec Reference:** `specs/03-cli-interface.md` - Generate Command
**Description:** Main generation command
**Files:**
- `src/ipe/cli/commands/__init__.py`
- `src/ipe/cli/commands/generate.py`
- `tests/cli/commands/test_generate.py`
**Dependencies:** Phase 5 complete
**Validation Against Spec:**
- ✅ Command syntax: `ipe generate SPEC --output PATH [OPTIONS]`
- ✅ All options work as specified
- ✅ Progress output matches spec examples
- ✅ Success message format correct
- ✅ Command works end-to-end
- ✅ Error handling complete
- ✅ Progress indicators work
- ✅ All core validation passes

### 🔀 Task 6.2: Init Command (Agent 2)
**Spec Reference:** `specs/03-cli-interface.md` - Init Command
**Description:** Interactive setup command
**Files:**
- `src/ipe/cli/commands/init.py`
- `tests/cli/commands/test_init.py`
**Dependencies:** Phase 5 complete
**Validation Against Spec:**
- ✅ Interactive prompts as specified
- ✅ Creates valid `ipe.json`
- ✅ Tests spec validation
- ✅ Provides immediate feedback
- ✅ Validation feedback clear
- ✅ All core validation passes

---

## Phase 7: Polish & Integration (Sequential - 1 Agent)

### Task 7.1: Integration Testing
**Spec Reference:** `SPECIFICATION.md` - Quality Standards
**Description:** End-to-end tests with real specs
**Files:**
- `tests/integration/`
- Additional fixtures
**Dependencies:** Phase 6 complete
**Validation Against Spec:**
- ✅ 90%+ test coverage achieved
- ✅ Works with real-world APIs (GitHub, Stripe)
- ✅ Sub-second generation for typical specs
- ✅ Generated code passes mypy strict
- ✅ Works with GitHub API spec
- ✅ Works with Stripe API spec
- ✅ Generated code functional
- ✅ All core validation passes

### Task 7.2: MVP Completion
**Spec Reference:** `SPECIFICATION.md` - MVP Phase
**Description:** Final polish and documentation
**Files:**
- `README.md` updates
- `examples/` directory
**Dependencies:** Task 7.1
**Validation Against Spec:**
- ✅ Essential commands only: generate, init, version
- ✅ Python generation fully functional
- ✅ Excellent developer experience achieved
- ✅ All core features implemented
- ✅ Quick start documentation works
- ✅ Examples run successfully
- ✅ All core validation passes

---

## 📊 Spec Compliance Checklist

**Architecture (specs/02-architecture.md):**
- [ ] Kernel architecture implemented
- [ ] Template plugin system functional
- [ ] Standardized data models used
- [ ] Module organization matches spec

**CLI Interface (specs/03-cli-interface.md):**
- [ ] All commands work as specified
- [ ] Output format matches examples
- [ ] Error messages helpful
- [ ] Exit codes correct

**Configuration (specs/04-configuration-system.md):**
- [ ] Single ipe.json file
- [ ] All fields validated
- [ ] Smart defaults work

**Code Generation (specs/05-code-generation.md):**
- [ ] Resource-based clients
- [ ] Type safety throughout
- [ ] Error handling complete
- [ ] Python idioms followed

**Quality Standards (CLAUDE.md):**
- [ ] No obvious comments
- [ ] NumPy docstrings for public APIs
- [ ] 90%+ test coverage
- [ ] All tools pass (mypy, ruff, pytest)

---

## 📊 Parallel Execution Summary

**Maximum Parallel Agents:**
- Phase 2: 3 agents
- Phase 3: 2 agents (after 3.1)
- Phase 5: 4 agents
- Phase 6: 2 agents

**Critical Sequential Path:**
1. Phase 1 (Foundation)
2. Task 3.1 (OpenAPI Models)
3. Phase 4 (Kernel)
4. Phase 7 (Integration)

**Total Tasks:** 19
**Parallel Tasks:** 13
**Sequential Tasks:** 6

This roadmap ensures every task is validated against the project specifications, maintaining consistency and quality throughout development while maximizing parallel execution opportunities.