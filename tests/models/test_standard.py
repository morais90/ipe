from ipe.models.standard import AuthScheme, StandardParameter, StandardProperty
from ipe.parsers import models as openapi


class TestStandardPropertyFromSchema:
    def test_extracts_validation_rules(self):
        schema = openapi.Schema.model_validate(
            {
                "type": "string",
                "minLength": 3,
                "maxLength": 64,
                "pattern": "^[a-z_]+$",
            }
        )

        prop = StandardProperty.from_schema(
            "username", schema, required_fields=["username"]
        )

        assert prop.model_dump() == {
            "name": "username",
            "schema_type": "string",
            "description": None,
            "schema_format": None,
            "required": True,
            "nullable": False,
            "default": None,
            "enum_values": None,
            "validation_rules": [
                {"rule_type": "min_length", "value": 3},
                {"rule_type": "max_length", "value": 64},
                {"rule_type": "pattern", "value": "^[a-z_]+$"},
            ],
            "model_names": [],
            "is_list": False,
            "discriminator": None,
            "item_primitive": None,
        }

    def test_extracts_numeric_bounds(self):
        schema = openapi.Schema.model_validate(
            {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
            }
        )

        prop = StandardProperty.from_schema("limit", schema, required_fields=[])

        assert prop.model_dump() == {
            "name": "limit",
            "schema_type": "integer",
            "description": None,
            "schema_format": None,
            "required": False,
            "nullable": False,
            "default": None,
            "enum_values": None,
            "validation_rules": [
                {"rule_type": "minimum", "value": 1.0},
                {"rule_type": "maximum", "value": 100.0},
            ],
            "model_names": [],
            "is_list": False,
            "discriminator": None,
            "item_primitive": None,
        }

    def test_extracts_enum_values(self):
        schema = openapi.Schema.model_validate(
            {
                "type": "string",
                "enum": ["pending", "succeeded", "failed"],
            }
        )

        prop = StandardProperty.from_schema(
            "status", schema, required_fields=["status"]
        )

        assert prop.model_dump() == {
            "name": "status",
            "schema_type": "string",
            "description": None,
            "schema_format": None,
            "required": True,
            "nullable": False,
            "default": None,
            "enum_values": ["pending", "succeeded", "failed"],
            "validation_rules": [],
            "model_names": [],
            "is_list": False,
            "discriminator": None,
            "item_primitive": None,
        }

    def test_resolves_model_reference(self):
        schema = openapi.Schema.model_validate({"$ref": "#/components/schemas/Money"})

        prop = StandardProperty.from_schema(
            "amount", schema, required_fields=["amount"]
        )

        assert prop.model_names == ["Money"]
        assert prop.is_list is False
        assert prop.item_primitive is None

    def test_resolves_array_of_models(self):
        schema = openapi.Schema.model_validate(
            {
                "type": "array",
                "items": {"$ref": "#/components/schemas/Charge"},
            }
        )

        prop = StandardProperty.from_schema("data", schema, required_fields=["data"])

        assert prop.is_list is True
        assert prop.model_names == ["Charge"]
        assert prop.item_primitive is None

    def test_resolves_array_of_primitives(self):
        schema = openapi.Schema.model_validate(
            {
                "type": "array",
                "items": {"type": "string"},
            }
        )

        prop = StandardProperty.from_schema("tags", schema, required_fields=[])

        assert prop.is_list is True
        assert prop.item_primitive == "string"
        assert prop.model_names == []

    def test_resolves_discriminated_union(self):
        schema = openapi.Schema.model_validate(
            {
                "oneOf": [
                    {"$ref": "#/components/schemas/CardDetails"},
                    {"$ref": "#/components/schemas/PixDetails"},
                ],
                "discriminator": {"propertyName": "type"},
            }
        )

        prop = StandardProperty.from_schema("details", schema, required_fields=[])

        assert prop.model_names == ["CardDetails", "PixDetails"]
        assert prop.discriminator == "type"
        assert prop.is_list is False


