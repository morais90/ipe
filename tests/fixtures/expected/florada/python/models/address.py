from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class Address(BaseModel):
    street: str
    number: str | None = None
    complement: str | None = None
    neighborhood: str | None = None
    city: str
    state: str
    postal_code: str
    country: Annotated[str, Field(min_length=2, max_length=2)]
