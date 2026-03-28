from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationRule:
    rule_type: str
    value: Any


@dataclass
class SecurityRequirement:
    scheme_name: str
    scopes: list[str] = field(default_factory=list)


@dataclass
class StandardProperty:
    name: str
    schema_type: str
    description: str | None = None
    schema_format: str | None = None
    required: bool = False
    nullable: bool = False
    default: Any | None = None
    enum_values: list[Any] | None = None


@dataclass
class StandardModel:
    name: str
    description: str | None = None
    properties: list[StandardProperty] = field(default_factory=list)
    required_fields: list[str] = field(default_factory=list)
    validation_rules: list[ValidationRule] = field(default_factory=list)


@dataclass
class StandardParameter:
    name: str
    location: str
    required: bool
    schema_type: str
    description: str | None = None
    schema_format: str | None = None
    default: Any | None = None


@dataclass
class RequestBody:
    required: bool
    content_types: list[str]
    schema_type: str
    description: str | None = None
    schema_format: str | None = None


@dataclass
class Response:
    status_code: str
    description: str | None = None
    content_type: str | None = None
    schema_type: str | None = None
    schema_format: str | None = None


@dataclass
class AuthScheme:
    name: str
    type: str
    scheme: str | None = None
    location: str | None = None
    header_name: str | None = None


@dataclass
class StandardOperation:
    operation_id: str
    method: str
    path: str
    summary: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    parameters: list[StandardParameter] = field(default_factory=list)
    request_body: RequestBody | None = None
    responses: list[Response] = field(default_factory=list)
    security: list[SecurityRequirement] = field(default_factory=list)
