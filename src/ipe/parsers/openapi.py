
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from ipe.core.exceptions import UnsupportedFeatureError, ValidationError
from ipe.parsers.models import OpenAPISpec
from ipe.parsers.resolver import resolve_refs


def parse_openapi(spec_dict: dict[str, Any]) -> OpenAPISpec:
    _validate_version(spec_dict)
    normalized = _normalize_30_to_31(spec_dict)
    resolved = resolve_refs(normalized)

    try:
        return OpenAPISpec.model_validate(resolved)
    except PydanticValidationError as exc:
        raise ValidationError(
            "Invalid OpenAPI specification structure",
            "Check the spec against the OpenAPI 3.x specification",
        ) from exc


def _validate_version(spec_dict: dict[str, Any]) -> None:
    version = spec_dict.get("openapi")
    swagger = spec_dict.get("swagger")

    if swagger:
        raise UnsupportedFeatureError(
            f"Swagger {swagger} is not supported",
            "Convert to OpenAPI 3.0+ using https://converter.swagger.io",
            feature="Swagger 2.0",
            version=str(swagger),
        )

    if not version:
        raise ValidationError(
            "Missing 'openapi' field",
            "Add an 'openapi' field with the version (e.g., '3.0.3' or '3.1.0')",
        )

    if not isinstance(version, str) or not version.startswith(("3.0", "3.1")):
        raise UnsupportedFeatureError(
            f"OpenAPI version {version} is not supported",
            "Use OpenAPI 3.0.x or 3.1.x",
            feature=f"OpenAPI {version}",
            version=str(version),
        )


def _normalize_30_to_31(spec_dict: dict[str, Any]) -> dict[str, Any]:
    version = spec_dict.get("openapi", "")
    if isinstance(version, str) and version.startswith("3.0"):
        _walk_schemas(spec_dict, _normalize_schema)
    return spec_dict


def _walk_schemas(node: Any, visitor: Callable[[dict[str, Any]], None]) -> None:
    if not isinstance(node, dict):
        return

    if "type" in node or "properties" in node or "allOf" in node:
        visitor(node)

    for value in node.values():
        if isinstance(value, dict):
            _walk_schemas(value, visitor)
        elif isinstance(value, list):
            for item in value:
                _walk_schemas(item, visitor)


def _normalize_schema(schema: dict[str, Any]) -> None:
    if schema.get("nullable") is True:
        current_type = schema.get("type")
        if isinstance(current_type, str):
            schema["type"] = [current_type, "null"]
        del schema["nullable"]
    elif "nullable" in schema:
        del schema["nullable"]

    if schema.get("exclusiveMinimum") is True:
        minimum = schema.get("minimum")
        if minimum is not None:
            schema["exclusiveMinimum"] = minimum
            del schema["minimum"]

    if schema.get("exclusiveMaximum") is True:
        maximum = schema.get("maximum")
        if maximum is not None:
            schema["exclusiveMaximum"] = maximum
            del schema["maximum"]

    if "example" in schema and "examples" not in schema:
        schema["examples"] = [schema["example"]]
        del schema["example"]
