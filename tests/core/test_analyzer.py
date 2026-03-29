from pathlib import Path

import pytest

from ipe.core.analyzer import SpecAnalyzer
from ipe.core.config import IpeConfig
from ipe.models.blueprint import APIBlueprint

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def petstore_blueprint() -> APIBlueprint:
    analyzer = SpecAnalyzer()
    spec = analyzer.parse(str(FIXTURES_DIR / "petstore.yaml"))
    config = IpeConfig(spec_path=str(FIXTURES_DIR / "petstore.yaml"))
    return analyzer.extract(spec, config)


class TestSpecAnalyzerParse:
    def test_parse_petstore(self):
        analyzer = SpecAnalyzer()

        spec = analyzer.parse(str(FIXTURES_DIR / "petstore.yaml"))

        assert spec.openapi == "3.0.0"
        assert spec.info.model_dump(by_alias=True, exclude_unset=True) == {
            "title": "Swagger Petstore",
            "version": "1.0.0",
            "license": {"name": "MIT"},
        }
        assert spec.paths is not None
        assert set(spec.paths.keys()) == {"/pets", "/pets/{petId}"}

    def test_parse_museum(self):
        analyzer = SpecAnalyzer()

        spec = analyzer.parse(str(FIXTURES_DIR / "museum.yaml"))

        assert spec.openapi == "3.1.0"
        assert spec.info.title == "Redocly Museum API"
        assert spec.info.version == "1.2.1"
        assert spec.paths is not None
        assert set(spec.paths.keys()) == {
            "/museum-hours",
            "/special-events",
            "/special-events/{eventId}",
            "/tickets",
            "/tickets/{ticketId}/qr",
        }

    def test_refs_resolve_lazily(self):
        analyzer = SpecAnalyzer()

        spec = analyzer.parse(str(FIXTURES_DIR / "petstore.yaml"))

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
        assert schema.items.type == "object"


class TestSpecAnalyzerExtractOperations:
    def test_operation_full_output(self, petstore_blueprint: APIBlueprint):
        assert petstore_blueprint.operations[0].model_dump() == {
            "operation_id": "listPets",
            "method": "GET",
            "path": "/pets",
            "summary": "List all pets",
            "description": None,
            "tags": ["pets"],
            "parameters": [
                {
                    "name": "limit",
                    "location": "query",
                    "required": False,
                    "schema_type": "integer",
                    "description": "How many items to return at one time (max 100)",
                    "schema_format": "int32",
                    "default": None,
                },
            ],
            "request_body": None,
            "responses": [
                {
                    "status_code": "200",
                    "description": "A paged array of pets",
                    "content_type": "application/json",
                    "schema_type": "array",
                    "schema_format": None,
                },
                {
                    "status_code": "default",
                    "description": "unexpected error",
                    "content_type": "application/json",
                    "schema_type": "object",
                    "schema_format": None,
                },
            ],
            "security": [],
        }

    def test_operation_with_request_body(self, petstore_blueprint: APIBlueprint):
        assert petstore_blueprint.operations[1].request_body is not None
        assert petstore_blueprint.operations[1].request_body.model_dump() == {
            "required": True,
            "content_types": ["application/json"],
            "schema_type": "object",
            "description": None,
            "schema_format": None,
        }

    def test_path_parameter(self, petstore_blueprint: APIBlueprint):
        assert petstore_blueprint.operations[2].parameters[0].model_dump() == {
            "name": "petId",
            "location": "path",
            "required": True,
            "schema_type": "string",
            "description": "The id of the pet to retrieve",
            "schema_format": None,
            "default": None,
        }


class TestSpecAnalyzerExtractModels:
    def test_pet_model_full_output(self, petstore_blueprint: APIBlueprint):
        assert petstore_blueprint.models[0].model_dump() == {
            "name": "Pet",
            "description": None,
            "properties": [
                {
                    "name": "id",
                    "schema_type": "integer",
                    "description": None,
                    "schema_format": "int64",
                    "required": True,
                    "nullable": False,
                    "default": None,
                    "enum_values": None,
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
                },
                {
                    "name": "tag",
                    "schema_type": "string",
                    "description": None,
                    "schema_format": None,
                    "required": False,
                    "nullable": False,
                    "default": None,
                    "enum_values": None,
                },
            ],
            "required_fields": ["id", "name"],
            "validation_rules": [],
        }

    def test_error_model_full_output(self, petstore_blueprint: APIBlueprint):
        assert petstore_blueprint.models[1].model_dump() == {
            "name": "Error",
            "description": None,
            "properties": [
                {
                    "name": "code",
                    "schema_type": "integer",
                    "description": None,
                    "schema_format": "int32",
                    "required": True,
                    "nullable": False,
                    "default": None,
                    "enum_values": None,
                },
                {
                    "name": "message",
                    "schema_type": "string",
                    "description": None,
                    "schema_format": None,
                    "required": True,
                    "nullable": False,
                    "default": None,
                    "enum_values": None,
                },
            ],
            "required_fields": ["code", "message"],
            "validation_rules": [],
        }

    def test_skips_array_schemas(self, petstore_blueprint: APIBlueprint):
        assert {m.name for m in petstore_blueprint.models} == {"Pet", "Error"}


class TestSpecAnalyzerExtractMeta:
    def test_blueprint_metadata(self):
        analyzer = SpecAnalyzer()
        spec = analyzer.parse(str(FIXTURES_DIR / "petstore.yaml"))
        config = IpeConfig(
            spec_path=str(FIXTURES_DIR / "petstore.yaml"),
            module_name="petstore",
        )

        blueprint = analyzer.extract(spec, config)

        assert blueprint.api_name == "Swagger Petstore"
        assert blueprint.spec_version == "1.0.0"
        assert blueprint.spec_description is None
        assert blueprint.base_url == "http://petstore.swagger.io/v1"
        assert blueprint.server_urls == ["http://petstore.swagger.io/v1"]
        assert blueprint.module_name == "petstore"
        assert blueprint.ipe_version == "0.1.0"

    def test_derive_module_name(self, petstore_blueprint: APIBlueprint):
        assert petstore_blueprint.module_name == "swagger_petstore"
