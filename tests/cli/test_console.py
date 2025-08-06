"""Tests for console utilities."""

from io import StringIO

from rich.console import Console

from ipe.cli.console import IpeConsole, console


class TestIpeConsole:
    def test_initialization(self):
        test_console = IpeConsole()
        assert isinstance(test_console.console, Console)

    def test_success_message_output(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.success("Test successful")

        result = output.getvalue()
        assert "✅ Test successful" in result

    def test_error_message_output(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.error("Test error")

        result = output.getvalue()
        assert "❌ Test error" in result

    def test_info_message_output(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.info("Test info")

        result = output.getvalue()
        assert "📋 Test info" in result

    def test_warning_message_output(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.warning("Test warning")

        result = output.getvalue()
        assert "⚠️  Test warning" in result

    def test_print_header_output(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.print_header()

        result = output.getvalue()
        assert "🌳 Ipê - OpenAPI Code Generator" in result

    def test_validation_error_without_suggestion(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.print_validation_error("Missing field")

        result = output.getvalue()
        assert "❌ OpenAPI specification is invalid" in result
        assert "📍 Missing field" in result

    def test_validation_error_with_suggestion(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.print_validation_error("Missing field", "Add the field")

        result = output.getvalue()
        assert "📍 Missing field" in result
        assert "💡 Suggestion:" in result
        assert "Add the field" in result

    def test_generation_summary_output(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.print_generation_summary("./output", 5, 1.2)

        result = output.getvalue()
        assert "✅ Generated successfully!" in result
        assert "📁 Output: ./output" in result
        assert "📊 Files: 5 created" in result
        assert "⏱️  Time: 1.2s" in result

    def test_next_steps_output(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.print_next_steps("my_client", "MyClient")

        result = output.getvalue()
        assert "from my_client import MyClient" in result
        assert "client = MyClient(" in result

    def test_url_fetch_output(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.print_url_fetch("https://example.com/api.yaml", 24.5)

        result = output.getvalue()
        assert "📡 GET https://example.com/api.yaml" in result
        assert "✅ Downloaded successfully (24.5 KB)" in result

    def test_progress_lifecycle(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.start_progress("Testing...")
        test_console.stop_progress()

        result = output.getvalue()
        assert "Testing..." in result

    def test_print_passthrough(self):
        output = StringIO()
        test_console = IpeConsole()
        test_console.console = Console(file=output, width=80)

        test_console.print("Custom message", style="bold")

        result = output.getvalue()
        assert "Custom message" in result

    def test_global_console_instance(self):
        assert isinstance(console, IpeConsole)
