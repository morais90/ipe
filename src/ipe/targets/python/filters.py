from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ipe.targets.base import LanguageTarget

_IDENTIFIER = re.compile(r"\w+")

_IMPORTABLE_TYPES: dict[str, tuple[str, str]] = {
    "UUID": ("uuid", "UUID"),
    "datetime": ("datetime", "datetime"),
    "date": ("datetime", "date"),
    "Any": ("typing", "Any"),
}

_SUCCESS_STATUSES = ("200", "201", "202", "203", "204")


def pyval(value: Any) -> str:
    return repr(value)


def success_response(responses: list[dict[str, Any]]) -> dict[str, Any] | None:
    by_status = {r.get("status_code"): r for r in responses}

    for status in _SUCCESS_STATUSES:
        if status in by_status:
            return by_status[status]

    return next(
        (r for r in responses if r.get("status_code", "").startswith("2")),
        None,
    )


class _ResponseView:
    def __init__(
        self,
        raw: dict[str, Any] | None,
        target: LanguageTarget | None = None,
    ) -> None:
        raw = raw or {}

        self._target = target

        raw_models = list(raw.get("model_names") or [])
        self.models: list[str] = (
            [target.naming.class_name(m) for m in raw_models]
            if target
            else raw_models
        )
        self.is_list: bool = bool(raw.get("is_list", False))
        self.discriminator: str | None = raw.get("discriminator")
        self.primitive: str | None = raw.get("primitive_type")

    @property
    def needs_adapter(self) -> bool:
        return bool(self.models) and (
            len(self.models) > 1 or self.discriminator is not None
        )

    def type_annotation(self) -> str:
        if not self.models:
            return self._render_primitive()

        base = " | ".join(self.models) if len(self.models) > 1 else self.models[0]
        return f"list[{base}]" if self.is_list else base

    def _render_primitive(self) -> str:
        if not self.primitive:
            return "None"

        if self._target is None:
            return self.primitive

        return self._target.resolve_type(self.primitive, None)

    def deserialize_expression(self) -> str:
        if not self.models:
            return "response.json()" if self.primitive else "None"

        if self.needs_adapter:
            return self._adapter_expression()

        return self._single_model_expression()

    def _adapter_expression(self) -> str:
        union = " | ".join(self.models)

        if self.discriminator:
            union = f'Annotated[{union}, Field(discriminator="{self.discriminator}")]'

        target = f"list[{union}]" if self.is_list else union
        return f"TypeAdapter({target}).validate_python(response.json())"

    def _single_model_expression(self) -> str:
        model = self.models[0]

        if self.is_list:
            return f"[{model}.model_validate(item) for item in response.json()]"

        return f"{model}.model_validate(response.json())"


def response_type(target: LanguageTarget, success: dict[str, Any] | None) -> str:
    return _ResponseView(success, target).type_annotation()


def response_deserialize(target: LanguageTarget, success: dict[str, Any] | None) -> str:
    return _ResponseView(success, target).deserialize_expression()


def type_imports(target: LanguageTarget, properties: list[dict[str, Any]]) -> str:
    pairs = [(p.get("schema_type", ""), p.get("schema_format")) for p in properties]
    return _compute_imports(target, pairs)


def param_type_imports(target: LanguageTarget, operations: list[dict[str, Any]]) -> str:
    pairs = [
        (p.get("schema_type", ""), p.get("schema_format"))
        for op in operations
        for p in op.get("parameters", [])
    ]
    return _compute_imports(target, pairs)


def resource_imports(
    target: LanguageTarget,
    operations: list[dict[str, Any]],
    module_name: str,
) -> str:
    sections = [
        param_type_imports(target, operations),
        _response_imports_block(target, operations, module_name),
    ]
    return "\n\n".join(s for s in sections if s)


def _response_imports_block(
    target: LanguageTarget,
    operations: list[dict[str, Any]],
    module_name: str,
) -> str:
    models, needs_adapter, needs_annotated = _scan_response_needs(operations)

    lines: list[str] = []

    if needs_annotated:
        lines.append("from typing import Annotated")

    pydantic_names = _pydantic_import_names(needs_adapter, needs_annotated)
    if pydantic_names:
        lines.append(f"from pydantic import {', '.join(pydantic_names)}")

    lines.extend(_model_import_lines(target, models, module_name))

    return "\n".join(lines)


def _scan_response_needs(
    operations: list[dict[str, Any]],
) -> tuple[set[str], bool, bool]:
    models: set[str] = set()
    needs_adapter = False
    needs_annotated = False

    for op in operations:
        view = _ResponseView(success_response(op.get("responses", [])))
        models.update(view.models)
        needs_adapter = needs_adapter or view.needs_adapter
        needs_annotated = needs_annotated or view.discriminator is not None

    return models, needs_adapter, needs_annotated


def _pydantic_import_names(needs_adapter: bool, needs_annotated: bool) -> list[str]:
    names: list[str] = []

    if needs_annotated:
        names.append("Field")
    if needs_adapter:
        names.append("TypeAdapter")

    return names


def _model_import_lines(
    target: LanguageTarget,
    models: set[str],
    module_name: str,
) -> list[str]:
    naming = target.naming
    return [
        f"from {module_name}.models.{naming.module_name(m)} import {naming.class_name(m)}"
        for m in sorted(models)
    ]


def _compute_imports(
    target: LanguageTarget,
    pairs: list[tuple[str, str | None]],
    always: set[str] | None = None,
) -> str:
    tokens: set[str] = set(always or set())

    for schema_type, schema_format in pairs:
        resolved = target.resolve_type(schema_type, schema_format)
        tokens.update(_IDENTIFIER.findall(resolved))

    modules: dict[str, set[str]] = {}
    for type_name, (module, name) in _IMPORTABLE_TYPES.items():
        if type_name in tokens:
            modules.setdefault(module, set()).add(name)

    if not modules:
        return ""

    lines = [
        f"from {module} import {', '.join(sorted(names))}"
        for module, names in sorted(modules.items())
    ]
    return "\n".join(lines)
