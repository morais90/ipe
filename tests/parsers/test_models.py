from typing import Any

import pytest
from pydantic import ValidationError

from ipe.parsers.models import Info, OpenAPISpec


class TestOpenAPISpecParsing:
    def test_petstore_30(self, petstore_spec: dict[str, Any]):
        spec = OpenAPISpec.model_validate(petstore_spec)

        assert spec.openapi == "3.0.0"
        assert spec.info.model_dump(by_alias=True, exclude_unset=True) == {
            "title": "Swagger Petstore",
            "version": "1.0.0",
            "license": {"name": "MIT"},
        }
        assert spec.servers is not None
        assert [s.model_dump(by_alias=True, exclude_unset=True) for s in spec.servers] == [
            {"url": "http://petstore.swagger.io/v1"},
        ]
        assert spec.paths is not None
        assert set(spec.paths.keys()) == {"/pets", "/pets/{petId}"}

    def test_petstore_operations(self, petstore_spec: dict[str, Any]):
        spec = OpenAPISpec.model_validate(petstore_spec)

        assert spec.paths is not None
        pets = spec.paths["/pets"]
        assert pets.get is not None
        assert pets.get.model_dump(by_alias=True, exclude_unset=True) == {
            "summary": "List all pets",
            "operationId": "listPets",
            "tags": ["pets"],
            "parameters": [
                {
                    "name": "limit",
                    "in": "query",
                    "description": "How many items to return at one time (max 100)",
                    "required": False,
                    "schema": {"type": "integer", "maximum": 100.0, "format": "int32"},
                },
            ],
            "responses": {
                "200": {
                    "description": "A paged array of pets",
                    "headers": {
                        "x-next": {
                            "description": "A link to the next page of responses",
                            "schema": {"type": "string"},
                        },
                    },
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Pets"},
                        },
                    },
                },
                "default": {
                    "description": "unexpected error",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"},
                        },
                    },
                },
            },
        }

    def test_petstore_components(self, petstore_spec: dict[str, Any]):
        spec = OpenAPISpec.model_validate(petstore_spec)

        assert spec.components is not None
        assert spec.components.schemas is not None
        assert spec.components.model_dump(by_alias=True, exclude_unset=True) == {
            "schemas": {
                "Pet": {
                    "type": "object",
                    "required": ["id", "name"],
                    "properties": {
                        "id": {"type": "integer", "format": "int64"},
                        "name": {"type": "string"},
                        "tag": {"type": "string"},
                    },
                },
                "Pets": {
                    "type": "array",
                    "maxItems": 100,
                    "items": {"$ref": "#/components/schemas/Pet"},
                },
                "Error": {
                    "type": "object",
                    "required": ["code", "message"],
                    "properties": {
                        "code": {"type": "integer", "format": "int32"},
                        "message": {"type": "string"},
                    },
                },
            },
        }

    def test_museum_31(self, museum_spec: dict[str, Any]):
        spec = OpenAPISpec.model_validate(museum_spec)

        assert spec.openapi == "3.1.0"
        assert spec.info.title == "Redocly Museum API"
        assert spec.info.version == "1.2.1"
        assert spec.info.terms_of_service == "https://redocly.com/subscription-agreement/"
        assert spec.info.contact is not None
        assert spec.info.contact.model_dump(exclude_unset=True) == {
            "email": "team@redocly.com",
            "url": "https://redocly.com/docs/cli/",
        }
        assert spec.info.license is not None
        assert spec.info.license.model_dump(exclude_unset=True) == {
            "name": "MIT",
            "url": "https://opensource.org/license/mit/",
        }

    def test_museum_paths_and_security(self, museum_spec: dict[str, Any]):
        spec = OpenAPISpec.model_validate(museum_spec)

        assert spec.paths is not None
        assert "/museum-hours" in spec.paths
        assert "/special-events" in spec.paths
        hours = spec.paths["/museum-hours"]
        assert hours.get is not None
        assert hours.get.operation_id == "getMuseumHours"
        assert hours.get.tags == ["Operations"]
        assert spec.components is not None
        assert spec.components.security_schemes is not None
        assert "MuseumPlaceholderAuth" in spec.components.security_schemes

    def test_petstore_expanded_parses(self, petstore_expanded_spec: dict[str, Any]):
        spec = OpenAPISpec.model_validate(petstore_expanded_spec)

        assert spec.openapi == "3.0.0"
        assert spec.paths is not None
        assert spec.components is not None
        assert spec.components.schemas is not None

    def test_api_with_examples_parses(self, api_with_examples_spec: dict[str, Any]):
        spec = OpenAPISpec.model_validate(api_with_examples_spec)

        assert spec.openapi == "3.0.0"
        assert spec.paths is not None


class TestOpenAPISpecMinimal:
    def test_minimal_valid_spec(self):
        raw = {
            "openapi": "3.0.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        spec = OpenAPISpec.model_validate(raw)

        assert spec.openapi == "3.0.0"
        assert spec.info.title == "Test"
        assert spec.info.version == "1.0.0"
        assert spec.paths == {}
        assert spec.components is None
        assert spec.servers is None
        assert spec.tags is None

    def test_missing_openapi_raises(self):
        raw = {
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
        }

        with pytest.raises(ValidationError):
            OpenAPISpec.model_validate(raw)

    def test_missing_info_raises(self):
        raw = {
            "openapi": "3.0.0",
            "paths": {},
        }

        with pytest.raises(ValidationError):
            OpenAPISpec.model_validate(raw)


class TestInfoModel:
    def test_full_info(self):
        raw = {
            "title": "My API",
            "version": "2.0.0",
            "summary": "A summary",
            "description": "A description",
            "termsOfService": "https://example.com/tos",
            "contact": {"name": "Dev", "email": "dev@example.com"},
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        }

        info = Info.model_validate(raw)

        assert info.model_dump(by_alias=True, exclude_unset=True) == {
            "title": "My API",
            "version": "2.0.0",
            "summary": "A summary",
            "description": "A description",
            "termsOfService": "https://example.com/tos",
            "contact": {"name": "Dev", "email": "dev@example.com"},
            "license": {"name": "MIT", "url": "https://opensource.org/licenses/MIT"},
        }

    def test_minimal_info(self):
        raw = {"title": "API", "version": "1.0.0"}

        info = Info.model_validate(raw)

        assert info.model_dump(by_alias=True, exclude_unset=True) == {
            "title": "API",
            "version": "1.0.0",
        }
