"""PaginationMeta model."""

from __future__ import annotations

from pydantic import BaseModel


class PaginationMeta(BaseModel):
    total: int | None = None
    has_more: bool | None = None
    next_cursor: str | None = None
