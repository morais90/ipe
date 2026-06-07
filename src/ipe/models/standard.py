from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from ipe.parsers import models as openapi


class ValidationRule(BaseModel):
    rule_type: str
    value: Any

    @classmethod
    def from_schema(cls, schema: openapi.Schema) -> list[ValidationRule]:
        rules: list[ValidationRule] = []
        for attr, rule_type in _SCHEMA_VALIDATION_MAP:
            value = getattr(schema, attr, None)
            if value is not None:
                rules.append(cls(rule_type=rule_type, value=value))
        return rules


_SCHEMA_VALIDATION_MAP = [
    ("min_length", "min_length"),
    ("max_length", "max_length"),
    ("pattern", "pattern"),
    ("minimum", "minimum"),
    ("maximum", "maximum"),
    ("exclusive_minimum", "exclusive_minimum"),
    ("exclusive_maximum", "exclusive_maximum"),
    ("min_items", "min_items"),
    ("max_items", "max_items"),
    ("multiple_of", "multiple_of"),
    ("unique_items", "unique_items"),
    ("min_properties", "min_properties"),
    ("max_properties", "max_properties"),
]


class SecurityRequirement(BaseModel):
    scheme_name: str
    scopes: list[str] = Field(default_factory=list)

    @classmethod
    def from_security(
        cls, raw: list[dict[str, list[str]]]
    ) -> list[SecurityRequirement]:
        return [
            cls(scheme_name=name, scopes=scopes)
            for req in raw
            for name, scopes in req.items()
        ]


class StandardProperty(BaseModel):
    name: str
    schema_type: str
    description: str | None = None
    schema_format: str | None = None
    required: bool = False
    nullable: bool = False
    default: Any | None = None
    enum_values: list[Any] | None = None

    @classmethod
    def from_schema(
        cls, name: str, schema: openapi.Schema, required_fields: list[str]
    ) -> StandardProperty:
        return cls(
            name=name,
            schema_type=_resolve_type(schema),
            description=schema.description,
            schema_format=schema.format,
            required=name in required_fields,
            nullable=_is_nullable(schema),
            default=schema.default,
            enum_values=schema.enum,
        )


class StandardModel(BaseModel):
    name: str
    description: str | None = None
    properties: list[StandardProperty] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    validation_rules: list[ValidationRule] = Field(default_factory=list)

    @classmethod
    def from_schema(cls, name: str, schema: openapi.Schema) -> StandardModel | None:
        if schema.type == "array" or schema.ref is not None:
            return None

        required_fields = schema.required or []
        properties = [
            StandardProperty.from_schema(prop_name, prop_schema, required_fields)
            for prop_name, prop_schema in (schema.properties or {}).items()
        ]

        return cls(
            name=name,
            description=schema.description,
            properties=properties,
            required_fields=required_fields,
            validation_rules=ValidationRule.from_schema(schema),
        )


class StandardParameter(BaseModel):
    name: str
    location: str
    required: bool
    schema_type: str
    description: str | None = None
    schema_format: str | None = None
    default: Any | None = None

    @classmethod
    def from_parameter(cls, param: openapi.Parameter) -> StandardParameter:
        schema = param.schema_ or openapi.Schema()
        return cls(
            name=param.name or "",
            location=param.in_ or "",
            required=param.required,
            schema_type=_resolve_type(schema),
            description=param.description,
            schema_format=schema.format,
            default=schema.default,
        )


class RequestBody(BaseModel):
    required: bool
    content_types: list[str]
    schema_type: str
    description: str | None = None
    schema_format: str | None = None

    @classmethod
    def from_request_body(
        cls, body: openapi.RequestBody
    ) -> RequestBody | None:
        if not body.content:
            return None

        content_types = list(body.content.keys())
        first_media = body.content[content_types[0]]
        schema = first_media.schema_ or openapi.Schema()

        return cls(
            required=body.required,
            content_types=content_types,
            schema_type=_resolve_type(schema),
            description=body.description,
            schema_format=schema.format,
        )


class Response(BaseModel):
    status_code: str
    description: str | None = None
    content_type: str | None = None
    model_names: list[str] = Field(default_factory=list)
    is_list: bool = False
    discriminator: str | None = None
    primitive_type: str | None = None

    @classmethod
    def from_response(
        cls, status_code: str, resp: openapi.Response
    ) -> Response:
        content_type = next(iter(resp.content), None) if resp.content else None
        schema: openapi.Schema | None = None
        if content_type and resp.content:
            schema = resp.content[content_type].schema_

        shape = _classify_response_schema(schema)
        return cls(
            status_code=status_code,
            description=resp.description,
            content_type=content_type,
            model_names=shape.model_names,
            is_list=shape.is_list,
            discriminator=shape.discriminator,
            primitive_type=shape.primitive_type,
        )


