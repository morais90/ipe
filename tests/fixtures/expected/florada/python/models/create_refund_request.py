from __future__ import annotations

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.money import Money


class CreateRefundRequest(BaseModel):
    amount: Money | None = None
    reason: Literal["duplicate", "fraudulent", "requested_by_customer"] | None = None
