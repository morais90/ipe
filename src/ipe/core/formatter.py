from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, Field


class FormatterConfig(BaseModel):
    name: str
    options: dict[str, Any] = Field(default_factory=dict)


class Formatter(Protocol):
    def verify(self) -> None:
        """Check that the formatter is available for use."""
        ...

    def format(self, output_dir: Path) -> None:
        """Format generated code in place.

        Parameters
        ----------
        output_dir : Path
            The directory of generated files to format.
        """
        ...
