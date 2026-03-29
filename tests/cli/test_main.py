from typer.testing import CliRunner

from ipe.cli.main import app


class TestMainCLI:
    def setup_method(self):
        self.runner = CliRunner()

    def test_version_command(self):
        result = self.runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "🌳 Ipê - OpenAPI Code Generator" in result.stdout
        assert "Version: 0.1.0" in result.stdout
        assert "Python compatibility: 3.12+" in result.stdout

    def test_version_flag(self):
        result = self.runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "🌳 Ipê - OpenAPI Code Generator" in result.stdout
        assert "Version: 0.1.0" in result.stdout

    def test_version_flag_short(self):
        result = self.runner.invoke(app, ["-V"])

        assert result.exit_code == 0
        assert "🌳 Ipê - OpenAPI Code Generator" in result.stdout
        assert "Version: 0.1.0" in result.stdout

    def test_help_flag(self):
        result = self.runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "🌳 Ipê - A next-generation OpenAPI code generator" in result.stdout

    def test_help_flag_short(self):
        result = self.runner.invoke(app, ["-h"])

        assert result.exit_code == 0
        assert "🌳 Ipê - A next-generation OpenAPI code generator" in result.stdout

    def test_no_args_shows_help(self):
        result = self.runner.invoke(app)

        assert result.exit_code == 0
        assert "🌳 Ipê - A next-generation OpenAPI code generator" in result.stdout
