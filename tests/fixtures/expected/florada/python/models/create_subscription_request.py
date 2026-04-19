"""CreateSubscriptionRequest model."""

from __future__ import annotations

from pydantic import BaseModel


class CreateSubscriptionRequest(BaseModel):
    plan_id: UUID
    payment_method_id: UUID | None = None
    trial_days: int | None = None
    metadata: dict[str, Any] | None = None
