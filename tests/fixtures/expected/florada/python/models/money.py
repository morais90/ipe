from __future__ import annotations

from pydantic import BaseModel


class Money(BaseModel):
    amount: int
    currency: str
