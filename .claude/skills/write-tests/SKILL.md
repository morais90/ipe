---
name: write-tests
description: >
  Guide for writing high-quality Python tests following project conventions.
  Use when asked to write, create, or add tests for Ipê modules including
  Pydantic models, CLI commands, parsers, or code generation components.
  Triggers on: "write tests", "add tests", "create test", "test this module",
  or any request involving pytest test creation.
allowed-tools: Bash(uv run pytest:*), Bash(uv run ruff:*), Bash(uv run mypy:*), Read, Write, Edit, MultiEdit, Grep, Glob, TodoWrite
argument-hint: "[module/file]"
---

# Python Test Best Practices

## Before You Write Anything

1. **Check for existing tests** — search `tests/` for the module. Don't duplicate coverage.
2. **Read the source** — identify the public API, parameters, return types, and exceptions raised. Pay attention to Pydantic validators, field defaults, and `model_dump` behavior.
3. **Read the models** — understand Pydantic BaseModel fields, validators, coercers, and serialization (`exclude_none`, `mode="json"`).
4. **Read the exception hierarchy** — `src/ipe/core/exceptions.py` defines all custom exceptions. Know which ones your module raises and their `details` dict structure.
5. **Check for existing fixtures** — search `tests/conftest.py` and `tests/fixtures/`. Reuse what's there.
6. **Check the config** — `src/ipe/core/config.py` defines `IpeConfig`. Many modules receive it as input.

## Principles

### Test at the Integration Boundary

Test through the entry point the user actually hits: CLI commands, public functions, Pydantic model construction — not internal helpers behind them.

A unit test on an internal function might pass while the public API is broken due to wrong validation, missing fields, or bad wiring. Testing through the public interface exercises the full stack in one shot.

**Prefer:**
```python
result = runner.invoke(app, ["generate", "--spec", str(spec_path)])
assert result.exit_code == 0
assert "Generated" in result.stdout
```

**Avoid:**
```python
result = _internal_generate_step(spec_data)
assert result.success is True
```

The exception is genuinely complex pure logic (naming conventions, template helpers, spec transformations) that benefits from unit tests. Even then, add an integration test to prove the wiring works.

### Test Behavior, Not Implementation

Assert what the public API returns given a certain state. Don't assert internal field declarations or private method calls — those tests break on refactors that don't change behavior.

### Tests Are Documentation

A new developer should understand what a module does by reading its tests — without comments.

- **No comments in test code.** If a test needs a comment, simplify the test.
- **No docstrings.** Not in modules, not in classes, not in methods.
- **Descriptive method names** tell the story: `test_invalid_module_name_raises_validation_error`.
- **Simple flow.** Each test has a clear setup, action, and assertion that's obvious at a glance.

### Test Isolation

Each test runs independently — no shared mutable state, no ordering dependencies. A test that passes in a group but fails alone (or vice versa) is broken. If two tests need the same data, each creates it through fixtures.

### No Logic in Tests

Tests should have no `if`/`else`, loops, or complex computation. If a test needs logic to build assertions, it's too complex — split it or simplify.

```python
# Bad — logic hides what's being tested
for field in config.model_dump():
    assert field in expected_fields

# Good — explicit and obvious
assert config.model_dump() == {
    "target": "python",
    "output_dir": Path("./output"),
    "module_name": None,
    "spec_path": "",
    "targets": {},
    "template_dir": None,
}
```

### Minimal Test Data

Create only the data each test needs. Excess data hides what matters for the assertion and makes failures harder to diagnose.

```python
# Bad — unrelated data obscures the test's intent
@pytest.fixture
def full_spec() -> dict[str, Any]:
    return {
        "openapi": "3.0.3",
        "info": {"title": "API", "version": "1.0.0", "description": "Full desc", "contact": {"name": "Dev"}},
        "servers": [{"url": "https://api.example.com"}],
        "paths": {"/users": {"get": {"operationId": "listUsers", "responses": {"200": {"description": "OK"}}}}},
        "components": {"schemas": {"User": {"type": "object"}}},
    }

# Good — only what this test needs
@pytest.fixture
def minimal_spec() -> dict[str, Any]:
    return {
        "openapi": "3.0.3",
        "info": {"title": "API", "version": "1.0.0"},
        "paths": {},
    }
```

### Prefer Real Objects Over Mocks

Use real instances by default. Mocks are a last resort for things you can't control: network calls (httpx), filesystem side effects that can't use `tmp_path`, or external process execution. Over-mocking produces tests that pass even when the real code is broken.

### Full Output Assertion

