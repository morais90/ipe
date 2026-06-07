import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from ipe.core.config import IpeConfig, create_default_config, load_config, save_config


@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    data = {"target": "python", "module_name": "test_api", "output_dir": "./generated"}
    path = tmp_path / "ipe.json"
    path.write_text(json.dumps(data))
    return path


@pytest.fixture
def full_config_data() -> dict[str, Any]:
    return {
        "module_name": "api_client",
        "target": "typescript",
        "output_dir": "/tmp/generated",
        "spec_path": "./api.yaml",
        "targets": {"python": {"async": True}},
        "template_dir": "/custom/templates",
    }


class TestIpeConfig:
    def test_defaults(self):
        config = IpeConfig()
        assert config.model_dump() == {
            "target": "python",
            "output_dir": Path("./output"),
            "module_name": None,
            "spec_path": "",
            "targets": {},
            "template_dir": None,
            "formatter": None,
            "auto_format": True,
        }

    def test_full_configuration(self, full_config_data: dict[str, Any]):
        config = IpeConfig(**full_config_data)
        assert config.module_name == "api_client"
        assert config.target == "typescript"
        assert config.output_dir == Path("/tmp/generated")
        assert config.spec_path == "./api.yaml"
        assert config.targets == {"python": {"async": True}}
        assert config.template_dir == Path("/custom/templates")

    @pytest.mark.parametrize(
        "invalid_name",
        [
            "123invalid",
            "test-client",
            "test.client",
            "test client",
            "test@client",
            "",
            "class",
        ],
    )
    def test_invalid_module_name(self, invalid_name: str):
        with pytest.raises(ValidationError) as exc_info:
            IpeConfig(module_name=invalid_name)

        error = exc_info.value.errors()[0]
        assert "invalid characters" in error["msg"] or "keyword" in error["msg"]

    @pytest.mark.parametrize(
        "valid_name",
        ["valid_name", "_private", "__dunder__", "CamelCase", "name123"],
    )
    def test_valid_module_names(self, valid_name: str):
        config = IpeConfig(module_name=valid_name)
        assert config.module_name == valid_name

    def test_module_name_none_is_valid(self):
        config = IpeConfig()
        assert config.module_name is None

    def test_output_dir_coerced_to_path(self):
        config = IpeConfig(output_dir="./custom/output")
        assert isinstance(config.output_dir, Path)
        assert config.output_dir == Path("./custom/output")

    def test_template_dir_coerced_to_path(self):
        config = IpeConfig(template_dir="./my/templates")
        assert isinstance(config.template_dir, Path)
        assert config.template_dir == Path("./my/templates")

    def test_template_dir_none_by_default(self):
        config = IpeConfig()
        assert config.template_dir is None

    def test_json_schema_has_all_fields(self):
        schema = IpeConfig.model_json_schema()
        assert schema["title"] == "IpeConfig"
        assert set(schema["properties"].keys()) == {
            "target",
            "output_dir",
            "module_name",
            "spec_path",
            "targets",
            "template_dir",
            "formatter",
            "auto_format",
        }


class TestConfigLoading:
    def test_load_valid_file(self, config_file: Path):
        config = load_config(config_file)
        assert config.module_name == "test_api"
        assert config.output_dir == Path("./generated")
        assert config.target == "python"

    def test_load_with_targets(self, tmp_path: Path):
        data = {"target": "python", "targets": {"python": {"async": True}}}
        config_path = tmp_path / "ipe.json"
        config_path.write_text(json.dumps(data))

        config = load_config(config_path)
        assert config.targets == {"python": {"async": True}}

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            load_config(Path("nonexistent.json"))

    def test_invalid_json(self, tmp_path: Path):
        config_path = tmp_path / "ipe.json"
        config_path.write_text("{invalid json}")

        with pytest.raises(ValueError, match="Invalid JSON"):
            load_config(config_path)

    def test_invalid_module_name_on_load(self, tmp_path: Path):
        data = {"module_name": "123-invalid"}
        config_path = tmp_path / "ipe.json"
        config_path.write_text(json.dumps(data))

        with pytest.raises(ValidationError, match="invalid characters"):
            load_config(config_path)


class TestConfigCreation:
    def test_create_with_defaults(self):
        config = create_default_config()
        assert config.target == "python"
        assert config.output_dir == Path("./output")
        assert config.module_name is None
        assert config.spec_path == ""

    def test_create_with_all_options(self):
        config = create_default_config(
            spec_path="./spec.yaml",
            output_dir="/tmp/out",
            module_name="custom_api",
        )
        assert config.module_name == "custom_api"
        assert config.output_dir == Path("/tmp/out")
        assert config.spec_path == "./spec.yaml"


class TestConfigSaving:
    def test_save_excludes_none_fields(self, tmp_path: Path):
        config = create_default_config()
        config_path = tmp_path / "ipe.json"

        save_config(config, config_path)

        saved_data = json.loads(config_path.read_text())
        assert saved_data == {
            "target": "python",
            "output_dir": "output",
            "spec_path": "",
            "targets": {},
            "auto_format": True,
        }

    def test_save_full_config(self, tmp_path: Path):
        config = IpeConfig(
            module_name="full_api",
            target="typescript",
            output_dir="/output",
            spec_path="./api.yaml",
            targets={"typescript": {"runtime": "fetch"}},
            template_dir="/custom",
        )
        config_path = tmp_path / "ipe.json"

        save_config(config, config_path)

        saved_data = json.loads(config_path.read_text())
        assert saved_data == {
            "module_name": "full_api",
            "target": "typescript",
            "output_dir": "/output",
            "spec_path": "./api.yaml",
            "targets": {"typescript": {"runtime": "fetch"}},
            "template_dir": "/custom",
            "auto_format": True,
        }

    def test_roundtrip(self, tmp_path: Path):
        original = IpeConfig(
            module_name="roundtrip",
            target="python",
            spec_path="./api.yaml",
            output_dir="/out",
        )
        config_path = tmp_path / "ipe.json"

        save_config(original, config_path)
        loaded = load_config(config_path)

        assert loaded.module_name == original.module_name
        assert loaded.target == original.target
        assert loaded.spec_path == original.spec_path
        assert loaded.output_dir == original.output_dir
