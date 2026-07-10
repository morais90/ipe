import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.prompt import Confirm, Prompt
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

_TOTAL_FLOWERS = 16
_BLOOM_INTERVAL = 0.4
_FULL_BLOOM_TIME = _TOTAL_FLOWERS * _BLOOM_INTERVAL

_IPE_PALETTE = ("yellow", "bright_magenta", "magenta", "white")
_WAVE_CYCLE = 3.0
_WAVE_SPREAD = 0.18

_CROWN_TEMPLATE = (
    "      {f1} {f2} {f3}",
    "    {f4} {f5} {f6} {f7} {f8}",
    "    {f9} {f10} {f11} {f12} {f13}",
    "      {f14} {f15} {f16}",
)

_TRUNK_LINES = (
    "       [dim]╲[/][bold yellow]│[/][dim]╱[/]",  # noqa: RUF001
    "        [bold yellow]┃[/]",
    "        [bold yellow]┃[/]",
    "        [bold yellow]┃[/]",
    "      [dim]──[/][bold yellow]┻[/][dim]──[/]",
)

_BLOOM_ORDER: tuple[int, ...] = (
    14,
    15,
    16,
    9,
    10,
    11,
    12,
    13,
    4,
    5,
    6,
    7,
    8,
    1,
    2,
    3,
)


def _format_duration(seconds: float) -> str:
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    if seconds < 60:
        return f"{seconds:.2f}s"
    return f"{seconds / 60:.1f}m"


class BloomingTree:
    def __init__(self, version: str, target: str, spec_path: str) -> None:
        self._version = version
        self._target = target
        self._spec_path = spec_path
        self._total_start = time.monotonic()
        self._current_phase: str | None = None
        self._current_start: float = 0.0
        self._current_files: int = 0
        self._finished = False

    def start_phase(self, name: str) -> None:
        """Begin tracking a new generation phase.

        Parameters
        ----------
        name : str
            The name of the phase now in progress.
        """
        self._current_phase = name
        self._current_start = time.monotonic()
        self._current_files = 0

    def add_file(self, _: Path) -> None:
        """Record that a file was produced in the current phase.

        Parameters
        ----------
        _ : Path
            The path of the generated file (unused).
        """
        self._current_files += 1

    def finish(self) -> None:
        """Mark generation as complete and fully bloom the tree."""
        self._finished = True
        self._current_phase = None

    def _bloom_count(self) -> int:
        if self._finished:
            return _TOTAL_FLOWERS
        elapsed = time.monotonic() - self._total_start
        return min(int(elapsed / _BLOOM_INTERVAL), _TOTAL_FLOWERS)

    def __rich__(self) -> RenderableType:
        layout = Table.grid(padding=(0, 4))
        layout.add_column()
        layout.add_column(vertical="middle")
        layout.add_row(self._render_tree(), self._render_info())

        parts: list[RenderableType] = [layout]
        if self._current_phase is not None:
            parts.append(Text(""))
            parts.append(self._render_active())
        return Group(*parts)

    def _render_tree(self) -> Text:
        bloomed = set(_BLOOM_ORDER[: self._bloom_count()])
        flowers = {
            f"f{i}": f"[{self._flower_style(i)}]❀[/]" if i in bloomed else "[dim]·[/]"
            for i in range(1, _TOTAL_FLOWERS + 1)
        }
        crown_lines = [row.format(**flowers) for row in _CROWN_TEMPLATE]
        all_lines = crown_lines + list(_TRUNK_LINES)
        return Text.from_markup("\n".join(all_lines))

    def _flower_style(self, position: int) -> str:
        if self._finished:
            return "bold yellow"

        elapsed = time.monotonic() - self._total_start
        if elapsed < _FULL_BLOOM_TIME:
            return "bold yellow"

        bloom_index = _BLOOM_ORDER.index(position)
        offset = (elapsed - _FULL_BLOOM_TIME) + bloom_index * _WAVE_SPREAD
        normalized = (offset % _WAVE_CYCLE) / _WAVE_CYCLE
        color = _IPE_PALETTE[int(normalized * len(_IPE_PALETTE))]
        return f"bold {color}"

    def _render_info(self) -> Text:
        return Text.assemble(
            ("ipê  ", "bold magenta"),
            (self._version, "dim"),
            "\n",
            ("OpenAPI → ", "dim"),
            (self._target, "cyan"),
            "\n",
            (f"from {self._spec_path}", "dim"),
        )

    def _render_active(self) -> RenderableType:
        elapsed = _format_duration(time.monotonic() - self._current_start)
        info_parts = [elapsed]
        if self._current_files:
            info_parts.append(f"{self._current_files:,} files")
        info = " · ".join(info_parts)

        text = Text.assemble(
            (f" {self._current_phase}", "bold cyan"),
            ("  ", ""),
            (info, "dim"),
        )

        row = Table.grid(padding=(0, 1))
        row.add_column(width=2)
        row.add_column()
        row.add_row(Spinner("dots", style="cyan"), text)
        return row


