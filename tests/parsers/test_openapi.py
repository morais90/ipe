from typing import Any

import pytest

from ipe.core.exceptions import UnsupportedFeatureError, ValidationError
from ipe.parsers.openapi import parse_openapi


class TestParseOpenAPI:
    def test_petstore_30(self, petstore_spec: dict[str, Any]):
        spec = parse_openapi(petstore_spec)

        assert spec.openapi == "3.0.0"
        assert spec.info.title == "Swagger Petstore"
        assert spec.paths is not None
        assert set(spec.paths.keys()) == {"/pets", "/pets/{petId}"}

    def test_museum_31(self, museum_spec: dict[str, Any]):
        spec = parse_openapi(museum_spec)

        assert spec.openapi == "3.1.0"
        assert spec.info.title == "Redocly Museum API"
        assert spec.paths is not None
        assert "/museum-hours" in spec.paths

    def test_petstore_swagger(self, petstore_swagger_spec: dict[str, Any]):
        spec = parse_openapi(petstore_swagger_spec)

        assert spec.paths is not None
        assert "/pet" in spec.paths

    def test_notion(self, notion_spec: dict[str, Any]):
        spec = parse_openapi(notion_spec)

        assert spec.openapi == "3.0.3"
        assert spec.paths is not None
        assert len(spec.paths) > 0

    def test_refs_resolved_lazily(self, petstore_spec: dict[str, Any]):
        spec = parse_openapi(petstore_spec)

        assert spec.paths is not None
        get_op = spec.paths["/pets"].get
        assert get_op is not None
        assert get_op.responses is not None
        resp = get_op.responses["200"]
        assert resp.content is not None
        schema = resp.content["application/json"].schema_
        assert schema is not None
        assert schema.ref == "#/components/schemas/Pets"
        assert schema.type == "array"
        assert schema.items is not None
        assert schema.items.ref == "#/components/schemas/Pet"
        assert schema.items.type == "object"
        assert set(schema.items.properties.keys()) == {"id", "name", "tag"}


class TestVersionValidation:
    def test_swagger_20_rejected(self, swagger2_spec: dict[str, Any]):
        with pytest.raises(UnsupportedFeatureError, match="Swagger 2.0"):
            parse_openapi(swagger2_spec)

    def test_missing_openapi_field(self):
        raw: dict[str, Any] = {
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
        }

        with pytest.raises(ValidationError, match="Missing 'openapi'"):
            parse_openapi(raw)

    def test_unsupported_version(self):
        raw: dict[str, Any] = {
            "openapi": "4.0.0",
            "info": {"title": "Future", "version": "1.0"},
            "paths": {},
        }

        with pytest.raises(UnsupportedFeatureError, match="4.0.0"):
            parse_openapi(raw)

    @pytest.mark.parametrize(
        "version",
        ["3.0.0", "3.0.1", "3.0.2", "3.0.3", "3.1.0"],
    )
    def test_supported_versions(self, version: str):
        raw: dict[str, Any] = {
            "openapi": version,
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
        }

        spec = parse_openapi(raw)

        assert spec.openapi == version


class TestNormalization30to31:
    def test_nullable_to_type_array(self):
        raw: dict[str, Any] = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "Nullable": {
                        "type": "string",
                        "nullable": True,
                    },
                },
            },
        }

        spec = parse_openapi(raw)

        assert spec.components is not None
        assert spec.components.schemas is not None
        assert spec.components.schemas["Nullable"].model_dump(by_alias=True, exclude_unset=True) == {
            "type": ["string", "null"],
        }

    def test_exclusive_minimum_boolean_to_number(self):
        raw: dict[str, Any] = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "Bounded": {
                        "type": "integer",
                        "minimum": 0,
                        "exclusiveMinimum": True,
                    },
                },
            },
        }

        spec = parse_openapi(raw)

        assert spec.components is not None
        assert spec.components.schemas is not None
        assert spec.components.schemas["Bounded"].model_dump(by_alias=True, exclude_unset=True) == {
            "type": "integer",
            "exclusiveMinimum": 0.0,
        }

    def test_exclusive_maximum_boolean_to_number(self):
        raw: dict[str, Any] = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "Bounded": {
                        "type": "integer",
                        "maximum": 100,
                        "exclusiveMaximum": True,
                    },
                },
            },
        }

        spec = parse_openapi(raw)

        assert spec.components is not None
        assert spec.components.schemas is not None
        assert spec.components.schemas["Bounded"].model_dump(by_alias=True, exclude_unset=True) == {
            "type": "integer",
            "exclusiveMaximum": 100.0,
        }

    def test_example_to_examples_array(self):
        raw: dict[str, Any] = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "WithExample": {
                        "type": "string",
                        "example": "hello",
                    },
                },
            },
        }

        spec = parse_openapi(raw)

        assert spec.components is not None
        assert spec.components.schemas is not None
        assert spec.components.schemas["WithExample"].model_dump(by_alias=True, exclude_unset=True) == {
            "type": "string",
            "examples": ["hello"],
        }

    def test_31_not_normalized(self):
        raw: dict[str, Any] = {
            "openapi": "3.1.0",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "Already31": {
                        "type": ["string", "null"],
                        "examples": ["hello"],
                    },
                },
            },
        }

        spec = parse_openapi(raw)

        assert spec.components is not None
        assert spec.components.schemas is not None
        assert spec.components.schemas["Already31"].model_dump(by_alias=True, exclude_unset=True) == {
            "type": ["string", "null"],
            "examples": ["hello"],
        }


class TestInvalidSpec:
    def test_invalid_structure(self):
        raw: dict[str, Any] = {
            "openapi": "3.0.0",
            "not_info": {},
        }

        with pytest.raises(ValidationError, match="Invalid OpenAPI"):
            parse_openapi(raw)
