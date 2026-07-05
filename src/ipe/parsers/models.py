from __future__ import annotations

import contextvars
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

_schema_registry: contextvars.ContextVar[dict[str, Schema] | None] = (
    contextvars.ContextVar("_schema_registry", default=None)
)


class OpenAPIBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        alias_generator=to_camel,
    )


# --- Leaf models (no forward references) ---


class Contact(OpenAPIBaseModel):
    name: str | None = None
    url: str | None = None
    email: str | None = None


class License(OpenAPIBaseModel):
    name: str
    url: str | None = None
    identifier: str | None = None


class ServerVariable(OpenAPIBaseModel):
    default: str
    enum: list[str] | None = None
    description: str | None = None


class Server(OpenAPIBaseModel):
    url: str
    description: str | None = None
    variables: dict[str, ServerVariable] | None = None


class ExternalDocs(OpenAPIBaseModel):
    url: str
    description: str | None = None


class Discriminator(OpenAPIBaseModel):
    property_name: str
    mapping: dict[str, str] | None = None


class XML(OpenAPIBaseModel):
    name: str | None = None
    namespace: str | None = None
    prefix: str | None = None
    attribute: bool = False
    wrapped: bool = False


class Tag(OpenAPIBaseModel):
    name: str
    description: str | None = None
    external_docs: ExternalDocs | None = None


class Example(OpenAPIBaseModel):
    ref: str | None = Field(default=None, alias="$ref")
    summary: str | None = None
    description: str | None = None
    value: Any | None = None
    external_value: str | None = None


class OAuthFlow(OpenAPIBaseModel):
    authorization_url: str | None = None
    token_url: str | None = None
    refresh_url: str | None = None
    scopes: dict[str, str] = Field(default_factory=dict)


class OAuthFlows(OpenAPIBaseModel):
    implicit: OAuthFlow | None = None
    password: OAuthFlow | None = None
    client_credentials: OAuthFlow | None = None
    authorization_code: OAuthFlow | None = None


class SecurityScheme(OpenAPIBaseModel):
    type: str
    description: str | None = None
    name: str | None = None
    in_: str | None = Field(default=None, alias="in")
    scheme: str | None = None
    bearer_format: str | None = None
    flows: OAuthFlows | None = None
    open_id_connect_url: str | None = None


class Link(OpenAPIBaseModel):
    ref: str | None = Field(default=None, alias="$ref")
    operation_ref: str | None = None
    operation_id: str | None = None
    parameters: dict[str, Any] | None = None
    request_body: Any | None = None
    description: str | None = None
    server: Server | None = None


# --- Schema (self-referencing, lazy $ref resolution) ---


class Schema(OpenAPIBaseModel):
    _LAZY_FIELDS: ClassVar[frozenset[str]] = frozenset()

    ref: str | None = Field(default=None, alias="$ref")

    type: str | list[str] | None = None
    nullable: bool | None = None
    format: str | None = None

    all_of: list[Schema] | None = None
    one_of: list[Schema] | None = None
    any_of: list[Schema] | None = None
    not_: Schema | None = Field(default=None, alias="not")

    items: Schema | None = None
    prefix_items: list[Schema] | None = None
    properties: dict[str, Schema] | None = None
    additional_properties: bool | Schema | None = None

    title: str | None = None
    description: str | None = None
    default: Any | None = None
    enum: list[Any] | None = None
    const: Any | None = None

    multiple_of: float | None = None
    maximum: float | None = None
    minimum: float | None = None
    exclusive_maximum: bool | float | None = None
    exclusive_minimum: bool | float | None = None
    max_length: int | None = None
    min_length: int | None = None
    pattern: str | None = None
    max_items: int | None = None
    min_items: int | None = None
    unique_items: bool | None = None
    max_properties: int | None = None
    min_properties: int | None = None
    required: list[str] | None = None

    discriminator: Discriminator | None = None
    read_only: bool | None = None
    write_only: bool | None = None
    xml: XML | None = None
    external_docs: ExternalDocs | None = None
    example: Any | None = None
    examples: list[Any] | None = None
    deprecated: bool | None = None

    def __getattribute__(self, name: str) -> Any:
        lazy_fields = type.__getattribute__(type(self), "_LAZY_FIELDS")
        if name not in lazy_fields:
            return super().__getattribute__(name)

        ref = super().__getattribute__("ref")
        if not ref:
            return super().__getattribute__(name)

        registry = _schema_registry.get()
        if registry is None:
            return super().__getattribute__(name)
        resolved = registry.get(ref)
        if resolved is not None and resolved is not self:
            return getattr(resolved, name)
        return super().__getattribute__(name)


def bind_schema_registry(schemas: dict[str, Schema]) -> None:
    """Register component schemas for lazy ``$ref`` resolution.

    Parameters
    ----------
    schemas : dict[str, Schema]
        The component schemas keyed by name.
    """
    _schema_registry.set(
        {f"#/components/schemas/{name}": schema for name, schema in schemas.items()}
    )


# --- Models that depend on Schema (ordered by dependency) ---


class Header(OpenAPIBaseModel):
    ref: str | None = Field(default=None, alias="$ref")
    description: str | None = None
    required: bool = False
    deprecated: bool = False
    schema_: Schema | None = Field(default=None, alias="schema")
    example: Any | None = None
    examples: dict[str, Example] | None = None


class Encoding(OpenAPIBaseModel):
    content_type: str | None = None
    headers: dict[str, Header] | None = None
    style: str | None = None
    explode: bool | None = None
    allow_reserved: bool = False


class MediaType(OpenAPIBaseModel):
    schema_: Schema | None = Field(default=None, alias="schema")
    example: Any | None = None
    examples: dict[str, Example] | None = None
    encoding: dict[str, Encoding] | None = None


class Parameter(OpenAPIBaseModel):
    ref: str | None = Field(default=None, alias="$ref")
    name: str | None = None
    in_: str | None = Field(default=None, alias="in")
    description: str | None = None
    required: bool = False
    deprecated: bool = False
    allow_empty_value: bool = False
    style: str | None = None
    explode: bool | None = None
    allow_reserved: bool = False
    schema_: Schema | None = Field(default=None, alias="schema")
    example: Any | None = None
    examples: dict[str, Example] | None = None
    content: dict[str, MediaType] | None = None


class RequestBody(OpenAPIBaseModel):
    ref: str | None = Field(default=None, alias="$ref")
    description: str | None = None
    content: dict[str, MediaType] | None = None
    required: bool = False


class Response(OpenAPIBaseModel):
    ref: str | None = Field(default=None, alias="$ref")
    description: str | None = None
    headers: dict[str, Header] | None = None
    content: dict[str, MediaType] | None = None
    links: dict[str, Link] | None = None


class Info(OpenAPIBaseModel):
    title: str
    version: str
    summary: str | None = None
    description: str | None = None
    terms_of_service: str | None = None
    contact: Contact | None = None
    license: License | None = Field(default=None, alias="license")


# --- Circular dependency: Operation ↔ PathItem ---
# Operation.callbacks references PathItem, PathItem references Operation.
# model_rebuild() at module end resolves this.

type Callback = dict[str, PathItem]


class Components(OpenAPIBaseModel):
    schemas: dict[str, Schema] | None = None
    responses: dict[str, Response] | None = None
    parameters: dict[str, Parameter] | None = None
    request_bodies: dict[str, RequestBody] | None = None
    headers: dict[str, Header] | None = None
    security_schemes: dict[str, SecurityScheme] | None = None
    examples: dict[str, Example] | None = None
    links: dict[str, Link] | None = None
    callbacks: dict[str, Callback] | None = None
    path_items: dict[str, PathItem] | None = None


class Operation(OpenAPIBaseModel):
    tags: list[str] | None = None
    summary: str | None = None
    description: str | None = None
    external_docs: ExternalDocs | None = None
    operation_id: str | None = None
    parameters: list[Parameter] | None = None
    request_body: RequestBody | None = None
    responses: dict[str, Response] | None = None
    callbacks: dict[str, Callback] | None = None
    deprecated: bool = False
    security: list[dict[str, list[str]]] | None = None
    servers: list[Server] | None = None


class PathItem(OpenAPIBaseModel):
    ref: str | None = Field(default=None, alias="$ref")
    summary: str | None = None
    description: str | None = None
    get: Operation | None = None
    put: Operation | None = None
    post: Operation | None = None
    delete: Operation | None = None
    options: Operation | None = None
    head: Operation | None = None
    patch: Operation | None = None
    trace: Operation | None = None
    servers: list[Server] | None = None
    parameters: list[Parameter] | None = None


class OpenAPISpec(OpenAPIBaseModel):
    openapi: str
    info: Info
    servers: list[Server] | None = None
    paths: dict[str, PathItem] | None = None
    components: Components | None = None
    security: list[dict[str, list[str]]] | None = None
    tags: list[Tag] | None = None
    external_docs: ExternalDocs | None = None
    json_schema_dialect: str | None = None
    webhooks: dict[str, PathItem] | None = None


Components.model_rebuild()
Operation.model_rebuild()
Schema._LAZY_FIELDS = frozenset(Schema.model_fields.keys()) - {"ref"}
