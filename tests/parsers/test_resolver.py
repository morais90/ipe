from typing import Any

import pytest

from ipe.core.exceptions import ValidationError
from ipe.parsers.resolver import resolve_refs


class TestResolveSimpleRefs:
    def test_no_refs_unchanged(self):
        spec: dict[str, Any] = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
        }

        result = resolve_refs(spec)

        assert result == {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
        }

    def test_single_ref(self):
        spec: dict[str, Any] = {
            "components": {
                "schemas": {
                    "Pet": {"type": "object", "properties": {"name": {"type": "string"}}},
                },
            },
            "paths": {
                "/pets": {
                    "get": {
                        "responses": {
                            "200": {
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Pet"},
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }

        result = resolve_refs(spec)

        resolved_schema = result["paths"]["/pets"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
        assert resolved_schema == {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }

    def test_does_not_mutate_original(self):
        spec: dict[str, Any] = {
            "components": {"schemas": {"A": {"type": "string"}}},
            "ref_user": {"$ref": "#/components/schemas/A"},
        }

        resolve_refs(spec)

        assert spec["ref_user"] == {"$ref": "#/components/schemas/A"}


class TestResolveRealSpecs:
    def test_petstore_expanded_spec_allof(self, petstore_expanded_spec: dict[str, Any]):
        result = resolve_refs(petstore_expanded_spec)

        pet_schema = result["components"]["schemas"]["Pet"]
        assert pet_schema["allOf"][0] == {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {"type": "string"},
                "tag": {"type": "string"},
            },
        }

    def test_petstore_expanded_spec_response_ref(self, petstore_expanded_spec: dict[str, Any]):
        result = resolve_refs(petstore_expanded_spec)

        error_schema = result["paths"]["/pets"]["get"]["responses"]["default"]["content"]["application/json"]["schema"]
        assert error_schema == {
            "type": "object",
            "required": ["code", "message"],
            "properties": {
                "code": {"type": "integer", "format": "int32"},
                "message": {"type": "string"},
            },
        }


class TestCircularRefs:
    def test_circular_ref_spec_does_not_loop(self, circular_ref_spec: dict[str, Any]):
        result = resolve_refs(circular_ref_spec)

        node = result["components"]["schemas"]["Node"]
        assert node["type"] == "object"
        assert node["properties"]["children"]["type"] == "array"
        nested = node["properties"]["children"]["items"]
        assert nested["type"] == "object"
        assert nested["properties"]["children"]["items"]["$ref"] == "#/components/schemas/Node"

    def test_mutual_circular_ref_spec(self, circular_ref_spec: dict[str, Any]):
        result = resolve_refs(circular_ref_spec)

        category = result["components"]["schemas"]["Category"]
        assert "properties" in category
        assert "subcategories" in category["properties"]


class TestRefErrors:
    def test_missing_ref_target(self):
        spec: dict[str, Any] = {
            "ref_user": {"$ref": "#/components/schemas/Missing"},
            "components": {"schemas": {}},
        }

        with pytest.raises(ValidationError, match="not found"):
            resolve_refs(spec)

    def test_external_ref_rejected(self):
        spec: dict[str, Any] = {
            "ref_user": {"$ref": "other.yaml#/components/schemas/Pet"},
        }

        with pytest.raises(ValidationError, match="Unsupported"):
            resolve_refs(spec)

    def test_tilde_encoded_path(self):
        spec: dict[str, Any] = {
            "components": {"schemas": {"a~b": {"type": "string"}}},
            "ref_user": {"$ref": "#/components/schemas/a~0b"},
        }

        result = resolve_refs(spec)

        assert result["ref_user"] == {"type": "string"}
