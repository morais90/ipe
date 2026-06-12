from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from florada_payments.models.money import Money


class Plan(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    amount: Money
    interval: Literal["daily", "weekly", "monthly", "yearly"]
    interval_count: Annotated[int, Field(ge=1)] = 1
    trial_days: Annotated[int, Field(ge=0)] = 0
    active: bool = True
    metadata: dict[str, Any] | None = None
