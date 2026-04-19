"""CardDetails model."""

from __future__ import annotations

from pydantic import BaseModel


class CardDetails(BaseModel):
    brand: str
    last4: str
    exp_month: int
    exp_year: int
    funding: str | None = None
    country: str | None = None
