from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.money import Money


class CaptureChargeRequest(BaseModel):
    amount: Money | None = None
