from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

if TYPE_CHECKING:
    from florada_payments.models.address import Address


class CreateCustomerRequest(BaseModel):
    email: str
    name: str | None = None
    phone: str | None = None
    document: str | None = None
    address: Address | None = None
    metadata: dict[str, Any] | None = None
