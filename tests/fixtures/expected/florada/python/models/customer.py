"""Customer model."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class Customer(BaseModel):
    id: UUID
    email: str
    name: str | None = None
    phone: str | None = None
    document: str | None = None
    address: dict[str, Any] | None = None
    default_payment_method_id: UUID | None = None
    metadata: dict[str, Any] | None = None
    created_at: datetime
