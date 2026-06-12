from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from florada_payments.models.customer import Customer
    from florada_payments.models.dispute import Dispute
    from florada_payments.models.money import Money
    from florada_payments.models.payment_method import PaymentMethod


class Charge(BaseModel):
    id: UUID
    amount: Money
    status: Literal["pending", "succeeded", "failed", "refunded", "disputed"]
    description: str | None = None
    customer: Customer | None = None
    customer_id: UUID | None = None
    payment_method: PaymentMethod | None = None
    payment_method_id: UUID | None = None
    capture_method: Literal["automatic", "manual"] = "automatic"
    captured: bool = False
    refunded_amount: Money | None = None
    dispute: Dispute | None = None
    metadata: dict[str, Any] | None = None
    statement_descriptor: Annotated[str, Field(max_length=22)] | None = None
    created_at: datetime
    captured_at: datetime | None = None
