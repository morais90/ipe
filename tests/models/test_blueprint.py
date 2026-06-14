import pytest

from ipe.models.blueprint import APIBlueprint, OutputFile
from ipe.models.standard import (
    AuthScheme,
    Response,
    SecurityRequirement,
    StandardModel,
    StandardOperation,
    StandardParameter,
    StandardProperty,
    ValidationRule,
)


@pytest.fixture
def minimal_blueprint() -> APIBlueprint:
    return APIBlueprint(
        api_name="Petstore",
        spec_version="3.0.0",
        spec_description=None,
        base_url=None,
        server_urls=[],
        operations=[],
        models=[],
        auth_schemes=[],
        module_name="petstore",
        generated_at="2026-03-28T00:00:00Z",
        ipe_version="0.1.0",
    )


@pytest.fixture
def full_blueprint() -> APIBlueprint:
    return APIBlueprint(
        api_name="Petstore",
        spec_version="3.0.0",
        spec_description="A sample API",
        base_url="https://petstore.example.com/v1",
        server_urls=["https://petstore.example.com/v1"],
        operations=[
            StandardOperation(
                operation_id="listPets",
                method="GET",
                path="/pets",
                summary="List all pets",
                parameters=[
                    StandardParameter(
                        name="limit",
                        location="query",
                        required=False,
                        schema_type="integer",
                        schema_format="int32",
                    ),
                ],
                responses=[
                    Response(
                        status_code="200",
                        description="A list of pets",
                        content_type="application/json",
                        model_names=["Pet"],
                    ),
                ],
                security=[SecurityRequirement(scheme_name="api_key")],
            ),
        ],
        models=[
            StandardModel(
                name="Pet",
                description="A pet",
                properties=[
                    StandardProperty(name="id", schema_type="integer", required=True),
                    StandardProperty(name="name", schema_type="string", required=True),
                    StandardProperty(
                        name="status",
                        schema_type="string",
                        enum_values=["available", "sold"],
                    ),
                ],
                required_fields=["id", "name"],
                validation_rules=[ValidationRule(rule_type="min_length", value=1)],
            ),
        ],
        auth_schemes=[
            AuthScheme(
                name="api_key",
                kind="apikey",
                location="header",
                parameter_name="X-API-Key",
            ),
        ],
        module_name="petstore",
        generated_at="2026-03-28T00:00:00Z",
        ipe_version="0.1.0",
        generator_config={"async": True},
    )


class TestOutputFile:
    def test_creation(self):
        out = OutputFile(
            template="client.py.jinja",
            output_path="petstore/client.py",
            context={"module_name": "petstore"},
        )

        assert out.model_dump() == {
            "template": "client.py.jinja",
            "output_path": "petstore/client.py",
            "context": {"module_name": "petstore"},
        }


class TestAPIBlueprint:
    def test_minimal(self, minimal_blueprint: APIBlueprint):
        assert minimal_blueprint.model_dump() == {
            "api_name": "Petstore",
            "spec_version": "3.0.0",
            "spec_description": None,
            "base_url": None,
            "server_urls": [],
            "operations": [],
            "models": [],
            "body_schemas": [],
            "auth_schemes": [],
            "module_name": "petstore",
            "generated_at": "2026-03-28T00:00:00Z",
            "ipe_version": "0.1.0",
            "generator_config": {},
        }

    def test_full(self, full_blueprint: APIBlueprint):
        assert full_blueprint.model_dump() == {
            "api_name": "Petstore",
            "spec_version": "3.0.0",
            "spec_description": "A sample API",
            "base_url": "https://petstore.example.com/v1",
            "server_urls": ["https://petstore.example.com/v1"],
            "operations": [
                {
                    "operation_id": "listPets",
                    "method": "GET",
                    "path": "/pets",
                    "summary": "List all pets",
                    "description": None,
                    "tags": [],
                    "parameters": [
                        {
                            "name": "limit",
                            "location": "query",
                            "required": False,
                            "schema_type": "integer",
                            "description": None,
                            "schema_format": "int32",
                            "default": None,
                            "enum_values": None,
                            "validation_rules": [],
                            "model_names": [],
                            "is_list": False,
                            "discriminator": None,
                            "item_primitive": None,
                        },
                    ],
                    "request_body": None,
                    "responses": [
                        {
                            "status_code": "200",
                            "description": "A list of pets",
                            "content_type": "application/json",
                            "model_names": ["Pet"],
                            "is_list": False,
                            "discriminator": None,
                            "primitive_type": None,
                        },
                    ],
                    "security": [{"scheme_name": "api_key", "scopes": []}],
                },
            ],
            "models": [
                {
                    "name": "Pet",
                    "description": "A pet",
                    "properties": [
                        {
                            "name": "id",
                            "schema_type": "integer",
                            "description": None,
                            "schema_format": None,
                            "required": True,
                            "nullable": False,
                            "default": None,
                            "enum_values": None,
                            "validation_rules": [],
                            "model_names": [],
                            "is_list": False,
                            "discriminator": None,
                            "item_primitive": None,
                        },
                        {
                            "name": "name",
                            "schema_type": "string",
                            "description": None,
                            "schema_format": None,
                            "required": True,
                            "nullable": False,
                            "default": None,
                            "enum_values": None,
                            "validation_rules": [],
                            "model_names": [],
                            "is_list": False,
                            "discriminator": None,
                            "item_primitive": None,
                        },
                        {
                            "name": "status",
                            "schema_type": "string",
                            "description": None,
                            "schema_format": None,
                            "required": False,
                            "nullable": False,
                            "default": None,
                            "enum_values": ["available", "sold"],
                            "validation_rules": [],
                            "model_names": [],
                            "is_list": False,
                            "discriminator": None,
                            "item_primitive": None,
                        },
                    ],
                    "required_fields": ["id", "name"],
                    "validation_rules": [
                        {"rule_type": "min_length", "value": 1},
                    ],
                },
            ],
            "auth_schemes": [
                {
                    "name": "api_key",
                    "kind": "apikey",
                    "location": "header",
                    "parameter_name": "X-API-Key",
                    "token_url": None,
                },
            ],
            "body_schemas": [],
            "module_name": "petstore",
            "generated_at": "2026-03-28T00:00:00Z",
            "ipe_version": "0.1.0",
            "generator_config": {"async": True},
        }
