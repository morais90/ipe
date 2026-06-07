from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class Charge(BaseModel):
    id: UUID
    amount: dict[str, Any]
    status: Literal["pending", "succeeded", "failed", "refunded", "disputed"]
    description: str | None = None
    customer: dict[str, Any] | None = None
    customer_id: UUID | None = None
    payment_method: dict[str, Any] | None = None
    payment_method_id: UUID | None = None
    capture_method: Literal["automatic", "manual"] = "automatic"
    captured: bool = False
    refunded_amount: dict[str, Any] | None = None
    dispute: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    statement_descriptor: Annotated[str, Field(max_length=22)] | None = None
    created_at: datetime
    captured_at: datetime | None = None
