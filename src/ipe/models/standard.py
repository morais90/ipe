from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from ipe.parsers import models as openapi


class ValidationRule(BaseModel):
    rule_type: str
    value: Any

    @classmethod
    def from_schema(cls, schema: openapi.Schema) -> list[ValidationRule]:
        """Extract validation rules from an OpenAPI schema.

        Parameters
        ----------
        schema : openapi.Schema
            The schema to read constraint keywords from.

        Returns
        -------
        list[ValidationRule]
            One rule per constraint present on the schema.
        """
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
        """Build security requirements from an OpenAPI security list.

        Parameters
        ----------
        raw : list[dict[str, list[str]]]
            The raw security requirement objects from the spec.

        Returns
        -------
        list[SecurityRequirement]
            One requirement per scheme reference.
        """
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
    validation_rules: list[ValidationRule] = Field(default_factory=list)
    model_names: list[str] = Field(default_factory=list)
    is_list: bool = False
    discriminator: str | None = None
    item_primitive: str | None = None

    @classmethod
    def from_schema(
        cls, name: str, schema: openapi.Schema, required_fields: list[str]
    ) -> StandardProperty:
        """Build a property from an OpenAPI schema.

        Parameters
        ----------
        name : str
            The property name.
        schema : openapi.Schema
            The schema describing the property.
        required_fields : list[str]
            The names of the parent model's required fields.

        Returns
        -------
        StandardProperty
            The language-agnostic property.
        """
        enum_values = _extract_enum_values(schema)
        shape = _classify_schema(schema)

        return cls(
            name=name,
            schema_type=_resolve_type(schema),
            description=schema.description,
            schema_format=schema.format,
            required=name in required_fields,
            nullable=_is_nullable(schema),
            default=schema.default,
            enum_values=enum_values,
            validation_rules=ValidationRule.from_schema(schema),
            model_names=[] if enum_values else shape.model_names,
            is_list=shape.is_list,
            discriminator=shape.discriminator,
            item_primitive=shape.primitive_type if shape.is_list else None,
        )


class StandardModel(BaseModel):
    name: str
    description: str | None = None
    properties: list[StandardProperty] = Field(default_factory=list)
    required_fields: list[str] = Field(default_factory=list)
    validation_rules: list[ValidationRule] = Field(default_factory=list)

    @classmethod
    def from_schema(cls, name: str, schema: openapi.Schema) -> StandardModel | None:
        """Build a model from an OpenAPI object schema.

        Parameters
        ----------
        name : str
            The model name.
        schema : openapi.Schema
            The schema describing the model.

        Returns
        -------
        StandardModel or None
            The model, or ``None`` when the schema is an array or a bare
            reference rather than an object.
        """
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
    enum_values: list[Any] | None = None
    validation_rules: list[ValidationRule] = Field(default_factory=list)
    model_names: list[str] = Field(default_factory=list)
    is_list: bool = False
    discriminator: str | None = None
    item_primitive: str | None = None

    @classmethod
    def from_parameter(cls, param: openapi.Parameter) -> StandardParameter:
        """Build a parameter from an OpenAPI parameter.

        Parameters
        ----------
        param : openapi.Parameter
            The OpenAPI parameter to convert.

        Returns
        -------
        StandardParameter
            The language-agnostic parameter.
        """
        schema = param.schema_ or openapi.Schema()
        enum_values = _extract_enum_values(schema)
        shape = _classify_schema(schema)

        return cls(
            name=param.name or "",
            location=param.in_ or "",
            required=param.required,
            schema_type=_resolve_type(schema),
            description=param.description,
            schema_format=schema.format,
            default=schema.default,
            enum_values=enum_values,
            validation_rules=ValidationRule.from_schema(schema),
            model_names=[] if enum_values else shape.model_names,
            is_list=shape.is_list,
            discriminator=shape.discriminator,
            item_primitive=shape.primitive_type if shape.is_list else None,
        )


