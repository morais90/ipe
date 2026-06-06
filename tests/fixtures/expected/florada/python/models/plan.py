"""Plan model."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Plan(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    amount: dict[str, Any]
    interval: str
    interval_count: int = 1
    trial_days: int = 0
    active: bool = True
    metadata: dict[str, Any] | None = None
