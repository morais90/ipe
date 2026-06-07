from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AttachPaymentMethodRequest(BaseModel):
    type_: str
    card: dict[str, Any] | None = None
    pix: dict[str, Any] | None = None
    is_default: bool = False