class RequestBody(BaseModel):
    required: bool
    content_type: str | None = None
    model_names: list[str] = Field(default_factory=list)
    is_list: bool = False
    discriminator: str | None = None
    primitive_type: str | None = None
    is_inline_object: bool = False
    description: str | None = None

    @classmethod
    def from_request_body(cls, body: openapi.RequestBody) -> RequestBody | None:
        """Build a request body from an OpenAPI request body.

        Parameters
        ----------
        body : openapi.RequestBody
            The OpenAPI request body to convert.

        Returns
        -------
        RequestBody or None
            The request body, or ``None`` when it has no usable content.
        """
        if not body.content:
            return None

        content_type = next(iter(body.content))
        schema = body.content[content_type].schema_
        shape = _classify_schema(schema)

        if _is_empty_shape(shape):
            return None

        return cls(
            required=body.required,
            content_type=content_type,
            model_names=shape.model_names,
            is_list=shape.is_list,
            discriminator=shape.discriminator,
            primitive_type=shape.primitive_type,
            is_inline_object=shape.is_inline_object,
            description=body.description,
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
    def from_response(cls, status_code: str, resp: openapi.Response) -> Response:
        """Build a response from an OpenAPI response.

        Parameters
        ----------
        status_code : str
            The HTTP status code the response is keyed under.
        resp : openapi.Response
            The OpenAPI response to convert.

        Returns
        -------
        Response
            The language-agnostic response.
        """
        content_type = next(iter(resp.content), None) if resp.content else None
        schema: openapi.Schema | None = None
        if content_type and resp.content:
            schema = resp.content[content_type].schema_

        shape = _classify_schema(schema)
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
    kind: str
    location: str | None = None
    parameter_name: str | None = None
    token_url: str | None = None

    @classmethod
    def from_security_scheme(
        cls, name: str, scheme: openapi.SecurityScheme
    ) -> AuthScheme:
        """Build an auth scheme from an OpenAPI security scheme.

        Parameters
        ----------
        name : str
            The name the scheme is registered under.
        scheme : openapi.SecurityScheme
            The OpenAPI security scheme to convert.

        Returns
        -------
        AuthScheme
            The language-agnostic auth scheme.
        """
        if scheme.type == "apiKey":
            return cls(
                name=name,
                kind="apikey",
                location=scheme.in_,
                parameter_name=scheme.name,
            )

        if scheme.type == "oauth2":
            token_url = _client_credentials_token_url(scheme)
            if token_url:
                return cls(
                    name=name,
                    kind="oauth2_client_credentials",
                    token_url=token_url,
                )
            return cls(name=name, kind="oauth2")

        return cls(name=name, kind=_auth_kind(scheme))


def _auth_kind(scheme: openapi.SecurityScheme) -> str:
    if scheme.type == "http":
        return "basic" if scheme.scheme == "basic" else "bearer"

    return "oauth2"


def _client_credentials_token_url(scheme: openapi.SecurityScheme) -> str | None:
    if scheme.flows is None or scheme.flows.client_credentials is None:
        return None

    return scheme.flows.client_credentials.token_url


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
        """Build an operation from an OpenAPI operation.

        Parameters
        ----------
        path : str
            The path template the operation is served at.
        method : str
            The HTTP method.
        operation : openapi.Operation
            The OpenAPI operation to convert.
        path_item : openapi.PathItem
            The path item, used to merge path-level parameters.

        Returns
        -------
        StandardOperation
            The language-agnostic operation.
        """
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


def _extract_enum_values(schema: openapi.Schema) -> list[Any] | None:
    if schema.enum:
        return schema.enum

    if schema.const is not None:
        return [schema.const]

    return None


_PRIMITIVE_TYPES = frozenset({"string", "integer", "number", "boolean"})


class _SchemaShape(BaseModel):
    model_names: list[str] = Field(default_factory=list)
    is_list: bool = False
    discriminator: str | None = None
    primitive_type: str | None = None
    is_inline_object: bool = False


def _classify_schema(schema: openapi.Schema | None) -> _SchemaShape:  # noqa: PLR0911
    if schema is None:
        return _SchemaShape()

    if schema.ref:
        name = _name_from_ref(schema.ref)
        return _SchemaShape(model_names=[name] if name else [])

    union_schemas = schema.one_of or schema.any_of
    if union_schemas:
        model_names = _collect_schema_ref_names(union_schemas)
        if model_names:
            discriminator = (
                schema.discriminator.property_name if schema.discriminator else None
            )
            return _SchemaShape(model_names=model_names, discriminator=discriminator)

    if schema.type == "array" and schema.items is not None:
        nested = _classify_schema(schema.items)
        return _SchemaShape(
            model_names=nested.model_names,
            is_list=True,
            discriminator=nested.discriminator,
            primitive_type=nested.primitive_type,
        )

    if isinstance(schema.type, str) and schema.type in _PRIMITIVE_TYPES:
        return _SchemaShape(primitive_type=schema.type)

    if _is_inline_object(schema):
        return _SchemaShape(is_inline_object=True)

    return _SchemaShape()


def _is_inline_object(schema: openapi.Schema) -> bool:
    has_object_type = schema.type == "object" or schema.type is None
    return has_object_type and bool(schema.properties)


def _is_empty_shape(shape: _SchemaShape) -> bool:
    return (
        not shape.model_names
        and not shape.primitive_type
        and not shape.is_inline_object
    )


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
