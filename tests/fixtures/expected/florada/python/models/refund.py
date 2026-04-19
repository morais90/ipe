"""Refund model."""

from __future__ import annotations

from pydantic import BaseModel


class Refund(BaseModel):
    id: UUID
    charge_id: UUID
    amount: dict[str, Any]
    status: str
    reason: str | None = None
    created_at: datetime
