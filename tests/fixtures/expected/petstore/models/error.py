"""Error model."""

from __future__ import annotations

from pydantic import BaseModel


class Error(BaseModel):
    code: int
    message: str
