"""CancelSubscriptionRequest model."""

from __future__ import annotations

from pydantic import BaseModel


class CancelSubscriptionRequest(BaseModel):
    at_period_end: bool = true
    reason: str | None = None
