"""PatchCustomerRequest model."""

from __future__ import annotations

from pydantic import BaseModel


class PatchCustomerRequest(BaseModel):
    email: str | None = None
    name: str | None = None
    phone: str | None = None
    document: str | None = None
    address: dict[str, Any] | None = None
    default_payment_method_id: UUID | None = None
    metadata: dict[str, Any] | None = None
