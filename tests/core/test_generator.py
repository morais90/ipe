from pathlib import Path

import pytest

from ipe.core.config import IpeConfig
from ipe.core.generator import CodeGenerator

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
EXPECTED_DIR = FIXTURES_DIR / "expected" / "petstore"


@pytest.fixture
def petstore_output(tmp_path: Path) -> dict[str, str]:
    config = IpeConfig(
        spec_path=str(FIXTURES_DIR / "petstore.yaml"),
        output_dir=tmp_path / "swagger_petstore",
    )

    CodeGenerator().run(config)

    output_dir = config.output_dir
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
