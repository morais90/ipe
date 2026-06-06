"""CreateCustomerRequest model."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class CreateCustomerRequest(BaseModel):
    email: str
    name: str | None = None
    phone: str | None = None
    document: str | None = None
    address: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
