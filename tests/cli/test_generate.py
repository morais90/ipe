from pathlib import Path

from typer.testing import CliRunner

from ipe.cli.main import app

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

runner = CliRunner()


class TestGenerateCommandSuccess:
    def test_exit_code_zero(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "petstore.yaml")

        result = runner.invoke(app, ["generate", spec, "--output", str(tmp_path)])

        assert result.exit_code == 0

    def test_creates_files_in_output_dir(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "petstore.yaml")

        runner.invoke(app, ["generate", spec, "--output", str(tmp_path)])

        generated = sorted(str(f.relative_to(tmp_path)) for f in tmp_path.rglob("*.py"))
        assert generated == [
            "__init__.py",
            "client.py",
            "exceptions.py",
            "models/__init__.py",
            "models/error.py",
            "models/pet.py",
            "resources/__init__.py",
            "resources/pets.py",
        ]

    def test_works_with_different_specs(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "museum.yaml")

        result = runner.invoke(app, ["generate", spec, "--output", str(tmp_path)])

        assert result.exit_code == 0
        assert sorted(str(f.relative_to(tmp_path)) for f in tmp_path.rglob("*.py")) != []


class TestGenerateCommandOptions:
    def test_custom_module_name(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "petstore.yaml")

        result = runner.invoke(
            app, ["generate", spec, "--output", str(tmp_path), "--module-name", "my_api"]
        )

        assert result.exit_code == 0

    def test_custom_target(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "petstore.yaml")

        result = runner.invoke(
            app, ["generate", spec, "--output", str(tmp_path), "--target", "python"]
        )

        assert result.exit_code == 0


class TestGenerateCommandErrors:
    def test_spec_not_found(self, tmp_path: Path):
        result = runner.invoke(app, ["generate", "/nonexistent.yaml", "--output", str(tmp_path)])

        assert result.exit_code == 1

    def test_unknown_target(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "petstore.yaml")

        result = runner.invoke(
            app, ["generate", spec, "--output", str(tmp_path), "--target", "rust"]
        )

        assert result.exit_code == 1

    def test_swagger_20_rejected(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "swagger2.yaml")

        result = runner.invoke(app, ["generate", spec, "--output", str(tmp_path)])

        assert result.exit_code == 1
