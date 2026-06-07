from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class PaymentMethod(BaseModel):
    id: UUID
    type_: str
    details: dict[str, Any] | None = None
    is_default: bool = False
    created_at: datetime
