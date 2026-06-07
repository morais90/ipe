from ipe.models.standard import StandardParameter, StandardProperty
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
        }


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
        }