class TestStandardParameterFromParameter:
    def test_extracts_validation_rules(self):
        param = openapi.Parameter.model_validate(
            {
                "name": "limit",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100,
                    "multipleOf": 5,
                },
            }
        )

        result = StandardParameter.from_parameter(param)

        assert result.model_dump() == {
            "name": "limit",
            "location": "query",
            "required": False,
            "schema_type": "integer",
            "description": None,
            "schema_format": None,
            "default": None,
            "enum_values": None,
            "validation_rules": [
                {"rule_type": "minimum", "value": 1.0},
                {"rule_type": "maximum", "value": 100.0},
                {"rule_type": "multiple_of", "value": 5.0},
            ],
            "model_names": [],
            "is_list": False,
            "discriminator": None,
            "item_primitive": None,
        }

    def test_extracts_enum_values(self):
        param = openapi.Parameter.model_validate(
            {
                "name": "status",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "string",
                    "enum": ["active", "archived"],
                },
            }
        )

        result = StandardParameter.from_parameter(param)

        assert result.model_dump() == {
            "name": "status",
            "location": "query",
            "required": False,
            "schema_type": "string",
            "description": None,
            "schema_format": None,
            "default": None,
            "enum_values": ["active", "archived"],
            "validation_rules": [],
            "model_names": [],
            "is_list": False,
            "discriminator": None,
            "item_primitive": None,
        }

    def test_resolves_array_of_primitives(self):
        param = openapi.Parameter.model_validate(
            {
                "name": "expand",
                "in": "query",
                "required": False,
                "schema": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            }
        )

        result = StandardParameter.from_parameter(param)

        assert result.is_list is True
        assert result.item_primitive == "string"
        assert result.model_names == []


class TestAuthSchemeFromSecurityScheme:
    def test_bearer(self):
        scheme = openapi.SecurityScheme.model_validate(
            {"type": "http", "scheme": "bearer"}
        )

        result = AuthScheme.from_security_scheme("bearerAuth", scheme)

        assert result.model_dump() == {
            "name": "bearerAuth",
            "kind": "bearer",
            "location": None,
            "parameter_name": None,
            "token_url": None,
        }

    def test_basic(self):
        scheme = openapi.SecurityScheme.model_validate(
            {"type": "http", "scheme": "basic"}
        )

        result = AuthScheme.from_security_scheme("basicAuth", scheme)

        assert result.kind == "basic"

    def test_api_key_in_header(self):
        scheme = openapi.SecurityScheme.model_validate(
            {"type": "apiKey", "in": "header", "name": "X-API-Key"}
        )

        result = AuthScheme.from_security_scheme("apiKeyAuth", scheme)

        assert result.model_dump() == {
            "name": "apiKeyAuth",
            "kind": "apikey",
            "location": "header",
            "parameter_name": "X-API-Key",
            "token_url": None,
        }

    def test_api_key_in_query(self):
        scheme = openapi.SecurityScheme.model_validate(
            {"type": "apiKey", "in": "query", "name": "api_key"}
        )

        result = AuthScheme.from_security_scheme("apiKeyAuth", scheme)

        assert result.model_dump() == {
            "name": "apiKeyAuth",
            "kind": "apikey",
            "location": "query",
            "parameter_name": "api_key",
            "token_url": None,
        }

    def test_oauth2_without_client_credentials(self):
        scheme = openapi.SecurityScheme.model_validate(
            {
                "type": "oauth2",
                "flows": {
                    "authorizationCode": {
                        "authorizationUrl": "https://e.com/authorize",
                        "tokenUrl": "https://e.com/token",
                        "scopes": {},
                    }
                },
            }
        )

        result = AuthScheme.from_security_scheme("oauth2", scheme)

        assert result.kind == "oauth2"
        assert result.token_url is None

    def test_oauth2_client_credentials(self):
        scheme = openapi.SecurityScheme.model_validate(
            {
                "type": "oauth2",
                "flows": {
                    "clientCredentials": {
                        "tokenUrl": "https://e.com/oauth/token",
                        "scopes": {"read": "Read"},
                    }
                },
            }
        )

        result = AuthScheme.from_security_scheme("oauth2", scheme)

        assert result.kind == "oauth2_client_credentials"
        assert result.token_url == "https://e.com/oauth/token"
