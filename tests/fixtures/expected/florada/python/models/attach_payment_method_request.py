"""AttachPaymentMethodRequest model."""

from __future__ import annotations

from pydantic import BaseModel


class AttachPaymentMethodRequest(BaseModel):
    type_: str
    card: dict[str, Any] | None = None
    pix: dict[str, Any] | None = None
    is_default: bool = false