class AuthScheme(BaseModel):
    name: str
    type: str
    scheme: str | None = None
    location: str | None = None
    header_name: str | None = None

    @classmethod
    def from_security_scheme(
        cls, name: str, scheme: openapi.SecurityScheme
    ) -> AuthScheme:
        header_name: str | None = None
        if scheme.type == "apiKey":
            header_name = scheme.name
        elif scheme.type == "http" and scheme.scheme == "bearer":
            header_name = "Authorization"

        return cls(
            name=name,
            type=scheme.type,
            scheme=scheme.scheme,
            location=scheme.in_,
            header_name=header_name,
        )


class StandardOperation(BaseModel):
    operation_id: str
    method: str
    path: str
    summary: str | None = None
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    parameters: list[StandardParameter] = Field(default_factory=list)
    request_body: RequestBody | None = None
    responses: list[Response] = Field(default_factory=list)
    security: list[SecurityRequirement] = Field(default_factory=list)

    @classmethod
    def from_operation(
        cls,
        path: str,
        method: str,
        operation: openapi.Operation,
        path_item: openapi.PathItem,
    ) -> StandardOperation:
        merged_params = _merge_parameters(
            path_item.parameters or [], operation.parameters or []
        )

        return cls(
            operation_id=operation.operation_id or _make_operation_id(method, path),
            method=method.upper(),
            path=path,
            summary=operation.summary,
            description=operation.description,
            tags=operation.tags or [],
            parameters=[StandardParameter.from_parameter(p) for p in merged_params],
            request_body=(
                RequestBody.from_request_body(operation.request_body)
                if operation.request_body
                else None
            ),
            responses=[
                Response.from_response(code, resp)
                for code, resp in (operation.responses or {}).items()
            ],
            security=(
                SecurityRequirement.from_security(operation.security)
                if operation.security
                else []
            ),
        )


def _merge_parameters(
    path_params: list[openapi.Parameter],
    op_params: list[openapi.Parameter],
) -> list[openapi.Parameter]:
    by_key: dict[tuple[str, str], openapi.Parameter] = {}
    for p in path_params:
        by_key[(p.name or "", p.in_ or "")] = p
    for p in op_params:
        by_key[(p.name or "", p.in_ or "")] = p
    return list(by_key.values())


def _make_operation_id(method: str, path: str) -> str:
    segments = [s for s in path.split("/") if s and not s.startswith("{")]
    return "_".join([method, *segments])


def _resolve_type(schema: openapi.Schema) -> str:
    t = schema.type
    if isinstance(t, list):
        return str(t[0])
    if isinstance(t, str):
        return t
    return "object"


def _is_nullable(schema: openapi.Schema) -> bool:
    if schema.nullable is True:
        return True
    return isinstance(schema.type, list) and "null" in schema.type


_PRIMITIVE_TYPES = frozenset({"string", "integer", "number", "boolean"})


class _ResponseShape(BaseModel):
    model_names: list[str] = Field(default_factory=list)
    is_list: bool = False
    discriminator: str | None = None
    primitive_type: str | None = None


def _classify_response_schema(schema: openapi.Schema | None) -> _ResponseShape:
    if schema is None:
        return _ResponseShape()

    if schema.ref:
        name = _name_from_ref(schema.ref)
        return _ResponseShape(model_names=[name] if name else [])

    union_schemas = schema.one_of or schema.any_of
    if union_schemas:
        model_names = _collect_schema_ref_names(union_schemas)
        if model_names:
            discriminator = (
                schema.discriminator.property_name if schema.discriminator else None
            )
            return _ResponseShape(model_names=model_names, discriminator=discriminator)

    if schema.type == "array" and schema.items is not None:
        nested = _classify_response_schema(schema.items)
        return _ResponseShape(
            model_names=nested.model_names,
            is_list=True,
            discriminator=nested.discriminator,
            primitive_type=nested.primitive_type,
        )

    if isinstance(schema.type, str) and schema.type in _PRIMITIVE_TYPES:
        return _ResponseShape(primitive_type=schema.type)

    return _ResponseShape()


def _name_from_ref(ref: str) -> str | None:
    prefix = "#/components/schemas/"

    if not ref.startswith(prefix):
        return None

    return ref[len(prefix) :]


def _collect_schema_ref_names(schemas: list[openapi.Schema]) -> list[str]:
    model_names: list[str] = []

    for sub_schema in schemas:
        if sub_schema.ref is None:
            continue

        model_name = _name_from_ref(sub_schema.ref)
        if model_name is not None:
            model_names.append(model_name)

    return model_names
