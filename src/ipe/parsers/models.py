from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class OpenAPIBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        populate_by_name=True,
        alias_generator=to_camel,
    )


class Contact(OpenAPIBaseModel):
    name: str | None = None
    url: str | None = None
    email: str | None = None


class License(OpenAPIBaseModel):
    name: str
    url: str | None = None
    identifier: str | None = None


class Info(OpenAPIBaseModel):
    title: str
    version: str
    summary: str | None = None
    description: str | None = None
    terms_of_service: str | None = None
    contact: Contact | None = None
    license: License | None = Field(default=None, alias="license")


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


class Tag(OpenAPIBaseModel):
    name: str
    description: str | None = None
    external_docs: ExternalDocs | None = None


class Discriminator(OpenAPIBaseModel):
    property_name: str
    mapping: dict[str, str] | None = None


class XML(OpenAPIBaseModel):
    name: str | None = None
    namespace: str | None = None
    prefix: str | None = None
    attribute: bool = False
    wrapped: bool = False


class Schema(OpenAPIBaseModel):
    ref: str | None = Field(default=None, alias="$ref")

    type: str | list[str] | None = None
    nullable: bool | None = None
    format: str | None = None

    all_of: list[dict[str, Any]] | None = None
    one_of: list[dict[str, Any]] | None = None
    any_of: list[dict[str, Any]] | None = None
    not_: dict[str, Any] | None = Field(default=None, alias="not")

    items: dict[str, Any] | None = None
    prefix_items: list[dict[str, Any]] | None = None
    properties: dict[str, dict[str, Any]] | None = None
    additional_properties: bool | dict[str, Any] | None = None

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


class MediaType(OpenAPIBaseModel):
    schema_: dict[str, Any] | None = Field(default=None, alias="schema")
    example: Any | None = None
    examples: dict[str, Any] | None = None
    encoding: dict[str, Any] | None = None


class Header(OpenAPIBaseModel):
    ref: str | None = Field(default=None, alias="$ref")
    description: str | None = None
    required: bool = False
    deprecated: bool = False
    schema_: dict[str, Any] | None = Field(default=None, alias="schema")
    example: Any | None = None
    examples: dict[str, Any] | None = None


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
    schema_: dict[str, Any] | None = Field(default=None, alias="schema")
    example: Any | None = None
    examples: dict[str, Any] | None = None
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
    links: dict[str, Any] | None = None


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


class Components(OpenAPIBaseModel):
    schemas: dict[str, dict[str, Any]] | None = None
    responses: dict[str, dict[str, Any]] | None = None
    parameters: dict[str, dict[str, Any]] | None = None
    examples: dict[str, dict[str, Any]] | None = None
    request_bodies: dict[str, dict[str, Any]] | None = None
    headers: dict[str, dict[str, Any]] | None = None
    security_schemes: dict[str, dict[str, Any]] | None = None
    links: dict[str, dict[str, Any]] | None = None
    callbacks: dict[str, dict[str, Any]] | None = None
    path_items: dict[str, dict[str, Any]] | None = None


class Operation(OpenAPIBaseModel):
    tags: list[str] | None = None
    summary: str | None = None
    description: str | None = None
    external_docs: ExternalDocs | None = None
    operation_id: str | None = None
    parameters: list[dict[str, Any]] | None = None
    request_body: dict[str, Any] | None = None
    responses: dict[str, dict[str, Any]] | None = None
    callbacks: dict[str, Any] | None = None
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
    parameters: list[dict[str, Any]] | None = None


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
    webhooks: dict[str, dict[str, Any]] | None = None
