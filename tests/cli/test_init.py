import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ipe.cli.main import app

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

runner = CliRunner()


class TestInit:
    def test_creates_config_from_validated_spec(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        spec = str(FIXTURES_DIR / "florada.yaml")

        result = runner.invoke(app, ["init"], input=f"{spec}\n\n\n\n")

        assert result.exit_code == 0
        assert "Validated Florada Payments" in result.output

        config = json.loads((tmp_path / "ipe.json").read_text())
        assert config == {
            "target": "python",
            "output_dir": "florada_payments",
            "module_name": "florada_payments",
            "spec_path": spec,
            "targets": {},
            "auto_format": True,
        }

    def test_accepts_overrides_for_module_and_output(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        spec = str(FIXTURES_DIR / "florada.yaml")

        result = runner.invoke(app, ["init"], input=f"{spec}\nmy_client\n./clients\n\n")

        assert result.exit_code == 0
        config = json.loads((tmp_path / "ipe.json").read_text())
        assert config["module_name"] == "my_client"
        assert config["output_dir"] == "clients"

    def test_aborts_when_not_overwriting_existing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "ipe.json").write_text('{"keep": true}')

        result = runner.invoke(app, ["init"], input="n\n")

        assert result.exit_code == 0
        assert json.loads((tmp_path / "ipe.json").read_text()) == {"keep": True}

    def test_saves_anyway_when_spec_is_invalid(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)

        result = runner.invoke(
            app, ["init"], input="/nonexistent/spec.yaml\nmy_api\n\n\ny\n"
        )

        assert result.exit_code == 0
        config = json.loads((tmp_path / "ipe.json").read_text())
        assert config["spec_path"] == "/nonexistent/spec.yaml"
        assert config["module_name"] == "my_api"
