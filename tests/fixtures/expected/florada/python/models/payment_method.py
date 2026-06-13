from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Literal
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.boleto_details import BoletoDetails
    from florada_payments.models.card_details import CardDetails
    from florada_payments.models.pix_details import PixDetails


class PaymentMethod(BaseModel):
    id: UUID
    type_: Literal["card", "pix", "boleto"]
    details: CardDetails | PixDetails | BoletoDetails | None = None
    is_default: bool = False
    created_at: datetime
