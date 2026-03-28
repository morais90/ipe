from pathlib import Path
from typing import Any

import pytest
import yaml

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any]:
    path = FIXTURES_DIR / name
    return yaml.safe_load(path.read_text())  # type: ignore[no-any-return]


def load_fixture_text(name: str) -> str:
    path = FIXTURES_DIR / name
    return path.read_text()


@pytest.fixture
def petstore_spec() -> dict[str, Any]:
    return load_fixture("petstore.yaml")


@pytest.fixture
def petstore_expanded_spec() -> dict[str, Any]:
    return load_fixture("petstore-expanded.yaml")


@pytest.fixture
def api_with_examples_spec() -> dict[str, Any]:
    return load_fixture("api-with-examples.yaml")


@pytest.fixture
def museum_spec() -> dict[str, Any]:
    return load_fixture("museum.yaml")


@pytest.fixture
def petstore_swagger_spec() -> dict[str, Any]:
    return load_fixture("petstore-swagger.yaml")


@pytest.fixture
def swagger2_spec() -> dict[str, Any]:
    return load_fixture("swagger2.yaml")


@pytest.fixture
def invalid_spec() -> dict[str, Any]:
    return load_fixture("invalid.yaml")


@pytest.fixture
def circular_ref_spec() -> dict[str, Any]:
    return load_fixture("circular_ref.yaml")


@pytest.fixture
def notion_spec() -> dict[str, Any]:
    return load_fixture("notion.yaml")


@pytest.fixture
def github_spec() -> dict[str, Any]:
    return load_fixture("github.yaml")


@pytest.fixture
def stripe_spec() -> dict[str, Any]:
    return load_fixture("stripe.yaml")
