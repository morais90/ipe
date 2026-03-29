from pathlib import Path
from typing import Any

import pytest

from ipe.core.analyzer import SpecAnalyzer
from ipe.core.config import IpeConfig
from ipe.core.renderer import TemplateTreeRenderer
from ipe.targets.python.target import PythonTarget

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
EXPECTED_DIR = FIXTURES_DIR / "expected" / "petstore"


@pytest.fixture
def petstore_output(tmp_path: Path) -> dict[str, str]:
    analyzer = SpecAnalyzer()
    spec = analyzer.parse(str(FIXTURES_DIR / "petstore.yaml"))
    config = IpeConfig(spec_path=str(FIXTURES_DIR / "petstore.yaml"))
    blueprint = analyzer.extract(spec, config)

    target = PythonTarget()
    resources = target.group(blueprint.operations)

    context: dict[str, Any] = {
        **blueprint.model_dump(),
        "resources": {
            target.naming.module_name(name): [
                operation.model_dump() for operation in operations
            ]
            for name, operations in resources.items()
        },
        "models": [
            {**model.model_dump(), "class_name": target.naming.class_name(model.name)}
            for model in blueprint.models
        ],
    }

    for operations in context["resources"].values():
        for operation in operations:
            operation["method_name"] = target.naming.method_name(operation["operation_id"])
            for parameter in operation["parameters"]:
                parameter["python_name"] = target.naming.field_name(parameter["name"])
                parameter["python_type"] = target.resolve_type(
                    parameter["schema_type"], parameter["schema_format"]
                )

    output_dir = tmp_path / "swagger_petstore"
    renderer = TemplateTreeRenderer(target)
    renderer.render(target.template_dir, output_dir, context)

    return {
        str(path.relative_to(output_dir)): path.read_text()
        for path in sorted(output_dir.rglob("*.py"))
    }


@pytest.mark.parametrize(
    "filename",
    [
        "__init__.py",
        "client.py",
        "exceptions.py",
        "models/__init__.py",
        "models/pet.py",
        "models/error.py",
        "resources/__init__.py",
        "resources/pets.py",
    ],
)
class TestGeneratedOutput:
    def test_file_matches_expected(self, petstore_output: dict[str, str], filename: str):
        expected = (EXPECTED_DIR / filename).read_text()

        assert petstore_output[filename] == expected
