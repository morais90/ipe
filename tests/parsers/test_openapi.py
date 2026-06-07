from typing import Any

import pytest

from ipe.core.exceptions import UnsupportedFeatureError, ValidationError
from ipe.parsers.openapi import parse_openapi


class TestParseOpenAPI:
    def test_florada_31(self, florada_spec: dict[str, Any]):
        spec = parse_openapi(florada_spec)

        assert spec.openapi == "3.1.0"
        assert spec.info.title == "Florada Payments"
        assert spec.paths is not None
        assert set(spec.paths.keys()) == {
            "/charges",
            "/charges/{charge_id}",
            "/charges/{charge_id}/capture",
            "/charges/{charge_id}/refunds",
            "/customers",
            "/customers/{customer_id}",
            "/customers/{customer_id}/payment-methods",
            "/customers/{customer_id}/payment-methods/{method_id}",
            "/customers/{customer_id}/subscriptions",
            "/customers/{customer_id}/subscriptions/{subscription_id}/cancel",
            "/disputes",
            "/disputes/{dispute_id}",
            "/disputes/{dispute_id}/evidence",
            "/plans",
            "/webhooks",
            "/webhooks/{webhook_id}",
        }

    def test_florada_v30(self, florada_v30_spec: dict[str, Any]):
        spec = parse_openapi(florada_v30_spec)

        assert spec.openapi == "3.0.3"
        assert spec.info.title == "Florada Payments"

    def test_refs_resolved_lazily(self, florada_spec: dict[str, Any]):
        spec = parse_openapi(florada_spec)

        assert spec.components is not None
        assert spec.components.schemas is not None
        charge = spec.components.schemas["Charge"]
        assert charge.properties is not None
        status_prop = charge.properties["status"]
        assert status_prop.ref == "#/components/schemas/ChargeStatus"
        assert status_prop.type == "string"
        assert status_prop.enum == [
            "pending",
            "succeeded",
            "failed",
            "refunded",
            "disputed",
        ]


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
        assert spec.components.schemas["Nullable"].model_dump(
            by_alias=True, exclude_unset=True
        ) == {
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
        assert spec.components.schemas["Bounded"].model_dump(
            by_alias=True, exclude_unset=True
        ) == {
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
        assert spec.components.schemas["Bounded"].model_dump(
            by_alias=True, exclude_unset=True
        ) == {
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
        assert spec.components.schemas["WithExample"].model_dump(
            by_alias=True, exclude_unset=True
        ) == {
            "type": "string",
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


class TestInlineComponentRefs:
    def test_parameter_ref_inlined(self, florada_spec: dict[str, Any]):
        spec = parse_openapi(florada_spec)

        get_charge = spec.paths["/charges/{charge_id}"].get  # type: ignore[index, union-attr]
        charge_id = get_charge.parameters[0]  # type: ignore[index, union-attr]

        assert charge_id.model_dump(by_alias=True, exclude_unset=True) == {
            "name": "charge_id",
            "in": "path",
            "required": True,
            "description": "Unique charge identifier",
            "schema": {"type": "string", "format": "uuid"},
        }

    def test_response_ref_inlined(self, florada_spec: dict[str, Any]):
        spec = parse_openapi(florada_spec)

        get_charge = spec.paths["/charges/{charge_id}"].get  # type: ignore[index, union-attr]
        not_found = get_charge.responses["404"]  # type: ignore[index, union-attr]

        assert not_found.model_dump(by_alias=True, exclude_unset=True) == {
            "description": "Resource not found",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/Error"},
                },
            },
        }

    def test_schema_ref_not_inlined(self, florada_spec: dict[str, Any]):
        spec = parse_openapi(florada_spec)

        charge = spec.components.schemas["Charge"]  # type: ignore[index, union-attr]
        status = charge.properties["status"]  # type: ignore[index]

        assert status.model_dump(by_alias=True, exclude_unset=True) == {
            "$ref": "#/components/schemas/ChargeStatus",
        }

    def test_spec_without_components_unchanged(self):
        raw: dict[str, Any] = {
            "openapi": "3.0.3",
            "info": {"title": "Test", "version": "1.0"},
            "paths": {
                "/items": {
                    "get": {
                        "responses": {"200": {"description": "OK"}},
                    },
                },
            },
        }

        spec = parse_openapi(raw)
        items_get = spec.paths["/items"].get  # type: ignore[index, union-attr]

        assert items_get.model_dump(by_alias=True, exclude_unset=True) == {
            "responses": {"200": {"description": "OK"}},
        }
