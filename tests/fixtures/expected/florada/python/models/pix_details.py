from __future__ import annotations

from pydantic import BaseModel


class PixDetails(BaseModel):
    key_type: str | None = None
    key: str | None = None