Assert the **entire** output with `==`. Never cherry-pick fields or use `in` to check individual keys. For Pydantic models, use `model_dump()` to assert the complete state.

```python
# Good
assert config.model_dump() == {
    "target": "python",
    "output_dir": Path("./output"),
    "module_name": None,
    "spec_path": "",
    "targets": {},
    "template_dir": None,
}

# Bad — hides missing/extra fields
assert config.target == "python"
assert "output_dir" in config.model_dump()
```

## Structure & Conventions

### One Module Per Test File

```
src/ipe/core/config.py     → tests/core/test_config.py
src/ipe/core/exceptions.py → tests/core/test_exceptions.py
src/ipe/parsers/openapi.py → tests/parsers/test_openapi.py
src/ipe/targets/python.py  → tests/targets/test_python.py
```

### Assert Output First, Side Effects After

```python
assert loaded.model_dump() == expected
assert config_path.exists()
```

When a test fails, the output diff tells you exactly what broke. Side effect checks are a secondary safety net.

### Full Output Assertion

Assert the **complete** model state or return value with `==`. Use serialize helpers to build the expected dict from the real object. This applies to Pydantic models, JSON outputs, and generated file contents.

```python
# Good
assert config.model_dump(exclude_none=True) == {
    "target": "python",
    "output_dir": Path("./output"),
    "spec_path": "",
    "targets": {},
}

# Bad — hides fields that shouldn't be there
assert config.target == "python"
```

### One Validator Per Test

Each Pydantic validator gets its own test with inputs that pass and inputs that fail. Combining validators makes it impossible to tell which one broke.

### Deterministic Ordering

Every function returning multiple results should have deterministic ordering. If results come back in unexpected order, fix the source — never use `sorted()` in the test.

### Fixtures Over Inline Setup

Data setup belongs in fixtures. Test methods focus on action + assertion.

```python
@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    data = {"target": "python", "spec_path": "./api.yaml"}
    path = tmp_path / "ipe.json"
    path.write_text(json.dumps(data))
    return path

class TestConfigLoading:
    def test_load_valid_file(self, config_file: Path):
        config = load_config(config_file)
        assert config.target == "python"
        assert config.spec_path == "./api.yaml"
```

## Building Expected Values

### Serialize Helpers

For complex objects, build a `serialize_*` function that bridges the object to its expected dict. This keeps assertions in sync with the actual serialization.

```python
def serialize_config(config: IpeConfig) -> dict[str, Any]:
    return config.model_dump(exclude_none=True, mode="json")


def serialize_operation(op: StandardOperation) -> dict[str, Any]:
    return {
        "operation_id": op.operation_id,
        "method": op.method,
        "path": op.path,
        "summary": op.summary,
        "parameters": [serialize_parameter(p) for p in op.parameters],
    }
```

### Path Fields

Pydantic serializes `Path` objects differently depending on `mode`. Use `mode="json"` for string comparison, omit for `Path` comparison:

```python
# mode="json" — paths become strings
assert config.model_dump(mode="json")["output_dir"] == "output"

# default mode — paths stay as Path
assert config.model_dump()["output_dir"] == Path("./output")
```

### Optional Fields and exclude_none

When testing saved/serialized output, use `exclude_none=True` to match the actual JSON behavior:

```python
saved_data = json.loads(config_path.read_text())
assert "module_name" not in saved_data  # None fields excluded
```

## CLI Testing

The project uses Typer with Rich output. Test commands through `CliRunner`:

```python
from typer.testing import CliRunner
from ipe.cli.main import app

runner = CliRunner()
```

- Use `runner.invoke(app, [...])` for all CLI tests
- Assert `result.exit_code` for success/failure
- Assert `result.stdout` for output content
- Use `tmp_path` for any file arguments

```python
def test_generate_with_invalid_spec(self):
    result = runner.invoke(app, ["generate", "--spec", "nonexistent.yaml"])
    assert result.exit_code == 1
    assert "not found" in result.stdout
```

## Filesystem Testing

### Always Use tmp_path

Never write to the real filesystem. pytest's `tmp_path` fixture provides an isolated temporary directory per test.

```python
def test_save_config(self, tmp_path: Path):
    config = IpeConfig(target="typescript")
    config_path = tmp_path / "ipe.json"

    save_config(config, config_path)

    saved = json.loads(config_path.read_text())
    assert saved["target"] == "typescript"
```

### Test File Content, Not Just Existence

```python
def test_generated_output(self, tmp_path: Path):
    generate(spec, output_dir=tmp_path)

    client_file = tmp_path / "client.py"
    assert client_file.exists()
    content = client_file.read_text()
    assert "class ApiClient:" in content
```

