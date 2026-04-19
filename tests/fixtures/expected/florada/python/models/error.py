"""Error model."""

from __future__ import annotations

from pydantic import BaseModel


class Error(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None
