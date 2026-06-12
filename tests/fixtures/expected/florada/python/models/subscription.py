from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Literal
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.plan import Plan


class Subscription(BaseModel):
    id: UUID
    customer_id: UUID
    plan: Plan
    status: Literal["active", "past_due", "cancelled", "trialing", "paused"]
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    trial_end: datetime | None = None
    cancelled_at: datetime | None = None
    cancel_at_period_end: bool = False
    payment_method_id: UUID | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime
