from __future__ import annotations

from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, Field


class CreateSubscriptionRequest(BaseModel):
    plan_id: UUID
    payment_method_id: UUID | None = None
    trial_days: Annotated[int, Field(ge=0, le=365)] | None = None
    metadata: dict[str, Any] | None = None
