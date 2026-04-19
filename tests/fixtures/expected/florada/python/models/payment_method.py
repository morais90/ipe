"""PaymentMethod model."""

from __future__ import annotations

from pydantic import BaseModel


class PaymentMethod(BaseModel):
    id: UUID
    type_: str
    details: dict[str, Any] | None = None
    is_default: bool = false
    created_at: datetime
