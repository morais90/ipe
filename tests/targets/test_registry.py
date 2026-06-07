from pathlib import Path
from typing import Any

import pytest

from ipe.core.exceptions import ConfigurationError
from ipe.models.blueprint import APIBlueprint, OutputFile
from ipe.targets.registry import TargetRegistry


class FakeNaming:
    def class_name(self, raw: str) -> str:
        return raw

    def method_name(self, raw: str) -> str:
        return raw

    def field_name(self, raw: str) -> str:
        return raw

    def module_name(self, raw: str) -> str:
        return raw


class FakeTarget:
    @property
    def name(self) -> str:
        return "fake"

    @property
    def naming(self) -> FakeNaming:
        return FakeNaming()

    def transform(self, blueprint: APIBlueprint) -> dict[str, Any]:
        return {}

    def plan(self, data: dict[str, Any]) -> list[OutputFile]:
        return []

    def get_template_dir(self) -> Path:
        return Path()

    def validate_config(self, config: dict[str, Any]) -> bool:
        return True

    def get_default_config(self) -> dict[str, Any]:
        return {}


@pytest.fixture
def registry() -> TargetRegistry:
    return TargetRegistry()


class TestTargetRegistry:
    def test_builtin_python_registered(self, registry: TargetRegistry):
        assert "python" in registry.list_languages()

    def test_register_and_get(self, registry: TargetRegistry):
        target = FakeTarget()

        registry.register(target)

        assert registry.get("fake") is target

    def test_list_languages_sorted(self, registry: TargetRegistry):
        registry.register(FakeTarget())

        assert registry.list_languages() == ["fake", "python"]

    def test_get_unknown_language(self, registry: TargetRegistry):
        with pytest.raises(ConfigurationError, match="Unknown target language: 'rust'"):
            registry.get("rust")

    def test_get_unknown_shows_available(self, registry: TargetRegistry):
        with pytest.raises(
            ConfigurationError, match="Unknown target language"
        ) as exc_info:
            registry.get("rust")

        assert exc_info.value.suggestion == "Available targets: python"

    def test_register_overwrites(self, registry: TargetRegistry):
        target1 = FakeTarget()
        target2 = FakeTarget()

        registry.register(target1)
        registry.register(target2)

        assert registry.get("fake") is target2
