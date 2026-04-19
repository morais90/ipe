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
def florada_spec() -> dict[str, Any]:
    return load_fixture("florada.yaml")


@pytest.fixture
def florada_v30_spec() -> dict[str, Any]:
    return load_fixture("florada-v3.0.yaml")


@pytest.fixture
def swagger2_spec() -> dict[str, Any]:
    return load_fixture("swagger2.yaml")


@pytest.fixture
def invalid_spec() -> dict[str, Any]:
    return load_fixture("invalid.yaml")


@pytest.fixture
def circular_ref_spec() -> dict[str, Any]:
    return load_fixture("circular_ref.yaml")
