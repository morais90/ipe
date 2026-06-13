from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from florada_payments.models.money import Money


class CreateChargeRequest(BaseModel):
    amount: Money
    customer_id: UUID | None = None
    payment_method_id: UUID
    description: str | None = None
    capture_method: Literal["automatic", "manual"] = "automatic"
    statement_descriptor: Annotated[str, Field(max_length=22)] | None = None
    metadata: dict[str, Any] | None = None
