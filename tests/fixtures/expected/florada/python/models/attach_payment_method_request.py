from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class AttachPaymentMethodRequest(BaseModel):
    type_: Literal["card", "pix", "boleto"]
    card: dict[str, Any] | None = None
    pix: dict[str, Any] | None = None
    is_default: bool = False
