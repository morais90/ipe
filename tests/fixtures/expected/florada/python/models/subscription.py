"""Subscription model."""

from __future__ import annotations

from pydantic import BaseModel


class Subscription(BaseModel):
    id: UUID
    customer_id: UUID
    plan: dict[str, Any]
    status: str
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    trial_end: datetime | None = None
    cancelled_at: datetime | None = None
    cancel_at_period_end: bool = false
    payment_method_id: UUID | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime
