from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class CreateRefundRequest(BaseModel):
    amount: dict[str, Any] | None = None
    reason: Literal["duplicate", "fraudulent", "requested_by_customer"] | None = None
