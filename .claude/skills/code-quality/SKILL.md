---
name: code-quality
description: Code quality and readability rules for the Ipê project. Use before writing or refactoring source files. Living document — append new rules as project conventions are identified. Currently covers Python style (vertical spacing, early returns, helper extraction, docstring rules, type hints, naming).
---

# Code Quality — Ipê

Apply these rules before writing or modifying source files. This is a living document — when the user corrects a pattern that should not repeat, add it here.

## Python

Rules below apply to any Python file under `src/ipe/`.

## Vertical Spacing

Separate **logical blocks** inside a function with one blank line. Each phase of a function should be visually distinct.

A "block" is anything that reads as a single intent: a guard, a local variable assignment, a loop, a final return.

**Bad — crammed:**
```python
def make_formatter(self, config):
    builders = {"ruff": RuffFormatter}
    builder = builders.get(config.name)
    if builder is None:
        raise IpeError(...)
    return builder(config.options)
```

**Good — blocks visible:**
```python
def make_formatter(self, config):
    builders = {"ruff": RuffFormatter}

    builder = builders.get(config.name)

    if builder is None:
        raise IpeError(...)

    return builder(config.options)
```

Same rule applies inside loops, classes, and modules. Between functions/classes at module level: two blank lines (PEP-8).

## Early Returns

Flatten branches with guard clauses. Prefer early returns over nested `if/else`.

**Bad:**
```python
def resolve(self, value):
    if value is not None:
        if value.ref:
            return self._lookup(value.ref)
        else:
            return value
    return None
```

**Good:**
```python
def resolve(self, value):
    if value is None:
        return None

    if not value.ref:
        return value

    return self._lookup(value.ref)
```

## Single-Purpose Helpers

If a function does more than one thing, split it. A helper should fit on a screen and have a name that describes its single job.

When extracting helpers from a class, prefer module-level private functions (`_helper`) when they don't need `self`. Methods only when they do.

## No Module Docstrings

Source files **do not** have module-level docstrings. Only public API functions and classes get docstrings (NumPy style).

Test files have **no** docstrings at all (modules, classes, methods).

## Type Hints

Always use modern syntax:
- `list[T]`, not `List[T]`
- `dict[K, V]`, not `Dict[K, V]`
- `X | None`, not `Optional[X]`
- `X | Y` unions, not `Union[X, Y]`

No implicit `Any`. mypy `--strict` must pass.

## Names

- Local variables describe **what** they hold, not their type: `model_names`, not `names_list`.
- Avoid single-char names (`s`, `n`, `x`) outside trivial comprehensions.
- Private helpers: `_leading_underscore`.

## Comments

Default: no comments. Add only when the **why** is non-obvious (hidden constraint, subtle invariant, workaround). Never narrate **what** the code does — the code does that.

Never reference the current PR, ticket, or change. Comments rot; PR descriptions don't.

## Imports

- Group with `ruff` defaults (stdlib, third-party, first-party).
- `ipe` is first-party.
- No wildcards.
- Sort within group.

## When You Catch Yourself...

- Writing a docstring on a module → delete it.
- Writing a comment that describes what the next line does → delete it.
- Nesting `if/else` 3 levels deep → restructure with early returns.
- Cramming 6 statements without blank lines → add vertical separation between logical phases.
- Naming variables `x`, `s`, `n` → rename to describe intent.
- Inlining a 10-line block with mixed concerns → extract a helper.

If you skip any of these, the canary dies. (See root CLAUDE.md.)
