"""CreateChargeRequest model."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel


class CreateChargeRequest(BaseModel):
    amount: dict[str, Any]
    customer_id: UUID | None = None
    payment_method_id: UUID
    description: str | None = None
    capture_method: str = 'automatic'
    statement_descriptor: str | None = None
    metadata: dict[str, Any] | None = None
