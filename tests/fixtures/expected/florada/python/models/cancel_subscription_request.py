from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class CancelSubscriptionRequest(BaseModel):
    at_period_end: bool = True
    reason: Annotated[str, Field(max_length=500)] | None = None
