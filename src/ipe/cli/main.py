import sys
import time
from pathlib import Path
from types import TracebackType
from typing import Annotated

import typer
from rich.traceback import install

from ipe import __version__
from ipe.cli.console import console
from ipe.core.config import IpeConfig
from ipe.core.exceptions import IpeError
from ipe.core.generator import CodeGenerator

install(show_locals=True)

app = typer.Typer(
    name="ipe",
    help="🌳 Ipê - A next-generation OpenAPI code generator",
    no_args_is_help=True,
    rich_markup_mode="rich",
    context_settings={"help_option_names": ["-h", "--help"]},
)


def version_callback(value: bool) -> None:
    """Show version information and exit.

    Parameters
    ----------
    value : bool
        Whether the version flag was provided.

    Raises
    ------
    typer.Exit
        Always exits after showing version.
    """
    if value:
        console.print_header()
        console.info(f"Version: {__version__}")
        console.info("Python compatibility: 3.9+")
        console.print()
        console.print("🔗 Documentation: https://github.com/ipeproject/ipe#readme")
        console.print("🐛 Issues: https://github.com/ipeproject/ipe/issues")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show version information and exit.",
        ),
    ] = None,
) -> None:
    """🌳 Ipê - A next-generation OpenAPI code generator with an obsession for developer experience."""


@app.command()
def generate(
    spec: Annotated[
        str,
        typer.Argument(help="Path or URL to OpenAPI specification"),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output directory"),
    ] = Path("./output"),
    target: Annotated[
        str,
        typer.Option("--target", "-t", help="Target language"),
    ] = "python",
    module_name: Annotated[
        str | None,
        typer.Option("--module-name", "-m", help="Generated module name"),
    ] = None,
) -> None:
    """Generate code from an OpenAPI specification."""
    console.print_header()
    console.info(f"Generating {target} client from {spec}")

    config = IpeConfig(
        spec_path=spec,
        output_dir=output,
        target=target,
        module_name=module_name,
    )

    start = time.monotonic()
    try:
        written = CodeGenerator().run(config)
    except IpeError as exc:
        console.error(str(exc))
        if exc.suggestion:
            console.info(f"Suggestion: {exc.suggestion}")
        raise typer.Exit(code=1) from exc

    duration = time.monotonic() - start
    console.print_generation_summary(str(output), len(written), duration)


@app.command()
def version() -> None:
    """Show version information."""
    console.print_header()
    console.info(f"Version: {__version__}")
    console.info("Python compatibility: 3.12+")
    console.print()
    console.print("🔗 Documentation: https://github.com/ipeproject/ipe#readme")
    console.print("🐛 Issues: https://github.com/ipeproject/ipe/issues")


def handle_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    """Handle uncaught exceptions with beautiful error formatting.

    Parameters
    ----------
    exc_type : type[BaseException]
        The exception type.
    exc_value : BaseException
        The exception instance.
    exc_traceback : Optional[TracebackType]
        The traceback object.
    """
    if exc_type is KeyboardInterrupt:
        console.print()
        console.warning("Operation cancelled by user")
        sys.exit(1)

    console.error("An unexpected error occurred")
    console.print()

    if hasattr(exc_value, "__cause__") and exc_value.__cause__:
        console.print(f"💥 {exc_value.__cause__}")
    else:
        console.print(f"💥 {exc_value}")


def cli_main() -> None:
    """Entry point for the CLI application."""
    sys.excepthook = handle_exception
    app()


if __name__ == "__main__":
    cli_main()
