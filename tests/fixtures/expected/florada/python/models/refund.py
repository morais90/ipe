from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.money import Money


class Refund(BaseModel):
    id: UUID
    charge_id: UUID
    amount: Money
    status: Literal["pending", "succeeded", "failed"]
    reason: Literal["duplicate", "fraudulent", "requested_by_customer", None] | None = (
        None
    )
    created_at: datetime
