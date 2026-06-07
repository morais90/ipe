import subprocess
from pathlib import Path
from typing import Any

from ipe.core.exceptions import FormatterError


def _options_to_args(options: dict[str, Any]) -> list[str]:
    args: list[str] = []

    for key, value in options.items():
        flag = f"--{key}"

        if isinstance(value, bool):
            if value:
                args.append(flag)
            continue

        if isinstance(value, list):
            args.extend([flag, ",".join(str(v) for v in value)])
            continue

        args.extend([flag, str(value)])

    return args


def _run(cmd: list[str]) -> None:
    try:
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise FormatterError(
            f"{cmd[0]} not found in PATH",
            f"Install {cmd[0]} and ensure it is on your PATH",
        ) from exc

    if result.returncode != 0:
        raise FormatterError(
            f"{' '.join(cmd[:2])} failed",
            result.stderr.strip() or result.stdout.strip(),
        )


_STRICT_RULES = (
    "E",
    "F",
    "W",
    "I",
    "N",
    "UP",
    "B",
    "C4",
    "SIM",
    "RUF",
)

_STRICT_IGNORE = (
    "E501",
    "RUF002",
    "RUF003",
)


class RuffFormatter:
    def __init__(self, options: dict[str, Any]) -> None:
        self._options = options

    def verify(self) -> None:
        _run(["ruff", "--version"])

    def format(self, output_dir: Path) -> None:
        options = dict(self._options)
        user_select = options.pop("select", None)
        user_ignore = options.pop("ignore", None)

        common = _options_to_args(options)

        select = user_select if user_select is not None else _STRICT_RULES
        ignore = user_ignore if user_ignore is not None else _STRICT_IGNORE

        check_args = [
            *common,
            "--select", ",".join(str(rule) for rule in select),
            "--ignore", ",".join(str(rule) for rule in ignore),
        ]

        _run(["ruff", "format", *common, str(output_dir)])
        _run(["ruff", "check", "--fix", *check_args, str(output_dir)])
