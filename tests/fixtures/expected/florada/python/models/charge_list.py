"""ChargeList model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ChargeList(BaseModel):
    data: list
    meta: dict[str, Any]
