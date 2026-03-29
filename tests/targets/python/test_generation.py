from pathlib import Path

import pytest

from ipe.core.config import IpeConfig
from ipe.core.generator import CodeGenerator

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"
EXPECTED_DIR = FIXTURES_DIR / "expected" / "petstore"


@pytest.fixture
def petstore_output(tmp_path: Path) -> dict[str, str]:
    config = IpeConfig(
        spec_path=str(FIXTURES_DIR / "petstore.yaml"),
        output_dir=tmp_path,
    )

    CodeGenerator().run(config)

    return {
        str(path.relative_to(tmp_path)): path.read_text()
        for path in sorted(tmp_path.rglob("*.py"))
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
class TestPythonPetstoreGeneration:
    def test_file_matches_expected(self, petstore_output: dict[str, str], filename: str):
        expected = (EXPECTED_DIR / filename).read_text()

        assert petstore_output[filename] == expected


class TestPythonMuseumGeneration:
    def test_generates_nested_resources(self, tmp_path: Path):
        config = IpeConfig(
            spec_path=str(FIXTURES_DIR / "museum.yaml"),
            output_dir=tmp_path,
        )

        CodeGenerator().run(config)

        generated = sorted(str(f.relative_to(tmp_path)) for f in tmp_path.rglob("*.py"))
        assert generated == [
            "__init__.py",
            "client.py",
            "exceptions.py",
            "models/__init__.py",
            "models/buy_museum_tickets.py",
            "models/date.py",
            "models/email.py",
            "models/error.py",
            "models/event_description.py",
            "models/event_id.py",
            "models/event_location.py",
            "models/event_name.py",
            "models/event_price.py",
            "models/museum_daily_hours.py",
            "models/museum_tickets_confirmation.py",
            "models/special_event.py",
            "models/special_event_fields.py",
            "models/ticket.py",
            "models/ticket_code_image.py",
            "models/ticket_confirmation.py",
            "models/ticket_id.py",
            "models/ticket_message.py",
            "models/ticket_type.py",
            "resources/__init__.py",
            "resources/museum_hours.py",
            "resources/special_events.py",
            "resources/tickets.py",
            "resources/tickets_qr.py",
        ]
