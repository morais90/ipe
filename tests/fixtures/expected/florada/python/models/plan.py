"""Plan model."""

from __future__ import annotations

from pydantic import BaseModel


class Plan(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    amount: dict[str, Any]
    interval: str
    interval_count: int = 1
    trial_days: int = 0
    active: bool = true
    metadata: dict[str, Any] | None = None
