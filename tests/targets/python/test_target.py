from pathlib import Path

import pytest

from ipe.core.analyzer import SpecAnalyzer
from ipe.core.config import IpeConfig
from ipe.models.standard import StandardOperation
from ipe.targets.python.target import PythonTarget

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


@pytest.fixture
def target() -> PythonTarget:
    return PythonTarget()


@pytest.fixture
def petstore_operations() -> list[StandardOperation]:
    analyzer = SpecAnalyzer()
    spec = analyzer.parse(str(FIXTURES_DIR / "petstore.yaml"))
    config = IpeConfig(spec_path=str(FIXTURES_DIR / "petstore.yaml"))
    blueprint = analyzer.extract(spec, config)
    return blueprint.operations


@pytest.fixture
def museum_operations() -> list[StandardOperation]:
    analyzer = SpecAnalyzer()
    spec = analyzer.parse(str(FIXTURES_DIR / "museum.yaml"))
    config = IpeConfig(spec_path=str(FIXTURES_DIR / "museum.yaml"))
    blueprint = analyzer.extract(spec, config)
    return blueprint.operations


class TestPythonTargetProperties:
    def test_name(self, target: PythonTarget):
        assert target.name == "python"

    def test_default_config(self, target: PythonTarget):
        assert target.get_default_config() == {
            "client_library": "httpx",
            "async_support": True,
        }


class TestPythonTargetResolveType:
    def test_petstore_parameter_types(self, target: PythonTarget, petstore_operations: list[StandardOperation]):
        list_pets = petstore_operations[0]
        limit_param = list_pets.parameters[0]

        assert target.resolve_type(limit_param.schema_type, limit_param.schema_format) == "int"

    def test_petstore_property_types(self, target: PythonTarget):
        analyzer = SpecAnalyzer()
        spec = analyzer.parse(str(FIXTURES_DIR / "petstore.yaml"))
        config = IpeConfig(spec_path=str(FIXTURES_DIR / "petstore.yaml"))
        blueprint = analyzer.extract(spec, config)
        pet_model = blueprint.models[0]

        assert target.resolve_type(pet_model.properties[0].schema_type, pet_model.properties[0].schema_format) == "int"
        assert target.resolve_type(pet_model.properties[1].schema_type, pet_model.properties[1].schema_format) == "str"

    def test_unknown_type_returns_any(self, target: PythonTarget):
        assert target.resolve_type("unknown", None) == "Any"

    def test_unknown_format_falls_back_to_base_type(self, target: PythonTarget):
        assert target.resolve_type("string", "unknown-format") == "str"


class TestPythonTargetGroup:
    def test_petstore_flat(self, target: PythonTarget, petstore_operations: list[StandardOperation]):
        resources = target.group(petstore_operations)

        assert set(resources.keys()) == {"pets"}
        assert resources["pets"][0].operation_id == "listPets"
        assert resources["pets"][1].operation_id == "createPets"
        assert resources["pets"][2].operation_id == "showPetById"

    def test_museum_nested(self, target: PythonTarget, museum_operations: list[StandardOperation]):
        resources = target.group(museum_operations)

        assert set(resources.keys()) == {
            "museum-hours",
            "special-events",
            "tickets",
            "tickets.qr",
        }
