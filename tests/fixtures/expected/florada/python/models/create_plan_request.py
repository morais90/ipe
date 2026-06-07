from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class CreatePlanRequest(BaseModel):
    name: str
    description: str | None = None
    amount: dict[str, Any]
    interval: str
    interval_count: int = 1
    trial_days: int | None = None
    active: bool = True
    metadata: dict[str, Any] | None = None
