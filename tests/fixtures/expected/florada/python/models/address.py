"""Address model."""

from __future__ import annotations

from pydantic import BaseModel


class Address(BaseModel):
    street: str
    number: str | None = None
    complement: str | None = None
    neighborhood: str | None = None
    city: str
    state: str
    postal_code: str
    country: str
