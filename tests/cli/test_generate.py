from pathlib import Path

import pytest
from typer.testing import CliRunner

from ipe.cli.main import app

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
EXPECTED_DIR = FIXTURES_DIR / "expected"

runner = CliRunner()


class TestGenerateCommandErrors:
    def test_spec_not_found(self, tmp_path: Path):
        result = runner.invoke(app, ["generate", "/nonexistent.yaml", "--output", str(tmp_path)])

        assert result.exit_code == 1

    def test_unknown_target(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "florada.yaml")

        result = runner.invoke(
            app, ["generate", spec, "--output", str(tmp_path), "--target", "rust"]
        )

        assert result.exit_code == 1

    def test_swagger_20_rejected(self, tmp_path: Path):
        spec = str(FIXTURES_DIR / "swagger2.yaml")

        result = runner.invoke(app, ["generate", spec, "--output", str(tmp_path)])

        assert result.exit_code == 1


@pytest.mark.parametrize(
    ("spec_name", "target", "expected_subdir"),
    [
        ("florada.yaml", "python", "florada/python"),
        ("florada-v3.0.yaml", "python", "florada/python"),
    ],
)
class TestGenerateGoldenFiles:
    def test_all_files_match_expected(
        self, tmp_path: Path, spec_name: str, target: str, expected_subdir: str
    ):
        spec = str(FIXTURES_DIR / spec_name)
        expected_dir = EXPECTED_DIR / expected_subdir

        result = runner.invoke(
            app, ["generate", spec, "--output", str(tmp_path), "--target", target]
        )

        assert result.exit_code == 0

        expected_files = sorted(
            str(f.relative_to(expected_dir)) for f in expected_dir.rglob("*.py")
        )
        generated_files = sorted(
            str(f.relative_to(tmp_path)) for f in tmp_path.rglob("*.py")
        )
        assert generated_files == expected_files

        for relative in expected_files:
            assert (tmp_path / relative).read_text() == (expected_dir / relative).read_text()
