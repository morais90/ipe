"""Rich console utilities for beautiful CLI output."""

from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text


class IpeConsole:
    """Beautiful console interface for Ipê CLI.

    Provides consistent styling and formatting for all CLI output with
    emojis, colors, and progress indicators as specified in the CLI design.
    """

    def __init__(self) -> None:
        """Initialize the console with Rich styling."""
        self.console = Console()
        self._progress: Progress | None = None

    def print_header(self) -> None:
        """Print the Ipê header with branding."""
        header = Text("🌳 Ipê - OpenAPI Code Generator", style="bold magenta")
        self.console.print(header)
        self.console.print()

    def success(self, message: str) -> None:
        """Print a success message with green checkmark.

        Parameters
        ----------
        message : str
            The success message to display.

        Examples
        --------
        >>> console = IpeConsole()
        >>> console.success("Generated successfully!")
        """
        self.console.print(f"✅ {message}", style="bold green")

    def error(self, message: str) -> None:
        """Print an error message with red X mark.

        Parameters
        ----------
        message : str
            The error message to display.

        Examples
        --------
        >>> console = IpeConsole()
        >>> console.error("OpenAPI specification is invalid")
        """
        self.console.print(f"❌ {message}", style="bold red")

    def info(self, message: str) -> None:
        """Print an informational message with blue info icon.

        Parameters
        ----------
        message : str
            The informational message to display.

        Examples
        --------
        >>> console = IpeConsole()
        >>> console.info("Found 25 endpoints, 12 models")
        """
        self.console.print(f"📋 {message}", style="bold blue")

    def warning(self, message: str) -> None:
        """Print a warning message with yellow warning icon.

        Parameters
        ----------
        message : str
            The warning message to display.

        Examples
        --------
        >>> console = IpeConsole()
        >>> console.warning("Using default configuration")
        """
        self.console.print(f"⚠️  {message}", style="bold yellow")

    def print_validation_error(
        self, error_msg: str, suggestion: str | None = None
    ) -> None:
        """Print a detailed validation error with helpful formatting.

        Parameters
        ----------
        error_msg : str
            The main error message.
        suggestion : str, optional
            A helpful suggestion to fix the error.

        Examples
        --------
        >>> console = IpeConsole()
        >>> console.print_validation_error(
        ...     "Missing required field 'description'",
        ...     "Add a description for the 200 response"
        ... )
        """
        self.error("OpenAPI specification is invalid")
        self.console.print()

        panel_content = f"📍 {error_msg}"
        if suggestion:
            panel_content += f"\n\n💡 Suggestion:\n   {suggestion}"

        panel = Panel(
            panel_content,
            title="Validation Error",
            title_align="left",
            border_style="red",
            padding=(1, 2),
        )
        self.console.print(panel)

    def print_generation_summary(
        self, output_path: str, files_created: int, duration: float
    ) -> None:
        """Print a beautiful generation completion summary.

        Parameters
        ----------
        output_path : str
            Path where files were generated.
        files_created : int
            Number of files created.
        duration : float
            Time taken in seconds.

        Examples
        --------
        >>> console = IpeConsole()
        >>> console.print_generation_summary("./client", 8, 0.8)
        """
        self.success("Generated successfully!")

        summary = (
            f"📁 Output: {output_path}\n"
            f"📊 Files: {files_created} created\n"
            f"⏱️  Time: {duration:.1f}s"
        )

        panel = Panel(
            summary,
            title="Generation Complete",
            title_align="left",
            border_style="green",
            padding=(1, 2),
        )
        self.console.print(panel)

    def print_next_steps(self, module_name: str, client_class: str) -> None:
        """Print helpful next steps after generation.

        Parameters
        ----------
        module_name : str
            The generated module name.
        client_class : str
            The main client class name.

        Examples
        --------
        >>> console = IpeConsole()
        >>> console.print_next_steps("petstore_client", "PetStoreClient")
        """
        steps = (
            f"• Import: from {module_name} import {client_class}\n"
            f'• Usage: client = {client_class}(base_url="https://api.example.com")'
        )

        panel = Panel(
            steps,
            title="💡 Next steps",
            title_align="left",
            border_style="blue",
            padding=(1, 2),
        )
        self.console.print(panel)

    def start_progress(self, description: str) -> None:
        """Start a progress indicator for long-running operations.

        Parameters
        ----------
        description : str
            Description of the operation in progress.

        Examples
        --------
        >>> console = IpeConsole()
        >>> console.start_progress("Validating OpenAPI specification...")
        """
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=self.console,
        )
        self._progress.start()
        self._progress.add_task(description)

    def stop_progress(self) -> None:
        """Stop the current progress indicator."""
        if self._progress:
            self._progress.stop()
            self._progress = None

    def print_url_fetch(self, url: str, size_kb: float) -> None:
        """Print URL fetch completion message.

        Parameters
        ----------
        url : str
            The URL that was fetched.
        size_kb : float
            Size of the downloaded content in KB.

        Examples
        --------
        >>> console = IpeConsole()
        >>> console.print_url_fetch("https://api.example.com/openapi.yaml", 24.5)
        """
        self.console.print("🌐 Fetching OpenAPI specification from URL...")
        self.console.print(f"   📡 GET {url}")
        self.success(f"Downloaded successfully ({size_kb:.1f} KB)")

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Pass-through to Rich console print for custom formatting.

        Parameters
        ----------
        *args : Any
            Arguments to pass to Rich console.print().
        **kwargs : Any
            Keyword arguments to pass to Rich console.print().
        """
        self.console.print(*args, **kwargs)


# Global console instance for consistent usage across CLI
console = IpeConsole()
