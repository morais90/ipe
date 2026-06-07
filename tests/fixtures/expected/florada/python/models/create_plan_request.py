from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class CreatePlanRequest(BaseModel):
    name: str
    description: str | None = None
    amount: dict[str, Any]
    interval: Literal["daily", "weekly", "monthly", "yearly"]
    interval_count: Annotated[int, Field(ge=1)] = 1
    trial_days: Annotated[int, Field(ge=0)] | None = None
    active: bool = True
    metadata: dict[str, Any] | None = None
