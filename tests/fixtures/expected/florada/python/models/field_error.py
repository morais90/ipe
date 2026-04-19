"""FieldError model."""

from __future__ import annotations

from pydantic import BaseModel


class FieldError(BaseModel):
    field: str
    message: str
    code: str | None = None
