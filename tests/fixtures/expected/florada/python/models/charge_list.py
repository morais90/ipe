"""ChargeList model."""

from __future__ import annotations

from pydantic import BaseModel


class ChargeList(BaseModel):
    data: list
    meta: dict[str, Any]
