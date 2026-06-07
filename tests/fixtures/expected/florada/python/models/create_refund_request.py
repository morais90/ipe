from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class CreateRefundRequest(BaseModel):
    amount: dict[str, Any] | None = None
    reason: str | None = None
