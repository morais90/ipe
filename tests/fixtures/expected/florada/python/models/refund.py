from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel


class Refund(BaseModel):
    id: UUID
    charge_id: UUID
    amount: dict[str, Any]
    status: Literal["pending", "succeeded", "failed"]
    reason: Literal["duplicate", "fraudulent", "requested_by_customer", None] | None = (
        None
    )
    created_at: datetime
