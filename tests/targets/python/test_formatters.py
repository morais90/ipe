from pathlib import Path
from unittest import mock

import pytest

from ipe.core.exceptions import FormatterError
from ipe.targets.python.formatters import RuffFormatter, _options_to_args


class TestOptionsToArgs:
    def test_empty(self):
        assert _options_to_args({}) == []

    def test_string_value(self):
        assert _options_to_args({"line-length": "100"}) == ["--line-length", "100"]

    def test_numeric_value(self):
        assert _options_to_args({"line-length": 100}) == ["--line-length", "100"]

    def test_true_bool_emits_flag_only(self):
        assert _options_to_args({"preview": True}) == ["--preview"]

    def test_false_bool_omits_flag(self):
        assert _options_to_args({"preview": False}) == []

    def test_list_joins_with_commas(self):
        assert _options_to_args({"select": ["I", "UP"]}) == ["--select", "I,UP"]


class TestRuffFormatterVerify:
    def test_verify_passes_when_ruff_present(self):
        formatter = RuffFormatter({})

        with mock.patch("ipe.targets.python.formatters.subprocess.run") as run:
            run.return_value = mock.Mock(returncode=0, stdout="", stderr="")
            formatter.verify()

        run.assert_called_once()

    def test_verify_raises_when_ruff_missing(self):
        formatter = RuffFormatter({})

        with mock.patch("ipe.targets.python.formatters.subprocess.run") as run:
            run.side_effect = FileNotFoundError("ruff")

            with pytest.raises(FormatterError, match="ruff not found"):
                formatter.verify()


class TestRuffFormatterFormat:
    def test_runs_format_and_check(self, tmp_path: Path):
        formatter = RuffFormatter({"line-length": 100})

        with mock.patch("ipe.targets.python.formatters.subprocess.run") as run:
            run.return_value = mock.Mock(returncode=0, stdout="", stderr="")
            formatter.format(tmp_path)

        commands = [call.args[0] for call in run.call_args_list]
        assert commands == [
            ["ruff", "format", "--line-length", "100", str(tmp_path)],
            [
                "ruff",
                "check",
                "--fix",
                "--exit-zero",
                "--line-length",
                "100",
                str(tmp_path),
            ],
        ]

    def test_propagates_subprocess_stderr(self, tmp_path: Path):
        formatter = RuffFormatter({})

        with mock.patch("ipe.targets.python.formatters.subprocess.run") as run:
            run.return_value = mock.Mock(returncode=2, stdout="", stderr="bad option")

            with pytest.raises(FormatterError) as exc_info:
                formatter.format(tmp_path)

        assert exc_info.value.suggestion == "bad option"
