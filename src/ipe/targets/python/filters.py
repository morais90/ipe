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
    "Annotated": ("typing", "Annotated"),
    "Literal": ("typing", "Literal"),
    "TYPE_CHECKING": ("typing", "TYPE_CHECKING"),
    "BaseModel": ("pydantic", "BaseModel"),
    "Field": ("pydantic", "Field"),
}

_SUCCESS_STATUSES = ("200", "201", "202", "203", "204")


def pyval(value: Any) -> str:
    """Render a Python literal for a value.

    Parameters
    ----------
    value : Any
        The value to render.

    Returns
    -------
    str
        The ``repr`` of the value.
    """
    return repr(value)


def success_response(responses: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Pick the success response from an operation's responses.

    Parameters
    ----------
    responses : list[dict[str, Any]]
        The serialized responses.

    Returns
    -------
    dict[str, Any] or None
        The best 2xx response, or ``None`` when there is none.
    """
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
            [target.naming.class_name(m) for m in raw_models] if target else raw_models
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
            union = f"Annotated[{union}, Field(discriminator={self.discriminator!r})]"

        target = f"list[{union}]" if self.is_list else union
        return f"TypeAdapter({target}).validate_python(response.json())"

    def _single_model_expression(self) -> str:
        model = self.models[0]

        if self.is_list:
            return f"[{model}.model_validate(item) for item in response.json()]"

        return f"{model}.model_validate(response.json())"


def response_type(target: LanguageTarget, success: dict[str, Any] | None) -> str:
    """Render the return type annotation for a success response.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    success : dict[str, Any] or None
        The success response, if any.

    Returns
    -------
    str
        The Python type annotation.
    """
    return _ResponseView(success, target).type_annotation()


def response_deserialize(target: LanguageTarget, success: dict[str, Any] | None) -> str:
    """Render the expression that deserializes a success response.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    success : dict[str, Any] or None
        The success response, if any.

    Returns
    -------
    str
        The deserialization expression.
    """
    return _ResponseView(success, target).deserialize_expression()


def type_imports(target: LanguageTarget, properties: list[dict[str, Any]]) -> str:
    """Render the value imports needed by a model's field types.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    properties : list[dict[str, Any]]
        The model's serialized properties.

    Returns
    -------
    str
        The joined import statements.
    """
    tokens = _collect_field_tokens(target, properties)
    return _build_imports_from_tokens(tokens)


def model_imports(
    target: LanguageTarget,
    model: dict[str, Any],
    module_name: str,
) -> str:
    """Render the imports needed by a generated model module.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    model : dict[str, Any]
        The serialized model.
    module_name : str
        The generated package's module name.

    Returns
    -------
    str
        The joined import blocks, including forward references.
    """
    properties = model.get("properties") or []

    tokens = _collect_field_tokens(target, properties)
    tokens.add("BaseModel")
    referenced = _referenced_models(properties)

    if referenced:
        tokens.add("TYPE_CHECKING")

    value_imports = _build_imports_from_tokens(tokens)
    forward_imports = _forward_ref_imports(target, referenced, module_name)

    return "\n\n".join(block for block in (value_imports, forward_imports) if block)


def _referenced_models(properties: list[dict[str, Any]]) -> set[str]:
    names: set[str] = set()

    for prop in properties:
        if prop.get("enum_values"):
            continue
        names.update(prop.get("model_names") or [])

    return names


def _forward_ref_imports(
    target: LanguageTarget,
    model_names: set[str],
    module_name: str,
) -> str:
    if not model_names:
        return ""

    naming = target.naming
    lines = [
        f"    from {module_name}.models.{naming.module_name(name)} "
        f"import {naming.class_name(name)}"
        for name in sorted(model_names)
    ]

    return "if TYPE_CHECKING:\n" + "\n".join(lines)


def param_type_imports(target: LanguageTarget, operations: list[dict[str, Any]]) -> str:
    """Render the value imports needed by operation parameter and body types.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    operations : list[dict[str, Any]]
        The serialized operations.

    Returns
    -------
    str
        The joined import statements.
    """
    params = [p for op in operations for p in op.get("parameters", [])]
    tokens = _collect_field_tokens(target, params)

    for body_type in _inline_body_types(target, operations):
        tokens.update(_IDENTIFIER.findall(body_type))

    return _build_imports_from_tokens(tokens)


def _collect_field_tokens(
    target: LanguageTarget,
    fields: list[dict[str, Any]],
) -> set[str]:
    tokens: set[str] = set()

    for field in fields:
        tokens.update(_IDENTIFIER.findall(field_type(target, field)))

    return tokens


def _inline_body_types(
    target: LanguageTarget,
    operations: list[dict[str, Any]],
) -> list[str]:
    rendered: list[str] = []

    for op in operations:
        body = op.get("request_body")
        if not body or body.get("model_names"):
            continue

        rendered.append(body_type(target, body))

    return rendered


def resource_imports(
    target: LanguageTarget,
    operations: list[dict[str, Any]],
    module_name: str,
) -> str:
    """Render every import a generated resource module needs.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    operations : list[dict[str, Any]]
        The serialized operations in the resource.
    module_name : str
        The generated package's module name.

    Returns
    -------
    str
        The joined import blocks.
    """
    sections = [
        param_type_imports(target, operations),
        _response_imports_block(target, operations, module_name),
        _body_imports_block(target, operations, module_name),
        _validation_import(module_name),
    ]
    return "\n\n".join(s for s in sections if s)


def _validation_import(module_name: str) -> str:
    return f"from {module_name}.exceptions import validated"


def _body_imports_block(
    target: LanguageTarget,
    operations: list[dict[str, Any]],
    module_name: str,
) -> str:
    domain_models, request_models = _scan_body_needs(operations)

    lines: list[str] = []
    lines.extend(_model_import_lines(target, domain_models, module_name, "models"))
    lines.extend(
        _model_import_lines(target, request_models, module_name, "models.requests")
    )

    return "\n".join(lines)


def _scan_body_needs(
    operations: list[dict[str, Any]],
) -> tuple[set[str], set[str]]:
    domain_models: set[str] = set()
    request_models: set[str] = set()

    for op in operations:
        body = op.get("request_body")
        if not body:
            continue

        model_names = body.get("model_names") or []
        if not model_names:
            continue

        bucket = request_models if body.get("is_inline_object") else domain_models
        bucket.update(model_names)

    return domain_models, request_models


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
    sub_path: str = "models",
) -> list[str]:
    naming = target.naming
    return [
        f"from {module_name}.{sub_path}.{naming.module_name(m)} import {naming.class_name(m)}"
        for m in sorted(models)
    ]


def _build_imports_from_tokens(tokens: set[str]) -> str:
    modules: dict[str, set[str]] = {}

    for type_name, (module, name) in _IMPORTABLE_TYPES.items():
        if type_name in tokens:
            modules.setdefault(module, set()).add(name)

    if not modules:
        return ""

    return "\n".join(
        f"from {module} import {', '.join(sorted(names))}"
        for module, names in sorted(modules.items())
    )


_CONTENT_TYPE_KWARG = {
    "application/json": "json",
    "application/x-www-form-urlencoded": "data",
    "multipart/form-data": "files",
}


def body_type(target: LanguageTarget, body: dict[str, Any] | None) -> str:
    """Render the type annotation for a request body.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    body : dict[str, Any] or None
        The serialized request body, if any.

    Returns
    -------
    str
        The Python type annotation.
    """
    if not body:
        return "None"

    models = body.get("model_names") or []

    if not models:
        return _render_bodyless_type(target, body)

    rendered = [target.naming.class_name(m) for m in models]
    base = " | ".join(rendered) if len(rendered) > 1 else rendered[0]

    return f"list[{base}]" if body.get("is_list") else base


def _render_bodyless_type(target: LanguageTarget, body: dict[str, Any]) -> str:
    if body.get("is_inline_object"):
        return "dict[str, Any]"

    primitive = body.get("primitive_type")
    if primitive:
        return target.resolve_type(primitive, None)

    return "dict[str, Any]"


def body_call_arg(body: dict[str, Any] | None) -> str:
    """Render the transport keyword argument that sends the request body.

    Parameters
    ----------
    body : dict[str, Any] or None
        The serialized request body, if any.

    Returns
    -------
    str
        The keyword argument expression, or an empty string when there is
        no body.
    """
    if not body:
        return ""

    kwarg = _CONTENT_TYPE_KWARG.get(body.get("content_type") or "", "content")
    models = body.get("model_names") or []

    if not models:
        return f"{kwarg}=body"

    if body.get("is_list"):
        dump = '[item.model_dump(mode="json") for item in body]'
    else:
        dump = 'body.model_dump(mode="json")'

    if not body.get("required"):
        dump = f"{dump} if body is not None else None"

    return f"{kwarg}={dump}"


_RULE_TO_FIELD_ARG: dict[str, str] = {
    "min_length": "min_length",
    "max_length": "max_length",
    "pattern": "pattern",
    "minimum": "ge",
    "maximum": "le",
    "exclusive_minimum": "gt",
    "exclusive_maximum": "lt",
    "min_items": "min_length",
    "max_items": "max_length",
    "multiple_of": "multiple_of",
}


def field_type(target: LanguageTarget, prop: dict[str, Any]) -> str:
    """Render the type annotation for a model field.

    Parameters
    ----------
    target : LanguageTarget
        The active language target.
    prop : dict[str, Any]
        The serialized property.

    Returns
    -------
    str
        The Python type annotation, wrapped in ``Annotated`` when the field
        carries validation rules.
    """
    base = _resolve_base_type(target, prop)
    args = _field_args(prop.get("validation_rules") or [])

    if not args:
        return base

    return f"Annotated[{base}, Field({args})]"


def _resolve_base_type(target: LanguageTarget, prop: dict[str, Any]) -> str:
    enum_values = prop.get("enum_values")
    if enum_values:
        rendered = ", ".join(repr(v) for v in enum_values)
        return f"Literal[{rendered}]"

    model_names = prop.get("model_names") or []
    if model_names:
        return _model_reference_type(target, prop, model_names)

    if prop.get("is_list"):
        return _list_type(target, prop)

    return target.resolve_type(prop.get("schema_type", ""), prop.get("schema_format"))


def _model_reference_type(
    target: LanguageTarget,
    prop: dict[str, Any],
    model_names: list[str],
) -> str:
    rendered = [target.naming.class_name(name) for name in model_names]
    base = " | ".join(rendered) if len(rendered) > 1 else rendered[0]

    discriminator = prop.get("discriminator")
    if discriminator:
        base = f"Annotated[{base}, Field(discriminator={discriminator!r})]"

    return f"list[{base}]" if prop.get("is_list") else base


def _list_type(target: LanguageTarget, prop: dict[str, Any]) -> str:
    item_primitive = prop.get("item_primitive")
    if item_primitive:
        return f"list[{target.resolve_type(item_primitive, None)}]"

    return "list[Any]"


def _field_args(rules: list[dict[str, Any]]) -> str:
    parts: list[str] = []

    for rule in rules:
        arg_name = _RULE_TO_FIELD_ARG.get(rule.get("rule_type", ""))
        if arg_name is None:
            continue

        value = _normalize_numeric(rule.get("value"))
        parts.append(f"{arg_name}={value!r}")

    return ", ".join(parts)


def _normalize_numeric(value: Any) -> Any:
    if isinstance(value, float) and value.is_integer():
        return int(value)

    return value
