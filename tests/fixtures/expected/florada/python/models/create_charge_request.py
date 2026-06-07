from __future__ import annotations

from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateChargeRequest(BaseModel):
    amount: dict[str, Any]
    customer_id: UUID | None = None
    payment_method_id: UUID
    description: str | None = None
    capture_method: Literal["automatic", "manual"] = "automatic"
    statement_descriptor: Annotated[str, Field(max_length=22)] | None = None
    metadata: dict[str, Any] | None = None