## Network Testing

### Use respx for httpx Mocking

The project uses httpx for HTTP requests. Mock at the transport level with respx:

```python
import respx
from httpx import Response

@respx.mock
def test_fetch_spec_from_url(self):
    respx.get("https://api.example.com/openapi.yaml").mock(
        return_value=Response(200, text="openapi: '3.0.3'")
    )

    result = fetch_spec("https://api.example.com/openapi.yaml")
    assert result.startswith("openapi:")

@respx.mock
def test_fetch_spec_404(self):
    respx.get("https://api.example.com/missing.yaml").mock(
        return_value=Response(404)
    )

    with pytest.raises(NetworkError, match="404"):
        fetch_spec("https://api.example.com/missing.yaml")
```

## Standard Test Cases

### Pydantic Models

| # | Test | Why |
|---|------|-----|
| 1 | `test_defaults` | All defaults match spec (assert full model_dump) |
| 2 | `test_full_configuration` | All fields accepted together |
| 3 | `test_invalid_<field>` | Each validator rejects bad input |
| 4 | `test_valid_<field>` | Edge cases that should pass |
| 5 | `test_serialization_roundtrip` | save → load → same state |

### File I/O Functions

| # | Test | Why |
|---|------|-----|
| 1 | `test_load_valid_file` | Happy path |
| 2 | `test_file_not_found` | Missing file raises clear error |
| 3 | `test_invalid_content` | Malformed content handled |
| 4 | `test_save_and_load_roundtrip` | Write then read produces same data |

### CLI Commands

| # | Test | Why |
|---|------|-----|
| 1 | `test_<command>_happy_path` | Command succeeds with valid input |
| 2 | `test_<command>_missing_args` | Missing required args show help |
| 3 | `test_<command>_invalid_input` | Bad input shows actionable error |

### Exception Hierarchy

| # | Test | Why |
|---|------|-----|
| 1 | `test_basic_<error>` | Message and inheritance correct |
| 2 | `test_<error>_with_context` | All detail fields stored in details dict |
| 3 | `test_all_inherit_from_ipe_error` | Base class catching works |

### OpenAPI Parsing

| # | Test | Why |
|---|------|-----|
| 1 | `test_parse_minimal_spec` | Simplest valid spec |
| 2 | `test_parse_full_spec` | All supported features |
| 3 | `test_reject_invalid_spec` | Clear error for bad input |
| 4 | `test_unsupported_version` | OpenAPI 2.0 rejected with suggestion |

### Code Generation (Targets)

| # | Test | Why |
|---|------|-----|
| 1 | `test_plan_returns_output_files` | Target.plan() returns correct file list |
| 2 | `test_generated_content` | Output file content matches expected |
| 3 | `test_naming_convention` | class_name, method_name, field_name correct |

## External Services

Use transport-level mocks instead of `mock.patch` for external services — real client code runs, only the network is stubbed.

- **HTTP APIs**: `respx` for httpx request mocking
- **Filesystem side effects**: `tmp_path` fixture (no mocking needed)
- **Internal side effects** (event dispatchers, template rendering): `mock.patch` is fine

### Mock Assertions

Prefer `assert_called_once_with` over manually inspecting `call_args`:

```python
# Good — explicit about what was expected
mock_renderer.render.assert_called_once_with(
    template_name="client.py.jinja",
    context=expected_context,
)

# Bad — hides expected values
mock_renderer.render.assert_called_once()
args, _ = mock_renderer.render.call_args
assert args[0] == "client.py.jinja"
```

## Common Pitfalls

### Path Comparison

`Path("./output")` and `Path("output")` are different objects but may resolve to the same location. Be explicit about which form your code returns:

```python
# Know what your code actually returns
assert config.output_dir == Path("./output")  # if default is Path("./output")
```

### Pydantic mode="json" vs Default

`model_dump()` returns Python types (`Path`, `None`). `model_dump(mode="json")` returns JSON-serializable types (`str`). Use the right one for your assertion.

### exclude_none Asymmetry

`save_config` uses `exclude_none=True`, so saved JSON won't have `None` fields. But `load_config` will return a model with defaults filled in. Test both directions explicitly.

### Parametrize Scope

Don't mix valid and invalid cases in the same parametrize — they need different assertion patterns. Use separate parametrized tests.

## Running Tests

```bash
uv run pytest tests/core/ -v           # specific directory
uv run pytest -k "test_config" -v      # by name pattern
uv run pytest --cov-fail-under=90      # enforce coverage
uv run ruff check tests/               # lint tests
uv run mypy src/ipe --strict           # type check
```
