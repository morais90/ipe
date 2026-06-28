import sys
import time
from pathlib import Path
from types import TracebackType
from typing import Annotated

import typer
from rich.traceback import install

from ipe import __version__
from ipe.cli.console import console
from ipe.core.analyzer import SpecAnalyzer
from ipe.core.config import IpeConfig, resolve_config, save_config
from ipe.core.exceptions import IpeError
from ipe.core.generator import CodeGenerator
from ipe.parsers.models import OpenAPISpec
from ipe.utils.naming import to_snake_case

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
        str | None,
        typer.Argument(help="Path or URL to OpenAPI specification"),
    ] = None,
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory"),
    ] = None,
    target: Annotated[
        str | None,
        typer.Option("--target", "-t", help="Target language"),
    ] = None,
    module_name: Annotated[
        str | None,
        typer.Option("--module-name", "-m", help="Generated module name"),
    ] = None,
    config: Annotated[
        Path,
        typer.Option("--config", help="Configuration file"),
    ] = Path("ipe.json"),
) -> None:
    """Generate code from an OpenAPI specification."""
    resolved = resolve_config(
        config,
        spec=spec,
        output=output,
        target=target,
        module_name=module_name,
    )

    if not resolved.spec_path:
        console.error("No OpenAPI spec provided")
        console.info("Pass a spec ('ipe generate api.yaml -o ./out') or run 'ipe init'")
        raise typer.Exit(code=2)

    start = time.monotonic()
    try:
        with console.generation_progress(
            __version__, resolved.target, resolved.spec_path
        ) as progress:
            result = CodeGenerator().run(
                resolved,
                on_phase=progress.on_phase,
                on_file=progress.on_file,
            )
    except IpeError as exc:
        console.error(str(exc))
        if exc.suggestion:
            console.info(f"Suggestion: {exc.suggestion}")
        raise typer.Exit(code=1) from exc

    duration = time.monotonic() - start
    console.print_completion(
        api_name=result.api_name,
        operations=result.operations,
        models=result.models,
        resources=result.resources,
        files=len(result.files),
        output_path=str(resolved.output_dir),
        duration=duration,
    )


@app.command()
def init(
    config: Annotated[
        Path,
        typer.Option("--config", help="Configuration file"),
    ] = Path("ipe.json"),
) -> None:
    """Set up an ipe.json project configuration interactively."""
    console.print_header()

    if config.exists() and not console.confirm(
        f"{config} already exists. Overwrite?", default=False
    ):
        console.warning("Cancelled.")
        raise typer.Exit()

    spec = console.ask("OpenAPI spec (file path or URL)")
    parsed = _validate_spec(spec)

    suggested_module = to_snake_case(parsed.info.title) if parsed else "api_client"
    module_name = console.ask("Module name", default=suggested_module)
    output = console.ask("Output directory", default=f"./{module_name}")
    target = console.ask("Target language", default="python")

    if parsed is None and not console.confirm(
        "Spec could not be validated. Save anyway?", default=True
    ):
        console.warning("Cancelled.")
        raise typer.Exit()

    save_config(
        IpeConfig(
            spec_path=spec,
            output_dir=Path(output),
            target=target,
            module_name=module_name,
        ),
        config,
    )

    console.print()
    console.info(f"Created {config}")
    console.print("  Next: run [bold magenta]ipe generate[/]")


def _validate_spec(spec: str) -> OpenAPISpec | None:
    try:
        parsed = SpecAnalyzer().parse(spec)
    except IpeError as exc:
        console.error(str(exc))
        if exc.suggestion:
            console.info(f"Suggestion: {exc.suggestion}")
        return None

    paths = len(parsed.paths or {})
    console.info(
        f"Validated {parsed.info.title} v{parsed.info.version} — {paths} paths"
    )
    return parsed


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
