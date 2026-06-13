from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.address import Address


class PatchCustomerRequest(BaseModel):
    email: str | None = None
    name: str | None = None
    phone: str | None = None
    document: str | None = None
    address: Address | None = None
    default_payment_method_id: UUID | None = None
    metadata: dict[str, Any] | None = None
