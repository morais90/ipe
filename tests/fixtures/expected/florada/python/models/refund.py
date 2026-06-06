"""Refund model."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Refund(BaseModel):
    id: UUID
    charge_id: UUID
    amount: dict[str, Any]
    status: str
    reason: str | None = None
    created_at: datetime