class GenerationProgress:
    def __init__(self, tree: BloomingTree) -> None:
        self._tree = tree

    def on_phase(self, name: str) -> None:
        """Report that a new phase has started.

        Parameters
        ----------
        name : str
            The name of the phase now in progress.
        """
        self._tree.start_phase(name)

    def on_file(self, path: Path) -> None:
        """Report that a file was generated.

        Parameters
        ----------
        path : Path
            The path of the generated file.
        """
        self._tree.add_file(path)


class IpeConsole:
    def __init__(self) -> None:
        self.console = Console()

    @contextmanager
    def generation_progress(
        self,
        version: str,
        target: str,
        spec_path: str,
    ) -> Iterator[GenerationProgress]:
        """Display a live blooming-tree progress view during generation.

        Parameters
        ----------
        version : str
            The Ipê version to show in the banner.
        target : str
            The language target being generated.
        spec_path : str
            Path or URL of the spec being generated from.

        Yields
        ------
        GenerationProgress
            A handle for reporting phase and file progress.
        """
        tree = BloomingTree(version, target, spec_path)
        progress = GenerationProgress(tree)
        self.console.print()
        with Live(tree, console=self.console, refresh_per_second=12):
            try:
                yield progress
            finally:
                tree.finish()
        self.console.print()

    def print_completion(
        self,
        api_name: str,
        operations: int,
        models: int,
        resources: int,
        files: int,
        output_path: str,
        duration: float,
    ) -> None:
        """Print a summary of a completed generation run.

        Parameters
        ----------
        api_name : str
            The name of the generated API.
        operations : int
            The number of operations generated.
        models : int
            The number of models generated.
        resources : int
            The number of resource groups generated.
        files : int
            The number of files written.
        output_path : str
            The directory the code was written to.
        duration : float
            The total generation time in seconds.
        """
        self.console.print(
            Text.assemble(
                ("  ❀── ", "bold yellow"),
                ("ready ", "bold"),
                (f"in {_format_duration(duration)}", "dim"),
            )
        )
        self._stat_row("api", api_name)
        self._stat_row("ops", f"{operations:,}")
        self._stat_row("models", f"{models:,}")
        self._stat_row("resources", f"{resources:,}")
        self._stat_row("files", f"{files:,}")
        self.console.print(
            Text.assemble(
                ("  └── ", "bold yellow"),
                (f"at {output_path}", "dim"),
            )
        )
        self.console.print()

    def _stat_row(self, label: str, value: str) -> None:
        self.console.print(
            Text.assemble(
                ("  │   ", "bold yellow"),
                (f"{label:<10}", "dim"),
                value,
            )
        )

    def error(self, message: str) -> None:
        """Print an error message.

        Parameters
        ----------
        message : str
            The error text to display.
        """
        self.console.print(Text.assemble(("✗  ", "bold red"), (message, "red")))

    def info(self, message: str) -> None:
        """Print an informational message.

        Parameters
        ----------
        message : str
            The text to display.
        """
        self.console.print(Text.assemble(("> ", "blue"), message))

    def warning(self, message: str) -> None:
        """Print a warning message.

        Parameters
        ----------
        message : str
            The warning text to display.
        """
        self.console.print(Text.assemble(("!  ", "bold yellow"), (message, "yellow")))

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print renderables to the console.

        Parameters
        ----------
        *args : Any
            Positional renderables passed through to Rich.
        **kwargs : Any
            Keyword arguments passed through to Rich.
        """
        self.console.print(*args, **kwargs)

    def ask(self, prompt: str, default: str | None = None) -> str:
        """Prompt the user for a text value.

        Parameters
        ----------
        prompt : str
            The question to display.
        default : str, optional
            The value returned when the user enters nothing.

        Returns
        -------
        str
            The user's response.
        """
        if default is None:
            return Prompt.ask(prompt, console=self.console)
        return Prompt.ask(prompt, default=default, console=self.console)

    def confirm(self, prompt: str, *, default: bool = False) -> bool:
        """Prompt the user for a yes/no answer.

        Parameters
        ----------
        prompt : str
            The question to display.
        default : bool, optional
            The answer returned when the user enters nothing.

        Returns
        -------
        bool
            The user's confirmation.
        """
        return Confirm.ask(prompt, default=default, console=self.console)

    def print_header(self) -> None:
        """Print the Ipê banner header."""
        self.console.print(
            Text.assemble(
                ("❀  ", "bold yellow"),
                ("ipê", "bold magenta"),
                ("  OpenAPI Code Generator", "dim"),
            )
        )
        self.console.print()


console = IpeConsole()
