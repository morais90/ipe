"""Tests for configuration management."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from ipe.core.config import IpeConfig, create_default_config, load_config, save_config


class TestIpeConfig:
    def test_minimal_configuration(self):
        config = IpeConfig(module_name="test_client", output_dir="./output")
        assert config.module_name == "test_client"
        assert config.generator == "python"
        assert config.output_dir == "output"
        assert config.spec_path is None
        assert config.base_url is None

    def test_full_configuration(self):
        config = IpeConfig(
            module_name="api_client",
            generator="typescript",
            output_dir="/tmp/generated",
            spec_path="./api.yaml",
            base_url="https://api.example.com",
        )
        assert config.module_name == "api_client"
        assert config.generator == "typescript"
        assert config.output_dir == "/tmp/generated"
        assert config.spec_path == "api.yaml"
        assert config.base_url == "https://api.example.com"

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            IpeConfig(module_name="test")

        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("output_dir",)
        assert errors[0]["type"] == "missing"

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
    def test_invalid_module_name_characters(self, invalid_name):
        with pytest.raises(ValidationError) as exc_info:
            IpeConfig(module_name=invalid_name, output_dir="./out")

        error = exc_info.value.errors()[0]
        assert "invalid characters" in error["msg"] or "keyword" in error["msg"]

    @pytest.mark.parametrize(
        "valid_name",
        [
            "valid_name",
            "_private",
            "__dunder__",
            "CamelCase",
            "name123",
            "name_with_123_numbers",
        ],
    )
    def test_valid_module_names(self, valid_name):
        config = IpeConfig(module_name=valid_name, output_dir="./out")
        assert config.module_name == valid_name

    def test_path_normalization(self):
        config = IpeConfig(
            module_name="test",
            output_dir="./output/../generated",
            spec_path="./specs/../api.yaml",
        )
        assert config.output_dir == "output/../generated"
        assert config.spec_path == "specs/../api.yaml"

    def test_json_schema_generation(self):
        schema = IpeConfig.model_json_schema()
        assert schema["title"] == "IpeConfig"
        assert "module_name" in schema["properties"]
        assert "generator" in schema["properties"]
        assert "output_dir" in schema["properties"]
        assert schema["required"] == ["module_name", "output_dir"]


class TestConfigLoading:
    def test_load_from_valid_file(self, tmp_path):
        config_data = {
            "module_name": "test_api",
            "output_dir": "./generated",
            "generator": "python",
        }
        config_path = tmp_path / "ipe.json"
        config_path.write_text(json.dumps(config_data))

        config = load_config(config_path)
        assert config.module_name == "test_api"
        assert config.output_dir == "generated"
        assert config.generator == "python"

    def test_file_not_found_error(self):
        with pytest.raises(FileNotFoundError) as exc_info:
            load_config(Path("nonexistent.json"))

        assert "Configuration file not found" in str(exc_info.value)
        assert "ipe init" in str(exc_info.value)

    def test_invalid_json_error(self, tmp_path):
        config_path = tmp_path / "ipe.json"
        config_path.write_text("{invalid json}")

        with pytest.raises(ValueError, match="Invalid JSON") as exc_info:
            load_config(config_path)

        assert "Invalid JSON" in str(exc_info.value)
        assert "line" in str(exc_info.value)
        assert "column" in str(exc_info.value)

    def test_validation_error_on_load(self, tmp_path):
        config_data = {"module_name": "123-invalid", "output_dir": "./out"}
        config_path = tmp_path / "ipe.json"
        config_path.write_text(json.dumps(config_data))

        with pytest.raises(ValidationError) as exc_info:
            load_config(config_path)

        assert "invalid characters" in str(exc_info.value)


class TestConfigCreation:
    def test_create_with_defaults(self):
        config = create_default_config("my_api")
        assert config.module_name == "my_api"
        assert config.output_dir == "generated"
        assert config.generator == "python"
        assert config.spec_path is None

    def test_create_with_custom_options(self):
        config = create_default_config(
            "custom_api", output_dir="/tmp/out", spec_path="./spec.yaml"
        )
        assert config.module_name == "custom_api"
        assert config.output_dir == "/tmp/out"
        assert config.spec_path == "spec.yaml"


class TestConfigSaving:
    def test_save_minimal_config(self, tmp_path):
        config = create_default_config("test_save")
        config_path = tmp_path / "ipe.json"

        save_config(config, config_path)

        assert config_path.exists()
        saved_data = json.loads(config_path.read_text())
        assert saved_data["module_name"] == "test_save"
        assert saved_data["output_dir"] == "generated"
        assert saved_data["generator"] == "python"
        assert "spec_path" not in saved_data
        assert "base_url" not in saved_data

    def test_save_full_config(self, tmp_path):
        config = IpeConfig(
            module_name="full_api",
            generator="typescript",
            output_dir="/output",
            spec_path="./api.yaml",
            base_url="https://api.example.com",
        )
        config_path = tmp_path / "ipe.json"

        save_config(config, config_path)

        saved_data = json.loads(config_path.read_text())
        assert saved_data["module_name"] == "full_api"
        assert saved_data["generator"] == "typescript"
        assert saved_data["output_dir"] == "/output"
        assert saved_data["spec_path"] == "api.yaml"
        assert saved_data["base_url"] == "https://api.example.com"
