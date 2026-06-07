from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, Field


class FormatterConfig(BaseModel):
    name: str
    options: dict[str, Any] = Field(default_factory=dict)


class Formatter(Protocol):
    def verify(self) -> None: ...

    def format(self, output_dir: Path) -> None: ...
