import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from ipe.cli.main import app

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

runner = CliRunner()


def expected_config(spec: str, module: str, output: str) -> dict[str, object]:
    return {
        "target": "python",
        "output_dir": output,
        "module_name": module,
        "spec_path": spec,
        "targets": {},
        "auto_format": True,
    }


class TestInit:
    def test_creates_config_from_validated_spec(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        spec = str(FIXTURES_DIR / "florada.yaml")

        result = runner.invoke(app, ["init"], input=f"{spec}\n\n\n\n")

        assert result.exit_code == 0
        assert "Validated Florada Payments" in result.output
        assert json.loads((tmp_path / "ipe.json").read_text()) == expected_config(
            spec, "florada_payments", "florada_payments"
        )

    def test_accepts_overrides_for_module_and_output(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        spec = str(FIXTURES_DIR / "florada.yaml")

        result = runner.invoke(app, ["init"], input=f"{spec}\nmy_client\n./clients\n\n")

        assert result.exit_code == 0
        assert json.loads((tmp_path / "ipe.json").read_text()) == expected_config(
            spec, "my_client", "clients"
        )

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
        assert json.loads((tmp_path / "ipe.json").read_text()) == expected_config(
            "/nonexistent/spec.yaml", "my_api", "my_api"
        )

    def test_suggests_a_valid_module_for_an_awkward_title(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        spec = tmp_path / "spec.yaml"
        spec.write_text(
            'openapi: "3.1.0"\ninfo:\n  title: 3D Service\n  version: "1"\npaths: {}\n'
        )

        result = runner.invoke(app, ["init"], input=f"{spec}\n\n\n\n")

        assert result.exit_code == 0
        assert json.loads((tmp_path / "ipe.json").read_text()) == expected_config(
            str(spec), "api_client", "api_client"
        )

    def test_reprompts_on_invalid_module_name(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.chdir(tmp_path)
        spec = str(FIXTURES_DIR / "florada.yaml")

        result = runner.invoke(
            app, ["init"], input=f"{spec}\nmy-client\nmy_client\n\n\n"
        )

        assert result.exit_code == 0
        assert "not a valid module name" in result.output
        assert json.loads((tmp_path / "ipe.json").read_text()) == expected_config(
            spec, "my_client", "my_client"
        )
