from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel


class PaymentMethod(BaseModel):
    id: UUID
    type_: Literal["card", "pix", "boleto"]
    details: dict[str, Any] | None = None
    is_default: bool = False
    created_at: datetime
