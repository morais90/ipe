"""Pet model."""

from __future__ import annotations

from pydantic import BaseModel


class Pet(BaseModel):
    id: int
    name: str
    tag: str | None = None
