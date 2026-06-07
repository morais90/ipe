from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Charge(BaseModel):
    id: UUID
    amount: dict[str, Any]
    status: str
    description: str | None = None
    customer: dict[str, Any] | None = None
    customer_id: UUID | None = None
    payment_method: dict[str, Any] | None = None
    payment_method_id: UUID | None = None
    capture_method: str = 'automatic'
    captured: bool = False
    refunded_amount: dict[str, Any] | None = None
    dispute: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    statement_descriptor: str | None = None
    created_at: datetime
    captured_at: datetime | None = None
