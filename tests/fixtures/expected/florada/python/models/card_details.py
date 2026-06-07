from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class CardDetails(BaseModel):
    brand: Literal["visa", "mastercard", "amex", "elo", "hipercard"]
    last4: Annotated[str, Field(min_length=4, max_length=4)]
    exp_month: Annotated[int, Field(ge=1, le=12)]
    exp_year: int
    funding: Literal["credit", "debit", "prepaid"] | None = None
    country: str | None = None
