from __future__ import annotations

from pydantic import BaseModel


class CancelSubscriptionRequest(BaseModel):
    at_period_end: bool = True
    reason: str | None = None
